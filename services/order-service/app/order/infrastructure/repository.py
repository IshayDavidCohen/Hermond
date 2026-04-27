from typing import Dict, Optional
from datetime import datetime

from pymongo.cursor import Cursor

from app.shared.database.mongodb import Database
from app.shared.database.base_repository import BaseRepository
from app.order.domain.entities.order import Order, OrderedItem, OrderStatus
from app.order.domain.repository_interfaces import IOrderRepository
from app.shared.utils import to_oid


class OrderRepository(BaseRepository, IOrderRepository):
    ACTIVE_COLLECTION = "active_orders"
    HISTORY_COLLECTION = "order_history"

    def __init__(self, db: Database):
        super().__init__(db, self.ACTIVE_COLLECTION)

    @staticmethod
    def _convert_order_doc_ids_to_mongo(doc: Dict) -> Dict:
        doc = doc.copy()

        supplier_id = to_oid(doc["supplier_id"])
        business_id = to_oid(doc["business_id"])
        if not supplier_id or not business_id:
            return {}

        doc["supplier_id"] = supplier_id
        doc["business_id"] = business_id

        items = doc.get("ordered_items", [])
        for item in items:
            item_id = to_oid(item["item_id"])
            if item_id:
                item["item_id"] = item_id
        doc["ordered_items"] = items

        return doc

    def create_order(self, order_data: Dict) -> Optional[str]:
        ordered_items = [
            OrderedItem(
                item_id=x["item_id"],
                quantity=x["quantity"],
                base_price=x["base_price"],
                price_at_order=x["price_at_order"],
            )
            for x in order_data.get("ordered_items", [])
        ]

        order = Order.new(
            supplier_id=order_data["supplier_id"],
            business_id=order_data["business_id"],
            estimated_eta=order_data.get("estimated_eta"),
            ordered_items=ordered_items,
            total_price=order_data.get("totalPrice") or order_data.get("total_price") or 0.0,
        )

        doc = order.from_entity()
        doc.pop("_id", None)

        doc = self._convert_order_doc_ids_to_mongo(doc)
        if not doc:
            return None
        return str(self._db.insert_one(self.ACTIVE_COLLECTION, doc).inserted_id)

    def get_active_order(self, order_id: str, projection: Optional[Dict] = None) -> Optional[Order]:
        oid = to_oid(order_id)
        if not oid:
            return None
        doc = self._db.find_one(self.ACTIVE_COLLECTION, {"_id": oid}, projection)
        return Order.to_entity(doc) if doc else None

    def get_order_history(self, order_id: str, projection: Optional[Dict] = None) -> Optional[Order]:
        oid = to_oid(order_id)
        if not oid:
            return None
        doc = self._db.find_one(self.HISTORY_COLLECTION, {"_id": oid}, projection)
        return Order.to_entity(doc) if doc else None

    def update_active_order_status(self, order_id: str, new_status: OrderStatus) -> bool:
        oid = to_oid(order_id)
        if not oid:
            return False
        now = datetime.now()
        result = self._db.update_one(
            self.ACTIVE_COLLECTION,
            {"_id": oid},
            {"status": new_status.value, "updated_at": now},
            operation="$set",
        )
        return result.modified_count == 1

    def update_active_order_fields(self, order_id: str, update_data: Dict) -> bool:
        oid = to_oid(order_id)
        if not oid:
            return False
        update_data = update_data.copy()
        update_data.pop("_id", None)
        update_data["updated_at"] = datetime.now()
        result = self._db.update_one(
            self.ACTIVE_COLLECTION,
            {"_id": oid},
            update_data,
            operation="$set",
        )
        return result.modified_count == 1

    def delete_active_order(self, order_id: str) -> bool:
        oid = to_oid(order_id)
        if not oid:
            return False
        result = self._db.delete_one(self.ACTIVE_COLLECTION, {"_id": oid})
        return result.deleted_count == 1

    def delete_order_history(self, order_id: str) -> bool:
        oid = to_oid(order_id)
        if not oid:
            return False
        result = self._db.delete_one(self.HISTORY_COLLECTION, {"_id": oid})
        return result.deleted_count == 1

    def archive_active_order(self, order_id: str) -> bool:
        oid = to_oid(order_id)
        if not oid:
            return False
        doc = self._db.find_one(self.ACTIVE_COLLECTION, {"_id": oid})
        if not doc:
            return False
        self._db.insert_one(self.HISTORY_COLLECTION, doc)
        self._db.delete_one(self.ACTIVE_COLLECTION, {"_id": oid})
        return True

    def get_multiple_active_orders(self, query: Dict, projection: Optional[Dict] = None) -> Cursor:
        return self._db.find_all(collection=self.ACTIVE_COLLECTION, query=query, subfield_query=projection)

    def get_multiple_order_history(self, query: Dict, projection: Optional[Dict] = None) -> Cursor:
        return self._db.find_all(collection=self.HISTORY_COLLECTION, query=query, subfield_query=projection)

    def get_active_orders_list(self, projection: Optional[Dict] = None) -> Cursor:
        return self._db.find_all(collection=self.ACTIVE_COLLECTION, query={}, subfield_query=projection)

    def get_order_history_list(self, projection: Optional[Dict] = None) -> Cursor:
        return self._db.find_all(collection=self.HISTORY_COLLECTION, query={}, subfield_query=projection)

    def get_order_history_page(self, query: Dict, *, limit: int, before: Optional[datetime] = None) -> Cursor:
        if before is not None:
            query = {**query, "updated_at": {"$lt": before}}
        return (
            self._db.find_all(collection=self.HISTORY_COLLECTION, query=query)
            .sort("updated_at", -1)
            .limit(limit)
        )

    def count_order_history(self, query: Dict) -> int:
        return self._db.db[self.HISTORY_COLLECTION].count_documents(query)
