from enum import Enum

class DeviceStatus(Enum):
    ACTIVE = "active"
    PENDING = "pending"
    DISABLED = "disabled"

class ErrorMessage:
    DEVICE_EXIST = "A device with this name exists."
    DEVICE_NOT_FOUND = "Device not found."
    MIISING_DEVICE_NAME = "Device name is missing."
    DEVICE_DELETE_ERROR = "Failed to delete device."
    WRONG_ACTIVATION_CODE = "The provided activation code is incorrect."
    EXPIRED_ACTIVATION_CODE = "This activation code has expired."
    DEVICE_ALREADY_ACTIVE = "This device is already active."