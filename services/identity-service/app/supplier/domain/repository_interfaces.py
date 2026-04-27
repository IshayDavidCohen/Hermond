from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from app.supplier.domain.entities.supplier import Supplier


class ISupplierRepository(ABC):
    @abstractmethod
    def create_supplier(self, supplier_data: Dict) -> str: ...

    @abstractmethod
    def get_supplier(self, supplier_id: str) -> Optional[Supplier]: ...

    @abstractmethod
    def update_supplier(self, supplier_id: str, update_data: Dict) -> bool: ...

    @abstractmethod
    def delete_supplier(self, supplier_id: str) -> bool: ...

    @abstractmethod
    def exists(self, supplier_id: str) -> bool: ...

    @abstractmethod
    def get_list_of_suppliers(self, suppliers: List[str]) -> List[Supplier]: ...

    @abstractmethod
    def add_item(self, supplier_id: str, item_id: str) -> bool: ...

    @abstractmethod
    def remove_item(self, supplier_id: str, item_id: str) -> bool: ...

    @abstractmethod
    def add_active_order(self, supplier_id: str, order_id: str) -> bool: ...
