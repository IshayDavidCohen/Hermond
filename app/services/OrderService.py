import collections

from typing import Dict, Union
from bson import ObjectId

# App Dependencies
from app.infra.repositories.OrderRepository import OrderRepository
from app.modules.Orders import OrderedItem


class OrderService:
    def __init__(self, order_repository: OrderRepository):
        self.OrderRepository = order_repository

        # Private Main Methods
        self.__update_supplier = self.OrderRepository.supplier_module.update_supplier
        self.__update_business = self.OrderRepository.business_module.update_business

    def create_order_for_each_supplier(self, order_data: Dict) -> Union[bool, Dict]:
        """
        Function creates

        :param order_data: Dict
        :return: True/False or Dict of failed supplier orders
        """

        #  TODO: Too many items will cause bigger ram usage than batching.
        #  TODO: I avoided batching to reduce tcp/ip request overhead.

        #  NOTE: This will need to be refactored if batching is required.

        ex = {'business': 'BusinessName',
              'orders': {'supplierA': {'id1': 5, 'id2': 3},
                         'supplierB': {'id3': 6},
                         'supplierC': {'id4': 13}
                         }
              }

        # TODO: Make sure you validate keys exist in routes
        successful_orders = {}

        business_id = order_data['business']

        # 1. Extract id's from payload and get items.
        item_id_list = [key for supplier in order_data['orders'].values() for key in supplier.keys()]
        items_list = list(self.OrderRepository.item_module.get_items_by(query={'_id': {'$in': item_id_list}},
                                                                        additional_query={'basePrice': 1,
                                                                                          'customPrices': 1}))

        if not items_list:
            # Logger - Could not retrieve items
            return False

        # 2. Check that no ID is missing in our list.
        if collections.Counter(item_id_list) != collections.Counter([str(item['_id']) for item in items_list]):
            # Logger - Missing items
            return False

        # 3. Transform data (add id and check for custom prices)
        transformed_items = {}
        for item in items_list:
            price_at_order = item['basePrice']

            if item['customPrices'].get(business_id):
                price_at_order = item['customPrices'].get(business_id)

            transformed_items[str(item['_id'])] = {'basePrice': item['basePrice'],
                                                   'priceAtOrder': price_at_order}

        # TODO: Implement estimated_eta in the future.
        # 4. Create order for each supplier
        for supplier_id, order in order_data['orders'].items():
            ordered_items, total_price = [], 0

            for item_id, amount in order.items():
                ordered_item_obj = OrderedItem(item_id=item_id,
                                               quantity=amount,
                                               base_price=transformed_items[item_id]['basePrice'],
                                               price_at_order=transformed_items[item_id]['priceAtOrder'])
                total_price = total_price + ordered_item_obj.total_price_for_item
                ordered_items.append(ordered_item_obj)

            new_order = {'supplier_id': ObjectId(supplier_id),
                         'business_id': ObjectId(business_id),
                         'estimated_eta': 0,
                         'ordered_items': ordered_items,
                         'total_price': total_price}

            # 5. Get Business and Supplier, validate and Create New Order
            supplier_document = self.OrderRepository.supplier_module.get_supplier(supplier_id=supplier_id)
            business_document = self.OrderRepository.business_module.get_business(business_id=business_id)

            if (not supplier_document) and (not business_document):
                # Logger - Unable to get supplier and business, skipping order
                return False

            order_id = self.OrderRepository.order_module.create_order(new_order)

            # 6. Add order_id to both Supplier and Business
            supplier_document['activeOrders'].append(order_id)
            business_document['activeOrders'].append(order_id)

            # 7. Update both documents
            s_updated = self.__update_supplier(supplier_id=supplier_id, update_data={'activeOrders': supplier_document['activeOrders']})
            b_updated = self.__update_business(business_id=business_id, update_data={'activeOrders': business_document['activeOrders']})

            # Maybe dont exit, just report it didn't succeed
            if s_updated is False or b_updated is False:
                # Logger - Unable to update one of the two
                return False

            successful_orders[supplier_document['companyName']] = True

        # 8. Finally check every order was created
        failed_orders = {c: flag for c, flag in successful_orders.items() if flag is False}
        if not failed_orders:
            # Logger - There are some failed orders
            return failed_orders

        return True
