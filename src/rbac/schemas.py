from pydantic import BaseModel

class RoleRead(BaseModel):
    id: int
    name: str

class CreateRole(BaseModel):
    name: str

class UpdateRole(BaseModel):
    name: str

class PermissionRead(BaseModel):
    id: int
    code: str

class RolePermissionRead(BaseModel):
    role_id: int
    permission_id: int