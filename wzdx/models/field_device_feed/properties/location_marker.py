from typing import Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum
from ..field_device_core_details import FieldDeviceCoreDetails


class MarkedLocationType(str, Enum):
    """
    The MarkedLocationType enumerated type describes options for what a :class:`MarkedLocation` can mark, such as the start or end of a road event.

    https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/enumerated-types/MarkedLocationType.md
    """

    AFAD = "afad"  # An automatic flagger assistance device.
    DELINEATOR = "delineator"  # A generic delineation point in a work zone. This value can be used for most types of marked locations that don't match any of the other values.
    FLAGGER = "flagger"  # A human who is directing traffic.
    LANE_SHIFT = "lane-shift"  # A lane shift.
    LANE_CLOSURE = "lane-closure"  # One or more lanes are closed.
    PERSONAL_DEVICE = "personal-device"  # A connected device that is worn or carried by an individual worker in a work zone.
    RAMP_CLOSURE = (
        "ramp-closure"  # The start of a closed ramp onto or off a main road or highway.
    )
    ROAD_CLOSURE = "road-closure"  # The start of a closed road.
    ROAD_EVENT_START = "road-event-start"  # The start point of a road event.
    ROAD_EVENT_END = "road-event-end"  # The end point of a road event.
    WORK_TRUCK_WITH_LIGHTS_FLASHING = "work-truck-with-lights-flashing"  # A work truck with lights flashing, actively engaged in construction or maintenance activity on the roadway.
    WORK_ZONE_START = "work-zone-start"  # The start point of a work zone.
    WORK_ZONE_END = "work-zone-end"  # The end point of a work zone.


class MarkedLocation(BaseModel):
    """
    The MarkedLocation object describes a specific location where a LocationMarker is placed, such as the start or end of a work zone road event. The marked location is typically within a road event, but is not required to be.

    Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/objects/MarkedLocation.md
    """

    type: MarkedLocationType = Field(
        alias="type",
        description="The type of location (e.g. start or end) that is marked.",
    )
    road_event_id: Optional[str] = Field(
        None,
        alias="road_event_id",
        description="The ID of a RoadEventFeature that the MarkedLocation applies to.",
    )


class MarkedLocationCoreDetails(FieldDeviceCoreDetails):
    device_type: Literal["location-marker"] = "location-marker"


class LocationMarker(BaseModel):
    """
    The LocationMarker object describes any GPS-enabled ITS device that is placed at a point on a roadway to dynamically know the location of something (often the beginning or end of a work zone). The LocationMarker contains a list of one or more MarkedLocation objects which indicate the type of location (such as the start or end) and optionally the ID of a RoadEventFeature that the location is associated with.

    The LocationMarker is a type of field device; it has a core_details property which contains the FieldDeviceCoreDetails and exists within a FieldDeviceFeature.

    Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/objects/LocationMarker.md
    """

    core_details: MarkedLocationCoreDetails = Field(
        alias="core_details",
        description="The core details of the field device shared by all field devices types, not specific to the location marker.",
    )
    marked_locations: list[MarkedLocation] = Field(
        alias="marked_locations",
        description="A list of locations that the LocationMarker is marking.",
    )
