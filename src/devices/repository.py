from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.devices.models import Device
from src.devices.schemas import UpdateDevice
from src.shared.pagination import get_page_offset

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
    db: AsyncSession,
    page: int,
    page_size: int,
    limit: int | None = None,
    
) -> list[Device]:
    
    result = await db.execute(
        select(Device)
        .order_by(Device.id)
        .offset(get_page_offset(page, page_size))
        .limit(limit if limit is None else page_size + 1)
    )
    return list(result.scalars().all())

async def add_device(
    db: AsyncSession,
    device: Device
) -> Device:

    db.add(device)
    await db.flush()

    return device

async def get_device_by_activation_code(
    db: AsyncSession,
    activation_code: str
) -> Device | None:
    result = await db.execute(select(Device).where(Device.activation_code == activation_code))
    return result.scalar_one_or_none()    

async def delete_device(
    db: AsyncSession,
    device_id: int
) -> bool:

    result = await db.execute(delete(Device).where(Device.id == device_id))
    return result.rowcount == 1

async def update_device(
    db: AsyncSession,
    device: Device,
    device_data: UpdateDevice
) -> Device:
    data = device_data.model_dump(exclude_unset=True)

    for field, value in data.items():
        setattr(device, field, value)

    await db.flush()

    return device