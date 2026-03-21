from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from pymongo.cursor import Cursor

from app.order.domain.entities.order import Order, OrderStatus


class IOrderRepository(ABC):
    @abstractmethod
    def create_order(self, order_data: Dict) -> Optional[str]: ...

    @abstractmethod
    def get_active_order(self, order_id: str) -> Optional[Order]: ...

    @abstractmethod
    def get_order_history(self, order_id: str) -> Optional[Order]: ...

    @abstractmethod
    def update_active_order_status(self, order_id: str, new_status: OrderStatus) -> bool: ...

    @abstractmethod
    def update_active_order_fields(self, order_id: str, update_data: Dict) -> bool: ...

    @abstractmethod
    def delete_active_order(self, order_id: str) -> bool: ...

    @abstractmethod
    def archive_active_order(self, order_id: str) -> bool: ...

    @abstractmethod
    def get_multiple_active_orders(self, query: Dict, projection: Optional[Dict] = None) -> Cursor: ...

    @abstractmethod
    def get_multiple_order_history(self, query: Dict, projection: Optional[Dict] = None) -> Cursor: ...
