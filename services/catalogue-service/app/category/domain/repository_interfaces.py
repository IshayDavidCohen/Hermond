from abc import ABC, abstractmethod
from typing import Dict, Optional

from pymongo.cursor import Cursor

from app.category.domain.entities.category import Category


class ICategoryRepository(ABC):
    @abstractmethod
    def create_category(self, category_data: Dict) -> str: ...

    @abstractmethod
    def get_category(self, category_id: str) -> Optional[Category]: ...

    @abstractmethod
    def update_category(self, category_id: str, update_data: Dict) -> bool: ...

    @abstractmethod
    def delete_category(self, category_id: str) -> bool: ...

    @abstractmethod
    def get_all_categories(self) -> Cursor: ...

    @abstractmethod
    def get_users(self, category_id: str) -> Dict[str, str]: ...

    @abstractmethod
    def add_user_to_category(self, category_id: str, username: str, supplier_id: str) -> bool: ...

    @abstractmethod
    def remove_user_from_category(self, category_id: str, username: str) -> bool: ...
