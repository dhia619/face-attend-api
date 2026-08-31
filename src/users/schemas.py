from pydantic import BaseModel, ConfigDict, EmailStr, Field
from src.rbac.schemas import RoleRead

class UserCreate(BaseModel):
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="User full name",
    )
    email: EmailStr = Field(
        ...,
        description="User email address",
    )
    role_id: int = Field(
        ...,
        description="Id of the user's role",
    )
    password: str = Field(
        ...,
        min_length=5,
        description="User password",
    )

class UserRead(BaseModel):
    id: int
    full_name: str
    email: str
    role: RoleRead

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    role_id: int | None = None
    refresh_token_hash: str | None = None

class ChangePassword(BaseModel):
    current_password: str = Field(
        ...,
        min_length=5,
        description="Current user password",
    )
    new_password: str = Field(
        ...,
        min_length=5,
        description="New user password",
    )

class ListUsersResponse(BaseModel):
    users: list[UserRead]
    page: int
    page_size: int
    has_next: bool