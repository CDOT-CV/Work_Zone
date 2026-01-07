from typing import Literal
from pydantic import BaseModel, Field
from enum import Enum
from ..field_device_core_details import FieldDeviceCoreDetails


class TrafficSignalMode(str, Enum):
    """
    The TrafficSignalMode enumerated type describes the current operating mode of a :class:`TrafficSignal`.

    Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/enumerated-types/TrafficSignalMode.md
    """

    BLANK = "blank"  # The signal is not displaying anything.
    FLASHING_RED = "flashing-red"  # The signal is in a flashing red state that could be part of startup or fault.
    FLASHING_YELLOW = "flashing-yellow"  # The signal is in a flashing yellow state that could be part of startup or fault.
    FULLY_ACTUATED = (
        "fully-actuated"  # The signal is using an external trigger for all movements.
    )
    MANUAL = "manual"  # The signal is using a manual trigger.
    PRE_TIMED = "pre-timed"  # The signal is using a timed cycle.
    SEMI_ACTUATED = "semi-actuated"  # The signal is using an external trigger only for the minor movements.
    UNKNOWN = "unknown"  # The current operating mode is not known.


class TrafficSignalCoreDetails(FieldDeviceCoreDetails):
    device_type: Literal["traffic-signal"] = "traffic-signal"


class TrafficSignal(BaseModel):
    """
    The TrafficSignal object describes a temporary traffic signal deployed on a roadway.

    The TrafficSignal is a type of field device; it has a core_details property which contains the :class:`FieldDeviceCoreDetails` and exists within a :class:`FieldDeviceFeature`.

    Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/objects/TrafficSignal.md
    """

    core_details: TrafficSignalCoreDetails = Field(
        alias="core_details",
        description="The core details of the traffic signal device.",
    )
    mode: TrafficSignalMode = Field(
        alias="mode", description="The current operating mode of the traffic signal."
    )
