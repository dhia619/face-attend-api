from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.recognition.dependencies import *
from src.recognition import service
from src.recognition.schemas import *
from src.devices.models import Device


recognition_router = APIRouter()


@recognition_router.post(
    "/kiosk/events",
    response_model=RecognitionResponse,
    status_code=201,
    description="Process a face recognition event submitted by a kiosk device."
)
async def create_kiosk_recognition_event(
    payload: RecognitionRequest,
    session: AsyncSession = Depends(get_db),
    device: Device = Depends(get_current_kiosk_device)
):
    return await service.process_recognition(session, payload)


@recognition_router.post(
    "/camera/events",
    response_model=RecognitionResponse,
    status_code=201,
    description="Process a face recognition event submitted from an IP camera.",
    dependencies=[Depends(verify_camera_worker_api_key)]
)
async def create_camera_recognition_event(
    payload: RecognitionRequest,
    session: AsyncSession = Depends(get_db),
):
    return await service.process_recognition(session, payload)