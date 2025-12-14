from typing import Dict, List, Optional

from app.infra.Database import Database
from app.infra.BaseDAO import BaseDAO
from app.domain.entities.Supplier import Supplier
from app.utilities.funcs import to_oid

class SupplierRepository(BaseDAO):
    COLLECTION = "suppliers"

    def __init__(self, db: Database):
        super().__init__(db, self.COLLECTION)

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
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

    def update_supplier(self, supplier_id: str, update_data: Dict) -> int:
        oid = to_oid(supplier_id)
        if not oid:
            return False
        return self._update_document(oid, update_data)

    def delete_supplier(self, supplier_id: str) -> bool:
        oid = to_oid(supplier_id)
        if not oid:
            return False
        return self._delete_document(oid)

    # -------------------------------------------------------------------------
    # "fast" ops / queries
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # Supplier <-> Items relationship
    # -------------------------------------------------------------------------
    def add_item(self, supplier_id: str, item_id: str) -> bool:
        supplier_id = to_oid(supplier_id)
        item_id = to_oid(item_id)
        if not supplier_id or not item_id:
            return False

        result = self._db.update_one(
            "suppliers",
            {"_id": supplier_id},
            {"items": item_id},
            operation="$addToSet"
        )
        return result.matched_count == 1

    def remove_item(self, supplier_id: str, item_id: str) -> bool:
        supplier_id = to_oid(supplier_id)
        item_id = to_oid(item_id)
        if not supplier_id or not item_id:
            return False

        # 3) remove if present (idempotent)
        result = self._db.update_one(
            "suppliers",
            {"_id": supplier_id},
            {"items": item_id},          # <-- payload only
            operation="$pull"
        )

        return result.matched_count == 1
