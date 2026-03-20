from dataclasses import dataclass

from app.shared.events import DomainEvent


@dataclass
class HandshakeAccepted(DomainEvent):
    """Published when a handshake is accepted by the recipient."""
    handshake_id: str
    sender_id: str
    recipient_id: str
    sender_type: str
    recipient_type: str
