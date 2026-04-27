import json
import logging
from typing import Callable, Dict

import redis as sync_redis

logger = logging.getLogger(__name__)

LOW_STOCK_THRESHOLD = 10


class EventSubscriber:
    def __init__(self, redis_url: str):
        self._redis = sync_redis.from_url(redis_url)
        self._pubsub = self._redis.pubsub()

    def subscribe(self, event_type: str, handler: Callable[[Dict], None]) -> None:
        self._pubsub.subscribe(**{event_type: lambda msg: self._dispatch(msg, handler)})

    def _dispatch(self, message, handler: Callable[[Dict], None]) -> None:
        if message["type"] != "message":
            return
        try:
            data = json.loads(message["data"])
            handler(data.get("payload", data))
        except Exception:
            logger.exception("Error handling event")

    def listen(self) -> None:
        """Blocking listen loop — run in a background thread."""
        for message in self._pubsub.listen():
            pass  # dispatched via callback in subscribe