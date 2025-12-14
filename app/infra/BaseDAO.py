from typing import List, Dict, Union, Optional
from bson import ObjectId
from pymongo.cursor import Cursor
from datetime import datetime

# App dependencies
from app.infra.Database import Database


class BaseDAO:
    def __init__(self, db: Database, collection: str):
        """
        Base class created to ease maintainability.
        Inheriting classes have specialized functionality.
        :param db: Active Database Connection (TCP/IP) instance.
        :param collection: str of collection
        """
        self._db = db
        self._collection = collection
    
    def _create_document(self, data: Dict) -> str:
        result = self._db.insert_one(self._collection, data)
        return str(result.inserted_id)
    
    def _get_document(self, document_id: ObjectId = None, query: Dict = None) -> Optional[Dict]:
        if document_id:
            query_by = {'_id': document_id}
        elif query:
            query_by = query
        else:
            return None

        document = self._db.find_one(self._collection, query_by)
        if document:
            document['_id'] = str(document['_id'])

        return document
    
    def _get_documents_by(self, query: Dict, additional_query: Optional[Dict] = None) -> Cursor:
        return self._db.find_all(collection=self._collection, query=query, subfield_query=additional_query)

    def _get_documents_list(self):
        return self._db.find_all(self._collection)

    def _update_document(self, document_id: ObjectId, update_data: Dict) -> int:
        """
        Function removes the ID if exists (should exist.), updateAt gets updated.
        Updates and returns the modified_count

        modified_count = 1 -> Success
        modified_count = 0 -> Failed :(

        :param document_id: ObjectId
        :param update_data: Dict
        :return: int
        """

        update_data = update_data.copy()

        # ID Exists, remove it
        if update_data.get('_id'):
            del update_data['_id']
        update_data['updated_at'] = datetime.now()

        result = self._db.update_one(self._collection, {'_id': document_id}, update_data)
        return result.modified_count > 0

    def _delete_document(self, document_id: ObjectId) -> bool:
        """
        Deletes document based on document's ID and returns confirmation

        deleted_count = 1 -> Success
        deleted_count = 0 -> Failed

        :param document_id: ObjectId
        :return: int
        """
        result = self._db.delete_one(self._collection, {'_id': document_id})
        return result.deleted_count > 0

    # Subfield manipulation

    def _get_subfields(self, document_id: Union[str, ObjectId], subfields: List, with_id: bool = False) -> Dict:
        """
        Returns a document's subfield's value with or without the id (Default: without)

        :param document_id: ID of document (Type: ObjectId)
        :param subfields: List of subfields to return Ex. ['address', 'phone', 'email']
        :param with_id: T/F
        :return: Dictionary with the subfields w/o '_id'.
        """
        subfield_query = {k: 1 for k in subfields}
        subfield_query['_id'] = with_id

        document = self._db.find_one(collection=self._collection,
                                     query={'_id': document_id},
                                     subfield_query=subfield_query)
        if not document:
            return {}

        if with_id and set(document.keys()) <= {'_id'}:
            return {}

        if with_id and '_id' in document and isinstance(document['_id'], ObjectId):
            document['_id'] = str(document['_id'])

        return document

    def _upsert_subfield(self, document_id: ObjectId, field_query: Dict) -> bool:
        result = self._db.update_one(self._collection, {'_id': document_id}, field_query, operation='$set')
        return result.modified_count > 0

    def _remove_subfield(self, document_id: ObjectId, field_query: str) -> bool:
        """
        Removal of a subfield in a document

        :param document_id: ObjectId
        :param field_query: field's name ex. 'custom_prices.[user_id]' or 'bid'
        :return:
        """
        query = {'_id': document_id, field_query: {'$exists': True}}
        update = {field_query: ''}

        result = self._db.update_one(self._collection, query, update, operation='$unset')

        return result.modified_count > 0



