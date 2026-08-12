from pydantic import BaseModel

class DepartmentRead(BaseModel):
    id: int
    name: str

class CreateDepartment(BaseModel):
    name: str