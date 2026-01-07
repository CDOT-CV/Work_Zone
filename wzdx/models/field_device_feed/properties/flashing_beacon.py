from typing import Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum
from ..field_device_core_details import FieldDeviceCoreDetails


class FlashingBeaconFunction(str, Enum):
    """
    The FlashingBeaconFunction enumerated type describes a list of options for what a :class:`FlashingBeacon` is being used to indicate.

    Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/enumerated-types/FlashingBeaconFunction.md
    """

    VEHICLE_ENTERING = "vehicle-entering"  # Vehicles are entering the roadway.
    QUEUE_WARNING = "queue-warning"  # There is a queue of vehicles.
    REDUCED_SPEED = "reduced-speed"  # There is a reduced speed limit.
    WORKERS_PRESENT = (
        "workers-present"  # There are workers present on or near the roadway.
    )


class FlashingBeaconCoreDetails(FieldDeviceCoreDetails):
    device_type: Literal["flashing-beacon"] = "flashing-beacon"


class FlashingBeacon(BaseModel):
    """
    The FlashingBeacon object describes a flashing warning beacon used to supplement a temporary traffic control device. A flashing warning beacon is mounted on a sign or channelizing device and used to indicate a warning condition and capture driver attention.

    The FlashingBeacon is a type of field device; it has a core_details property which contains the :class:`FieldDeviceCoreDetails` and exists within a :class:`FieldDeviceFeature`.

    Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/objects/FlashingBeacon.md
    """

    core_details: FlashingBeaconCoreDetails = Field(
        alias="core_details",
        description="The core details of the field device that are shared by all types of field devices, not specific to flashing beacons.",
    )
    function: FlashingBeaconFunction = Field(
        alias="function",
        description="Describes the function or purpose of the flashing beacon, i.e. what it is being used to indicate.",
    )
    is_flashing: Optional[bool] = Field(
        None,
        alias="is_flashing",
        description="A yes/no value indicating if the flashing beacon is currently in use and flashing.",
    )
    sign_text: Optional[str] = Field(
        None,
        alias="sign_text",
        description="The text on the sign the beacon is mounted on, if applicable.",
    )
