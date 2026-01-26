from typing import Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum
from ..field_device_core_details import FieldDeviceCoreDetails

class FlashingBeaconFunction(str, Enum):
    VEHICLE_ENTERING = "vehicle-entering"
    QUEUE_WARNING = "queue-warning"
    REDUCED_SPEED = "reduced-speed"
    WORKERS_PRESENT = "workers-present"

class FlashingBeaconCoreDetails(FieldDeviceCoreDetails):
    device_type: Literal["flashing-beacon"] = "flashing-beacon"

class FlashingBeacon(BaseModel):
    core_details: FlashingBeaconCoreDetails = Field(alias="core_details")
    function: FlashingBeaconFunction = None
    is_flashing: Optional[bool] = Field(None, alias="is_flashing")
    sign_text: Optional[str] = Field(None, alias="sign_text")
