from datetime import datetime, date
from pydantic import BaseModel

from src.config import get_settings

settings = get_settings()

class AttendanceRecordRead(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    check_type: str
    timestamp: datetime
    device_id: int
    device_name: str
    confidence: float
    department_name: str | None

class EmployeeTodayStatus(BaseModel):
    employee_id: int
    full_name: str
    department_name: str | None
    is_present: bool
    current_status: str
    last_seen_at: datetime | None
    is_late: bool | None
    late_minutes: int | None

class TodayAttendanceResponse(BaseModel):
    date: str
    total_employees: int
    present: int
    absent: int
    currently_in: int
    currently_out: int
    late: int
    employees: list[EmployeeTodayStatus]

class AttendanceFilterParams(BaseModel):
    page: int = 1
    page_size: int = settings.PAGINATION_PAGE_SIZE
    employee_id: int | None = None
    employee_search: str | None = None
    department_id: int | None = None
    check_type: str | None = None
    date_from: date | None = None
    date_to: date | None = None

class ListAttendanceRecordsResponse(BaseModel):
    records: list[AttendanceRecordRead]
    page: int
    page_size: int
    has_next: bool