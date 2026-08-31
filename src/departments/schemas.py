from pydantic import BaseModel, Field

class DepartmentRead(BaseModel):
    id: int
    name: str = Field(
        ...,
        min_length=2,
        description= "Department name"
    )

class CreateDepartment(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        description= "Department name"
    )

class ListDepartmentsResponse(BaseModel):
    departments: list[DepartmentRead]
    page: int
    page_size: int
    has_next: bool