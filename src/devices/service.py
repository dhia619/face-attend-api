from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status

from datetime import datetime, timezone, timedelta
from typing import Any

import src.devices.repository as repository
from src.devices.models import Device
from src.devices.constants import ErrorMessage, DeviceStatus
from src.devices.schemas import CreateDevice
from src.auth.security import hash_secret, generate_activation_code, verify_secret, create_device_tokens
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

    device_activation_data = _get_activation_code()
    
    device = Device(
        name=device_data.name,
        status=DeviceStatus.PENDING.value,
        activation_code_hash=device_activation_data.get("activation_code_hash"),
        activation_expires_at=device_activation_data.get("activation_expires_at")
    )

    device = await repository.add_device(
        db=db,
        device=device,
    )

    if device:
        await db.commit()
        return device_activation_data.get("activation_code")

def _get_activation_code() -> dict[str, Any]:

    activation_code = generate_activation_code()
    activation_code_hash = hash_secret(activation_code)
    activation_expires_at = (
        datetime.now(timezone.utc) + 
        timedelta(minutes=settings.KIOSK_ACTIVATION_CODE_EXPIRE_MINUTES)
    )

    return {
        "activation_code": activation_code,
        "activation_code_hash": activation_code_hash,
        "activation_expires_at": activation_expires_at
    }

async def get_devices(
    db: AsyncSession  
) -> list[Device]:

    return await repository.get_devices(db)

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
    device_id: int,
    activation_code: str
) -> dict[str, str]:

    device = await get_device(db=db, device_id=device_id)

    if not verify_secret(activation_code, device.activation_code_hash):
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
    device.activation_code_hash = None
    device.activation_expires_at = None

    await db.commit()

    return create_device_tokens(device_id)

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
    device.activation_code_hash=device_activation_data.get("activation_code_hash")
    device.activation_expires_at=device_activation_data.get("activation_expires_at")

    await db.commit()

    return device_activation_data.get("activation_code")