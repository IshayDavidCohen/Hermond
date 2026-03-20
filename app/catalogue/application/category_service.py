from typing import Dict, List

from app.catalogue.domain.repository_interfaces import ICategoryRepository
from app.catalogue.domain.entities.category import Category
from app.shared.exceptions import NotFoundError


class CategoryService:
    def __init__(self, category_repository: ICategoryRepository):
        self.category_repository = category_repository

    def create_category(self, category_data: Dict) -> str:
        """Create a new category."""
        return self.category_repository.create_item(category_data)

    def get_category(self, category_id: str) -> Category:
        """Retrieve a category by ID."""
        category = self.category_repository.get_category(category_id)
        if not category:
            raise NotFoundError(f"Category {category_id} not found")
        return category

    def list_categories(self) -> List[Category]:
        """Return all categories."""
        cursor = self.category_repository.get_all_categories()
        return [Category.to_entity(doc) for doc in cursor]

    def delete_category(self, category_id: str) -> bool:
        """Delete a category."""
        if not self.category_repository.get_category(category_id):
            raise NotFoundError(f"Category {category_id} not found")
        return self.category_repository.delete_category(category_id)
