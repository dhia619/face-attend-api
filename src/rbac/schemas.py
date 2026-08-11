from pydantic import BaseModel

class RoleResponse(BaseModel):
    id: int
    name: str

class CreateRole(BaseModel):
    name: str

class UpdateRole(BaseModel):
    name: str

class PermissionResponse(BaseModel):
    id: int
    code: str

class RolePermissionResponse(BaseModel):
    role_id: int
    permission_id: int