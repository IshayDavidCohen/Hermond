from functools import lru_cache

from app.config import settings
from app.shared.database.mongodb import Database
from app.shared.events.publisher import EventPublisher
from app.handshake.infrastructure.repository import HandshakeRepository
from app.handshake.application.service import HandshakeService


@lru_cache()
def get_db() -> Database:
    return Database(database_name=settings.DB_NAME, connection_uri=settings.MONGO_URI)


@lru_cache()
def get_event_publisher() -> EventPublisher:
    return EventPublisher(redis_url=settings.REDIS_URL)


def get_handshake_repo() -> HandshakeRepository:
    return HandshakeRepository(db=get_db())


def get_handshake_service() -> HandshakeService:
    return HandshakeService(
        handshake_repository=get_handshake_repo(),
        event_publisher=get_event_publisher(),
    )
