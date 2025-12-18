# device_feed/properties/traffic_signal.py
from typing import Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum
from ..field_device_core_details import FieldDeviceCoreDetails

class TrafficSignalMode(str, Enum):
    BLANK = "blank"
    FLASHING_RED = "flashing-red"
    FLASHING_YELLOW = "flashing-yellow"
    FULLY_ACTUATED = "fully-actuated"
    MANUAL = "manual"
    PRE_TIMED = "pre-timed"
    SEMI_ACTUATED = "semi-actuated"
    UNKNOWN = "unknown"

class TrafficSignalCoreDetails(FieldDeviceCoreDetails):
    device_type: Literal["traffic-signal"] = "traffic-signal"

class TrafficSignal(BaseModel):
    core_details: TrafficSignalCoreDetails = Field(alias="core_details")
    mode: Optional[TrafficSignalMode] = None