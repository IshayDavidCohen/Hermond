from functools import lru_cache

from app.config import settings
from app.shared.database.mongodb import Database
from app.shared.events.publisher import EventPublisher
from app.item.infrastructure.repository import ItemRepository
from app.category.infrastructure.repository import CategoryRepository
from app.item.application.service import ItemService
from app.category.application.service import CategoryService


@lru_cache()
def get_db() -> Database:
    return Database(database_name=settings.DB_NAME, connection_uri=settings.MONGO_URI)


@lru_cache()
def get_event_publisher() -> EventPublisher:
    return EventPublisher(redis_url=settings.REDIS_URL)


def get_item_repo() -> ItemRepository:
    return ItemRepository(db=get_db())


def get_category_repo() -> CategoryRepository:
    return CategoryRepository(db=get_db())


def get_item_service() -> ItemService:
    return ItemService(item_repository=get_item_repo())


def get_category_service() -> CategoryService:
    return CategoryService(category_repository=get_category_repo())
