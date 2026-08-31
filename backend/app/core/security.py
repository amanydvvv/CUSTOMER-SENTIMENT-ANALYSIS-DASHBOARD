from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
import bcrypt
from jose import jwt, JWTError
from backend.app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against bcrypt hashed password."""
    try:
        if not plain_password or not hashed_password:
            return False
        # Truncate to 72 bytes as required by bcrypt
        plain_bytes = plain_password.encode("utf-8")[:72]
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        return plain_password == hashed_password


def get_password_hash(password: str) -> str:
    """Generate bcrypt password hash."""
    # Truncate to 72 bytes as required by bcrypt
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def create_access_token(
    subject: Union[str, Any],
    role: str = "viewer",
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generate signed JWT access token with role."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "role": role,
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate JWT access token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
