from functools import wraps
from flask import request, jsonify
import firebase_admin
from firebase_admin import auth


def verify_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if Authorization header exists
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No token provided'}), 401

        try:
            # Extract token from "Bearer <token>"
            token = auth_header.split(' ')[1]

            # Verify token with Firebase
            decoded_token = auth.verify_id_token(token)

            # Add user info to request
            request.user = decoded_token

            # Continue to the route handler
            return f(*args, **kwargs)

        except IndexError:
            # If token format is invalid
            return jsonify({'error': 'Invalid token format'}), 401
        except auth.InvalidIdTokenError:
            # If token is expired or invalid
            return jsonify({'error': 'Token expired or invalid'}), 401
        except Exception as e:
            # Any other errors
            return jsonify({'error': f'Token verification failed: {str(e)}'}), 401

    return decorated_function
