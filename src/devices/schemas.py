from pydantic import BaseModel

class DeviceRead(BaseModel):
    id: int
    name: str
    status: str
    type: str
    rtsp_url: str | None = None

class CreateDevice(BaseModel):
    name: str
    type: str
    rtsp_url: str | None = None

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
    enabled: bool | None = None

class ActivateDeviceResponse(BaseModel):
    device_activation_code: str

class ListDevicesResponse(BaseModel):
    devices: list[DeviceRead]
    page: int
    page_size: int
    has_next: bool