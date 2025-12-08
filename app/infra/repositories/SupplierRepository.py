from typing import Dict, List, Optional
from bson import ObjectId

from app.modules.CategoryModule import CategoryModule
from app.modules.ItemModule import ItemModule
from app.modules.SupplierModule import SupplierModule


class SupplierRepository:
    def __init__(self, supplier_module: SupplierModule, category_module: CategoryModule, item_module: ItemModule):
        self._supplier_module = supplier_module
        self._category_module = category_module
        self._item_module = item_module

    def create_supplier(self, supplier_data: Dict) -> str:
        return self._supplier_module.create_supplier(supplier_data)

    def update_supplier(self, supplier_id: str, update_data: Dict) -> int:
        oid = ObjectId(supplier_id)
        return self._supplier_module.update_supplier(oid, update_data)

    def get_supplier(self, supplier_id: str, query: Dict = None) -> Dict:
        oid = ObjectId(supplier_id)
        supplier = self._supplier_module.get_supplier(oid, query=query)
        if supplier:
            supplier['_id'] = str(supplier['_id'])
        return supplier

    def append_item_to_supplier(self, supplier_id: str, item_id: str) -> bool:
        supplier = self.get_supplier(supplier_id)
        if not supplier:
            return False

        items = supplier.get('items', [])
        items.append(ObjectId(item_id))

        result = self.update_supplier(supplier_id, {'items': items})
        return bool(result)

    def remove_item_from_supplier(self, supplier_id: str, item_id: str) -> bool:
        supplier = self.get_supplier(supplier_id)
        if not supplier:
            return False

        items = supplier.get('items', [])
        # supplier['items'] might contain ObjectId or str, be defensive:
        cleaned = []
        for item in items:
            if isinstance(item, ObjectId):
                if str(item) != item_id:
                    cleaned.append(item)
            else:
                if item != item_id:
                    cleaned.append(item)

        result = self.update_supplier(supplier_id, {'items': cleaned})
        return bool(result)

    def get_suppliers_by(self, query: Dict, additional_query: Dict = None) -> List:
        return list(self._supplier_module.get_suppliers_by(query, additional_query))

    def create_item(self, item_data: Dict) -> str:
        return self._item_module.create_item(item_data)

    def update_item(self, item_id: str, update_data: Dict) -> int:
        return self._item_module.update_item(item_id, update_data)

    def delete_item(self, item_id: str) -> int:
        return self._item_module.delete_item(item_id)

    def get_item(self, item_id: str) -> Optional[Dict]:
        return self._item_module.get_item(item_id)

    def get_items_by(self, query: Dict, additional_query: Dict = None) -> List:
        return list(self._item_module.get_items_by(query, additional_query))

    def add_user_to_category(self, category: str, supplier_name: str, supplier_id: str) -> int:
        return self._category_module.add_user(
            category=category,
            username=supplier_name,
            user_id=supplier_id)

    def get_users_from_category(self, category: str) -> List:
        return self._category_module.get_users(category=category)

    def get_suppliers_from_category(self, category: str) -> List[Dict]:
        users = self.get_users_from_category(category)  # maybe list[ObjectId] / list[str]
        if not users:
            return []

        # If 'users' is a list of supplier_ids / ObjectIds:
        supplier_ids = [str(u) for u in users]

        return list(self._supplier_module.get_suppliers_by(
            {'_id': {'$in': [ObjectId(sid) for sid in supplier_ids]}}
        ))
