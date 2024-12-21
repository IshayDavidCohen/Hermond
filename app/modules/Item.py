from typing import Dict, List, Union, Optional
from pymongo.cursor import CursorType
from bson import ObjectId
from datetime import datetime

# App dependencies
from app.Database import Database


class ItemModule:
    def __init__(self, db: Database):
        self.db = db
        self.collection = 'itemsCollection'

    def create_item(self, item_data: Dict) -> str:
        """
        Function creates a new supplier's item

        * Required Data in dictionary
            supplierId: str (supplier id document)
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
        item_data['supplierId'] = ObjectId(item_data['supplierId'])

        # Dictionary of custom prices - of type {businessId: price}
        item_data['customPrices'] = {}

        item_data['createdAt'] = datetime.utcnow()
        item_data['updatedAt'] = datetime.utcnow()

        result = self.db.insert_one(self.collection, item_data)
        return str(result.inserted_id)

    def get_item(self, item_id: Union[str, ObjectId]) -> Optional[Dict]:
        """
        An item document from the itemCollection in MongoDB
        :param item_id: Union[str, ObjectId]
        :return: Item Document (Type: Dict)
        """
        return self.db.find_one(self.collection, {'_id': ObjectId(item_id)})

    def get_items_by(self, query: Dict) -> Optional[Union[CursorType]]:
        """
        An all item documents from the itemCollection in MongoDB depending on query
        :param query: Dict
        :return: Item Document (Type: Dict)
        """
        return self.db.find_all(collection=self.collection, query=query)

    def get_items_list(self) -> Optional[CursorType]:
        """
        All items
        :return: pd.cursor.Cursor instance (subscriptable)
        """
        return self.db.find_all(self.collection)

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
        update_data = update_data.copy()

        if update_data.get('_id'):
            del update_data['_id']
        update_data['updatedAt'] = datetime.utcnow()

        return self.db.update_one(self.collection, {'_id': ObjectId(item_id)}, update_data).modified_count

    def delete_item(self, item_id: Union[str, ObjectId]) -> int:
        """
        Deletes document based on the Item ID and returns confirmation

        deleted_count = 1 -> Success
        deleted_count = 0 -> Fail
        :param item_id: Union[str, ObjectId]
        :return: int (0,1)
        """
        return self.db.delete_one(self.collection, {'_id': ObjectId(item_id)}).deleted_count

    def get_subfield(self, item_id: Union[str, ObjectId], subfields: List, with_id: bool = False) -> Dict:
        """
        Returns a document's subfield's value with or without the id (Default: without)


        :param item_id: ID of the Item (type: str)
        :param subfields: List of subfields to return Ex. ['basePrice', 'customPrices', 'unit']
        :param with_id: T/F
        :return: Dictionary with the subfields w/o '_id'
        """
        subfield_query = {k: 1 for k in subfields}
        subfield_query['_id'] = with_id

        document = self.db.find_one(collection=self.collection, query={'_id': ObjectId(item_id)},
                                    subfield_query=subfield_query)

        if len(document.keys()) == 1 and with_id:
            return {}

        # ObjectId -> str
        if document and with_id:
            document['_id'] = str(document['_id'])

        return document
