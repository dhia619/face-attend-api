from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.devices.models import Device

async def get_device_by_id(
    db: AsyncSession,
    device_id: int
) -> Device | None:

    return await db.get(Device, device_id)

async def get_device_by_name(
    db: AsyncSession,
    device_name: str
) -> Device | None:

    result = await db.execute(select(Device).where(Device.name == device_name))
    return result.scalar_one_or_none()

async def get_devices(
    db: AsyncSession
) -> list[Device]:
    
    result = await db.execute(select(Device))
    return list(result.scalars().all())

async def add_device(
    db: AsyncSession,
    device: Device
) -> Device:

    db.add(device)
    await db.flush()

    return device

async def delete_device(
    db: AsyncSession,
    device_id: int
) -> bool:

    result = await db.execute(delete(Device).where(Device.id == device_id))
    return result.rowcount == 1