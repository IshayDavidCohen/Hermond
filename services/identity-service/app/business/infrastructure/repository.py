from typing import Dict, List, Optional, Union
from datetime import datetime
from pymongo.cursor import Cursor
from bson import ObjectId

from app.shared.database.mongodb import Database
from app.shared.database.base_repository import BaseRepository
from app.business.domain.entities.business import Business
from app.business.domain.repository_interfaces import IBusinessRepository
from app.shared.utils import to_oid


class BusinessRepository(BaseRepository, IBusinessRepository):
    COLLECTION = "businesses"

    def __init__(self, db: Database):
        super().__init__(db, self.COLLECTION)

    def create_business(self, business_data: Dict) -> str:
        business_entity = Business.new(
            bid=business_data["bid"],
            company_name=business_data["company_name"],
            desc=business_data["desc"],
            icon=business_data["icon"],
            banner=business_data["banner"],
            email=business_data["email"],
            phone=business_data["phone"],
            address=business_data["address"],
            shipping_address=business_data["shipping_address"],
            categories=business_data["categories"],
        )
        doc = business_entity.from_entity()
        doc.pop("_id", None)
        doc["created_at"] = datetime.now()
        doc["updated_at"] = datetime.now()
        return self._create_document(doc)

    def get_business(self, business_id: str, projection: Dict = None) -> Optional[Business]:
        oid = to_oid(business_id)
        if not oid:
            return None
        doc = self._db.find_one(self.COLLECTION, {"_id": oid}, projection)
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        return Business.to_entity(doc)

    def update_business(self, business_id: str, update_data: Dict) -> bool:
        oid = to_oid(business_id)
        if not oid:
            return False

        update_data = update_data.copy()
        update_data.pop("_id", None)
        update_data["updated_at"] = datetime.now()

        if "my_suppliers" in update_data and isinstance(update_data["my_suppliers"], dict):
            update_data["my_suppliers"] = {
                k: to_oid(v) for k, v in update_data["my_suppliers"].items() if isinstance(v, str)
            }

        if "handshake_requests" in update_data and isinstance(update_data["handshake_requests"], dict):
            update_data["handshake_requests"] = {
                k: to_oid(v) for k, v in update_data["handshake_requests"].items() if isinstance(v, str)
            }

        if "active_orders" in update_data and isinstance(update_data["active_orders"], list):
            update_data["active_orders"] = [to_oid(x) for x in update_data["active_orders"] if isinstance(x, str)]

        if "order_history" in update_data and isinstance(update_data["order_history"], list):
            update_data["order_history"] = [to_oid(x) for x in update_data["order_history"] if isinstance(x, str)]

        result = self._db.update_one(self.COLLECTION, {"_id": oid}, update_data, operation="$set")
        return result.modified_count == 1

    def delete_business(self, business_id: str) -> bool:
        oid = to_oid(business_id)
        if not oid:
            return False
        result = self._db.delete_one(self.COLLECTION, {"_id": oid})
        return result.deleted_count == 1

    def exists(self, business_id: str) -> bool:
        oid = to_oid(business_id)
        if not oid:
            return False
        return self._db.find_one(self.COLLECTION, {"_id": oid}, {"_id": 1}) is not None

    def get_business_by(self, query: Dict, projection: Optional[Dict] = None) -> Union[Cursor, List[Dict]]:
        return self._db.find_all(collection=self.COLLECTION, query=query, subfield_query=projection)

    def get_business_list(self, projection: Optional[Dict] = None) -> Cursor:
        return self._db.find_all(collection=self.COLLECTION, query={}, subfield_query=projection)

    def get_subfield(self, business_id: str, subfields: List, with_id: bool = False) -> Dict:
        oid = to_oid(business_id)
        if not oid:
            return {}
        return self._get_subfields(document_id=oid, subfields=subfields, with_id=with_id)

    def add_supplier(self, business_id: str, supplier_name: str, supplier_id: str) -> bool:
        bid = to_oid(business_id)
        sid = to_oid(supplier_id)
        if not bid or not sid:
            return False
        result = self._db.update_one(
            self.COLLECTION,
            {"_id": bid, f"my_suppliers.{supplier_name}": {"$exists": False}},
            {f"my_suppliers.{supplier_name}": sid},
            operation="$set",
        )
        return result.modified_count == 1

    def add_active_order(self, business_id: str, order_id: str) -> bool:
        bid = to_oid(business_id)
        oid = to_oid(order_id)
        if not bid or not oid:
            return False
        result = self._db.update_one(
            self.COLLECTION,
            {"_id": bid},
            {"active_orders": oid},
            operation="$addToSet",
        )
        return result.matched_count == 1

    def add_order_to_history(self, business_id: str, order_id: str) -> bool:
        bid = to_oid(business_id)
        oid = to_oid(order_id)
        if not bid or not oid:
            return False
        result = self._db.update_one(
            self.COLLECTION,
            {"_id": bid},
            {"order_history": oid},
            operation="$addToSet",
        )
        return result.matched_count == 1

    def remove_active_order(self, business_id: str, order_id: str) -> bool:
        bid = to_oid(business_id)
        oid = to_oid(order_id)
        if not bid or not oid:
            return False
        result = self._db.update_one(
            self.COLLECTION,
            {"_id": bid},
            {"active_orders": oid},
            operation="$pull",
        )
        return result.matched_count == 1
