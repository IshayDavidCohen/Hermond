from typing import Dict, List, Union, Optional
from pymongo.cursor import Cursor
from bson import ObjectId

# App dependencies
from app.infra.Database import Database
from app.modules.BaseDAO import BaseDAO

from app.domain.Item import Item

class ItemModule(BaseDAO):
    def __init__(self, db: Database):
        self.collection = 'items'
        self.db = db
        super().__init__(db, self.collection)

    def create_item(self, item_entity: Item) -> str:
        doc = item_entity.from_entity()
        doc.pop('_id', None)
        return self._create_document(doc)

    def get_item(self, item_id: str, query: Dict = None) -> Optional[Dict]:
        oid = ObjectId(item_id)
        return self._get_document(document_id=oid, query=query)

    def get_items_by(self, query: Dict, additional_query: Optional[Dict] = None) -> Cursor:
        """
        An all item documents from the itemCollection in MongoDB depending on query
        :param query: Dict
        :param additional_query: Query(Dict)
        :return: Item Document (Type: Dict)
        """
        return self._get_documents_by(query=query, additional_query=additional_query)

    def get_items_list(self) -> Optional[Cursor]:
        """
        All items
        :return: pd.cursor.Cursor instance (subscriptable)
        """
        return self._get_documents_list()

    def update_item(self, item_id: str, update_data: Dict) -> int:
        """
        Function removes ID Object if exists, updateAt gets updated.
        Updates and returns the modified_count to verify.

        modified_count = 1 -> Success
        modified_count = 0 -> Fail

        :param item_id: Union[str, ObjectId]
        :param update_data: Dict
        :return: int (0,1)
        """
        oid = ObjectId(item_id)
        return self._update_document(document_id=oid, update_data=update_data)

    def delete_item(self, item_id: str) -> int:
        """
        Deletes document based on the Item ID and returns confirmation

        deleted_count = 1 -> Success
        deleted_count = 0 -> Fail
        :param item_id: Union[str, ObjectId]
        :return: int (0,1)
        """
        oid=ObjectId(item_id)
        return self._delete_document(document_id=oid)

    def get_subfields(self, item_id: str, subfields: List, with_id: bool = False) -> Dict:
        """
        Returns a document's subfield's value with or without the id (Default: without)


        :param item_id: ID of the Item (type: str)
        :param subfields: List of subfields to return Ex. ['base_price', 'custom_prices', 'unit']
        :param with_id: T/F
        :return: Dictionary with the subfields w/o '_id'
        """
        item_id = ObjectId(item_id)
        return self._get_subfields(document_id=item_id, subfields=subfields, with_id=with_id)

    def edit_user_custom_price(self, item_id: str, user_id: str, price: float) -> bool:
        field = {f'custom_prices.{user_id}': price}
        item_id = ObjectId(item_id)
        return self._upsert_subfield(document_id=item_id, field_query=field)

    def remove_user_custom_price(self, item_id: str, user_id: str) -> bool:
        field_query = f'custom_prices.{user_id}'
        item_id = ObjectId(item_id)
        return self._remove_subfield(document_id=item_id, field_query=field_query)
