from functools import lru_cache

from app.config import settings
from app.shared.database.mongodb import Database
from app.shared.events.publisher import EventPublisher
from app.business.infrastructure.repository import BusinessRepository
from app.supplier.infrastructure.repository import SupplierRepository
from app.supplier.infrastructure.clients.catalogue_client import CatalogueClient
from app.business.application.service import BusinessService
from app.supplier.application.service import SupplierService


@lru_cache()
def get_db() -> Database:
    return Database(database_name=settings.DB_NAME, connection_uri=settings.MONGO_URI)


@lru_cache()
def get_event_publisher() -> EventPublisher:
    return EventPublisher(redis_url=settings.REDIS_URL)


def get_business_repo() -> BusinessRepository:
    return BusinessRepository(db=get_db())


def get_supplier_repo() -> SupplierRepository:
    return SupplierRepository(db=get_db())


@lru_cache()
def get_catalogue_client() -> CatalogueClient:
    return CatalogueClient(base_url=settings.CATALOGUE_SERVICE_URL)


def get_business_service() -> BusinessService:
    return BusinessService(business_repository=get_business_repo())


def get_supplier_service() -> SupplierService:
    return SupplierService(
        supplier_repository=get_supplier_repo(),
        catalogue_client=get_catalogue_client(),
    )
