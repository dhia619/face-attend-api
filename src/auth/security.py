from datetime import datetime, timedelta, timezone
from typing import Any
from jose import JWTError, jwt
from src.config import get_settings
from bcrypt import gensalt, hashpw, checkpw

settings = get_settings()

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = gensalt()
    hashed_bytes = hashpw(password_bytes, salt)
    
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

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