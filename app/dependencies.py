from functools import lru_cache

from app.config import settings
from app.shared.database.mongodb import Database

from app.identity.infrastructure.business_repository import BusinessRepository
from app.identity.infrastructure.supplier_repository import SupplierRepository
from app.identity.application.business_service import BusinessService
from app.identity.application.supplier_service import SupplierService

from app.catalogue.infrastructure.item_repository import ItemRepository
from app.catalogue.infrastructure.category_repository import CategoryRepository
from app.catalogue.application.item_service import ItemService
from app.catalogue.application.category_service import CategoryService

from app.handshake.infrastructure.handshake_repository import HandshakeRepository
from app.handshake.application.handshake_service import HandshakeService

from app.ordering.infrastructure.order_repository import OrderRepository
from app.ordering.application.order_service import OrderService


@lru_cache()
def get_db() -> Database:
    return Database(
        database_name=settings.DB_NAME,
        connection_uri=settings.MONGO_URI,
    )


# ---------------------------------------------------------------------------
# Repositories
# ---------------------------------------------------------------------------

def get_business_repo(db: Database = None) -> BusinessRepository:
    db = db or get_db()
    return BusinessRepository(db=db)


def get_supplier_repo(db: Database = None) -> SupplierRepository:
    db = db or get_db()
    return SupplierRepository(db=db)


def get_item_repo(db: Database = None) -> ItemRepository:
    db = db or get_db()
    return ItemRepository(db=db)


def get_category_repo(db: Database = None) -> CategoryRepository:
    db = db or get_db()
    return CategoryRepository(db=db)


def get_handshake_repo(db: Database = None) -> HandshakeRepository:
    db = db or get_db()
    return HandshakeRepository(db=db)


def get_order_repo(db: Database = None) -> OrderRepository:
    db = db or get_db()
    return OrderRepository(db=db)


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

def get_business_service() -> BusinessService:
    return BusinessService(business_repository=get_business_repo())


def get_supplier_service() -> SupplierService:
    return SupplierService(
        supplier_repository=get_supplier_repo(),
        item_repository=get_item_repo(),
        category_repository=get_category_repo(),
    )


def get_item_service() -> ItemService:
    return ItemService(item_repository=get_item_repo())


def get_category_service() -> CategoryService:
    return CategoryService(category_repository=get_category_repo())


def get_handshake_service() -> HandshakeService:
    return HandshakeService(handshake_repository=get_handshake_repo())


def get_order_service() -> OrderService:
    return OrderService(
        order_repository=get_order_repo(),
        item_repository=get_item_repo(),
        supplier_repository=get_supplier_repo(),
        business_repository=get_business_repo(),
    )
