from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional
from enum import Enum


class HandshakeStatus(str, Enum):
    PENDING = 'pending'
    ACKNOWLEDGED = 'acknowledged'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'


@dataclass
class Handshake:
    id: Optional[str]
    sender_id: str
    recipient_id: str
    sender_type: str
    recipient_type: str
    status: HandshakeStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def new(cls, *, sender_id: str, recipient_id: str, sender_type: str,
            recipient_type: str, now: Optional[datetime] = None) -> "Handshake":
        now = now or datetime.now()
        return cls(id=None, sender_id=sender_id, recipient_id=recipient_id,
                   sender_type=sender_type, recipient_type=recipient_type,
                   status=HandshakeStatus.PENDING, created_at=now, updated_at=now)

    @classmethod
    def to_entity(cls, doc: Dict) -> "Handshake":
        return cls(
            id=str(doc["_id"]),
            sender_id=str(doc["sender_id"]),
            recipient_id=str(doc["recipient_id"]),
            sender_type=doc.get("sender_type", ""),
            recipient_type=doc.get("recipient_type", ""),
            status=HandshakeStatus(doc["status"]),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )

    def from_entity(self) -> Dict:
        doc = {
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "sender_type": self.sender_type,
            "recipient_type": self.recipient_type,
            "status": self.status.value if isinstance(self.status, HandshakeStatus) else str(self.status),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.id is not None:
            doc["_id"] = self.id
        return doc
