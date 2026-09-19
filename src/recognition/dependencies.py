from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import APIKeyHeader

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.config import get_settings
from src.auth.security import decode_device_access_token
import src.auth.constants as auth_constants
import src.devices.constants as devices_constants
from src.devices.repository import get_device_by_id

settings = get_settings()

device_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.BASE_API_PATH}/devices/activate",
    scheme_name="DeviceAuth"
)

async def get_current_kiosk_device(
    token: str = Depends(device_oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
):
    payload = decode_device_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=auth_constants.ErrorMessage.INVALID_TOKEN
        )
    device_id = payload.get("sub")
    device = await get_device_by_id(db, int(device_id))
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=devices_constants.ErrorMessage.DEVICE_NOT_FOUND
        )
    return device

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_camera_worker_api_key(api_key: str = Depends(api_key_header)) -> None:
    camera_worker_api_key = settings.CAMERA_WORKER_API_KEY

    if api_key != camera_worker_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=devices_constants.ErrorMessage.INVALID_API_KEY,
        )