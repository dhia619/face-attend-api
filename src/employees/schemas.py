from datetime import datetime

from pydantic import BaseModel

class CreateEmployee(BaseModel):
    full_name: str
    department_id: int | None = None
    email: str
    phone: str
    hire_date: datetime | None = None
    face_image: str

class UpdateEmployee(BaseModel):
    full_name: str | None = None
    department_id: int | None = None
    email: str | None = None
    phone: str | None = None
    hire_date: datetime | None = None

class DeleteEmployee(BaseModel):
    employee_id: int

class EmployeeRead(BaseModel):
    id: int
    full_name: str
    department_id: int| None
    email: str
    phone: str | None
    hire_date: datetime | None

class UpdateFaceEmbedding(BaseModel):
    embeddings: list[float]