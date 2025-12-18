# device_feed/properties/flashing_beacon.py
from typing import Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum
from ..field_device_core_details import FieldDeviceCoreDetails

class FlashingBeaconFunction(str, Enum):
    VEHICLE_ENTERING = "vehicle-entering"
    QUEUE_WARNING = "queue-warning"
    REDUCED_SPEED = "reduced-speed"
    WORKERS_PRESENT = "workers-present"
    FLAGGER_PRESENT = "flagger-present"
    ROAD_WORK = "road-work"
    UTILITY_WORK = "utility-work"
    MAINTENANCE_WORK = "maintenance-work"
    CONSTRUCTION = "construction"
    INCIDENT = "incident"
    EMERGENCY = "emergency"
    CONGESTION = "congestion"
    WEATHER = "weather"
    SCHOOL_ZONE = "school-zone"
    PEDESTRIAN_CROSSING = "pedestrian-crossing"
    OTHER = "other"
    UNKNOWN = "unknown"

class FlashingBeaconCoreDetails(FieldDeviceCoreDetails):
    device_type: Literal["flashing-beacon"] = "flashing-beacon"

class FlashingBeacon(BaseModel):
    core_details: FlashingBeaconCoreDetails = Field(alias="core_details")
    function: Optional[FlashingBeaconFunction] = None
    is_flashing: Optional[bool] = Field(None, alias="is_flashing")