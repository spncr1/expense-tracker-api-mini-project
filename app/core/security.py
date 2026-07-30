from datetime import UTC, datetime, timedelta
import hashlib

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings


def _prepare_password(password: str) -> bytes:
    # bcrypt has a password length limit, so we hash first to create a fixed-size input.
    return hashlib.sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    password_bytes = _prepare_password(password)
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = _prepare_password(plain_password)
    stored_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, stored_password)


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    # sub identifies who the token belongs to; exp tells the API when to reject it.
    payload = {
        "sub": str(user_id),
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def get_user_id_from_token(token: str) -> int | None:
    settings = get_settings()

    try:
        # jwt.decode checks the signature and expiry before returning the payload.
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        return None

    user_id = payload.get("sub")

    if user_id is None:
        return None

    try:
        return int(user_id)
    except ValueError:
        return None
