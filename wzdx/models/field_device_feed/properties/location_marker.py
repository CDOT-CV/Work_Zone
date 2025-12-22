# device_feed/properties/marked_location.py
from typing import Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum
from ..field_device_core_details import FieldDeviceCoreDetails

class MarkedLocationType(str, Enum):
    AFAD = "afad"
    DELINEATOR = "delineator"
    FLAGGER = "flagger"
    LANE_SHIFT = "lane-shift"
    LANE_CLOSURE = "lane-closure"
    PERSONAL_DEVICE = "personal-device"
    RAMP_CLOSURE = "ramp-closure"
    ROAD_CLOSURE = "road-closure"
    ROAD_EVENT_START = "road-event-start"
    ROAD_EVENT_END = "road-event-end"
    WORK_TRUCK_WITH_LIGHTS_FLASHING = "work-truck-with-lights-flashing"
    WORK_ZONE_START = "work-zone-start"
    WORK_ZONE_END = "work-zone-end"

class MarkedLocation(BaseModel):
    type: MarkedLocationType
    road_event_id: Optional[str] = None

class MarkedLocationCoreDetails(FieldDeviceCoreDetails):
    device_type: Literal["location-marker"] = "location-marker"

class LocationMarker(BaseModel):
    core_details: MarkedLocationCoreDetails = Field(alias="core_details")
    marked_locations: Optional[list[MarkedLocation]] = Field(None, alias="marked_locations")