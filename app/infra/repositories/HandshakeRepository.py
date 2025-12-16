from typing import Optional, Dict, List
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
    def initiate_handshake(self, *, sender_id: str, recipient_id: str, sender_type: str, recipient_type: str,) -> Optional[str]:
        sender_oid = to_oid(sender_id)
        recipient_oid = to_oid(recipient_id)
        if not sender_oid or not recipient_oid:
            err = "sender_id/recipient_id must be valid ObjectId strings"
            return None

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
            err = f"Invalid status: {new_status}"
            return False

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


    # -------------------------------------------------------------------------
    # Convenience queries (ID conversion happens here – NOT in services)
    # -------------------------------------------------------------------------
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
            ]
        }
        
        doc = self._db.find_one(self.COLLECTION, query)
        return Handshake.to_entity(doc) if doc else None
    
    def get_handshakes_for_user(
            self,
            *,
            user_id: str,
            user_type: Optional[str] = None,
            projection: Optional[Dict] = None
    ) -> List[Handshake]:
        """
        List handshakes where user appears as sender or recipient
        IF user_type is provided, filters matches by sender_type/recipient_type accordingly.
        """
        user_oid = to_oid(user_id)
        if not user_oid:
            return []

        if user_type:
            query = {
                "$or": [
                    {"sender_id": user_oid, "sender_type": user_type},
                    {"recipient_id": user_oid, "recipient_type": user_type},
                ]
            }
        else:
            query = {"$or": [{"sender_id": user_oid}, {"recipient_id": user_oid}]}

        cursor = self._db.find_all(collection=self.COLLECTION, query=query, subfield_query=projection)
        docs = list(cursor) if cursor else []
        return [Handshake.to_entity(d) for d in docs]
        