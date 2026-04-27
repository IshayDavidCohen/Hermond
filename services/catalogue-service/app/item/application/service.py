from typing import Dict, Optional

from app.item.domain.repository_interfaces import IItemRepository
from app.item.domain.entities.item import Item
from app.shared.exceptions import NotFoundError


class ItemService:
    def __init__(self, item_repository: IItemRepository):
        self.item_repository = item_repository

    def get_item(self, item_id: str) -> Item:
        item = self.item_repository.get_item(item_id)
        if not item:
            raise NotFoundError(f"Item {item_id} not found")
        return item

    def update_item(self, item_id: str, update_data: Dict) -> bool:
        if not self.item_repository.item_exists(item_id):
            raise NotFoundError(f"Item {item_id} not found")
        return self.item_repository.update_item(item_id, update_data)

    def set_custom_price(self, item_id: str, business_id: str, price: float) -> bool:
        if not self.item_repository.item_exists(item_id):
            raise NotFoundError(f"Item {item_id} not found")
        return self.item_repository.edit_user_custom_price(item_id, business_id, price)

    def remove_custom_price(self, item_id: str, business_id: str) -> bool:
        if not self.item_repository.item_exists(item_id):
            raise NotFoundError(f"Item {item_id} not found")
        return self.item_repository.remove_user_custom_price(item_id, business_id)
