from pydantic import BaseModel
from datetime import datetime

class RecognitionRequest(BaseModel):
    face_image: str
    device_id: int

class RecognitionResponse(BaseModel):
    employee_id: int | None = None
    full_name: str | None = None
    email: str | None = None
    check_type: str | None = None
    confidence: float | None = None
    timestamp: datetime | None = None
    already_recorded: bool | None = None