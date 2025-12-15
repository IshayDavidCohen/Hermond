from typing import List, Dict, Tuple, Union

# App Dependencies (Modules and Functions)
from app.infra.repositories.SupplierRepository import SupplierRepository
from app.infra.repositories.ItemRepository import ItemRepository
from app.infra.repositories.CategoryRepository import CategoryRepository

from app.domain.entities.Supplier import Supplier


class SupplierService:
    def __init__(self,
                 supplier_repository: SupplierRepository,
                 item_repository: ItemRepository,
                 category_repository: CategoryRepository):

        self.supplier_repository = supplier_repository
        self.item_repository = item_repository
        self.category_repository = category_repository

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

        # TODO: for MVP V1 validate all categories exist before creating supplier
        category_validity_map: Dict[str, int] = {c: 0 for c in supplier_data['categories']}
        for c in categories:
            added = self.category_repository.add_user_to_category(
                category_id=c,
                username=supplier_name,
                supplier_id=supplier_id
            )
            category_validity_map[c] = added

        # Check if the supplier was added to all categories
        if 0 in category_validity_map.values():
            print('[CREATE SUPPLIER] Not all categories were updated')

        return supplier_id, category_validity_map

    def get_supplier(self, supplier_id: str) -> Supplier:
        return self.supplier_repository.get_supplier(supplier_id=supplier_id)

    def get_suppliers_from_category(self, category: str) -> List[Supplier]:
        all_users = self.category_repository.get_users(category)
        if not all_users:
            return []

        supplier_ids = list(all_users.values())
        return self.supplier_repository.get_list_of_suppliers(supplier_ids)

    # Handling Items for Supplier
    def create_item(self, item_data: Dict):
        """
        Wrapper function.
        Function creates an item document in the itemCollection in MongoDB.
        :param item_data: Dict
        :return:
        """
        # TODO: PASSED
        supplier_id = item_data.get('supplier_id')
        if not supplier_id:
            return '[CREATE ITEM] supplier_id missing'

        supplier_exists = self.supplier_repository.exists(supplier_id=supplier_id)
        if not supplier_exists:
            return '[CREATE ITEM] Supplier not found'

        item_id, _ = self.item_repository.create_item(item_data=item_data)
        if not item_id:
            return '[CREATE ITEM] Failed to create item'

        updated = self.supplier_repository.add_item(
            supplier_id=supplier_id,
            item_id=item_id
        )
        if not updated:
            return '[CREATE ITEM] Failed to append item to supplier'

        return item_id

    def delete_item(self, item_id: str) -> Union[str, bool]:
        """
        Wrapper function.
        Function deletes item id from supplier's items list and updates the supplier document then deletes the item.
        :param item_id: item document id (Type: str)
        :return: 0 if item not found, else return the result of the delete_item function from the item_module (0,1)
        """
        item_exists = self.item_repository.item_exists(item_id=item_id)
        if not item_exists:
            return '[DELETE ITEM] Item not found'

        supplier_id = self.item_repository.get_supplier_id_from_item(item_id=item_id)
        if not supplier_id:
            return '[DELETE ITEM] Supplier ID not found from item (critical)'

        removed_item = self.supplier_repository.remove_item(supplier_id=supplier_id, item_id=item_id)
        if not removed_item:
            return '[DELETE ITEM] Failed to remove item from supplier'

        deleted_item = self.item_repository.delete_item(item_id)
        if not deleted_item:
            return '[DELETE ITEM] Failed to delete item from item repository'

        return True

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
