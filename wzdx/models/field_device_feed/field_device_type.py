# device_feed/field_device_type.py
from typing_extensions import Literal

FieldDeviceType = Literal[
    "arrow-board",
    "camera",
    "dynamic-message-sign",
    "flashing-beacon",
    "hybrid-sign",
    "location-marker",
    "traffic-sensor",
    "traffic-signal",
]
