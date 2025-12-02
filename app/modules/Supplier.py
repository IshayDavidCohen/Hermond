from typing import Dict, Optional, List, Union
from pymongo.cursor import Cursor
from bson import ObjectId
from datetime import datetime

# App dependencies
from app.infra.Database import Database
from app.infra.repositories.BaseRepository import _BaseRepository


class SupplierModule(_BaseRepository):
    def __init__(self, db: Database):
        self.db = db
        self.collection = 'suppliers'
        super().__init__(db, self.collection)

    def create_supplier(self, supplier_data: Dict) -> str:
        """
        Function creates a new supplier document

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

        :param supplier_data: Data (Type: Dict)
        :return: New supplier's document id (Type: str)
        """

        # Adding data on top of supplier_data

        # Dictionary of approved businesses and handshake requests, of type: {companyName: ObjectId}
        supplier_data['approvedBusinesses'] = {}
        supplier_data['handshakeRequests'] = {}

        # List of item id's, active orders, and order history, of type: [ObjectId, ObjectId, ..., ObjectId]
        supplier_data['items'] = []
        supplier_data['activeOrders'] = []
        supplier_data['orderHistory'] = []

        supplier_data['createdAt'] = datetime.utcnow()
        supplier_data['updatedAt'] = datetime.utcnow()

        # Push new document
        return self._create_document(supplier_data)

    def get_supplier(self, supplier_id: Union[str, ObjectId] = None, query: Dict = None) -> Optional[Dict]:
        """
        Function is able to get supplier in two ways,
        1) By Supplier's ID
        2) By Document's subfield/key value (IMPORTANT! - returns the first document with that value)

        :param supplier_id: ID (Type: str)
        :param query: Filtering parameters (Type: dict)
        :return:
        """
        # if supplier_id:
        #     query_by = {'_id': ObjectId(supplier_id)}
        # elif query:
        #     query_by = query
        # else:
        #     return None
        #
        # document = self.db.find_one(self.collection, query_by)
        # if document:
        #     document['_id'] = str(document['_id'])

        # return document
        return self._get_document(document_id=supplier_id, query=query)

    def get_suppliers_by(self, query: Dict, additional_query: Optional[Dict] = None) -> Cursor:
        """
        Function returns all suppliers filling the query requirement.

        :param query: Dict
        :param additional_query: Query(Dict)
        :return: Can return multiple (Type: Cursor from pymongo) or singular (Type: Dict)
        """
        # return self.db.find_all(collection=self.collection, query=query, subfield_query=additional_query)
        return self._get_documents_by(query=query, additional_query=additional_query)

    def get_suppliers_list(self) -> Cursor:
        """
        :return: pd.cursor.Cursor instance (subscriptable)
        """
        # return self.db.find_all(self.collection)
        return self._get_documents_list()

    def update_supplier(self, supplier_id: Union[str, ObjectId], update_data: Dict) -> int:
        """
        Function removes the ID if exists (should exist.), updateAt gets updated.
        Updates and returns the modified_count

        modified_count = 1 -> Success
        modified_count = 0 -> Failed :(

        :param supplier_id: Union[str, ObjectId]
        :param update_data: Dict
        :return: int
        """

        # update_data = update_data.copy()
        #
        # # ID Exists, remove it
        # if update_data.get('_id'):
        #     del update_data['_id']
        # update_data['updatedAt'] = datetime.utcnow()
        #
        # return self.db.update_one(self.collection, {'_id': ObjectId(supplier_id)}, update_data).modified_count
        return self._update_document(document_id=supplier_id, update_data=update_data)

    def delete_supplier(self, supplier_id: Union[str, ObjectId]) -> int:
        """
        Deletes document based on Supplier's ID and returns confirmation

        deleted_count = 1 -> Success
        deleted_count = 0 -> Failed

        :param supplier_id: Union[str, ObjectId]
        :return: int
        """
        # return self.db.delete_one(self.collection, {'_id': ObjectId(supplier_id)}).deleted_count
        return self._delete_document(document_id=supplier_id)

    # Complex Ops
    def get_subfields(self, supplier_id: Union[str, ObjectId], subfields: List, with_id: bool = False) -> Dict:
        """
        Returns a document's subfield's value with or without the id (Default: without)

        :param supplier_id: ID of Supplier (Type: str)
        :param subfields: List of subfields to return Ex. ['address', 'phone', 'email']
        :param with_id: T/F
        :return: Dictionary with the subfields w/o '_id'.
        """
        # subfield_query = {k: 1 for k in subfields}
        # subfield_query['_id'] = with_id
        #
        # document = self.db.find_one(collection=self.collection, query={'_id': ObjectId(supplier_id)},
        #                             subfield_query=subfield_query)
        #
        # if len(document.keys()) == 1 and with_id:
        #     return {}
        #
        # # ObjectId -> str
        # if document and with_id:
        #     document['_id'] = str(document['_id'])
        #
        # return document
        return self._get_subfields(document_id=supplier_id, subfields=subfields, with_id=with_id)

