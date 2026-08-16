from pydantic import BaseModel

class DeviceRead(BaseModel):
    id: int
    name: str

class CreateDevice(BaseModel):
    name: str

class ActivateDevice(BaseModel):
    activation_code: str

class DeviceCredentials(BaseModel):
    access_token: str
    refresh_token: str


class RefreshRequest(BaseModel):
    refresh_token: str

class UpdateDevice(BaseModel):
    name: str | None = None
    refresh_token_hash: str | None = None