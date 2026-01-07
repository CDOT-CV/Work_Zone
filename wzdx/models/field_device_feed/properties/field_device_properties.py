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
    """
    Extract the ``device_type`` discriminator value from a field device object.

    This helper is used by the Pydantic ``Discriminator`` on ``FieldDeviceProperties``
    to implement a discriminated union based on ``core_details.device_type``.
    It supports both raw dictionaries and model instances that expose a
    ``core_details`` attribute.

    Args:
        v: Either a mapping-like object (typically a ``dict``) containing a
           ``"core_details"`` key, or a model instance with a ``core_details``
           attribute that in turn has a ``device_type`` attribute.

    Returns:
        The value of ``device_type`` used to select the appropriate concrete
        field device model in the ``FieldDeviceProperties`` union, or ``None``
        if it cannot be determined.
    """
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
