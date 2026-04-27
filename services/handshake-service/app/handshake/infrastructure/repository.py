from typing import Optional, Dict, List
from datetime import datetime

from app.shared.utils import to_oid
from app.shared.database.base_repository import BaseRepository
from app.shared.database.mongodb import Database
from app.handshake.domain.entities.handshake import Handshake, HandshakeStatus
from app.handshake.domain.repository_interfaces import IHandshakeRepository


class HandshakeRepository(BaseRepository, IHandshakeRepository):
    COLLECTION = "handshakes"

    def __init__(self, db: Database):
        super().__init__(db, self.COLLECTION)

    def initiate_handshake(self, *, sender_id: str, recipient_id: str,
                           sender_type: str, recipient_type: str) -> Optional[str]:
        sender_oid = to_oid(sender_id)
        recipient_oid = to_oid(recipient_id)
        if not sender_oid or not recipient_oid:
            return None
        handshake = Handshake.new(sender_id=sender_id, recipient_id=recipient_id,
                                  sender_type=sender_type, recipient_type=recipient_type)
        doc = handshake.from_entity()
        doc.pop("_id", None)
        doc["sender_id"] = sender_oid
        doc["recipient_id"] = recipient_oid
        return self._create_document(doc)

    def get_handshake(self, handshake_id: str, projection: Optional[Dict] = None) -> Optional[Handshake]:
        hid = to_oid(handshake_id)
        if not hid:
            return None
        doc = self._db.find_one(self.COLLECTION, {"_id": hid}, projection)
        if not doc:
            return None
        return Handshake.to_entity(doc)

    def update_status(self, handshake_id: str, new_status: HandshakeStatus) -> bool:
        if new_status not in HandshakeStatus:
            return False
        hid = to_oid(handshake_id)
        if not hid:
            return False
        now = datetime.now()
        result = self._db.update_one(
            self.COLLECTION, {"_id": hid},
            {"status": new_status.value, "updated_at": now}, operation="$set",
        )
        return result.modified_count == 1

    def close_handshake(self, handshake_id: str) -> bool:
        hid = to_oid(handshake_id)
        if not hid:
            return False
        result = self._db.delete_one(self.COLLECTION, {"_id": hid})
        return result.deleted_count == 1

    def find_pending_between(self, sender_id: str, recipient_id: str) -> Optional[Handshake]:
        sender_oid = to_oid(sender_id)
        recipient_oid = to_oid(recipient_id)
        if not sender_oid or not recipient_oid:
            return None
        query = {
            "status": HandshakeStatus.PENDING.value,
            "$or": [
                {"sender_id": sender_oid, "recipient_id": recipient_oid},
                {"sender_id": recipient_oid, "recipient_id": sender_oid},
            ],
        }
        doc = self._db.find_one(self.COLLECTION, query)
        return Handshake.to_entity(doc) if doc else None

    def get_handshakes_for_user(self, *, user_id: str, user_type: Optional[str] = None,
                                projection: Optional[Dict] = None) -> List[Handshake]:
        user_oid = to_oid(user_id)
        if not user_oid:
            return []
        if user_type:
            query = {"$or": [
                {"sender_id": user_oid, "sender_type": user_type},
                {"recipient_id": user_oid, "recipient_type": user_type},
            ]}
        else:
            query = {"$or": [{"sender_id": user_oid}, {"recipient_id": user_oid}]}
        cursor = self._db.find_all(collection=self.COLLECTION, query=query, subfield_query=projection)
        docs = list(cursor) if cursor else []
        return [Handshake.to_entity(d) for d in docs]
