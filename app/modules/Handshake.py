from typing import Union, Dict, List, Optional
from bson import ObjectId
from datetime import datetime
from pymongo.cursor import CursorType

# App Dependencies
from app.Database import Database

STATUS_OPTIONS = ['accepted', 'rejected', 'pending', 'acknowledged']


class HandshakeModule:
    def __init__(self, db: Database):
        self.db = db
        self.collection = 'handshakeCollection'

    def initiate_handshake(self, sender_id: Union[str, ObjectId], recipient_id: Union[str, ObjectId], sender: str, recipient: str) -> str:
        """
        Function creates a new handshake document

        :param sender_id: Initiator ID (Type: str, ObjectId)
        :param recipient_id: Recipient ID (Type: str, ObjectId)
        :param sender: Initiator type (Type: str)
        :param recipient: Recipient type (Type: str)

        :return: New handshake document id (Type: str)
        """
        handshake_obj = {'sender_id': ObjectId(sender_id),
                         'recipient_id': ObjectId(recipient_id),
                         'senderType': sender,
                         'recipientType': recipient,
                         'status': 'pending',  # Default value when handshake is created
                         'createdAt': datetime.utcnow(),
                         'updatedAt': datetime.utcnow()}
        result = self.db.insert_one(self.collection, handshake_obj)
        return str(result.inserted_id)

    def get_handshake(self, handshake_id: Union[str, ObjectId]) -> Optional[Dict]:
        document = self.db.find_one(self.collection, {'_id': ObjectId(handshake_id)})
        if document:
            document = self.remove_object_id(document)
        return document

    def get_multiple_handshakes(self, query: Dict) -> Optional[CursorType]:
        return self.db.find_all(self.collection, query)

    def get_handshake_list(self) -> Optional[CursorType]:
        return self.db.find_all(self.collection)

    def update_status(self, status_change: str, handshake_id: Optional[Union[str, ObjectId]] = None, handshake_document: Optional[Dict] = None) -> Union[bool, str]:

        # LOGGER
        if status_change not in STATUS_OPTIONS:
            return 'Status change must be either accepted, rejected, or pending'

        # Fetch required data.
        if handshake_id is None and handshake_document is None:
            return 'No handshake document provided'

        elif handshake_document and handshake_document.get('_id'):
            # Document is given alongside ID
            document = handshake_document
            handshake_id = handshake_document['_id']
        else:
            # Fetch the handshake document if not provided
            document = self.get_handshake(handshake_id)

        if document:
            del document['_id']

            self.apply_object_id(document)

            document['updatedAt'] = datetime.utcnow()
            document['status'] = status_change

            return self.db.update_one(self.collection, {'_id': ObjectId(handshake_id)}, document).modified_count
        return False

    def close_handshake(self, handshake_id):
        return self.db.delete_one(self.collection, {'_id': ObjectId(handshake_id)})

    @staticmethod
    def apply_object_id(document: Dict) -> Dict:
        if document.get('_id'):
            document['_id'] = ObjectId(document['_id'])
        document['sender_id'] = ObjectId(document['sender_id'])
        document['recipient_id'] = ObjectId(document['recipient_id'])
        return document

    @staticmethod
    def remove_object_id(document: Dict) -> Dict:
        if document.get('_id'):
            document['_id'] = str(document['_id'])
        document['sender_id'] = str(document['sender_id'])
        document['recipient_id'] = str(document['recipient_id'])
        return document
