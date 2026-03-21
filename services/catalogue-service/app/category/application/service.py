from typing import Dict, List

from app.category.domain.repository_interfaces import ICategoryRepository
from app.category.domain.entities.category import Category
from app.shared.exceptions import NotFoundError


class CategoryService:
    def __init__(self, category_repository: ICategoryRepository):
        self.category_repository = category_repository

    def create_category(self, category_data: Dict) -> str:
        return self.category_repository.create_category(category_data)

    def get_category(self, category_id: str) -> Category:
        category = self.category_repository.get_category(category_id)
        if not category:
            raise NotFoundError(f"Category {category_id} not found")
        return category

    def list_categories(self) -> List[Category]:
        cursor = self.category_repository.get_all_categories()
        return [Category.to_entity(doc) for doc in cursor]

    def delete_category(self, category_id: str) -> bool:
        if not self.category_repository.get_category(category_id):
            raise NotFoundError(f"Category {category_id} not found")
        return self.category_repository.delete_category(category_id)
