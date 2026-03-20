from fastapi import Header, HTTPException, status

from app.shared.auth.firebase import verify_firebase_token


async def get_current_user(authorization: str = Header(...)) -> dict:
    """FastAPI dependency that extracts and verifies a Firebase bearer token."""
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
        )

    token = parts[1]
    try:
        decoded = verify_firebase_token(token)
        return decoded
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {exc}",
        )
