from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from pymongo.cursor import Cursor

from app.item.domain.entities.item import Item


class IItemRepository(ABC):
    @abstractmethod
    def create_item(self, item_data: Dict) -> Tuple[Optional[str], Optional[Item]]: ...

    @abstractmethod
    def get_item(self, item_id: str) -> Optional[Item]: ...

    @abstractmethod
    def update_item(self, item_id: str, update_data: Dict) -> bool: ...

    @abstractmethod
    def delete_item(self, item_id: str) -> bool: ...

    @abstractmethod
    def item_exists(self, item_id: str) -> bool: ...

    @abstractmethod
    def get_items_by(self, query: Dict, projection: Optional[Dict] = None) -> Cursor: ...

    @abstractmethod
    def get_supplier_id_from_item(self, item_id: str) -> Optional[str]: ...

    @abstractmethod
    def edit_user_custom_price(self, item_id: str, user_id: str, price: float) -> bool: ...

    @abstractmethod
    def remove_user_custom_price(self, item_id: str, user_id: str) -> bool: ...
