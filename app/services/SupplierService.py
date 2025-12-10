from typing import List, Dict, Tuple

# App Dependencies (Modules and Functions)
from app.infra.repositories.SupplierRepository import SupplierRepository
from app.infra.repositories.ItemRepository import ItemRepository
from app.utilities.funcs import get_carousel_data


class SupplierService:
    def __init__(self, supplier_repository: SupplierRepository, item_repository: ItemRepository):
        # For easy access outside the class
        self.supplier_repository = supplier_repository
        self.item_repository = item_repository

    def create_supplier(self, supplier_data: Dict) -> Tuple[str, Dict]:
        """
        Wrapper function of SupplierModule.create_supplier

        Function creates a supplier document in the supplierCollection in MongoDB and
        adds the supplier to the category.

        :param supplier_data: Data (Type: Dict)
        :return: New supplier document id (Type: str)
        """
        categories = supplier_data.get('categories', [])
        supplier_name = supplier_data.get('company_name', '')
        supplier_id = self.supplier_repository.create_supplier(supplier_data)

        category_validity_map: Dict[str, int] = {c: 0 for c in supplier_data['categories']}
        for c in categories:
            added = self.supplier_repository.add_user_to_category(
                category=c,
                supplier_name=supplier_name,
                supplier_id=supplier_id
            )
            category_validity_map[c] = added

        # Check if the supplier was added to all categories
        if 0 in category_validity_map.values():
            print('[CREATE SUPPLIER] Not all categories were updated')

        return supplier_id, category_validity_map

    def get_suppliers_from_category(self, category: str) -> List[Dict]:
        """Return raw supplier dicts for a given category."""
        return self.supplier_repository.get_suppliers_from_category(category)

    def get_category_supplier_carousel(self, category: str) -> List[Dict]:
        """
        Function returns a list of suppliers in a category in a format that can be used for a carousel.
        :param category: category id (Type: str)
        :return: List of dicts in format (Type: List)
        """
        users = self.get_suppliers_from_category(category)
        carousel = get_carousel_data(
            data_list=users,
            keys={
                'link': '_id',
                'title': 'company_name',
                'desc': 'desc',
                'banner': 'banner',
                'icon': 'icon'
                }
        )
        return carousel

    # Handling Items for Supplier
    def create_item(self, item_data: Dict):
        """
        Wrapper function.
        Function creates an item document in the itemCollection in MongoDB.
        :param item_data: Dict
        :return:
        """
        supplier_id = item_data.get('supplier_id')
        if not supplier_id:
            return '[CREATE ITEM] supplier_id missing'

        supplier = self.supplier_repository.get_supplier(supplier_id=supplier_id)
        if not supplier:
            return '[CREATE ITEM] Supplier not found'

        item_id = self.item_repository.create_item(item_data=item_data)
        if not item_id:
            return '[CREATE ITEM] Failed to create item'

        updated = self.supplier_repository.append_item_to_supplier(
            supplier_id=supplier_id,
            item_id=item_id
        )
        if not updated:
            return '[CREATE ITEM] Failed to append item to supplier'

        return item_id

    def delete_item(self, item_id: str) -> int:
        """
        Wrapper function.
        Function deletes item id from supplier's items list and updates the supplier document then deletes the item.
        :param item_id: item document id (Type: str)
        :return: 0 if item not found, else return the result of the delete_item function from the item_module (0,1)
        """
        item = self.item_repository.get_item(item_id)
        if not item:
            return 0

        self.supplier_repository.remove_item_from_supplier(
            supplier_id=item.supplier_id,
            item_id=item_id
        )

        return self.item_repository.delete_item(item_id)

    def update_item(self, item_id: str, update_data: Dict) -> int:
        return self.item_repository.update_item(item_id, update_data)

    def get_supplier_items(self, supplier_id: str, business_id: str = None) -> List:
        """
        Function returns all items that belong to a supplier.
        Optional: If business_id is provided, it will check if the business has a custom price for the item.
        :param supplier_id: supplier document id (Type: str)
        :param business_id: business document id (Type: str)
        :return: List of items (Type: List)
        """

        items = self.item_repository.get_items_by(query={'supplier_id': supplier_id})

        supplier_items: List[Dict] = []
        for item in items:
            if not item:
                continue

            item['_id'] = str(item['_id'])
            if business_id:
                custom_price = item.get('custom_prices', {}).get(business_id)
                if custom_price:
                    item['base_price'] = custom_price

            supplier_items.append(item)

        return supplier_items
