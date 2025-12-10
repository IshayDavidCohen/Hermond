from typing import Union, Dict, Optional
from pymongo.cursor import Cursor

from app.infra.Database import Database
from bson import ObjectId
from datetime import datetime

ORDER_STATUS = ['pending', 'accepted', 'rejected', 'delivering', 'arrived']


class OrderedItem:
    def __init__(self, item_id, quantity, base_price, price_at_order):
        self.item_id = item_id
        self.quantity = quantity
        self.base_price = base_price
        self.price_at_order = price_at_order
        self.total_price_for_item = quantity * price_at_order


class OrderModule:
    def __init__(self, db: Database):
        self.db = db
        self.order_collection = 'active_orders'
        self.history_collection = 'order_history'

    def create_order(self, order_data: Dict) -> str:
        """
        Function creates a new order document

        * Required Data in dictionary
        supplier_id: str (supplier id document)
        business_id: str (business id document)
        estimated_eta: datetime
        ordered_items: List of item objects
        totalPrice: float

        :param order_data: Data (Type: Dict)
        :return: New order document id (Type: str)
        """

        # Adding data on top of order_data
        order_data['status'] = 'pending'  # Default value when order is created
        order_data['created_at'] = datetime.now()
        order_data['updated_at'] = datetime.now()

        result = self.db.insert_one(self.order_collection, order_data)

        return str(result.inserted_id)

    #  ==============================/* Order History */

    def get_active_order(self, order_id: Union[str, ObjectId] = None, query: Dict = None) -> Optional[Dict]:
        return self.__get_order(self.order_collection, order_id, query)

    def get_multiple_active_orders(self, query: Dict, additional_query: Optional[Dict] = None) -> Optional[Union[Dict, Cursor]]:
        return self.__get_multiple_orders(self.order_collection, query, additional_query)

    def get_active_orders_list(self) -> Optional[Cursor]:
        return self.__get_order_list(self.order_collection)

    #  ==============================/* Order History */

    def get_order_history(self, order_id: Union[str, ObjectId], query: Dict = None) -> Optional[Dict]:
        return self.__get_order(self.history_collection, order_id, query)

    def get_multiple_order_history(self, query: Dict, additional_query: Optional[Dict] = None) -> Optional[Union[Dict, Cursor]]:
        return self.__get_multiple_orders(self.history_collection, query, additional_query)

    def get_order_history_list(self) -> Optional[Cursor]:
        return self.__get_order_list(self.history_collection)

    def update_order(self, collection: str, order_id: Union[str, ObjectId], update_data: Dict, status: str) -> int:

        update_data = update_data.copy()

        # ID Exists, remove it
        if update_data.get('_id'):
            del update_data['_id']

        # Must update status
        update_data['status'] = status

        update_data['updated_at'] = datetime.now()
        return self.db.update_one(collection, {'_id': ObjectId(order_id)}, update_data).modified_count

    def delete_order(self, collection: str, order_id: Union[str, ObjectId]) -> int:
        return self.db.delete_one(collection, {'_id': ObjectId(order_id)}).deleted_count

    # Complex functions

    # Private functions
    def __get_order(self, collection: str, order_id: Union[str, ObjectId] = None, query: Dict = None) -> Optional[Dict]:
        if order_id:
            query_by = {'_id': ObjectId(order_id)}
        elif query:
            query_by = query
        else:
            return None

        document = self.db.find_one(collection, query_by)
        if document:
            document['_id'] = str(document['_id'])

        return document

    def __get_multiple_orders(self, collection: str, query: Dict, additional_query: Optional[Dict] = None) -> Optional[Union[Dict, Cursor]]:
        return self.db.find_all(collection=collection, query=query, subfield_query=additional_query)

    def __get_order_list(self, collection) -> Optional[Cursor]:
        return self.db.find_all(collection)
