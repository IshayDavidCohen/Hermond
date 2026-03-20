from typing import List, Tuple, Optional

from app.handshake.domain.repository_interfaces import IHandshakeRepository
from app.handshake.domain.entities.handshake import Handshake, HandshakeStatus
from app.handshake.domain.events import HandshakeAccepted
from app.shared.events import EventBus
from app.shared.exceptions import NotFoundError, ForbiddenError, ConflictError


class HandshakeService:
    def __init__(self, handshake_repository: IHandshakeRepository):
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
        """Returns (handshake_id, created)."""
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

        Rules
        -----
        - Only the recipient can ACCEPT / REJECT when status is PENDING.
        - Only the sender can ACKNOWLEDGE when status is ACCEPTED / REJECTED.
        """
        handshake = self.get_handshake(handshake_id)
        if handshake is None:
            raise NotFoundError(f"Handshake {handshake_id} not found")

        current = handshake.status

        if new_status in (HandshakeStatus.ACCEPTED, HandshakeStatus.REJECTED):
            if actor_user_id != handshake.recipient_id:
                raise ForbiddenError("Only the recipient may accept/reject")
            if current != HandshakeStatus.PENDING:
                raise ConflictError(f"Cannot {new_status.value} from {current.value}")

        elif new_status == HandshakeStatus.ACKNOWLEDGED:
            # BUG FIX: was checking recipient_id, should be sender_id
            if actor_user_id != handshake.sender_id:
                raise ForbiddenError("Only the sender may acknowledge")
            if current not in (HandshakeStatus.ACCEPTED, HandshakeStatus.REJECTED):
                raise ConflictError(f"Cannot acknowledge from {current.value}")

        else:
            raise ConflictError(f"Unsupported status update: {new_status}")

        result = self.handshake_repository.update_status(handshake_id, new_status)

        if result and new_status == HandshakeStatus.ACCEPTED:
            EventBus.publish(
                HandshakeAccepted(
                    handshake_id=handshake_id,
                    sender_id=handshake.sender_id,
                    recipient_id=handshake.recipient_id,
                    sender_type=handshake.sender_type,
                    recipient_type=handshake.recipient_type,
                )
            )

        return result

    def close_handshake(self, handshake_id: str) -> bool:
        """Delete a handshake record."""
        return self.handshake_repository.close_handshake(handshake_id)

    def get_handshake(self, handshake_id: str) -> Optional[Handshake]:
        """Retrieve a handshake by ID."""
        return self.handshake_repository.get_handshake(handshake_id)

    def list_user_handshakes(
        self, *, user_id: str, user_type: Optional[str] = None
    ) -> List[Handshake]:
        """List handshakes for a user."""
        return self.handshake_repository.get_handshakes_for_user(
            user_id=user_id, user_type=user_type
        )
