from enum import Enum

class FieldDeviceStatus(str, Enum):
    ERROR = "error"
    OK = "ok"
    UNKNOWN = "unknown"
    WARNING = "warning"
