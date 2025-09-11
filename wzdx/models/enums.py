from enum import Enum


class EventType(Enum):
    WORK_ZONE = "work-zone"
    DETOUR = "detour"


class WorkZoneType(Enum):
    STATIC = "static"
    MOVING = "moving"
    PLANNED_MOVING_AREA = "planned-moving-area"


class LocationMethod(Enum):
    CHANNEL_DEVICE_METHOD = "channel-device-method"
    SIGN_METHOD = "sign-method"
    JUNCTION_METHOD = "junction-method"
    OTHER = "other"
    UNKNOWN = "unknown"


class VehicleImpact(Enum):
    ALL_LANES_CLOSED = "all-lanes-closed"
    SOME_LANES_CLOSED = "some-lanes-closed"
    ALL_LANES_OPEN = "all-lanes-open"
    ALTERNATING_ONE_WAY = "alternating-one-way"
    SOME_LANES_CLOSED_MERGE_LEFT = "some-lanes-closed-merge-left"
    SOME_LANES_CLOSED_MERGE_RIGHT = "some-lanes-closed-merge-right"
    ALL_LANES_OPEN_SHIFT_LEFT = "all-lanes-open-shift-left"
    ALL_LANES_OPEN_SHIFT_RIGHT = "all-lanes-open-shift-right"
    SOME_LANES_CLOSED_SPLIT = "some-lanes-closed-split"
    FLAGGING = "flagging"
    TEMPORARY_TRAFFIC_SIGNAL = "temporary-traffic-signal"
    UNKNOWN = "unknown"


class RestrictionType(Enum):
    LOCAL_ACCESS_ONLY = "local-access-only"
    NO_TRUCKS = "no-trucks"
    TRAVEL_PEAK_HOURS_ONLY = "travel-peak-hours-only"
    HOV_3 = "hov-3"
    HOV_2 = "hov-2"
    NO_PARKING = "no-parking"
    REDUCED_WIDTH = "reduced-width"
    REDUCED_HEIGHT = "reduced-height"
    REDUCED_LENGTH = "reduced-length"
    REDUCED_WEIGHT = "reduced-weight"
    AXLE_LOAD_LIMIT = "axle-load-limit"
    GROSS_WEIGHT_LIMIT = "gross-weight-limit"
    TOWING_PROHIBITED = "towing-prohibited"
    PERMITTED_OVERSIZE_LOADS_PROHIBITED = "permitted-oversize-loads-prohibited"
    NO_PASSING = "no-passing"


class WorkTypeName(Enum):
    NON_ENCROACHMENT = "non-encroachment"
    MINOR_ROAD_DEFECT_REPAIR = "minor-road-defect-repair"
    ROADSIDE_WORK = "roadside-work"
    OVERHEAD_WORK = "overhead-work"
    BELOW_ROAD_WORK = "below-road-work"
    BARRIER_WORK = "barrier-work"
    SURFACE_WORK = "surface-work"
    PAINTING = "painting"
    ROADWAY_RELOCATION = "roadway-relocation"
    ROADWAY_CREATION = "roadway-creation"


class LaneStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    SHIFT_LEFT = "shift-left"
    SHIFT_RIGHT = "shift-right"
    MERGE_LEFT = "merge-left"
    MERGE_RIGHT = "merge-right"
    ALTERNATING_FLOW = "alternating-flow"


class LaneType(Enum):
    GENERAL = "general"
    EXIT_LANE = "exit-lane"
    EXIT_RAMP = "exit-ramp"
    ENTRANCE_LANE = "entrance-lane"
    ENTRANCE_RAMP = "entrance-ramp"
    SIDEWALK = "sidewalk"
    BIKE_LANE = "bike-lane"
    SHOULDER = "shoulder"
    PARKING = "parking"
    MEDIAN = "median"
    TWO_WAY_CENTER_TURN_LANE = "two-way-center-turn-lane"


class UnitOfMeasurement(Enum):
    FEET = "feet"
    INCHES = "inches"
    CENTIMETERS = "centimeters"
    POUNDS = "pounds"
    TONS = "tons"
    KILOGRAMS = "kilograms"
    MILES = "miles"
    KILOMETERS = "kilometers"


class WorkerPresenceMethod(Enum):
    CAMERA_MONITORING = "camera-monitoring"
    ARROW_BOARD_PRESENT = "arrow-board-present"
    CONES_PRESENT = "cones-present"
    MAINTENANCE_VEHICLE_PRESENT = "maintenance-vehicle-present"
    WEARABLES_PRESENT = "wearables-present"
    MOBILE_DEVICE_PRESENT = "mobile-device-present"
    CHECK_IN_APP = "check-in-app"
    CHECK_IN_VERBAL = "check-in-verbal"
    SCHEDULED = "scheduled"


class WorkerPresenceDefinition(Enum):
    WORKERS_IN_WORK_ZONE_WORKING = "workers-in-work-zone-working"
    WORKERS_IN_WORK_ZONE_NOT_WORKING = "workers-in-work-zone-not-working"
    MOBILE_EQUIPMENT_IN_WORK_ZONE_MOVING = "mobile-equipment-in-work-zone-moving"
    MOBILE_EQUIPMENT_IN_WORK_ZONE_NOT_MOVING = (
        "mobile-equipment-in-work-zone-not-moving"
    )
    FIXED_EQUIPMENT_IN_WORK_ZONE = "fixed-equipment-in-work-zone"
    HUMANS_BEHIND_BARRIER = "humans-behind-barrier"
    HUMANS_IN_RIGHT_OF_WAY = "humans-in-right-of-way"


class WorkerPresenceConfidence(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RelatedRoadEventType(Enum):
    FIRST_IN_SEQUENCE = "first-in-sequence"
    NEXT_IN_SEQUENCE = "next-in-sequence"
    FIRST_OCCURRENCE = "first-occurrence"
    NEXT_OCCURRENCE = "next-occurrence"
    RELATED_WORK_ZONE = "related-work-zone"
    RELATED_DETOUR = "related-detour"
    PLANNED_MOVING_OPERATION = "planned-moving-operation"
    ACTIVE_MOVING_OPERATION = "active-moving-operation"


class Direction(Enum):
    NORTHBOUND = "northbound"
    EASTBOUND = "eastbound"
    SOUTHBOUND = "southbound"
    WESTBOUND = "westbound"
    INNER_LOOP = "inner-loop"
    OUTER_LOOP = "outer-loop"
    UNDEFINED = "undefined"
    UNKNOWN = "unknown"
