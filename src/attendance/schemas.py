from datetime import datetime
from pydantic import BaseModel

class EmployeeTodayStatus(BaseModel):
    employee_id: int
    full_name: str
    department_name: str | None
    is_present: bool
    current_status: str
    last_seen_at: datetime | None

class TodayAttendanceResponse(BaseModel):
    date: str
    total_employees: int
    present: int
    absent: int
    currently_in: int
    currently_out: int
    employees: list[EmployeeTodayStatus]