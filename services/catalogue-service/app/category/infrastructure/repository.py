from typing import Dict, List, Optional, Union
from datetime import datetime

from bson import ObjectId
from pymongo.cursor import Cursor

from app.shared.database.mongodb import Database
from app.shared.database.base_repository import BaseRepository
from app.category.domain.entities.category import Category
from app.category.domain.repository_interfaces import ICategoryRepository
from app.shared.utils import to_oid


class CategoryRepository(BaseRepository, ICategoryRepository):
    COLLECTION = "categories"

    def __init__(self, db: Database):
        super().__init__(db, self.COLLECTION)

    @staticmethod
    def _canon_category_id(category_id: str) -> str:
        return category_id.strip()

    @staticmethod
    def _users_to_mongo(users: Dict[str, str]) -> Dict[str, ObjectId]:
        return {k: to_oid(v) for k, v in (users or {}).items()}

    def create_category(self, category_data: Dict) -> str:
        category_entity = Category.new(
            oid=self._canon_category_id(category_data['oid']),
            title=category_data['title'],
            icon=category_data['icon'],
            image=category_data['image'],
            users=category_data['users'],
        )
        doc = category_entity.from_entity()
        doc["_id"] = self._canon_category_id(doc["_id"])
        doc["users"] = self._users_to_mongo(doc.get("users", {}))
        return self._create_document(doc)

    def get_category(self, category_id: str) -> Optional[Category]:
        category_id = self._canon_category_id(category_id)
        doc = self._db.find_one(self.COLLECTION, {"_id": category_id})
        if not doc:
            return None
        return Category.to_entity(doc)

    def update_category(self, category_id: str, update_data: Dict) -> bool:
        category_id = self._canon_category_id(category_id)
        update_data = update_data.copy()
        update_data.pop("_id", None)

        if "users" in update_data and isinstance(update_data["users"], dict):
            update_data["users"] = self._users_to_mongo(update_data["users"])

        update_data["updated_at"] = datetime.now()
        result = self._db.update_one(self.COLLECTION, {"_id": category_id}, update_data)
        return result.modified_count == 1

    def delete_category(self, category_id: str) -> bool:
        category_id = self._canon_category_id(category_id)
        result = self._db.delete_one(self.COLLECTION, {"_id": category_id})
        return result.deleted_count == 1

    def get_categories_by(self, query: Dict, projection: Optional[Dict] = None) -> Union[Cursor, List[Dict]]:
        return self._db.find_all(collection=self.COLLECTION, query=query, subfield_query=projection)

    def get_all_categories(self) -> Cursor:
        return self._db.find_all(self.COLLECTION)

    def get_users(self, category_id: str) -> Dict[str, str]:
        cat = self.get_category(category_id)
        return cat.users if cat else {}

    def add_user_to_category(self, category_id: str, username: str, supplier_id: str) -> bool:
        category_id = self._canon_category_id(category_id)
        supplier_oid = to_oid(supplier_id)
        result = self._db.update_one(
            self.COLLECTION,
            {"_id": category_id, f"users.{username}": {"$exists": False}},
            {f"users.{username}": supplier_oid},
            operation="$set",
        )
        return result.modified_count == 1

    def remove_user_from_category(self, category_id: str, username: str) -> bool:
        category_id = self._canon_category_id(category_id)
        result = self._db.update_one(
            self.COLLECTION,
            {"_id": category_id, f"users.{username}": {"$exists": True}},
            {f"users.{username}": ""},
            operation="$unset",
        )
        return result.modified_count == 1

    def get_subfield(self, category_id: str, subfields: List, with_id: bool = False) -> Dict:
        category_id = self._canon_category_id(category_id)
        return self._get_subfields(document_id=category_id, subfields=subfields, with_id=with_id)
