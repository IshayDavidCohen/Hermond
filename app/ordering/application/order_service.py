import collections
import logging
from typing import Dict, List, Optional, Union

from app.ordering.domain.entities.order import Order, OrderStatus
from app.ordering.domain.repository_interfaces import IOrderRepository
from app.shared.exceptions import NotFoundError, ValidationError, ConflictError

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(
        self,
        order_repository: IOrderRepository,
        item_repository,
        supplier_repository,
        business_repository,
    ):
        self.order_repository = order_repository
        self.item_repository = item_repository
        self.supplier_repository = supplier_repository
        self.business_repository = business_repository

    def create_order_for_each_supplier(self, order_data: Dict) -> Union[bool, Dict]:
        """Create one order per supplier from a multi-supplier cart.

        Expected payload:
            {"business": "<business_id>", "orders": {"<supplier_id>": {"<item_id>": qty, ...}, ...}}
        """
        business_id = order_data["business"]
        orders_by_supplier: Dict[str, Dict[str, int]] = order_data["orders"]

        if not self.business_repository.exists(business_id):
            raise NotFoundError(f"Business {business_id} not found")

        item_ids: List[str] = [
            iid for sup in orders_by_supplier.values() for iid in sup.keys()
        ]
        if not item_ids:
            raise ValidationError("No items in order")

        item_docs = list(
            self.item_repository.get_items_by(
                query={"_id": {"$in": item_ids}},
                projection={"base_price": 1, "custom_prices": 1, "supplier_id": 1},
            )
        )
        if not item_docs:
            raise NotFoundError("Items not found")

        got_ids = [str(d["_id"]) for d in item_docs]
        if collections.Counter(item_ids) != collections.Counter(got_ids):
            missing = list(
                (collections.Counter(item_ids) - collections.Counter(got_ids)).keys()
            )
            raise ValidationError(f"Missing items: {missing}")

        from app.catalogue.domain.entities.item import Item
        items: Dict[str, Item] = {str(d["_id"]): Item.to_entity(d) for d in item_docs}

        created = {}
        failed = {}

        for supplier_id, supplier_order in orders_by_supplier.items():
            if not self.supplier_repository.exists(supplier_id):
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

                if item.supplier_id != supplier_id:
                    failed.setdefault(supplier_id, {"error": "item_supplier_mismatch", "items": []})
                    failed[supplier_id]["items"].append(item_id)
                    continue

                price_at_order = item.base_price
                if item.custom_prices and item.custom_prices.get(business_id):
                    price_at_order = item.custom_prices[business_id]

                line_total = float(quantity) * float(price_at_order)
                total_price += line_total

                ordered_items.append({
                    "item_id": item_id,
                    "quantity": int(quantity),
                    "base_price": float(item.base_price),
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

            supplier_linked = self.supplier_repository.add_active_order(supplier_id, order_id)
            business_linked = self.business_repository.add_active_order(business_id, order_id)

            if not supplier_linked or not business_linked:
                failed[supplier_id] = {"error": "link_failed", "order_id": order_id}
                continue

            created[supplier_id] = {"order_id": order_id, "totalPrice": float(total_price)}

        if failed:
            return {"created": created, "failed": failed}

        return True

    def get_active_order(self, order_id: str) -> Order:
        """Retrieve an active order by ID."""
        order = self.order_repository.get_active_order(order_id)
        if not order:
            raise NotFoundError(f"Active order {order_id} not found")
        return order

    def get_order_from_history(self, order_id: str) -> Order:
        """Retrieve an order from history by ID."""
        order = self.order_repository.get_order_history(order_id)
        if not order:
            raise NotFoundError(f"Order history {order_id} not found")
        return order

    def update_order_status(self, order_id: str, new_status_str: str) -> bool:
        """Update the status of an active order."""
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
        """Move a completed/rejected order to history."""
        order = self.get_active_order(order_id)
        if order.status not in (OrderStatus.ARRIVED, OrderStatus.REJECTED):
            raise ConflictError(
                f"Can only archive arrived or rejected orders, current: {order.status.value}"
            )
        return self.order_repository.archive_active_order(order_id)

    def list_business_active_orders(self, business_id: str) -> List[Order]:
        """List active orders for a business."""
        from app.shared.utils import to_oid
        bid = to_oid(business_id)
        if not bid:
            return []
        cursor = self.order_repository.get_multiple_active_orders({"business_id": bid})
        return [Order.to_entity(doc) for doc in cursor]

    def list_supplier_active_orders(self, supplier_id: str) -> List[Order]:
        """List active orders for a supplier."""
        from app.shared.utils import to_oid
        sid = to_oid(supplier_id)
        if not sid:
            return []
        cursor = self.order_repository.get_multiple_active_orders({"supplier_id": sid})
        return [Order.to_entity(doc) for doc in cursor]
