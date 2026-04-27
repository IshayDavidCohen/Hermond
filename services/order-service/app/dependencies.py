from functools import lru_cache

from app.config import settings
from app.shared.database.mongodb import Database
from app.order.infrastructure.repository import OrderRepository
from app.order.infrastructure.clients.identity_client import IdentityClient
from app.order.infrastructure.clients.catalogue_client import CatalogueClient
from app.order.application.service import OrderService


@lru_cache()
def get_db() -> Database:
    return Database(database_name=settings.DB_NAME, connection_uri=settings.MONGO_URI)

@lru_cache()
def get_event_publisher() -> EventPublisher:
    return EventPublisher(redis_url=settings.REDIS_URL)

@lru_cache()
def get_identity_client() -> IdentityClient:
    return IdentityClient(base_url=settings.IDENTITY_SERVICE_URL)


@lru_cache()
def get_catalogue_client() -> CatalogueClient:
    return CatalogueClient(base_url=settings.CATALOGUE_SERVICE_URL)


def get_order_repo() -> OrderRepository:
    return OrderRepository(db=get_db())


def get_order_service() -> OrderService:
    return OrderService(
        order_repository=get_order_repo(),
        identity_client=get_identity_client(),
        catalogue_client=get_catalogue_client(),
        event_publisher=get_event_publisher(),
    )
