from flask import Blueprint, current_app, jsonify, request

# App dependencies
from app.utilities.funcs import check_dict_validity
from app.utilities.validation_formats import SUPPLIER, SUPPLIER_ITEM

# Presentation
from app.presentation.mappers import supplier_to_carousel_item
from app.presentation.carousel import get_carousel_data

supplier_bp = Blueprint('supplier_bp', __name__)


@supplier_bp.route('/create/profile', methods=['POST'])
def create_supplier_route():
    # TODO: PASSED
    supplier_service = current_app.config['supplier_service']
    # Listen and get data from POST
    creation_data = request.get_json()

    # Quick validity check
    if check_dict_validity(validity_map=SUPPLIER, data=creation_data):
        returned_id, category_validity_map = supplier_service.create_supplier(creation_data)

        return jsonify({'id': returned_id}), 201

    # Didn't pass validity
    return 'Missing fields or values', 400


@supplier_bp.route('/get/<supplier_id>', methods=['GET'])
def get_supplier_route(supplier_id):
    # TODO: PASSED
    supplier_service = current_app.config['supplier_service']
    supplier = supplier_service.get_supplier(supplier_id)
    # TODO: For now convert entity, but in the future should use mapper
    return jsonify(supplier.from_entity()), 200


@supplier_bp.route('/get/category_carousel/<category_id>', methods=['GET'])
def get_category_carousel(category_id):
    supplier_service = current_app.config['supplier_service']

    suppliers = supplier_service.get_suppliers_from_category(category_id)
    # Map Supplier entities -> simple dicts for UI
    data_list = [supplier_to_carousel_item(s) for s in suppliers]

    carousel = get_carousel_data(
        data_list=data_list,
        keys={
            "link": "link",
            "title": "title",
            "desc": "desc",
            "banner": "banner",
            "icon": "icon",
        },
    )
    return jsonify(carousel), 200


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

    result = supplier_service.delete_item(item_id)
    if isinstance(result, str):
        return jsonify({'message': result}), 400
    return jsonify({'message': result}), 200
