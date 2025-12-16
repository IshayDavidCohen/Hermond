from flask import Blueprint, current_app, jsonify, request

# App dependencies
from app.domain.entities.Handshake import HandshakeStatus
from app.utilities.funcs import check_dict_validity
from app.utilities.validation_formats import HANDSHAKE

from app.presentation.mappers import handshake_to_dict

handshake_bp = Blueprint('handshake_bp', __name__)


@handshake_bp.route('/create', methods=['POST'])
def create_handshake_route():
    handshake_service = current_app.config['handshake_service']

    creation_data = request.get_json() or {}
    if not check_dict_validity(validity_map=HANDSHAKE, data=creation_data):
        return 'Missing fields or values', 400

    hid, created = handshake_service.create_handshake(
        sender_id=creation_data['sender_id'],
        recipient_id=creation_data['recipient_id'],
        sender_type=creation_data['sender_type'],
        recipient_type=creation_data['recipient_type']
    )
    return jsonify({'id': hid, 'created': created, 'existed': not created}), (201 if created else 200)


@handshake_bp.route('/get/<handshake_id>', methods=['GET'])
def get_handshake_route(handshake_id: str):
    handshake_service = current_app.config['handshake_service']
    handshake = handshake_service.get_handshake(handshake_id)
    if not handshake:
        return 'Handshake not found', 404
    return jsonify(handshake_to_dict(handshake)), 200


@handshake_bp.route('/get/user_handshakes/<user_type>/<user_id>', methods=['GET'])
def get_user_handshakes_route(user_type: str, user_id: str):
    handshake_service = current_app.config['handshake_service']
    handshakes = handshake_service.list_user_handshakes(user_id=user_id, user_type=user_type)
    return jsonify([handshake_to_dict(h) for h in handshakes]), 200

# Backward-compatible: old endpoint used GET + path params
@handshake_bp.route('/ack/<user_id>/<handshake_id>/<response>', methods=['GET'])
def ack_handshake_routes(user_id: str, handshake_id: str, response: str):
    return respond_handshake_route(user_id, handshake_id, response)

@handshake_bp.route('/respond/<user_id>/<handshake_id>/<response>', methods=['POST', 'GET'])
def respond_handshake_route(user_id: str, handshake_id: str, response: str):
    handshake_service = current_app.config['handshake_service']

    try:
        status = HandshakeStatus(response)
    except ValueError:
        return 'Invalid response', 400

    try:
        ok = handshake_service.respond_to_handshake(
            actor_user_id=user_id,
            handshake_id=handshake_id,
            new_status=status,
        )
        return jsonify({'success': ok}), 200
    except Exception as e:
        name = e.__class__.__name__
        if name == 'HandshakeNotFound':
            return 'Handshake not found', 404
        if name == 'HandshakeForbidden':
            return 'Forbidden', 403
        if name == 'HandshakeInvalidTransition':
            return str(e), 409
        return 'Internal error', 500

@handshake_bp.route('/close/<handshake_id>', methods=['DELETE'])
def close_handshake_route(handshake_id: str):
    handshake_service = current_app.config['handshake_service']
    ok = handshake_service.close_handshake(handshake_id)
    if not ok:
        return 'Handshake not found', 404
    return jsonify({'success': True}), 200