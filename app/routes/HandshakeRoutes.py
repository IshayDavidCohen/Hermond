from flask import Blueprint, current_app, jsonify, request

# App dependencies
from app.modules.Handshake import STATUS_OPTIONS
from app.utilities.funcs import check_dict_validity
from app.utilities.validation_formats import HANDSHAKE

handshake_bp = Blueprint('handshake_bp', __name__)


@handshake_bp.route('/create', methods=['POST'])
def create_handshake_route():
    handshake_service = current_app.config['handshake_service']

    # Listen and get data from POST
    creation_data = request.get_json()

    # Quick validity check
    if check_dict_validity(validity_map=HANDSHAKE, data=creation_data):
        # Logger - Add filed to pass validity.

        hid, created = handshake_service.new_handshake(sender_id=creation_data['sender_id'],
                                                     recipient_id=creation_data['recipient_id'],
                                                     sender_type=creation_data['sender_type'],
                                                     recipient_type=creation_data['recipient_type'])
        return jsonify({'id': hid, 'created': created, 'existed': not created}), 201

    return 'Missing fields or values', 400


@handshake_bp.route('/get/<handshake_id>', methods=['GET'])
def get_handshake_route(handshake_id):
    handshake_service = current_app.config['handshake_service']
    return jsonify(handshake_service.handshake_module.get_handshake(handshake_id)), 201


@handshake_bp.route('/get/user_handshakes/<user_type>/<user_id>', methods=['GET'])
def get_user_handshakes_route(user_type, user_id):
    handshake_service = current_app.config['handshake_service']
    handshakes = handshake_service.get_user_handshakes(user_id, user_type)
    if handshakes:
        return jsonify(handshakes), 200
    return 'No handshakes found', 404


@handshake_bp.route('/ack/<user_id>/<handshake_id>/<response>', methods=['GET'])
def ack_handshake_routes(user_id, handshake_id, response):
    handshake_service = current_app.config['handshake_service']

    if response in STATUS_OPTIONS:
        return jsonify({'success': handshake_service.process_handshake(user_id, handshake_id, response)}), 201
    return 'Invalid response', 400

# @supplier_bp.route('/get/<supplier_id>', methods=['GET'])
# def get_supplier_route(supplier_id):
#     supplier_service = current_app.config['supplier_service']
#     return jsonify(supplier_service.supplier_module.get_supplier(supplier_id)), 201
#
#
# @supplier_bp.route('/get/category_carousel/<category_id>', methods=['GET'])
# def get_category_carousel(category_id):
#     supplier_service = current_app.config['supplier_service']
#     return jsonify(supplier_service.get_supplier_carousel(category_id=category_id)), 201
#
#
# @supplier_bp.route('/create/item', methods=['POST'])
# def create_supplier_item():
#     supplier_service = current_app.config['supplier_service']
#
#     # Listen and get data from POST
#     creation_data = request.get_json()
#
#     # Quick validity check
#     if check_dict_validity(validity_map=SUPPLIER_ITEM, data=creation_data):
#         returned_id = supplier_service.create_item(creation_data)
#         return jsonify({'id': returned_id}), 201
#     return 'Missing fields or values', 400
#
#
# @supplier_bp.route('/delete/item/<item_id>', methods=['DELETE'])
# def delete_supplier_item(item_id):
#     supplier_service = current_app.config['supplier_service']
#     return jsonify(supplier_service.delete_item(item_id)), 201
