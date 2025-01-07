from typing import Union, Dict, List, Optional
from pymongo.cursor import CursorType

from app.Database import Database
from bson import ObjectId
from datetime import datetime

ORDER_STATUS = ['pending', 'accepted', 'rejected', 'delivering', 'arrived']


class OrderedItem:
    def __init__(self, item_id, quantity, price_at_order):
        self.item_id = item_id
        self.quantity = quantity
        self.price_at_order = price_at_order
        self.total_price_for_item = quantity * price_at_order


class OrderModule:
    def __init__(self, db: Database):
        self.db = db
        self.order_collection = 'activeOrders'
        self.history_collection = 'orderHistory'

    def create_order(self, order_data: Dict) -> str:
        """
        Function creates a new order document

        * Required Data in dictionary
        supplierId: str (supplier id document)
        businessId: str (business id document)
        estimatedETA: datetime
        items: List of item objects
        totalPrice: float

        :param order_data: Data (Type: Dict)
        :return: New order document id (Type: str)
        """

        # Adding data on top of order_data
        order_data['status'] = 'pending'  # Default value when order is created
        order_data['createdAt'] = datetime.utcnow()
        order_data['updatedAt'] = datetime.utcnow()

        result = self.db.insert_one(self.order_collection, order_data)

        return str(result.inserted_id)

    #  ==============================/* Order History */

    def get_activeOrder(self, order_id: Union[str, ObjectId] = None, query: Dict = None) -> Optional[Dict]:
        return self.__get_order(self.order_collection, order_id, query)

    def get_multiple_activeOrders(self, query: Dict) -> Optional[Union[Dict, CursorType]]:
        return self.__get_multiple_orders(self.order_collection, query)

    def get_activeOrders_list(self) -> Optional[CursorType]:
        return self.__get_order_list(self.order_collection)

    #  ==============================/* Order History */

    def get_orderHistory(self, order_id: Union[str, ObjectId], query: Dict = None) -> Optional[Dict]:
        return self.__get_order(self.history_collection, order_id, query)

    def get_multiple_orderHistory(self, query: Dict) -> Optional[Union[Dict, CursorType]]:
        return self.__get_multiple_orders(self.history_collection, query)

    def get_orderHistory_list(self) -> Optional[CursorType]:
        return self.__get_order_list(self.history_collection)

    def update_order(self, collection: str, order_id: Union[str, ObjectId], update_data: Dict, status: str) -> int:

        update_data = update_data.copy()

        # ID Exists, remove it
        if update_data.get('_id'):
            del update_data['_id']

        # Must update status
        update_data['status'] = status

        update_data['updatedAt'] = datetime.utcnow()
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

    def __get_multiple_orders(self, collection: str, query: Dict) -> Optional[Union[Dict, CursorType]]:
        return self.db.find_all(collection=collection, query=query)

    def __get_order_list(self, collection) -> Optional[CursorType]:
        return self.db.find_all(collection)
