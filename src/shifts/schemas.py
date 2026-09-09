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
    department_id: int | None
    start_time: time
    end_time: time | None

class ShiftUpdate(BaseModel):
    name: str | None
    department_id: int | None
    start_time: time | None
    end_time: time | None

class ListShiftsResponse(BaseModel):
    shifts: list[ShiftRead]
    page: int
    page_size: int
    has_next: bool