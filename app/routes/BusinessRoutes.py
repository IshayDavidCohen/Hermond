from flask import Blueprint, request, jsonify, current_app
from app.utilities.validation_formats import BUSINESS
from app.utilities.funcs import check_dict_validity
from requests import get

business_bp = Blueprint('business_bp', __name__)


@business_bp.route('/create/profile', methods=['POST'])
def create_business_route():
    business_service = current_app.config['business_service']

    # Listen and get data from POST
    creation_data = request.get_json()

    if check_dict_validity(validity_map=BUSINESS, data=creation_data):
        returned_id = business_service.create_business(creation_data)
        return jsonify({'id': returned_id}), 201

    return 'Missing fields or values', 400

