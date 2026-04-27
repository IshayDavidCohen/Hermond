import collections
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Union

from app.order.domain.entities.order import Order, OrderStatus
from app.order.domain.repository_interfaces import IOrderRepository
from app.order.infrastructure.clients.identity_client import IdentityClient
from app.order.infrastructure.clients.catalogue_client import CatalogueClient
from app.shared.events.publisher import EventPublisher
from app.shared.exceptions import NotFoundError, ValidationError, ConflictError
from app.shared.utils import to_oid

logger = logging.getLogger(__name__)

DEFAULT_RECENT_HISTORY_WINDOW = timedelta(days=7)
HISTORY_PAGE_MAX = 100


def _parse_history_cursor(cursor: Optional[str]) -> Optional[datetime]:
    """Opaque ISO-8601 cursor from a previous page. Malformed = start over."""
    if not cursor:
        return None
    try:
        return datetime.fromisoformat(cursor)
    except (ValueError, TypeError):
        return None

class OrderService:
    def __init__(
        self,
        order_repository: IOrderRepository,
        identity_client: IdentityClient,
        catalogue_client: CatalogueClient,
        event_publisher: EventPublisher,
    ):
        self.order_repository = order_repository
        self.identity_client = identity_client
        self.catalogue_client = catalogue_client
        self.event_publisher = event_publisher

    async def create_order_for_each_supplier(self, order_data: Dict) -> Union[bool, Dict]:
        business_id = order_data["business"]
        orders_by_supplier: Dict[str, Dict[str, int]] = order_data["orders"]

        biz_exists = await self.identity_client.business_exists(business_id)
        if not biz_exists:
            raise NotFoundError(f"Business {business_id} not found")

        item_ids: List[str] = [
            iid for sup in orders_by_supplier.values() for iid in sup.keys()
        ]
        if not item_ids:
            raise ValidationError("No items in order")

        item_docs = await self.catalogue_client.get_items_batch(item_ids)
        if not item_docs:
            raise NotFoundError("Items not found")

        got_ids = [str(d["_id"]) for d in item_docs]
        if collections.Counter(item_ids) != collections.Counter(got_ids):
            missing = list(
                (collections.Counter(item_ids) - collections.Counter(got_ids)).keys()
            )
            raise ValidationError(f"Missing items: {missing}")

        items: Dict[str, Dict] = {str(d["_id"]): d for d in item_docs}

        created = {}
        failed = {}

        for supplier_id, supplier_order in orders_by_supplier.items():
            sup_exists = await self.identity_client.supplier_exists(supplier_id)
            if not sup_exists:
                failed[supplier_id] = {"error": "supplier_not_found"}
                continue

            ordered_items = []
            total_price = 0.0

            for item_id, quantity in supplier_order.items():
                item = items.get(item_id)
                if not item:
                    failed.setdefault(supplier_id, {"error": "missing_items_for_supplier", "items": []})
                    failed[supplier_id]["items"].append(item_id)
                    continue

                if str(item.get("supplier_id")) != supplier_id:
                    failed.setdefault(supplier_id, {"error": "item_supplier_mismatch", "items": []})
                    failed[supplier_id]["items"].append(item_id)
                    continue

                base_price = float(item.get("base_price", 0))
                price_at_order = base_price
                custom_prices = item.get("custom_prices", {})
                if custom_prices and custom_prices.get(business_id):
                    price_at_order = float(custom_prices[business_id])

                line_total = float(quantity) * float(price_at_order)
                total_price += line_total

                ordered_items.append({
                    "item_id": item_id,
                    "quantity": int(quantity),
                    "base_price": base_price,
                    "price_at_order": float(price_at_order),
                    "total_price_for_item": float(line_total),
                })

            if supplier_id in failed:
                continue

            order_id = self.order_repository.create_order({
                "supplier_id": supplier_id,
                "business_id": business_id,
                "estimated_eta": None,
                "ordered_items": ordered_items,
                "totalPrice": float(total_price),
            })

            supplier_linked = await self.identity_client.add_supplier_active_order(supplier_id, order_id)
            business_linked = await self.identity_client.add_business_active_order(business_id, order_id)

            if not supplier_linked or not business_linked:
                failed[supplier_id] = {"error": "link_failed", "order_id": order_id}
                continue

            # ── Inventory decrement event ────────────────────────
            try:
                self.event_publisher.publish("order.created", {
                    "order_id": order_id,
                    "supplier_id": supplier_id,
                    "items": [
                        {"item_id": oi["item_id"], "quantity": oi["quantity"]}
                        for oi in ordered_items
                    ],
                })
            except Exception:
                logger.warning(
                    "Failed to publish inventory decrement for order %s — "
                    "stock will need manual adjustment",
                    order_id,
                )
            # ── End inventory decrement event ──────────────────

            created[supplier_id] = {"order_id": order_id, "totalPrice": float(total_price)}

        if failed:
            return {"created": created, "failed": failed}

        return True

    def get_active_order(self, order_id: str) -> Order:
        order = self.order_repository.get_active_order(order_id)
        if not order:
            raise NotFoundError(f"Active order {order_id} not found")
        return order

    def get_order_from_history(self, order_id: str) -> Order:
        order = self.order_repository.get_order_history(order_id)
        if not order:
            raise NotFoundError(f"Order history {order_id} not found")
        return order

    def update_order_status(self, order_id: str, new_status_str: str) -> bool:
        try:
            new_status = OrderStatus(new_status_str)
        except ValueError:
            raise ValidationError(f"Invalid order status: {new_status_str}")

        order = self.get_active_order(order_id)

        valid_transitions = {
            OrderStatus.PENDING: {OrderStatus.ACCEPTED, OrderStatus.REJECTED},
            OrderStatus.ACCEPTED: {OrderStatus.DELIVERING},
            OrderStatus.DELIVERING: {OrderStatus.ARRIVED},
        }

        allowed = valid_transitions.get(order.status, set())
        if new_status not in allowed:
            raise ConflictError(
                f"Cannot transition from {order.status.value} to {new_status.value}"
            )

        return self.order_repository.update_active_order_status(order_id, new_status)

    def archive_order(self, order_id: str) -> bool:
        order = self.get_active_order(order_id)
        if order.status not in (OrderStatus.ARRIVED, OrderStatus.REJECTED):
            raise ConflictError(
                f"Can only archive arrived or rejected orders, current: {order.status.value}"
            )
        return self.order_repository.archive_active_order(order_id)


    # Old Methods, not deprecated.
    def list_business_active_orders(self, business_id: str) -> List[Order]:
        bid = to_oid(business_id)
        if not bid:
            return []
        cursor = self.order_repository.get_multiple_active_orders({"business_id": bid})
        return [Order.to_entity(doc) for doc in cursor]

    def list_supplier_active_orders(self, supplier_id: str) -> List[Order]:
        sid = to_oid(supplier_id)
        if not sid:
            return []
        cursor = self.order_repository.get_multiple_active_orders({"supplier_id": sid})
        return [Order.to_entity(doc) for doc in cursor]

    # New Methods
    def list_business_orders(self, business_id: str, *, since: Optional[datetime] = None) -> List[Order]:
        bid = to_oid(business_id)
        if not bid:
            return []

        since = since or datetime.now(timezone.utc) - DEFAULT_RECENT_HISTORY_WINDOW
        active_docs = self.order_repository.get_multiple_active_orders({"business_id": bid})
        recent_history_docs = self.order_repository.get_multiple_order_history({"business_id": bid, "updated_at": {"$gte": since}})

        return [Order.to_entity(doc) for doc in active_docs] + [Order.to_entity(doc) for doc in recent_history_docs]

    def list_supplier_orders(self, supplier_id: str, *, since: Optional[datetime] = None) -> List[Order]:
        sid = to_oid(supplier_id)
        if not sid:
            return []

        since = since or datetime.now(timezone.utc) - DEFAULT_RECENT_HISTORY_WINDOW
        active_docs = self.order_repository.get_multiple_active_orders({"supplier_id": sid})
        recent_history_docs = self.order_repository.get_multiple_order_history({"supplier_id": sid, "updated_at": {"$gte": since}})

        return [Order.to_entity(doc) for doc in active_docs] + [Order.to_entity(doc) for doc in recent_history_docs]

    def list_business_history(self, business_id: str, *, cursor: Optional[str], limit: int) -> Tuple[List[Order], Optional[str], bool, int]:
        return self._list_history_page(party_field="business_id", party_id=business_id, cursor=cursor, limit=limit)

    def list_supplier_history(self, supplier_id: str, *, cursor: Optional[str], limit: int) -> Tuple[List[Order], Optional[str], bool, int]:
        return self._list_history_page(party_field="supplier_id", party_id=supplier_id, cursor=cursor, limit=limit)

    def _list_history_page(
            self,
            *,
            party_field: str,
            party_id: str,
            cursor: Optional[str],
            limit: int,
    ) -> Tuple[List[Order], Optional[str], bool, int]:  # ← added int for total

        pid = to_oid(party_id)
        if not pid:
            return [], None, False, 0

        limit = max(1, min(limit, HISTORY_PAGE_MAX))
        before = _parse_history_cursor(cursor)

        # Count total only on first page (no cursor) to avoid repeat work
        if before is None:
            total = self.order_repository.count_order_history({party_field: pid})
        else:
            total = -1  # signal to route handler: don't override previous total

        docs = list(
            self.order_repository.get_order_history_page(
                {party_field: pid},
                limit=limit + 1,
                before=before,
            )
        )
        has_more = len(docs) > limit
        docs = docs[:limit]
        orders = [Order.to_entity(d) for d in docs]
        next_cursor = orders[-1].updated_at.isoformat() if has_more and orders else None
        return orders, next_cursor, has_more, total
