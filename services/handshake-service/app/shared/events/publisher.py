import json
import logging
import redis as sync_redis

logger = logging.getLogger(__name__)


class EventPublisher:
    def __init__(self, redis_url: str):
        self._redis = sync_redis.from_url(redis_url)

    def publish(self, event_type: str, payload: dict) -> None:
        message = json.dumps({"event_type": event_type, "payload": payload})
        self._redis.publish(event_type, message)
        logger.info("Published event %s", event_type)
