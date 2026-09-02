import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.deepface.client import get_face_embedding
from src.recognition.schemas import RecognitionRequest, RecognitionResponse
import src.recognition.constants as recognition_constants
import src.employees.repository as employee_repository
from src.employees.models import Employee
import src.devices.repository as device_repository
import src.devices.constants as devices_constants
import src.attendance.repository as attendance_repository
from src.attendance.constants import CheckType
from src.attendance.models import AttendanceRecord

logger = logging.getLogger(__name__)
settings = get_settings()

async def process_recognition(
    db: AsyncSession,
    payload: RecognitionRequest,
) -> Employee | None:

    device = await device_repository.get_device_by_id(db, payload.device_id)
    if not device or not device.status == devices_constants.DeviceStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=devices_constants.ErrorMessage.DEVICE_NOT_FOUND
        )

    embedding = await get_face_embedding(payload.face_image)
    if embedding is None:
        return RecognitionResponse(
            employee_id=None,
            full_name=None,
            email=None,
            check_type=None,
            confidence=None,
            timestamp=None,
            already_recorded=False
        )

    recognition_data = await employee_repository.find_closest_employee(
        db=db, 
        embedding=embedding, 
        distance_threshold=settings.DISTANCE_THRESHOLD
    )

    if recognition_data is None:
        return RecognitionResponse(
            employee_id=None,
            full_name=None,
            email=None,
            check_type=None,
            confidence=None,
            timestamp=None,
            already_recorded=False
        )

    employee: Employee = recognition_data.get("employee")
    confidence = 1 - recognition_data.get("distance")
    recent = await attendance_repository.get_recent_record(
        db=db, 
        employee_id=employee.id, 
        cooldown_minutes=settings.RECOGNITION_COOLDOWN_MINUTES
    )
    if recent:
        logger.info(
            f"""Employee {employee.id} already recorded 
            {settings.RECOGNITION_COOLDOWN_MINUTES}min ago, skipping
            """
        )
        return RecognitionResponse(
            employee_id=employee.id,
            full_name=employee.full_name,
            email=employee.email,
            check_type=recent.check_type,
            confidence=confidence,
            timestamp=recent.timestamp,
            already_recorded=True # avoid duplicate feedback at kiosk side.
        )

    check_type = await determine_check_type(db, employee.id)

    attendance_record = AttendanceRecord(
        employee_id=employee.id,
        check_type=check_type,
        timestamp=datetime.now(timezone.utc),
        confidence=confidence
    )

    record = await attendance_repository.add_attendance_record(
        db=db,
        attendance_record=attendance_record
    )
    await db.commit()

    logger.info(
        f"Employee {employee.id} ({employee.full_name}) "
        f"{check_type} on device {device.id} "
        f"confidence={confidence}"
    )

    return RecognitionResponse(
        employee_id=employee.id,
        full_name=employee.full_name,
        email=employee.email,
        check_type=check_type,
        confidence=confidence,
        timestamp=record.timestamp,
        already_recorded=False
    )


async def determine_check_type(db: AsyncSession, employee_id: int) -> str:

    last = await attendance_repository.get_last_record_today(db, employee_id)

    if last is None:
        return CheckType.CHECK_IN.value

    if last.check_type == CheckType.CHECK_IN.value:
        return CheckType.CHECK_OUT.value

    return CheckType.CHECK_IN.value