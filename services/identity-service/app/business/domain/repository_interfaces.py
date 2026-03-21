from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from app.business.domain.entities.business import Business


class IBusinessRepository(ABC):
    @abstractmethod
    def create_business(self, business_data: Dict) -> str: ...

    @abstractmethod
    def get_business(self, business_id: str) -> Optional[Business]: ...

    @abstractmethod
    def update_business(self, business_id: str, update_data: Dict) -> bool: ...

    @abstractmethod
    def delete_business(self, business_id: str) -> bool: ...

    @abstractmethod
    def exists(self, business_id: str) -> bool: ...

    @abstractmethod
    def add_supplier(self, business_id: str, supplier_name: str, supplier_id: str) -> bool: ...

    @abstractmethod
    def add_active_order(self, business_id: str, order_id: str) -> bool: ...

    @abstractmethod
    def add_order_to_history(self, business_id: str, order_id: str) -> bool: ...

    @abstractmethod
    def remove_active_order(self, business_id: str, order_id: str) -> bool: ...
