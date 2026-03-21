from typing import Dict, List, Optional, Tuple

from pymongo.cursor import Cursor

from app.shared.database.mongodb import Database
from app.shared.database.base_repository import BaseRepository
from app.item.domain.entities.item import Item
from app.item.domain.repository_interfaces import IItemRepository
from app.shared.utils import to_oid


class ItemRepository(BaseRepository, IItemRepository):
    COLLECTION = "items"

    def __init__(self, db: Database):
        super().__init__(db, self.COLLECTION)

    def create_item(self, item_data: Dict) -> Tuple[Optional[str], Optional[Item]]:
        item_entity = Item.new(
            supplier_id=item_data['supplier_id'],
            name=item_data['name'],
            category=item_data['category'],
            image=item_data['image'],
            desc=item_data['desc'],
            base_price=item_data['base_price'],
            unit=item_data['unit'],
            currency=item_data['currency'],
        )
        doc = item_entity.from_entity()
        doc.pop("_id", None)

        supplier_oid = to_oid(item_entity.supplier_id)
        if not supplier_oid:
            return None, None

        doc["supplier_id"] = supplier_oid
        item_id = self._create_document(doc)
        return item_id, item_entity

    def get_item(self, item_id: str) -> Optional[Item]:
        oid = to_oid(item_id)
        if not oid:
            return None
        doc = self._get_document(document_id=oid)
        if not doc:
            return None
        return Item.to_entity(doc)

    def update_item(self, item_id: str, update_data: Dict) -> bool:
        oid = to_oid(item_id)
        if not oid:
            return False
        return self._update_document(document_id=oid, update_data=update_data)

    def delete_item(self, item_id: str) -> bool:
        oid = to_oid(item_id)
        if not oid:
            return False
        return self._delete_document(document_id=oid)

    def item_exists(self, item_id: str) -> bool:
        oid = to_oid(item_id)
        if not oid:
            return False
        return self._db.find_one(self.COLLECTION, {"_id": oid}, {"_id": 1}) is not None

    def get_items_by(self, query: Dict, projection: Optional[Dict] = None) -> Cursor:
        return self._get_documents_by(query=query, additional_query=projection)

    def get_supplier_id_from_item(self, item_id: str) -> Optional[str]:
        oid = to_oid(item_id)
        if not oid:
            return None
        doc = self._db.find_one(self.COLLECTION, {"_id": oid}, {"supplier_id": 1})
        if not doc:
            return None
        supplier_id = doc.get("supplier_id")
        return str(supplier_id) if supplier_id is not None else None

    def get_subfields(self, item_id: str, subfields: List, with_id: bool = False) -> Dict:
        oid = to_oid(item_id)
        if not oid:
            return {}
        return self._get_subfields(document_id=oid, subfields=subfields, with_id=with_id)

    def edit_user_custom_price(self, item_id: str, user_id: str, price: float) -> bool:
        oid = to_oid(item_id)
        if not oid:
            return False
        field = {f"custom_prices.{user_id}": price}
        return self._upsert_subfield(document_id=oid, field_query=field)

    def remove_user_custom_price(self, item_id: str, user_id: str) -> bool:
        oid = to_oid(item_id)
        if not oid:
            return False
        field_query = f"custom_prices.{user_id}"
        return self._remove_subfield(document_id=oid, field_query=field_query)
