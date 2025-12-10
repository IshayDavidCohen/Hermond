from typing import Dict, List, Optional
from bson import ObjectId

from app.modules.CategoryModule import CategoryModule
from app.modules.SupplierModule import SupplierModule

from app.domain.Supplier import Supplier

class SupplierRepository:
    def __init__(self, supplier_module: SupplierModule, category_module: CategoryModule):
        self._supplier_module = supplier_module
        self._category_module = category_module

    def create_supplier(self, supplier_data: Dict) -> str:
        supplier_entity = Supplier.new(
            business_id=supplier_data['bid'],
            company_name=supplier_data['company_name'],
            desc=supplier_data['desc'],
            icon=supplier_data['icon'],
            banner=supplier_data['banner'],
            email=supplier_data['email'],
            phone=supplier_data['phone'],
            address=supplier_data['address'],
            shipping_address=supplier_data['shipping_address'],
            categories=supplier_data['categories'],
        )
        return self._supplier_module.create_supplier(supplier_entity)

    def get_supplier(self, supplier_id: str, query: Dict = None) -> Optional[Supplier]:
        doc = self._supplier_module.get_supplier(supplier_id, query=query)
        if not doc:
            return None
        return Supplier.to_entity(doc)

    def update_supplier(self, supplier_id: str, update_data: Dict) -> int:
        return self._supplier_module.update_supplier(supplier_id, update_data)


    # -------------------------------------------------------------------------
    # Supplier list / queries
    # -------------------------------------------------------------------------
    def get_suppliers_by(self, query: Dict, additional_query: Dict = None) -> List:
        return list(self._supplier_module.get_suppliers_by(query, additional_query))

    # -------------------------------------------------------------------------
    # Items <-> Supplier relationship
    # -------------------------------------------------------------------------
    def append_item_to_supplier(self, supplier_id: str, item_id: str) -> bool:
        supplier: Optional[Supplier] = self.get_supplier(supplier_id)
        if not supplier:
            return False

        items: List[str] = list(supplier.items or [])
        if item_id in items:
            return True

        items.append(item_id)

        result = self.update_supplier(supplier_id, {'$addToSet': {'items': items}})
        return bool(result)

    def remove_item_from_supplier(self, supplier_id: str, item_id: str) -> bool:
        supplier: Optional[Supplier] = self.get_supplier(supplier_id)
        if not supplier:
            return False

        items: List[str] = list(supplier.items or [])
        if item_id not in items:
            return True
        items.remove(item_id)

        result = self.update_supplier(supplier_id, {'$addToSet': {'items': items}})
        return bool(result)

    # -------------------------------------------------------------------------
    # Categories <-> Suppliers relationship
    # -------------------------------------------------------------------------
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

    def add_user_to_category(self, category: str, supplier_name: str, supplier_id: str) -> int:
        return self._category_module.add_user(
            category=category,
            username=supplier_name,
            user_id=supplier_id)