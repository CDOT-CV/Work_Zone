from typing import Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum
from ..field_device_core_details import FieldDeviceCoreDetails

class HybridSignDynamicMessageFunction(str, Enum):
    SPEED_LIMIT = "speed-limit"
    TRAVEL_TIME = "travel-time"
    OTHER = "other"

class HybridSignCoreDetails(FieldDeviceCoreDetails):
    device_type: Literal["hybrid-sign"] = "hybrid-sign"

class HybridSign(BaseModel):
    core_details: HybridSignCoreDetails = Field(alias="core_details")
    dynamic_message_function: Optional[HybridSignDynamicMessageFunction] = Field(
        None, alias="dynamic_message_function"
    )
    dynamic_message_text: Optional[str] = Field(None, alias="dynamic_message_text")
    static_sign_text: Optional[str] = Field(None, alias="static_sign_text")
