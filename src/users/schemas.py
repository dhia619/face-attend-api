from pydantic import BaseModel

class UserCreate(BaseModel):
    full_name: str
    email: str
    role_id: int
    password: str

class UserRead(BaseModel):
    id: int
    full_name: str
    email: str
    role_id: int

class UserUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    role_id: int | None = None
    refresh_token_hash: str | None = None

class ChangePassword(BaseModel):
    current_password: str
    new_password: str