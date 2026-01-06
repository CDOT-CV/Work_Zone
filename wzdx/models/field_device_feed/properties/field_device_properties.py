from typing import Annotated

from pydantic import Discriminator, Tag
from .arrow_board import ArrowBoard
from .camera import Camera
from .dynamic_message_sign import DynamicMessageSign
from .flashing_beacon import FlashingBeacon
from .hybrid_sign import HybridSign
from .location_marker import LocationMarker
from .traffic_sensor import TrafficSensor
from .traffic_signal import TrafficSignal

def get_device_type(v):
    """Discriminator function to get device_type from core_details"""
    if isinstance(v, dict):
        return v.get("core_details", {}).get("device_type")
    return getattr(v.core_details, "device_type", None)

# Discriminated union based on core_details.device_type
FieldDeviceProperties = Annotated[
    Annotated[ArrowBoard, Tag("arrow-board")]
    | Annotated[Camera, Tag("camera")]
    | Annotated[DynamicMessageSign, Tag("dynamic-message-sign")]
    | Annotated[FlashingBeacon, Tag("flashing-beacon")]
    | Annotated[HybridSign, Tag("hybrid-sign")]
    | Annotated[LocationMarker, Tag("location-marker")]
    | Annotated[TrafficSensor, Tag("traffic-sensor")]
    | Annotated[TrafficSignal, Tag("traffic-signal")],
    Discriminator(get_device_type),
]
