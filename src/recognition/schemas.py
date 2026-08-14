from pydantic import BaseModel
from datetime import datetime

class RecognitionRequest(BaseModel):
    face_image: str
    device_id: int

class RecognitionResponse(BaseModel):
    employee_id: int
    full_name: str
    email: str
    check_type: str
    confidence: float
    timestamp: datetime
    already_recorded: bool