import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from typing import Dict

from app.config import settings
from app.dependencies import get_db, get_event_publisher, get_item_repo
from app.shared.middleware import register_middleware
from app.item.api.routes import router as item_router
from app.item.api.internal_routes import router as item_internal_router
from app.category.api.routes import router as category_router
from app.category.api.internal_routes import router as category_internal_router

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

LOW_STOCK_THRESHOLD = 10


# PATCH /items/{item_id}/inventory
# Body: { stock_quantity?: int, track_inventory?: bool, stock_status?: str }
# → For manual stock updates and toggle

# POST /items/{item_id}/toggle-stock
# → Quick out-of-stock toggle (sets stock_status without changing quantity)

def handle_order_created(payload: dict) -> None:
    """Decrement stock for items that have inventory tracking enabled."""
    item_repo = get_item_repo()

    for entry in payload.get("items", []):
        item = item_repo.get_item(entry["item_id"])
        if not item:
            continue

        ordered_qty = entry["quantity"]
        # Clamp: can't decrement below 0
        actual_qty = min(ordered_qty, item.stock_quantity)
        new_qty = item.stock_quantity - actual_qty
        update: Dict = {"stock_quantity": new_qty}
        if new_qty <= 0:
            update["out_of_stock"] = True
        item_repo.update_item(entry["item_id"], update)

        logger.info(
            "Stock decremented for item %s: %d → %d (%s)",
            entry["item_id"], item.stock_quantity, new_qty,
        )


def _start_event_listener() -> threading.Thread:
    """Subscribe to Redis events and run the blocking listener in a daemon thread."""
    import json
    import redis as sync_redis

    redis_client = sync_redis.from_url(settings.REDIS_URL)
    pubsub = redis_client.pubsub()

    def _on_message(message):
        if message["type"] != "message":
            return
        try:
            data = json.loads(message["data"])
            payload = data.get("payload", data)
            handle_order_created(payload)
        except Exception:
            logger.exception("Error handling order.created event")

    pubsub.subscribe(**{"order.created": _on_message})

    thread = threading.Thread(target=pubsub.listen, daemon=True)
    thread.start()
    logger.info("Event subscriber listening on 'order.created'")
    return thread


@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("Starting Catalogue Service...")
    db = get_db()
    health = db.health_check()
    logger.info("MongoDB health: %s", health.get("is_connected"))

    listener_thread = _start_event_listener()

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