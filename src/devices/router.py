from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.devices.schemas import *
from src.devices.models import Device
import src.devices.service as service
from src.users.models import User
from src.rbac.dependencies import require_permission
from src.rbac.constants import PermissionCode
from src.auth.schemas import TokenResponse
from src.recognition.dependencies import get_current_kiosk_device

device_router = APIRouter()


@device_router.get(
    "/me",
    response_model=DeviceRead,
)
async def get_current_device(
    device: Device = Depends(get_current_kiosk_device)
):
    """
    Called by kiosk on startup to get its own info.
    Uses device JWT — no admin auth needed.
    """
    return device

@device_router.post("/refresh", response_model=TokenResponse)
async def refresh_device_credentials(
    payload: RefreshRequest,
    session: AsyncSession = Depends(get_db),
):
    return await service.refresh_credentials(
        db=session,
        refresh_token=payload.refresh_token
    )

@device_router.get("", response_model=list[DeviceRead])
async def list_devices(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.DEVICES_READ))
):
    return await service.get_devices(db=session)


@device_router.get("/{device_id}", response_model=DeviceRead)
async def get_device(
    device_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.DEVICES_READ))
):
    return await service.get_device(db=session, device_id=device_id)


@device_router.post(
    "", 
    status_code=status.HTTP_201_CREATED
)
async def create_device(
    device_data: CreateDevice,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.DEVICES_WRITE))
):
    device_activation_code = await service.add_device(
        db=session,
        device_data=device_data
    )

    return JSONResponse(
        content={
            "device_activation_code": device_activation_code
        }
    )


@device_router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.DEVICES_WRITE))
):
    await service.delete_device(db=session, device_id=device_id)


@device_router.post(
    "/activate",
    response_model=DeviceCredentials,
)
async def activate_device(
    activate_device: ActivateDevice,
    session: AsyncSession = Depends(get_db)
):
   return await service.activate_device(
        db=session, 
        activation_code=activate_device.activation_code
    )

@device_router.patch("/{device_id}/activation-code")
async def regenerate_device_activation_code(
    device_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(PermissionCode.DEVICES_WRITE))
):

    device_activation_code = await service.get_new_activation_code(session, device_id)
    return JSONResponse(
        content={
            "device_activation_code": device_activation_code
        }
    )