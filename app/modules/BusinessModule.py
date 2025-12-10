from typing import Union, Optional, Dict, List
from pymongo.cursor import Cursor
from bson import ObjectId
from datetime import datetime

from app.infra.Database import Database
from app.modules.BaseDAO import BaseDAO

class BusinessModule(BaseDAO):
    def __init__(self, db: Database):
        self.db = db
        self.collection = 'businesses'
        super().__init__(db, self.collection)

    def create_business(self, business_data: Dict) -> str:
        """
        Function creates a new business document

        * Required Data in dictionary
        bid (business id): str
        company_name: str
        desc: str
        icon: str
        banner: str
        email: str
        phone: str
        address: str
        shipping_address: str
        categories: List ['Dairy', ...]

        :param business_data: Data (Type: Dict)
        :return: New business's document id (Type: str)
        """

        # Adding data on top of business_data

        # Dictionary of my_suppliers and handshake requests - of type: {company_name: ObjectId}
        business_data['my_suppliers'] = {}
        business_data['handshake_requests'] = {}

        # List of active orders, and order history - of type: [ObjectId, ObjectId, ..., ObjectId]
        business_data['active_orders'] = []
        business_data['order_history'] = []

        business_data['created_at'] = datetime.now()
        business_data['updated_at'] = datetime.now()

        # Push new document
        result = self.db.insert_one(self.collection, business_data)
        return str(result.inserted_id)

    def get_business(self, business_id: str, query: Dict = None) -> Optional[Dict]:
        """
        Function is able to get business in two ways,
        1) By Supplier's ID
        2) By Document's subfield/key value (IMPORTANT! - returns the first document with that value)

        :param business_id: ID (Type: str)
        :param query: Filtering parameters (Type: dict)
        :return:
        """
        if business_id:
            query_by = {'_id': ObjectId(business_id)}
        elif query:
            query_by = query
        else:
            return None

        document = self.db.find_one(self.collection, query_by)
        if document:
            document['_id'] = str(document['_id'])

        return document

    def get_business_by(self, query: Dict, additional_query: Optional[Dict] = None) -> Optional[Union[Dict, Cursor]]:
        """
        Function returns all business filling the query requirement.

        :param query: Dict
        :param additional_query: A Query(Dict) used for additional functionality.
        :return: Can return multiple (Type: Cursor from pymongo) or singular (Type: Dict)
        """
        return self.db.find_all(collection=self.collection, query=query, subfield_query=additional_query)

    def get_business_list(self) -> Optional[Cursor]:
        """
        I mean. come on.
        :return:
        """
        return self.db.find_all(self.collection)

    def update_business(self, business_id: str, update_data: Dict) -> int:
        """
        Function removes the ID if exists (should exist.), updateAt gets updated.
        Updates and returns the modified_count

        modified_count = 1 -> Success
        modified_count = 0 -> Failed :(

        :param business_id: str
        :param update_data: Dict
        :return: int
        """

        update_data = update_data.copy()

        # ID Exists, remove it
        if update_data.get('_id'):
            del update_data['_id']
        update_data['updated_at'] = datetime.now()

        business_id = ObjectId(business_id)
        return self.db.update_one(self.collection, {'_id': business_id}, update_data).modified_count

    def delete_business(self, business_id: str) -> int:
        """
        Deletes document based on Supplier's ID and returns confirmation

        deleted_count = 1 -> Success
        deleted_count = 0 -> Failed

        :param business_id: str
        :return: int
        """
        business_id = ObjectId(business_id)
        return self.db.delete_one(self.collection, {'_id': business_id}).deleted_count

    # Complex Ops
    def get_subfield(self, business_id: str, subfields: List, with_id: bool = False) -> Dict:
        """
        Returns a document's subfield's value with or without the id (Default: without)

        :param business_id: ID of Supplier (Type: str, ObjectId)
        :param subfields: List of subfields to return Ex. ['address', 'phone', 'email']
        :param with_id: T/F
        :return: Dictionary with the subfields w/o '_id'.
        """
        business_id = ObjectId(business_id)
        return self._get_subfields(document_id=business_id, subfields=subfields, with_id=with_id)

    def add_supplier(self, business_id: str, supplier_name: str, supplier_id: str) -> int:
        try:
            # Using atomic operations to avoid mutex problems and overwrite.
            business_id = ObjectId(business_id)
            supplier_id = ObjectId(supplier_id)

            result = self.db.update_one(
                self.collection,
                {'_id': business_id, f'my_suppliers.{supplier_name}': {'$exists': False}},
                {f'my_suppliers.{supplier_name}': supplier_id}  # Use $push if duplicates are allowed
            )
            return result.modified_count > 0
        except Exception as e:
            # Handle exceptions (e.g., log the error)
            return False
