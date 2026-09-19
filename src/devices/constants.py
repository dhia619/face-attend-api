from enum import Enum

class DeviceStatus(Enum):
    ACTIVE = "active"
    PENDING = "pending"
    DISABLED = "disabled"

class DeviceType(Enum):
    KIOSK = "kiosk"
    IP_CAMERA = "ip-camera"

class ErrorMessage:
    DEVICE_EXIST = "A device with this name exists."
    DEVICE_NOT_FOUND = "Device not found."
    MIISING_DEVICE_NAME = "Device name is missing."
    DEVICE_DELETE_ERROR = "Failed to delete device."
    WRONG_ACTIVATION_CODE = "The provided activation code is incorrect."
    EXPIRED_ACTIVATION_CODE = "This activation code has expired."
    DEVICE_ALREADY_ACTIVE = "This device is already active."
    CANNOT_CHANGE_PENDING_STATUS = "Cannot change status of pending device."
    DEVICE_TYPE_NOT_SUPPORTED = "This device type is not supported."
    INVALID_API_KEY = "Invalid API key."