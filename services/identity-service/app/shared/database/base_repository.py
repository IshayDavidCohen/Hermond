from typing import List, Dict, Optional
from bson import ObjectId
from pymongo.cursor import Cursor
from datetime import datetime

from app.shared.database.mongodb import Database


class BaseRepository:
    def __init__(self, db: Database, collection: str):
        self._db = db
        self._collection = collection

    def _create_document(self, data: Dict) -> str:
        result = self._db.insert_one(self._collection, data)
        return str(result.inserted_id)

    def _get_document(self, document_id: ObjectId = None, query: Dict = None) -> Optional[Dict]:
        if document_id:
            query_by = {"_id": document_id}
        elif query:
            query_by = query
        else:
            return None
        document = self._db.find_one(self._collection, query_by)
        if document:
            document["_id"] = str(document["_id"])
        return document

    def _get_documents_by(self, query: Dict, additional_query: Optional[Dict] = None) -> Cursor:
        return self._db.find_all(collection=self._collection, query=query, subfield_query=additional_query)

    def _get_documents_list(self) -> Cursor:
        return self._db.find_all(self._collection)

    def _update_document(self, document_id: ObjectId, update_data: Dict) -> bool:
        update_data = update_data.copy()
        if update_data.get("_id"):
            del update_data["_id"]
        update_data["updated_at"] = datetime.now()
        result = self._db.update_one(self._collection, {"_id": document_id}, update_data)
        return result.modified_count > 0

    def _delete_document(self, document_id: ObjectId) -> bool:
        result = self._db.delete_one(self._collection, {"_id": document_id})
        return result.deleted_count > 0

    def _get_subfields(self, document_id, subfields: List, with_id: bool = False) -> Dict:
        subfield_query = {k: 1 for k in subfields}
        subfield_query["_id"] = with_id
        document = self._db.find_one(collection=self._collection, query={"_id": document_id}, subfield_query=subfield_query)
        if not document:
            return {}
        if with_id and set(document.keys()) <= {"_id"}:
            return {}
        if with_id and "_id" in document and isinstance(document["_id"], ObjectId):
            document["_id"] = str(document["_id"])
        return document

    def _upsert_subfield(self, document_id: ObjectId, field_query: Dict) -> bool:
        result = self._db.update_one(self._collection, {"_id": document_id}, field_query, operation="$set")
        return result.modified_count > 0

    def _remove_subfield(self, document_id: ObjectId, field_query: str) -> bool:
        query = {"_id": document_id, field_query: {"$exists": True}}
        update = {field_query: ""}
        result = self._db.update_one(self._collection, query, update, operation="$unset")
        return result.modified_count > 0
