import collections

from typing import Dict, Union, List

# App Dependencies
from app.infra.repositories.OrderRepository import OrderRepository
from app.infra.repositories.ItemRepository import ItemRepository
from app.infra.repositories.SupplierRepository import SupplierRepository
from app.infra.repositories.BusinessRepository import BusinessRepository

from app.domain.entities.Item import Item

class OrderService:
    def __init__(
            self,
            order_repository: OrderRepository,
            item_repository: ItemRepository,
            supplier_repository: SupplierRepository,
            business_repository: BusinessRepository
            ):
        self.order_repository = order_repository
        self.item_repository = item_repository
        self.supplier_repository = supplier_repository
        self.business_repository = business_repository


    def create_order_for_each_supplier(self, order_data: Dict) -> Union[bool, Dict]:
        """
        Expected payload shape:
        {
          "business": "<business_id>",
          "orders": {
             "<supplier_id>": {"<item_id>": quantity, ...},
             ...
          },
        }

        Returns:
          True on success, or dict describing failures.
        """
        business_id = order_data["business"]
        orders_by_supplier: Dict[str, Dict[str, int]] = order_data["orders"]

        # 0) Validate business exists (fast exists check in repo)
        if not self.business_repository.exists(business_id):
            return {"error": "business_not_found", "business_id": business_id}

        # 1) Collect all item ids
        item_ids: List[str] = [iid for sup in orders_by_supplier.values() for iid in sup.keys()]
        if not item_ids:
            return {"error": "no_items"}

        # 2) Fetch items with minimal fields (repo should handle ObjectId conversion internally)
        #    We want: base_price, custom_prices, supplier_id
        # TODO: Check ObjectId conversions in item repo layer
        item_docs = list(
            self.item_repository.get_items_by(
                query={"_id": {"$in": item_ids}},
                projection={"base_price": 1, "custom_prices": 1, "supplier_id": 1},
            )
        )
        if not item_docs:
            return {"error": "items_not_found"}

        # 3) Ensure none missing
        got_ids = [str(d["_id"]) for d in item_docs]
        if collections.Counter(item_ids) != collections.Counter(got_ids):
            missing = list((collections.Counter(item_ids) - collections.Counter(got_ids)).keys())
            return {"error": "missing_items", "missing_item_ids": missing}

        # 4) Convert to entities + build lookup
        items: Dict[str, Item] = {str(d["_id"]): Item.to_entity(d) for d in item_docs}

        # 5) Create an order per supplier
        created = {}
        failed = {}

        for supplier_id, supplier_order in orders_by_supplier.items():
            # Validate supplier exists
            if not self.supplier_repository.exists(supplier_id):
                failed[supplier_id] = {"error": "supplier_not_found"}
                continue

            # Build ordered_items payload and total
            ordered_items = []
            total_price = 0.0

            # Validate: item belongs to this supplier + compute price_at_order
            for item_id, quantity in supplier_order.items():
                item = items.get(item_id)
                if not item:
                    failed.setdefault(supplier_id, {"error": "missing_items_for_supplier", "items": []})
                    failed[supplier_id]["items"].append(item_id)
                    continue

                # IMPORTANT: prevents ordering supplier A items through supplier B
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

            # If any per-supplier item failures, skip creating that supplier's order
            if supplier_id in failed:
                continue

            # 6) Create order (repo converts supplier_id/business_id/item_id -> ObjectId)
            order_id = self.order_repository.create_order({
                "supplier_id": supplier_id,
                "business_id": business_id,
                "estimated_eta": None,
                "ordered_items": ordered_items,
                "totalPrice": float(total_price),   # keep DB schema stable
            })

            # 7) Link order to supplier + business atomically (use $addToSet)
            supplier_linked = self.supplier_repository.add_active_order(supplier_id, order_id)
            business_linked = self.business_repository.add_active_order(business_id, order_id)

            if not supplier_linked or not business_linked:
                # Optional: consider compensating action (delete order / mark failed)
                failed[supplier_id] = {"error": "link_failed", "order_id": order_id}
                continue

            created[supplier_id] = {"order_id": order_id, "totalPrice": float(total_price)}

        if failed:
            return {"created": created, "failed": failed}

        return True