from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status

from datetime import datetime, timezone, timedelta
from typing import Any

import src.devices.repository as repository
from src.devices.models import Device
from src.devices.constants import ErrorMessage, DeviceStatus
from src.devices.schemas import (
    CreateDevice, 
    UpdateDevice, 
    ActivateDeviceResponse,
)
from src.auth.security import (
    generate_activation_code, 
    create_device_tokens,
    decode_device_refresh_token,
    hash_refresh_token,
    verify_refresh_token,
)
from src.auth.constants import ErrorMessage as AuthErrorMessage
from src.config import get_settings

settings = get_settings()

async def add_device(
    db: AsyncSession,
    device_data: CreateDevice
) -> str:

    if not device_data.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessage.MIISING_DEVICE_NAME
        )
    
    if await repository.get_device_by_name(
        db=db,
        device_name=device_data.name
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=ErrorMessage.DEVICE_EXIST
        )

    while True:
        device_activation_data = _get_activation_code()
        if not await repository.get_device_by_activation_code(
            db=db, 
            activation_code=device_activation_data.get("activation_code")
        ):
            break

    device = Device(
        name=device_data.name,
        status=DeviceStatus.PENDING.value,
        activation_code=device_activation_data.get("activation_code"),
        activation_expires_at=device_activation_data.get("activation_expires_at")
    )

    device = await repository.add_device(
        db=db,
        device=device,
    )

    if device:
        await db.commit()
        return ActivateDeviceResponse(
            device_activation_code=device_activation_data.get("activation_code")
        )

def _get_activation_code() -> dict[str, Any]:

    activation_code = generate_activation_code()
    activation_expires_at = (
        datetime.now(timezone.utc) + 
        timedelta(minutes=settings.KIOSK_ACTIVATION_CODE_EXPIRE_MINUTES)
    )

    return {
        "activation_code": activation_code,
        "activation_expires_at": activation_expires_at
    }

async def get_devices(
    db: AsyncSession,
    page: int,
    page_size: int
) -> dict[str, Any]:

    devices = await repository.get_devices(
        db=db,
        page=page,
        page_size=page_size,
        limit=page_size + 1
    )
    return {
        "devices": devices[:page_size],
        "page": page,
        "page_size": page_size,
        "has_next": len(devices) > page_size
    }

async def get_device(
    db: AsyncSession,
    device_id: int
) -> Device:

    device = await repository.get_device_by_id(
        db=db, 
        device_id=device_id
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessage.DEVICE_NOT_FOUND
        )

    return device

async def delete_device(
    db: AsyncSession,
    device_id: int
) -> None:
    
    _ = await get_device(db=db, device_id=device_id)
    
    if not await repository.delete_device(
        db=db, 
        device_id=device_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessage.DEVICE_DELETE_ERROR
        )

    await db.commit()

async def activate_device(
    db: AsyncSession,
    activation_code: str
) -> dict[str, str]:
    
    device = await repository.get_device_by_activation_code(
        db=db,
        activation_code=activation_code
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessage.WRONG_ACTIVATION_CODE
        )

    if not datetime.now(timezone.utc) < device.activation_expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessage.EXPIRED_ACTIVATION_CODE
        )

    device.status = DeviceStatus.ACTIVE.value
    device.activation_code = None
    device.activation_expires_at = None

    credentials = create_device_tokens(device.id)

    await _rotate_refresh_token(
        db=db,
        device=device,
        new_refresh_token=credentials.get("refresh_token")
    )

    return credentials

async def get_new_activation_code(
    db: AsyncSession,
    device_id: int
) -> str:

    device = await get_device(db, device_id)

    if device.status == DeviceStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessage.DEVICE_ALREADY_ACTIVE
        )

    device_activation_data = _get_activation_code()
    device.activation_code=device_activation_data.get("activation_code")
    device.activation_expires_at=device_activation_data.get("activation_expires_at")

    await db.commit()

    return ActivateDeviceResponse(
        device_activation_code=device_activation_data.get("activation_code")
    )

async def refresh_credentials(
    db: AsyncSession,
    refresh_token: str
) -> dict[str, str]:
    payload = decode_device_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AuthErrorMessage.INVALID_TOKEN
        )

    device_id = payload.get("sub")
    device = await get_device(db, int(device_id))
    if not verify_refresh_token(refresh_token, device.refresh_token_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AuthErrorMessage.INVALID_TOKEN
        )

    credentials = create_device_tokens(device.id)

    await _rotate_refresh_token(
        db=db,
        device=device,
        new_refresh_token=credentials.get("refresh_token")
    )
    return credentials


async def _rotate_refresh_token(
    db: AsyncSession,
    device: Device,
    new_refresh_token: str
) -> None:

    device = await repository.update_device(
        db=db,
        device=device,
        device_data=UpdateDevice(
            refresh_token_hash=hash_refresh_token(new_refresh_token)
        )
    )

    await db.commit()


async def update_device(
    db: AsyncSession,
    device_id: int,
    device_data: UpdateDevice
) -> None:

    device = await get_device(db, device_id)

    if device_data.name:
        device.name = device_data.name

    if device_data.enabled != None:
        if device.status == DeviceStatus.PENDING.value:
            raise HTTPException(
                detail=ErrorMessage.CANNOT_CHANGE_PENDING_STATUS,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        device.status = (
            DeviceStatus.ACTIVE.value
            if device_data.enabled 
            else DeviceStatus.DISABLED.value
        )

    await db.commit()

    return device