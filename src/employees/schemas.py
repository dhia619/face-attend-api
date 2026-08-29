from datetime import date

from pydantic import BaseModel, EmailStr, Field


class CreateEmployee(BaseModel):
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Employee full name",
    )

    department_id: int | None = Field(
        default=None,
        gt=0,
        description="Department ID",
    )

    email: EmailStr = Field(
        ...,
        description="Employee email address",
    )

    phone: str = Field(
        ...,
        min_length=7,
        max_length=20,
        pattern=r"^\+?[0-9\s\-()]+$",
        description="Employee phone number",
        examples=["+216 20 123 456"],
    )

    hire_date: date | None = Field(
        default=None,
        description="Employee hire date",
    )

    face_image: str = Field(
        ...,
        min_length=1,
        description="Employee face image in base64 format",
    )


class UpdateEmployee(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    department_id: int | None = Field(
        default=None,
        gt=0,
    )

    email: EmailStr | None = Field(
        default=None,
    )

    phone: str | None = Field(
        default=None,
        min_length=7,
        max_length=20,
        pattern=r"^\+?[0-9\s\-()]+$",
    )

    hire_date: date | None = Field(
        default=None,
    )


class DeleteEmployee(BaseModel):
    employee_id: int = Field(
        ...,
        gt=0,
        description="Employee ID to delete",
    )


class EmployeeRead(BaseModel):
    id: int = Field(
        ...,
        gt=0,
    )

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    department_id: int | None = Field(
        default=None,
        gt=0,
    )

    email: EmailStr

    phone: str | None = Field(
        default=None,
        min_length=7,
        max_length=20,
        pattern=r"^\+?[0-9\s\-()]+$",
    )

    hire_date: date | None = Field(
        default=None,
    )


class CreateEmbedding(BaseModel):
    face_image: str = Field(
        ...,
        min_length=1,
        description="Employee face image in base64 format",
    )