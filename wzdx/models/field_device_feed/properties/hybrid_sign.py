from typing import Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum
from ..field_device_core_details import FieldDeviceCoreDetails


class HybridSignDynamicMessageFunction(str, Enum):
    """
    The HybridSignDynamicMessageFunction enumerated type describes options for the function of the dynamic message displayed by the electronic display on a :class:`HybridSign`.

    Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/enumerated-types/HybridSignDynamicMessageFunction.md
    """

    SPEED_LIMIT = "speed-limit"  # The message is a speed limit.
    TRAVEL_TIME = "travel-time"  # The message is a travel time.
    OTHER = "other"  # The hybrid sign message function is not one of the other options described by this enumerated type.


class HybridSignCoreDetails(FieldDeviceCoreDetails):
    device_type: Literal["hybrid-sign"] = "hybrid-sign"


class HybridSign(BaseModel):
    """
    The HybridSign object describes a hybrid sign that contains static text (e.g. on an aluminum sign) along with a single electronic message display, used to provide information to travelers. This object is intended to be general to represent hybrid signs with multiple functions, such as variable speed limit signs (VSLS), hybrid travel time signs, and other similar systems.

    The HybridSign is a type of field device; it has a core_details property which contains the :class:`FieldDeviceCoreDetails` and exists within a :class:`FieldDeviceFeature`.

    Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/objects/HybridSign.md
    """

    core_details: HybridSignCoreDetails = Field(
        alias="core_details",
        description="The core details of the field device shared by all field devices types, not specific to hybrid signs.",
    )
    dynamic_message_function: HybridSignDynamicMessageFunction = Field(
        alias="dynamic_message_function",
        description="The function the dynamic message displayed (e.g. a speed limit).",
    )
    dynamic_message_text: Optional[str] = Field(
        None,
        alias="dynamic_message_text",
        description="A text representation of the message currently posted to the electronic component of the hybrid sign.",
    )
    static_sign_text: Optional[str] = Field(
        None,
        alias="static_sign_text",
        description="The static text on the non-electronic component of the hybrid sign.",
    )
