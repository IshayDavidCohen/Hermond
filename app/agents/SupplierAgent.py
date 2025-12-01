from typing import List, Dict, Tuple
from bson import ObjectId

# App Dependencies (Modules and Functions)
from app.repositories.SupplierRepository import SupplierRepository
from app.utilities.funcs import get_carousel_data


class SupplierAgent:
    def __init__(self, supplier_repo: SupplierRepository):
        # For easy access outside the class
        self.supplier_module = supplier_repo.supplier_module
        self.SupplierRepository = supplier_repo

    def create_supplier(self, supplier_data: Dict) -> Tuple[str, Dict]:
        """
        Wrapper function of SupplierModule.create_supplier

        Function creates a supplier document in the supplierCollection in MongoDB and
        adds the supplier to the category.

        :param supplier_data: Data (Type: Dict)
        :return: New supplier document id (Type: str)
        """
        category_validity_map = {k: 0 for k in supplier_data['categories']}
        _id = self.supplier_module.create_supplier(supplier_data)
        for c in supplier_data['categories']:
            added = self.SupplierRepository.category_module.add_user(category=c, username=supplier_data['companyName'],
                                                                     user_id=_id)
            category_validity_map[c] = added

        # Check if the supplier was added to all categories
        if 0 in category_validity_map.values():
            print('[CREATE SUPPLIER] Not all categories were updated')

        return _id, category_validity_map

    def get_suppliers_from_category(self, category_id: str) -> List:
        """
        Function returns all suppliers in a category.
        :param category_id: category id (Type: str)
        :return: List of suppliers (Type: List)
        """
        users = self.SupplierRepository.category_module.get_users(category=category_id)

        if users:
            return [user for user in self.supplier_module.get_suppliers_by({'_id': {'$in': list(users.values())}})]
        return []

    def get_supplier_carousel(self, category_id: str) -> List[Dict]:
        """
        Function returns a list of suppliers in a category in a format that can be used for a carousel.
        :param category_id: category id (Type: str)
        :return: List of dicts in format (Type: List)
        """
        users = self.get_suppliers_from_category(category_id)
        carousel = get_carousel_data(users, {'link': '_id',
                                             'title': 'companyName',
                                             'desc': 'desc',
                                             'banner': 'banner',
                                             'icon': 'icon'})
        for item in carousel:
            item['link'] = str(item['link'])

        return carousel

    # Handling Items for Supplier
    def create_item(self, item_data: Dict):
        """
        Wrapper function.
        Function creates an item document in the itemCollection in MongoDB.
        :param item_data: Dict
        :return:
        """
        supplier = self.supplier_module.get_supplier(supplier_id=item_data['supplier_id'])
        if supplier:
            _id = self.SupplierRepository.item_module.create_item(item_data=item_data)
            supplier['items'].append(ObjectId(_id))
            self.supplier_module.update_supplier(supplier_id=supplier['_id'], update_data={'items': supplier['items']})
            return _id
        else:
            return '[CREATE ITEM] Supplier not found'

    def delete_item(self, item_id: str) -> int:
        """
        Wrapper function.
        Function deletes item id from supplier's items list and updates the supplier document then deletes the item.
        :param item_id: item document id (Type: str)
        :return: 0 if item not found, else return the result of the delete_item function from the item_module (0,1)
        """
        item = self.SupplierRepository.item_module.get_item(item_id)
        if item:
            supplier = self.supplier_module.get_supplier(supplier_id=item['supplier_id'])
            supplier['items'].remove(item_id)
            self.supplier_module.update_supplier(supplier_id=supplier['_id'], update_data={'items': supplier['items']})
            return self.SupplierRepository.item_module.delete_item(item_id)
        else:
            return 0

    def update_item(self, item_id: str, update_data: Dict) -> int:
        """
        Wrapper function.
        Function updates an item document in the itemCollection in MongoDB.
        :param item_id: item document id (Type: str)
        :param update_data: Data (Type: Dict)
        :return: result of the update_item function from the item_module (0,1)
        """
        return self.SupplierRepository.item_module.update_item(item_id, update_data)

    def get_supplier_items(self, supplier_id: str, business_id: str = None) -> List:
        """
        Function returns all items that belong to a supplier.
        Optional: If business_id is provided, it will check if the business has a custom price for the item.
        :param supplier_id: supplier document id (Type: str)
        :param business_id: business document id (Type: str)
        :return: List of items (Type: List)
        """

        # Fetches all items containing the supplier_id.
        items_cursor = self.SupplierRepository.item_module.get_items_by(query={'supplier_id': supplier_id})

        supplier_items = []
        for item in items_cursor:
            if item:
                item['_id'] = str(item['_id'])
                supplier_items.append(item)

                if business_id:
                    # Check if the business has a custom price for the item
                    custom_price = item['customPrices'].get(business_id)
                    if custom_price:
                        item['basePrice'] = custom_price

        return supplier_items
