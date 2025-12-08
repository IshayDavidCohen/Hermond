from typing import Dict, List, Union, Optional
from pymongo.cursor import Cursor
from bson import ObjectId
from datetime import datetime

# App dependencies
from app.infra.Database import Database
from app.infra.repositories.BaseRepository import BaseRepository


class ItemModule(BaseRepository):
    def __init__(self, db: Database):
        self.collection = 'itemsCollection'
        self.db = db
        super().__init__(db, self.collection)

    def create_item(self, item_data: Dict) -> str:
        """
        Function creates a new supplier's item

        * Required Data in dictionary
            supplier_id: str (supplier id document)
            itemName: str
            itemCategory: str
            image: str
            desc: str
            basePrice: int
            unit: str
            currency: str

        :param item_data: Data (Type: Dict)
        :return: New item document id (Type: str)
        """

        # Adding data on top of item_data

        # Convert to ObjectId if is or isn't
        item_data['supplier_id'] = ObjectId(item_data['supplier_id'])

        # Dictionary of custom prices - of type {business_id: price}
        item_data['customPrices'] = {}

        item_data['createdAt'] = datetime.utcnow()
        item_data['updatedAt'] = datetime.utcnow()

        # Inherit call
        return self._create_document(item_data)

    # TODO: When a document is fetched, make sure all ObjectId's are acc string
    def get_item(self, item_id: Union[str, ObjectId] = None, query: Dict = None) -> Optional[Dict]:
        """
        An item document from the itemCollection in MongoDB
        :param item_id: Union[str, ObjectId]
        :return: Item Document (Type: Dict)
        :param query: Optional way to query a specific data.
        """

        return self._get_document(document_id=item_id, query=query)

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

    def update_item(self, item_id: Union[str, ObjectId], update_data: Dict) -> int:
        """
        Function removes ID Object if exists, updateAt gets updated.
        Updates and returns the modified_count to verify.

        modified_count = 1 -> Success
        modified_count = 0 -> Fail

        :param item_id: Union[str, ObjectId]
        :param update_data: Dict
        :return: int (0,1)
        """

        return self._update_document(document_id=item_id, update_data=update_data)

    def delete_item(self, item_id: Union[str, ObjectId]) -> int:
        """
        Deletes document based on the Item ID and returns confirmation

        deleted_count = 1 -> Success
        deleted_count = 0 -> Fail
        :param item_id: Union[str, ObjectId]
        :return: int (0,1)
        """
        return self._delete_document(document_id=item_id)

    def get_subfields(self, item_id: Union[str, ObjectId], subfields: List, with_id: bool = False) -> Dict:
        """
        Returns a document's subfield's value with or without the id (Default: without)


        :param item_id: ID of the Item (type: str)
        :param subfields: List of subfields to return Ex. ['basePrice', 'customPrices', 'unit']
        :param with_id: T/F
        :return: Dictionary with the subfields w/o '_id'
        """
        return self._get_subfields(document_id=item_id, subfields=subfields, with_id=with_id)

    def edit_user_custom_price(self, item_id: str, user_id: Union[str, ObjectId], price: float) -> bool:
        field = {f'customPrices.{ObjectId(user_id)}': price}
        return self._upsert_subfield(document_id=item_id, field_query=field)

    def remove_user_custom_price(self, item_id: str, user_id: Union[str, ObjectId]) -> bool:
        field_query = f'customPrices.{ObjectId(user_id)}'
        return self._remove_subfield(document_id=item_id, field_query=field_query)
