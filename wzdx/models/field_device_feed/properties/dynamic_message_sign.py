# device_feed/properties/dynamic_message_sign.py
from typing import Literal
from pydantic import BaseModel, Field
from ..field_device_core_details import FieldDeviceCoreDetails

class DynamicMessageSignCoreDetails(FieldDeviceCoreDetails):
    device_type: Literal["dynamic-message-sign"] = "dynamic-message-sign"

class DynamicMessageSign(BaseModel):
    core_details: DynamicMessageSignCoreDetails = Field(alias="core_details")
    message_multi_string: str = Field(None, alias="message_multi_string")
