from typing import Union, Optional, Dict, List
from pymongo.cursor import CursorType
from bson import ObjectId
from datetime import datetime

from app.Database import Database


class BusinessModule:
    def __init__(self, db: Database):
        self.db = db
        self.collection = 'businesses'

    def create_business(self, business_data: Dict) -> str:
        """
        Function creates a new business document

        * Required Data in dictionary
        bid (business id): str
        companyName: str
        desc: str
        icon: str
        banner: str
        email: str
        phone: str
        address: str
        shippingAddress: str
        categories: List ['Dairy', ...]

        :param business_data: Data (Type: Dict)
        :return: New business's document id (Type: str)
        """

        # Adding data on top of business_data

        # Dictionary of mySuppliers and handshake requests - of type: {companyName: ObjectId}
        business_data['mySuppliers'] = {}
        business_data['handshakeRequests'] = {}

        # List of active orders, and order history - of type: [ObjectId, ObjectId, ..., ObjectId]
        business_data['activeOrders'] = []
        business_data['orderHistory'] = []

        business_data['createdAt'] = datetime.utcnow()
        business_data['updatedAt'] = datetime.utcnow()

        # Push new document
        result = self.db.insert_one(self.collection, business_data)
        return str(result.inserted_id)

    def get_business(self, business_id: Union[str, ObjectId] = None, query: Dict = None) -> Optional[Dict]:
        """
        Function is able to get business in two ways,
        1) By Supplier's ID
        2) By Document's subfield/key value (IMPORTANT! - returns the first document with that value)

        :param business_id: ID (Type: str, ObjectId)
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

    def get_business_by(self, query: Dict) -> Optional[Union[Dict, CursorType]]:
        """
        Function returns all business filling the query requirement.

        :param query: Dict
        :return: Can return multiple (Type: CursorType from pymongo) or singular (Type: Dict)
        """
        return self.db.find_all(collection=self.collection, query=query)

    def get_business_list(self) -> Optional[CursorType]:
        """
        I mean. come on.
        :return:
        """
        return self.db.find_all(self.collection)

    def update_business(self, business_id: Union[str, ObjectId], update_data: Dict) -> int:
        """
        Function removes the ID if exists (should exist.), updateAt gets updated.
        Updates and returns the modified_count

        modified_count = 1 -> Success
        modified_count = 0 -> Failed :(

        :param business_id: str, ObjectId
        :param update_data: Dict
        :return: int
        """

        update_data = update_data.copy()

        # ID Exists, remove it
        if update_data.get('_id'):
            del update_data['_id']
        update_data['updatedAt'] = datetime.utcnow()

        return self.db.update_one(self.collection, {'_id': ObjectId(business_id)}, update_data).modified_count

    def delete_business(self, business_id: Union[str, ObjectId]) -> int:
        """
        Deletes document based on Supplier's ID and returns confirmation

        deleted_count = 1 -> Success
        deleted_count = 0 -> Failed

        :param business_id: Union[str, ObjectId]
        :return: int
        """
        return self.db.delete_one(self.collection, {'_id': ObjectId(business_id)}).deleted_count

    # Complex Ops
    def get_subfield(self, business_id: Union[str, ObjectId], subfields: List, with_id: bool = False) -> Dict:
        """
        Returns a document's subfield's value with or without the id (Default: without)

        :param business_id: ID of Supplier (Type: str, ObjectId)
        :param subfields: List of subfields to return Ex. ['address', 'phone', 'email']
        :param with_id: T/F
        :return: Dictionary with the subfields w/o '_id'.
        """
        subfield_query = {k: 1 for k in subfields}
        subfield_query['_id'] = with_id

        document = self.db.find_one(collection=self.collection, query={'_id': ObjectId(business_id)},
                                    subfield_query=subfield_query)

        if len(document.keys()) == 1 and with_id:
            return {}

        # ObjectId -> str
        if document and with_id:
            document['_id'] = str(document['_id'])

        return document

    def add_supplier(self, business_id: Union[str, ObjectId], supplier_name: str, supplier_id: Union[str, ObjectId]) -> int:
        try:
            # Using atomic operations to avoid mutex problems and overwrite.
            result = self.db.update_one(
                self.collection,
                {'_id': ObjectId(business_id), f'mySuppliers.{supplier_name}': {'$exists': False}},
                {f'mySuppliers.{supplier_name}': ObjectId(supplier_id)}  # Use $push if duplicates are allowed
            )
            return result.modified_count > 0
        except Exception as e:
            # Handle exceptions (e.g., log the error)
            return False
