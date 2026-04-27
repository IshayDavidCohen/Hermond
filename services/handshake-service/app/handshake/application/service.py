from typing import List, Tuple, Optional

from app.handshake.domain.repository_interfaces import IHandshakeRepository
from app.handshake.domain.entities.handshake import Handshake, HandshakeStatus
from app.shared.events.publisher import EventPublisher
from app.shared.exceptions import NotFoundError, ForbiddenError, ConflictError


class HandshakeService:
    def __init__(self, handshake_repository: IHandshakeRepository,
                 event_publisher: Optional[EventPublisher] = None):
        self.handshake_repository = handshake_repository
        self.event_publisher = event_publisher

    def create_handshake(self, *, sender_id: str, recipient_id: str,
                         sender_type: str, recipient_type: str,
                         dedupe_pending: bool = True) -> Tuple[str, bool]:
        if dedupe_pending:
            existing = self.handshake_repository.find_pending_between(sender_id, recipient_id)
            if existing and existing.id:
                return existing.id, False
        hid = self.handshake_repository.initiate_handshake(
            sender_id=sender_id, recipient_id=recipient_id,
            sender_type=sender_type, recipient_type=recipient_type,
        )
        return hid, True

    def respond_to_handshake(self, *, actor_user_id: str, handshake_id: str,
                             new_status: HandshakeStatus) -> bool:
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
            if actor_user_id != handshake.sender_id:
                raise ForbiddenError("Only the sender may acknowledge")
            if current not in (HandshakeStatus.ACCEPTED, HandshakeStatus.REJECTED):
                raise ConflictError(f"Cannot acknowledge from {current.value}")
        else:
            raise ConflictError(f"Unsupported status update: {new_status}")

        result = self.handshake_repository.update_status(handshake_id, new_status)

        if result and new_status == HandshakeStatus.ACCEPTED and self.event_publisher:
            self.event_publisher.publish("handshake.accepted", {
                "handshake_id": handshake_id,
                "sender_id": handshake.sender_id,
                "recipient_id": handshake.recipient_id,
                "sender_type": handshake.sender_type,
                "recipient_type": handshake.recipient_type,
            })

        return result

    def close_handshake(self, handshake_id: str) -> bool:
        return self.handshake_repository.close_handshake(handshake_id)

    def get_handshake(self, handshake_id: str) -> Optional[Handshake]:
        return self.handshake_repository.get_handshake(handshake_id)

    def list_user_handshakes(self, *, user_id: str, user_type: Optional[str] = None) -> List[Handshake]:
        return self.handshake_repository.get_handshakes_for_user(user_id=user_id, user_type=user_type)
