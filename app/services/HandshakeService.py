from typing import List, Tuple, Optional

# App Dependencies
from app.infra.repositories.HandshakeRepository import HandshakeRepository
from app.domain.entities.Handshake import Handshake, HandshakeStatus


class HandshakeError(Exception):
    """Base error type for handshake workflows."""


class HandshakeNotFound(HandshakeError):
    pass


class HandshakeForbidden(HandshakeError):
    pass


class HandshakeInvalidTransition(HandshakeError):
    pass

class HandshakeService:
    def __init__(self, handshake_repository: HandshakeRepository):
        self.handshake_repository = handshake_repository

    def create_handshake(
        self,
        *,
        sender_id: str,
        recipient_id: str,
        sender_type: str,
        recipient_type: str,
        dedupe_pending: bool = True,
    ) -> Tuple[str, bool]:
        """Returns (handshake_id, created)"""
        if dedupe_pending:
            existing = self.handshake_repository.find_pending_between(sender_id, recipient_id)
            if existing and existing.id:
                return existing.id, False

        hid = self.handshake_repository.initiate_handshake(
            sender_id=sender_id,
            recipient_id=recipient_id,
            sender_type=sender_type,
            recipient_type=recipient_type,
        )
        return hid, True

    def respond_to_handshake(
            self,
            *,
            actor_user_id: str,
            handshake_id: str,
            new_status: HandshakeStatus,
    ) -> bool:
        """Authorization + transition checks, then status update.

        Rules:
        - Only recipient can ACCEPT/REJECT when PENDING.
        - Only sender can ACKNOWLEDGE when ACCEPTED/REJECTED.
        """
        handshake = self.get_handshake(handshake_id)
        if handshake is None:
            raise HandshakeNotFound(f"Handshake {handshake_id} not found")

        current = handshake.status

        if new_status in (HandshakeStatus.ACCEPTED, HandshakeStatus.REJECTED):
            if actor_user_id != handshake.recipient_id:
                raise HandshakeForbidden("Only the recipient may accept/reject")
            if current != HandshakeStatus.PENDING:
                raise HandshakeInvalidTransition(f"Cannot {new_status.value} from {current.value}")

        elif new_status == HandshakeStatus.ACKNOWLEDGED:
            if actor_user_id != handshake.recipient_id:
                raise HandshakeForbidden("Only the sender may acknowledge")
            if current not in (HandshakeStatus.ACCEPTED, HandshakeStatus.REJECTED):
                raise HandshakeInvalidTransition(f"Cannot acknowledge from {current.value}")

        else:
            raise HandshakeInvalidTransition(f"Unsupported status update: {new_status}")

        return self.handshake_repository.update_status(handshake_id, new_status)

    def close_handshake(self, handshake_id: str) -> bool:
        return self.handshake_repository.close_handshake(handshake_id)

    def get_handshake(self, handshake_id: str) -> Optional[Handshake]:
        return self.handshake_repository.get_handshake(handshake_id)

    def list_user_handshakes(self, *, user_id: str, user_type: Optional[str] = None) -> List[Handshake]:
        return self.handshake_repository.get_handshakes_for_user(user_id=user_id, user_type=user_type)
