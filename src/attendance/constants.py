from enum import Enum 

class CheckType(Enum):
    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"

class AttendanceStatus(Enum):
    IN = "in"
    OUT = "out"
    NOT_ARRIVED = "not_arrived_yet"