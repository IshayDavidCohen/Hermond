import logging
from typing import Dict, List, Tuple

from app.supplier.domain.entities.supplier import Supplier
from app.supplier.domain.repository_interfaces import ISupplierRepository
from app.supplier.infrastructure.clients.catalogue_client import CatalogueClient
from app.shared.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class SupplierService:
    def __init__(
        self,
        supplier_repository: ISupplierRepository,
        catalogue_client: CatalogueClient,
    ):
        self.supplier_repository = supplier_repository
        self.catalogue_client = catalogue_client

    async def create_supplier(self, supplier_data: Dict) -> Tuple[str, Dict]:
        categories = supplier_data.get("categories", [])
        supplier_name = supplier_data.get("company_name", "")
        supplier_id = self.supplier_repository.create_supplier(supplier_data)

        category_validity_map: Dict[str, int] = {c: 0 for c in categories}
        for c in categories:
            added = await self.catalogue_client.add_user_to_category(
                category_id=c,
                username=supplier_name,
                supplier_id=supplier_id,
            )
            category_validity_map[c] = int(added)

        if 0 in category_validity_map.values():
            logger.warning("Not all categories were updated for supplier %s", supplier_id)

        return supplier_id, category_validity_map

    def get_supplier(self, supplier_id: str) -> Supplier:
        supplier = self.supplier_repository.get_supplier(supplier_id=supplier_id)
        if not supplier:
            raise NotFoundError(f"Supplier {supplier_id} not found")
        return supplier

    async def get_suppliers_from_category(self, category: str) -> List[Supplier]:
        all_users = await self.catalogue_client.get_category_users(category)
        if not all_users:
            return []
        supplier_ids = list(all_users.values())
        return self.supplier_repository.get_list_of_suppliers(supplier_ids)

    async def create_item(self, item_data: Dict) -> str:
        supplier_id = item_data.get("supplier_id")
        if not supplier_id:
            raise ValidationError("supplier_id is required")

        if not self.supplier_repository.exists(supplier_id=supplier_id):
            raise NotFoundError(f"Supplier {supplier_id} not found")

        item_id = await self.catalogue_client.create_item(item_data=item_data)
        if not item_id:
            raise ValidationError("Failed to create item")

        updated = self.supplier_repository.add_item(
            supplier_id=supplier_id, item_id=item_id
        )
        if not updated:
            raise ValidationError("Failed to append item to supplier")

        return item_id

    async def delete_item(self, item_id: str) -> bool:
        exists = await self.catalogue_client.item_exists(item_id=item_id)
        if not exists:
            raise NotFoundError(f"Item {item_id} not found")

        supplier_id = await self.catalogue_client.get_supplier_id_from_item(item_id=item_id)
        if not supplier_id:
            raise ValidationError("Supplier ID not found from item")

        removed = self.supplier_repository.remove_item(
            supplier_id=supplier_id, item_id=item_id
        )
        if not removed:
            raise ValidationError("Failed to remove item from supplier")

        deleted = await self.catalogue_client.delete_item(item_id)
        if not deleted:
            raise ValidationError("Failed to delete item")

        return True

    def update_supplier(self, supplier_id: str, update_data: Dict) -> bool:
        if not self.supplier_repository.exists(supplier_id):
            raise NotFoundError(f"Supplier {supplier_id} not found")
        return self.supplier_repository.update_supplier(supplier_id, update_data)

    def delete_supplier(self, supplier_id: str) -> bool:
        if not self.supplier_repository.exists(supplier_id):
            raise NotFoundError(f"Supplier {supplier_id} not found")
        return self.supplier_repository.delete_supplier(supplier_id)

    async def get_supplier_items(self, supplier_id: str, business_id: str = None) -> List:
        items = await self.catalogue_client.get_items_batch([])
        supplier_items = []
        for item in items:
            if str(item.get("supplier_id")) != supplier_id:
                continue
            if business_id:
                custom_price = item.get("custom_prices", {}).get(business_id)
                if custom_price:
                    item["base_price"] = custom_price
            supplier_items.append(item)
        return supplier_items
