# device_feed/field_device_type.py
from enum import Enum

class FieldDeviceType(str, Enum):
    ARROW_BOARD = "arrow-board"
    CAMERA = "camera"
    DYNAMIC_MESSAGE_SIGN = "dynamic-message-sign"
    FLASHING_BEACON = "flashing-beacon"
    HYBRID_SIGN = "hybrid-sign"
    LOCATION_MARKER = "location-marker"
    TRAFFIC_SENSOR = "traffic-sensor"
    TRAFFIC_SIGNAL = "traffic-signal"