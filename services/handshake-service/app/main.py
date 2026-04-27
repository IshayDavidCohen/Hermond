import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.dependencies import get_db
from app.shared.middleware import register_middleware
from app.handshake.api.routes import router as handshake_router

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("Starting Handshake Service...")
    db = get_db()
    health = db.health_check()
    logger.info("MongoDB health: %s", health.get("is_connected"))
    yield
    logger.info("Shutting down Handshake Service...")
    db.close()


def create_app() -> FastAPI:
    application = FastAPI(title="Handshake Service", version="0.1.0", lifespan=lifespan)
    register_middleware(application)
    application.include_router(handshake_router, prefix="/api/v1")

    @application.get("/health")
    async def health_check():
        db = get_db()
        return db.health_check()

    return application


app = create_app()
