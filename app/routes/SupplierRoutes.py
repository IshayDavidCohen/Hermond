from flask import Blueprint, current_app, jsonify, request

# App dependencies
from app.utilities.funcs import check_dict_validity
from app.utilities.validation_formats import SUPPLIER, SUPPLIER_ITEM

supplier_bp = Blueprint('supplier_bp', __name__)


@supplier_bp.route('/create/profile', methods=['POST'])
def create_supplier_route():
    supplier_service = current_app.config['supplier_service']

    # Listen and get data from POST
    creation_data = request.get_json()

    # Quick validity check
    if check_dict_validity(validity_map=SUPPLIER, data=creation_data):
        returned_id, category_validity_map = supplier_service.create_supplier(creation_data)

        return jsonify({'id': returned_id}), 201

    # Didn't pass validity :( womp womp
    return 'Missing fields or values', 400


@supplier_bp.route('/get/<supplier_id>', methods=['GET'])
def get_supplier_route(supplier_id):
    supplier_service = current_app.config['supplier_service']
    return jsonify(supplier_service.supplier_module.get_supplier(supplier_id)), 201


@supplier_bp.route('/get/category_carousel/<category_id>', methods=['GET'])
def get_category_carousel(category_id):
    supplier_service = current_app.config['supplier_service']
    return jsonify(supplier_service.get_supplier_carousel(category_id=category_id)), 201


@supplier_bp.route('/create/item', methods=['POST'])
def create_supplier_item():
    supplier_service = current_app.config['supplier_service']

    # Listen and get data from POST
    creation_data = request.get_json()

    # Quick validity check
    if check_dict_validity(validity_map=SUPPLIER_ITEM, data=creation_data):
        returned_id = supplier_service.create_item(creation_data)
        return jsonify({'id': returned_id}), 201
    return 'Missing fields or values', 400


@supplier_bp.route('/delete/item/<item_id>', methods=['DELETE'])
def delete_supplier_item(item_id):
    supplier_service = current_app.config['supplier_service']
    return jsonify(supplier_service.delete_item(item_id)), 201
