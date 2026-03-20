import logging
from contextlib import asynccontextmanager

import firebase_admin
from fastapi import FastAPI

from app.config import settings
from app.dependencies import get_db
from app.shared.middleware import register_middleware

from app.identity.api.business_routes import router as business_router
from app.identity.api.supplier_routes import router as supplier_router
from app.catalogue.api.item_routes import router as item_router
from app.catalogue.api.category_routes import router as category_router
from app.handshake.api.handshake_routes import router as handshake_router
from app.ordering.api.order_routes import router as order_router

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("Starting Vendor API...")

    if not firebase_admin._apps:
        firebase_admin.initialize_app()

    db = get_db()
    health = db.health_check()
    logger.info("MongoDB health: %s", health.get("is_connected"))

    yield

    logger.info("Shutting down Vendor API...")
    db.close()


def create_app() -> FastAPI:
    application = FastAPI(
        title="Vendor API",
        version="0.1.0",
        lifespan=lifespan,
    )

    register_middleware(application)

    application.include_router(business_router, prefix="/api/v1")
    application.include_router(supplier_router, prefix="/api/v1")
    application.include_router(item_router, prefix="/api/v1")
    application.include_router(category_router, prefix="/api/v1")
    application.include_router(handshake_router, prefix="/api/v1")
    application.include_router(order_router, prefix="/api/v1")

    @application.get("/health")
    async def health_check():
        db = get_db()
        return db.health_check()

    return application


app = create_app()
