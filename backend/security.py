
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from backend import config


def hash_password(password: str) -> str:
    """Hash a plain-text password with bcrypt (salt is generated automatically)."""
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False



DUMMY_HASH = hash_password("dummy-password-for-timing")


def create_access_token(user_id: int, business_id: int, role: str) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "business_id": business_id,
        "role": role,
        "iat": now,
        "exp": now + timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    }

    return jwt.encode(
        payload,
        config.JWT_SECRET_KEY,
        algorithm=config.JWT_ALGORITHM
    )


def decode_access_token(token: str) -> dict | None:
    """Return the token payload, or None if the token is invalid or expired."""
    try:
        return jwt.decode(
            token,
            config.JWT_SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
    except (jwt.PyJWTError, TypeError):
        return None
