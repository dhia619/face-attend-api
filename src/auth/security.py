from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from bcrypt import gensalt, hashpw, checkpw
import secrets
import hashlib

from src.config import get_settings
from src.auth.constants import CHARS

settings = get_settings()

def hash_secret(secret: str) -> str:
    secret_bytes = secret.encode('utf-8')
    salt = gensalt()
    hashed_bytes = hashpw(secret_bytes, salt)
    
    return hashed_bytes.decode('utf-8')

def verify_secret(plain_secret: str, hashed_secret: str) -> bool:
    return checkpw(
        plain_secret.encode('utf-8'), 
        hashed_secret.encode('utf-8')
    )

def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def verify_refresh_token(token: str, token_hash: str) -> bool:
    return hashlib.sha256(token.encode("utf-8")).hexdigest() == token_hash

def generate_activation_code(blocks: int = 3, block_len: int = 4) -> str:
    """Generates an activation code with format XXXX-XXXX-XXXX."""
    code_blocks = [
        "".join(secrets.choice(CHARS) for _ in range(block_len))
        for _ in range(blocks)
    ]
    return "-".join(code_blocks)

def _create_token(
    data: dict[str, Any],
    token_type: str,
    expires_in: timedelta,
) -> str:
    payload = data.copy()
    payload.update(
        {
            "type": token_type,
            "exp": datetime.now(timezone.utc) + expires_in,
        }
    )

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

def create_access_token(data: dict[str, Any]) -> str:
    return _create_token(
        data=data,
        token_type="access",
        expires_in=timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    )
 
def create_refresh_token(data: dict[str, Any]) -> str:
    return _create_token(
        data=data,
        token_type="refresh",
        expires_in=timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        ),
    )

def decode_token(token: str, expected_type: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if payload.get("type") != expected_type:
            return None

        return payload

    except JWTError:
        return None

def decode_access_token(token: str) -> dict[str, Any] | None:
    return decode_token(token, expected_type="access")
    
def decode_refresh_token(token: str) -> dict[str, Any] | None:
    return decode_token(token, expected_type="refresh")

def create_device_tokens(device_id: int) -> dict[str, str]:
    """Generates both access and refresh tokens scoped specifically to a device."""
    access_token = _create_token(
        data={"sub": str(device_id)},
        token_type="device_access",
        expires_in=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = _create_token(
        data={"sub": str(device_id)},
        token_type="device_refresh",
        expires_in=timedelta(days=365),
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

def decode_device_access_token(token: str) -> dict[str, Any] | None:
    return decode_token(token, expected_type="device_access")

def decode_device_refresh_token(token: str) -> dict[str, Any] | None:
    return decode_token(token, expected_type="device_refresh")