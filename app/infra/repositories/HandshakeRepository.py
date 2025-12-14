from typing import Optional, Dict
from pymongo.cursor import Cursor
from datetime import datetime

from app.utilities.funcs import to_oid
from app.infra.BaseDAO import BaseDAO
from app.infra.Database import Database

from app.domain.entities.Handshake import Handshake, HandshakeStatus

class HandshakeRepository(BaseDAO):
    COLLECTION = "handshakes"
    def __init__(self, db: Database):
        super().__init__(db, self.COLLECTION)

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    def initiate_handshake(self, *, sender_id: str, recipient_id: str, sender_type: str, recipient_type: str,) -> str:
        sender_oid = to_oid(sender_id)
        recipient_oid = to_oid(recipient_id)
        if not sender_oid or not recipient_oid:
            raise ValueError("sender_id/recipient_id must be valid ObjectId strings")

        handshake = Handshake.new(
            sender_id=sender_id,
            recipient_id=recipient_id,
            sender_type=sender_type,
            recipient_type=recipient_type,
        )

        doc = handshake.from_entity()
        doc.pop("_id", None)

        # Convert relationship ids to ObjectId for Mongo storage
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
            raise ValueError(f"Invalid status: {new_status}")

        hid = to_oid(handshake_id)
        if not hid:
            return False

        now = datetime.now()
        result = self._db.update_one(
            self.COLLECTION,
            {"_id": hid},
            {"status": new_status.value, "updated_at": now},
            operation="$set",
        )
        return result.modified_count == 1

    def close_handshake(self, handshake_id: str) -> bool:
        hid = to_oid(handshake_id)
        if not hid:
            return False
        result = self._db.delete_one(self.COLLECTION, {"_id": hid})
        return result.deleted_count == 1

    # ----------------------------
    # Queries
    # ----------------------------
    def get_multiple_handshakes(self, query: Dict, projection: Optional[Dict] = None) -> Cursor:
        return self._db.find_all(collection=self.COLLECTION, query=query, subfield_query=projection)

    def get_handshake_list(self, projection: Optional[Dict] = None) -> Cursor:
        return self._db.find_all(collection=self.COLLECTION, query={}, subfield_query=projection)

