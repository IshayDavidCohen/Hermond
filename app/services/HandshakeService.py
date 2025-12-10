from typing import List, Dict, Tuple, Union
from bson import ObjectId

# App Dependencies
from app.infra.repositories.HandshakeRepository import HandshakeRepository


class HandshakeService:
    def __init__(self, handshake_repo: HandshakeRepository):
        self.handshake_module = handshake_repo.handshake_module
        self.HandshakeRepository = handshake_repo

        # Private Main Methods (Used only for more readable code and is implemented only in class)
        self.__initiate_handshake = self.HandshakeRepository.handshake_module.initiate_handshake
        self.__update_business = self.HandshakeRepository.business_module.update_business
        self.__update_supplier = self.HandshakeRepository.supplier_module.update_supplier

    def new_handshake(self, sender_id: Union[ObjectId, str], recipient_id: Union[ObjectId, str], sender_type: str, recipient_type: str) -> Tuple[str, bool]:
        """
        Function initiates a new handshake between two entities.
        Payload should contain the following:
        sender_id: str
        recipient_id: str
        sender: 'business' or 'supplier'
        recipient: 'business' or 'supplier'

        :param sender_id: ObjectId or str
        :param recipient_id: ObjectId or str
        :param sender_type: str
        :param recipient_type: str

        :return: 0/1 (Type: int)
        """
        business_status, supplier_status = False, False

        # 1. Get sender and recipient using __retrieve_user_by_type
        sender = self.__retrieve_user_by_type(sender_id, sender_type)
        recipient = self.__retrieve_user_by_type(recipient_id, recipient_type)

        if not sender or not recipient:
            # Logger
            print('Sender or recipient not found')
            return '', False

        # 2. Check if handshake already exists (checking one side is enough)
        if sender['handshake_requests'].get(recipient['company_name']):
            # Logger
            print('Handshake already exists')
            return '', False

        # 3. Initiate the Handshake and get handshake_id (str of ObjectId)
        hid = self.__initiate_handshake(sender_id=sender_id,
                                        recipient_id=recipient_id,
                                        sender=sender_type,
                                        recipient=recipient_type)

        # 4. Update both to include handshake_id in their handshake_requests
        sender['handshake_requests'][recipient['company_name']] = ObjectId(hid)
        recipient['handshake_requests'][sender['company_name']] = ObjectId(hid)

        if sender_type == 'business':
            business_status = self.__update_business(business_id=sender['_id'],
                                                     update_data={'handshake_requests': sender['handshake_requests']})

            supplier_status = self.__update_supplier(supplier_id=recipient['_id'],
                                                     update_data={'handshake_requests': recipient['handshake_requests']})

        elif sender_type == 'supplier':
            supplier_status = self.__update_supplier(supplier_id=sender['_id'],
                                                     update_data={'handshake_requests': sender['handshake_requests']})

            business_status = self.__update_business(business_id=recipient['_id'],
                                                     update_data={'handshake_requests': recipient['handshake_requests']})

        return hid, all([business_status, supplier_status])

    def get_user_handshakes(self, user_id: str, user_type: str) -> List:
        """
        Function returns all handshakes that belong to a user.
        :param user_id: str of ObjectId
        :param user_type: business/supplier
        :return: List
        """

        user = self.__retrieve_user_by_type(user_id=user_id, user_type=user_type)

        if user:
            cursor = self.handshake_module.get_multiple_handshakes(
                {'_id': {'$in': list(user['handshake_requests'].values())}})

            handshakes = [h for h in cursor]
            if handshakes:
                # Convert ObjectId to str
                return [self.handshake_module.remove_object_id(h) for h in handshakes]
        return []

    def process_handshake(self, user_id: str, handshake_id: str, status: str) -> bool:
        """
        Wrapper function.
        Function updates the status of a handshake.
        :param user_id: str of ObjectId
        :param handshake_id: str of ObjectId
        :param status: accepted/rejected
        :return: 0/1 (Type: int)
        """

        handshake = self.handshake_module.get_handshake(handshake_id)
        if handshake:

            # Response from the recipient
            if user_id == str(handshake['recipient_id']) and (status in ['accepted', 'rejected']):
                response = self.handshake_module.update_status(handshake_document=handshake, status_change=status)

                if status == 'accepted' and response:
                    return self.__close_handshake(action='accepted', handshake_document=handshake)

                return response  # Something went wrong with updating the status

            # Response from the sender
            elif user_id == str(handshake['sender_id']) and (status == 'acknowledged'):

                # Change response to acknowledged, initiating handshake deletion in 24 hours.
                response = self.handshake_module.update_status(handshake_id=handshake_id, status_change=status)

                if response:
                    # Finalize the handshake (acknowledged)
                    return self.__close_handshake(action='acknowledged', handshake_document=handshake)

                return response  # Something went wrong with updating the status
        return False

    def __close_handshake(self, action: str, handshake_id: str = None, handshake_document: Dict = None) -> bool:
        business_updated_flag, supplier_updated_flag = False, False

        if handshake_id is None and handshake_document is None:
            return False
        elif handshake_id and (handshake_document is None):
            handshake_document = self.handshake_module.get_handshake(handshake_id)

        if handshake_document:

            # Set the respective keys for each supplier and business
            sender_key = 'approved_businesses' if handshake_document['senderType'] == 'supplier' else 'my_suppliers'
            recipient_key = 'approved_businesses' if handshake_document['recipientType'] == 'supplier' else 'my_suppliers'

            # Retrieve the sender and recipient
            sender = self.__retrieve_user_by_type(handshake_document['sender_id'],
                                                  handshake_document['senderType'])

            recipient = self.__retrieve_user_by_type(handshake_document['recipient_id'],
                                                     handshake_document['recipientType'])

            if not sender and not recipient:
                return False

            query = {'sender_query': {}, 'recipient_query': {}}

            # Execute the given action.
            if action == 'accepted':
                sender[sender_key][recipient['company_name']] = ObjectId(recipient['_id'])
                recipient[recipient_key][sender['company_name']] = ObjectId(sender['_id'])
                query['sender_query'] = {sender_key: sender[sender_key]}
                query['recipient_query'] = {recipient_key: recipient[recipient_key]}

            elif action == 'acknowledged':
                del sender['handshake_requests'][recipient['company_name']]
                del recipient['handshake_requests'][sender['company_name']]
                query['sender_query'] = {'handshake_requests': sender['handshake_requests']}
                query['recipient_query'] = {'handshake_requests': recipient['handshake_requests']}

            # Update both
            if handshake_document['senderType'] == 'business':
                business_updated_flag = self.__update_business(business_id=sender['_id'],
                                                               update_data=query['sender_query'])

                supplier_updated_flag = self.__update_supplier(supplier_id=recipient['_id'],
                                                               update_data=query['recipient_query'])

            elif handshake_document['senderType'] == 'supplier':

                supplier_updated_flag = self.__update_supplier(supplier_id=sender['_id'],
                                                               update_data=query['sender_query'])

                business_updated_flag = self.__update_business(business_id=recipient['_id'],
                                                               update_data=query['recipient_query'])

            return all([business_updated_flag, supplier_updated_flag])
        return False

    def __retrieve_user_by_type(self, user_id: str, user_type: str) -> Dict:
        module_map = {
            'business': self.HandshakeRepository.business_module,
            'supplier': self.HandshakeRepository.supplier_module
        }
        method_map = {
            'business': 'get_business',
            'supplier': 'get_supplier'
        }
        method = getattr(module_map[user_type], method_map[user_type], None)
        if method:
            return method(user_id)
        return {}
