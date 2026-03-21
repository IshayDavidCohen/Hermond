from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from app.handshake.domain.entities.handshake import Handshake, HandshakeStatus


class IHandshakeRepository(ABC):
    @abstractmethod
    def initiate_handshake(self, *, sender_id: str, recipient_id: str,
                           sender_type: str, recipient_type: str) -> Optional[str]: ...

    @abstractmethod
    def get_handshake(self, handshake_id: str) -> Optional[Handshake]: ...

    @abstractmethod
    def update_status(self, handshake_id: str, new_status: HandshakeStatus) -> bool: ...

    @abstractmethod
    def close_handshake(self, handshake_id: str) -> bool: ...

    @abstractmethod
    def find_pending_between(self, sender_id: str, recipient_id: str) -> Optional[Handshake]: ...

    @abstractmethod
    def get_handshakes_for_user(self, *, user_id: str, user_type: Optional[str] = None) -> List[Handshake]: ...
