import logging
from typing import Callable, Dict, List, Type

logger = logging.getLogger(__name__)


class DomainEvent:
    """Marker base class for all domain events."""


class EventBus:
    """Simple synchronous in-process event bus.

    Designed to be swapped out for a message broker later without
    changing publishing code.
    """

    _handlers: Dict[Type[DomainEvent], List[Callable]] = {}

    @classmethod
    def subscribe(cls, event_type: Type[DomainEvent], handler: Callable) -> None:
        cls._handlers.setdefault(event_type, []).append(handler)

    @classmethod
    def publish(cls, event: DomainEvent) -> None:
        handlers = cls._handlers.get(type(event), [])
        for handler in handlers:
            try:
                handler(event)
            except Exception:
                logger.exception(
                    "Handler %s failed for event %s",
                    handler.__name__,
                    type(event).__name__,
                )

    @classmethod
    def clear(cls) -> None:
        cls._handlers.clear()
