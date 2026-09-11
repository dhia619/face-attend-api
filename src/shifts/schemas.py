from pydantic import BaseModel
from datetime import time

class ShiftRead(BaseModel):
    id: int
    name: str
    department_id: int | None
    start_time: time
    end_time: time | None

class ShiftCreate(BaseModel):
    name: str
    department_id: int
    start_time: time
    end_time: time

class ShiftUpdate(BaseModel):
    name: str | None = None
    start_time: time | None = None
    end_time: time | None = None

class ListShiftsResponse(BaseModel):
    shifts: list[ShiftRead]
    page: int
    page_size: int
    has_next: bool