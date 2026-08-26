from pydantic import BaseModel, ConfigDict, Field

class RoleRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class CreateRole(BaseModel):
    name: str = Field(min_length=2)
    permission_ids: list[int] = []

class UpdateRole(BaseModel):
    name: str = Field(min_length=2)
    permission_ids: list[int] = []

class PermissionRead(BaseModel):
    id: int
    code: str

class RolePermissionRead(BaseModel):
    role_id: int
    permission_id: int

class AssignPermissions(BaseModel):
    permission_ids: list[int]