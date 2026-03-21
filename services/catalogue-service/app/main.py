import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.dependencies import get_db
from app.shared.middleware import register_middleware
from app.item.api.routes import router as item_router
from app.category.api.routes import router as category_router
from app.item.api.internal_routes import router as item_internal_router
from app.category.api.internal_routes import router as category_internal_router

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("Starting Catalogue Service...")
    db = get_db()
    health = db.health_check()
    logger.info("MongoDB health: %s", health.get("is_connected"))
    yield
    logger.info("Shutting down Catalogue Service...")
    db.close()


def create_app() -> FastAPI:
    application = FastAPI(title="Catalogue Service", version="0.1.0", lifespan=lifespan)
    register_middleware(application)
    application.include_router(item_router, prefix="/api/v1")
    application.include_router(category_router, prefix="/api/v1")
    application.include_router(item_internal_router)
    application.include_router(category_internal_router)

    @application.get("/health")
    async def health_check():
        db = get_db()
        return db.health_check()

    return application


app = create_app()
