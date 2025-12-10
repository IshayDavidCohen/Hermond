from typing import Dict, Optional, List, Union
from pymongo.cursor import Cursor
from bson import ObjectId

# App dependencies
from app.infra.Database import Database
from app.modules.BaseDAO import BaseDAO
from app.domain.Supplier import Supplier


class SupplierModule(BaseDAO):
    def __init__(self, db: Database):
        self.db = db
        self.collection = 'suppliers'
        super().__init__(db, self.collection)

    def create_supplier(self, supplier_entity: Supplier) -> str:
        doc = supplier_entity.from_entity()
        doc.pop("_id", None)
        return self._create_document(doc)

    def get_supplier(self, supplier_id: str, query: Dict = None) -> Optional[Dict]:
        """
        Function is able to get supplier in two ways,
        1) By Supplier's ID
        2) By Document's subfield/key value (IMPORTANT! - returns the first document with that value)

        :param supplier_id: ID (Type: str)
        :param query: Filtering parameters (Type: dict)
        :return:
        """
        oid = ObjectId(supplier_id)
        return self._get_document(document_id=oid, query=query)

    def get_suppliers_by(self, query: Dict, additional_query: Optional[Dict] = None) -> Cursor:
        """
        Function returns all suppliers filling the query requirement.

        :param query: Dict
        :param additional_query: Query(Dict)
        :return: Can return multiple (Type: Cursor from pymongo) or singular (Type: Dict)
        """
        return self._get_documents_by(query=query, additional_query=additional_query)

    def get_suppliers_list(self) -> Cursor:
        """
        :return: pd.cursor.Cursor instance (subscriptable)
        """
        return self._get_documents_list()

    def update_supplier(self, supplier_id: str, update_data: Dict) -> int:
        """
        Function removes the ID if exists (should exist.), updateAt gets updated.
        Updates and returns the modified_count

        modified_count = 1 -> Success
        modified_count = 0 -> Failed :(

        :param supplier_id: Union[str, ObjectId]
        :param update_data: Dict
        :return: int
        """
        oid = ObjectId(supplier_id)
        return self._update_document(document_id=oid, update_data=update_data)

    def delete_supplier(self, supplier_id: str) -> int:
        """
        Deletes document based on Supplier's ID and returns confirmation

        deleted_count = 1 -> Success
        deleted_count = 0 -> Failed

        :param supplier_id: Union[str, ObjectId]
        :return: int
        """
        oid = ObjectId(supplier_id)
        return self._delete_document(document_id=oid)

    # Complex Ops
    def get_subfields(self, supplier_id: str, subfields: List, with_id: bool = False) -> Dict:
        """
        Returns a document's subfield's value with or without the id (Default: without)

        :param supplier_id: ID of Supplier (Type: str)
        :param subfields: List of subfields to return Ex. ['address', 'phone', 'email']
        :param with_id: T/F
        :return: Dictionary with the subfields w/o '_id'.
        """
        supplier_id = ObjectId(supplier_id)
        return self._get_subfields(document_id=supplier_id, subfields=subfields, with_id=with_id)

