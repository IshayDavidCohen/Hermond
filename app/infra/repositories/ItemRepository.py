
from typing import Dict, Optional, List

from app.modules.ItemModule import ItemModule
from app.domain.Item import Item

class ItemRepository:
    def __init__(self, item_module: ItemModule):
        self._item_module = item_module

    # -------------------------------------------------------------------------
    # Item CRUD (delegated to ItemModule)
    # -------------------------------------------------------------------------
    def create_item(self, item_data: Dict) -> str:
        item_entity: Item = Item.new(
            supplier_id=item_data['supplier_id'],
            name=item_data['name'],
            category=item_data['category'],
            image=item_data['image'],
            desc=item_data['desc'],
            base_price=item_data['base_price'],
            unit=item_data['unit'],
            currency=item_data['currency'],
        )
        return self._item_module.create_item(item_entity)

    def get_item(self, item_id: str) -> Optional[Item]:
        doc = self._item_module.get_item(item_id)
        if not doc:
            return None
        return Item.to_entity(doc)

    def update_item(self, item_id: str, update_data: Dict) -> int:
        return self._item_module.update_item(item_id, update_data)

    def delete_item(self, item_id: str) -> int:
        return self._item_module.delete_item(item_id)

    def get_items_by(self, query: Dict, additional_query: Dict = None) -> List:
        return list(self._item_module.get_items_by(query, additional_query))

