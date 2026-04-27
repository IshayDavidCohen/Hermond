from typing import Dict, List, Optional
from bson import ObjectId

from app.shared.database.mongodb import Database
from app.shared.database.base_repository import BaseRepository
from app.supplier.domain.entities.supplier import Supplier
from app.supplier.domain.repository_interfaces import ISupplierRepository
from app.shared.utils import to_oid


class SupplierRepository(BaseRepository, ISupplierRepository):
    COLLECTION = "suppliers"

    def __init__(self, db: Database):
        super().__init__(db, self.COLLECTION)

    def create_supplier(self, supplier_data: Dict) -> str:
        supplier_entity = Supplier.new(
            business_id=supplier_data['bid'],
            company_name=supplier_data['company_name'],
            desc=supplier_data['desc'],
            icon=supplier_data['icon'],
            banner=supplier_data['banner'],
            email=supplier_data['email'],
            phone=supplier_data['phone'],
            address=supplier_data['address'],
            shipping_address=supplier_data['shipping_address'],
            categories=supplier_data['categories'],
        )
        doc = supplier_entity.from_entity()
        doc.pop("_id", None)
        return self._create_document(doc)

    def get_supplier(self, supplier_id: str, projection: Dict = None) -> Optional[Supplier]:
        oid = to_oid(supplier_id)
        if not oid:
            return None
        doc = self._db.find_one(self.COLLECTION, {"_id": oid}, projection)
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        return Supplier.to_entity(doc)

    def update_supplier(self, supplier_id: str, update_data: Dict) -> bool:
        oid = to_oid(supplier_id)
        if not oid:
            return False
        return self._update_document(oid, update_data)

    def delete_supplier(self, supplier_id: str) -> bool:
        oid = to_oid(supplier_id)
        if not oid:
            return False
        return self._delete_document(oid)

    def exists(self, supplier_id: str) -> bool:
        oid = to_oid(supplier_id)
        if not oid:
            return False
        return self._db.find_one(self.COLLECTION, {"_id": oid}, {"_id": 1}) is not None

    def get_list_of_suppliers(self, suppliers: List[str]) -> List[Supplier]:
        obj_ids = [to_oid(sid) for sid in suppliers]
        obj_ids = [x for x in obj_ids if x is not None]
        if not obj_ids:
            return []
        docs = list(self._get_documents_by({"_id": {"$in": obj_ids}}))
        return [Supplier.to_entity(d) for d in docs] if docs else []

    def add_item(self, supplier_id: str, item_id: str) -> bool:
        sup_oid = to_oid(supplier_id)
        item_oid = to_oid(item_id)
        if not sup_oid or not item_oid:
            return False
        result = self._db.update_one(
            self.COLLECTION,
            {"_id": sup_oid},
            {"items": item_oid},
            operation="$addToSet",
        )
        return result.matched_count == 1

    def remove_item(self, supplier_id: str, item_id: str) -> bool:
        sup_oid = to_oid(supplier_id)
        item_oid = to_oid(item_id)
        if not sup_oid or not item_oid:
            return False
        result = self._db.update_one(
            self.COLLECTION,
            {"_id": sup_oid},
            {"items": item_oid},
            operation="$pull",
        )
        return result.matched_count == 1

    def add_active_order(self, supplier_id: str, order_id: str) -> bool:
        supplier_oid = to_oid(supplier_id)
        order_oid = to_oid(order_id)
        if not supplier_oid or not order_oid:
            return False
        result = self._db.update_one(
            self.COLLECTION,
            {"_id": supplier_oid},
            {"active_orders": order_oid},
            operation="$addToSet",
        )
        return result.matched_count == 1
