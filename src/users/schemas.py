from pydantic import BaseModel

class UserRead(BaseModel):
    id: int
    full_name: str
    email: str
    role_id: int