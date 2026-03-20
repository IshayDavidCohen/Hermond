import logging
from typing import Dict, List, Tuple

from app.identity.domain.entities.supplier import Supplier
from app.identity.domain.repository_interfaces import ISupplierRepository
from app.shared.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class SupplierService:
    def __init__(
        self,
        supplier_repository: ISupplierRepository,
        item_repository,
        category_repository,
    ):
        self.supplier_repository = supplier_repository
        self.item_repository = item_repository
        self.category_repository = category_repository

    def create_supplier(self, supplier_data: Dict) -> Tuple[str, Dict]:
        """Create a new supplier and register with categories."""
        categories = supplier_data.get("categories", [])
        supplier_name = supplier_data.get("company_name", "")
        supplier_id = self.supplier_repository.create_supplier(supplier_data)

        category_validity_map: Dict[str, int] = {c: 0 for c in categories}
        for c in categories:
            added = self.category_repository.add_user_to_category(
                category_id=c,
                username=supplier_name,
                supplier_id=supplier_id,
            )
            category_validity_map[c] = added

        if 0 in category_validity_map.values():
            logger.warning("Not all categories were updated for supplier %s", supplier_id)

        return supplier_id, category_validity_map

    def get_supplier(self, supplier_id: str) -> Supplier:
        """Retrieve a supplier by ID. Raises NotFoundError if not found."""
        supplier = self.supplier_repository.get_supplier(supplier_id=supplier_id)
        if not supplier:
            raise NotFoundError(f"Supplier {supplier_id} not found")
        return supplier

    def get_suppliers_from_category(self, category: str) -> List[Supplier]:
        """Get all suppliers belonging to a category."""
        all_users = self.category_repository.get_users(category)
        if not all_users:
            return []
        supplier_ids = list(all_users.values())
        return self.supplier_repository.get_list_of_suppliers(supplier_ids)

    def create_item(self, item_data: Dict) -> str:
        """Create an item for a supplier. Raises on validation failures."""
        supplier_id = item_data.get("supplier_id")
        if not supplier_id:
            raise ValidationError("supplier_id is required")

        if not self.supplier_repository.exists(supplier_id=supplier_id):
            raise NotFoundError(f"Supplier {supplier_id} not found")

        item_id, _ = self.item_repository.create_item(item_data=item_data)
        if not item_id:
            raise ValidationError("Failed to create item")

        updated = self.supplier_repository.add_item(
            supplier_id=supplier_id, item_id=item_id
        )
        if not updated:
            raise ValidationError("Failed to append item to supplier")

        return item_id

    def delete_item(self, item_id: str) -> bool:
        """Delete an item and remove it from its supplier's items list."""
        if not self.item_repository.item_exists(item_id=item_id):
            raise NotFoundError(f"Item {item_id} not found")

        supplier_id = self.item_repository.get_supplier_id_from_item(item_id=item_id)
        if not supplier_id:
            raise ValidationError("Supplier ID not found from item")

        removed = self.supplier_repository.remove_item(
            supplier_id=supplier_id, item_id=item_id
        )
        if not removed:
            raise ValidationError("Failed to remove item from supplier")

        deleted = self.item_repository.delete_item(item_id)
        if not deleted:
            raise ValidationError("Failed to delete item")

        return True

    def update_item(self, item_id: str, update_data: Dict) -> bool:
        """Update an item's fields."""
        return self.item_repository.update_item(item_id, update_data)

    def update_supplier(self, supplier_id: str, update_data: Dict) -> bool:
        """Update a supplier profile. Raises NotFoundError if not found."""
        if not self.supplier_repository.exists(supplier_id):
            raise NotFoundError(f"Supplier {supplier_id} not found")
        return self.supplier_repository.update_supplier(supplier_id, update_data)

    def delete_supplier(self, supplier_id: str) -> bool:
        """Delete a supplier profile. Raises NotFoundError if not found."""
        if not self.supplier_repository.exists(supplier_id):
            raise NotFoundError(f"Supplier {supplier_id} not found")
        return self.supplier_repository.delete_supplier(supplier_id)

    def get_supplier_items(self, supplier_id: str, business_id: str = None) -> List:
        """Return all items for a supplier, with optional custom pricing for a business."""
        items = self.item_repository.get_items_by(query={"supplier_id": supplier_id})

        supplier_items: List[Dict] = []
        for item in items:
            if not item:
                continue
            item["_id"] = str(item["_id"])
            if business_id:
                custom_price = item.get("custom_prices", {}).get(business_id)
                if custom_price:
                    item["base_price"] = custom_price
            supplier_items.append(item)

        return supplier_items
