from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.recognition.dependencies import get_current_kiosk_device
from src.recognition import service
from src.recognition.schemas import RecognitionRequest, RecognitionResponse
from src.devices.models import Device

recognition_router = APIRouter()

@recognition_router.post(
    "/events",
    response_model=RecognitionResponse,
    status_code=201
)
async def create_recognition_event(
    payload: RecognitionRequest,
    session: AsyncSession = Depends(get_db),
    device: Device = Depends(get_current_kiosk_device)
):
    return await service.process_recognition(session, payload)