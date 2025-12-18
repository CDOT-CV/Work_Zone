# device_feed/field_device_status.py
from enum import Enum

class FieldDeviceStatus(str, Enum):
    ERROR = "error"
    OK = "ok"
    UNKNOWN = "unknown"
    WARNING = "warning"