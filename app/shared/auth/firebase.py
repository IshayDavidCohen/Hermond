import logging

from firebase_admin import auth

logger = logging.getLogger(__name__)


def verify_firebase_token(token: str) -> dict:
    """Verify a Firebase ID token and return the decoded claims.

    Raises firebase_admin.auth.InvalidIdTokenError on failure.
    """
    return auth.verify_id_token(token)
