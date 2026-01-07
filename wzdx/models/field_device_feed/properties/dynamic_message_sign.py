from typing import Literal
from pydantic import BaseModel, Field
from ..field_device_core_details import FieldDeviceCoreDetails


class DynamicMessageSignCoreDetails(FieldDeviceCoreDetails):
    device_type: Literal["dynamic-message-sign"] = "dynamic-message-sign"


class DynamicMessageSign(BaseModel):
    """
    The DynamicMessageSign object describes a dynamic message sign (DMS)—also known as changeable message sign (CMS) or variable message sign (VMS)—which is an electronic traffic sign deployed on the roadway used to provide information to travelers.

    The DynamicMessageSign is a type of field device; it has a core_details property which contains the :class:`FieldDeviceCoreDetails` and exists within a :class:`FieldDeviceFeature`.

    Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/objects/DynamicMessageSign.md
    """

    core_details: DynamicMessageSignCoreDetails = Field(
        alias="core_details",
        description="The core details of the field device that are shared by all types of field devices, not specific to dynamic message signs.",
    )
    message_multi_string: str = Field(
        alias="message_multi_string",
        description="The MULTI (Mark-Up Language for Transportation Information, see [NTCIP 1203 v03](https://www.ntcip.org/file/2018/11/NTCIP1203v03f.pdf)) formatted string describing the message currently posted to the sign.",
    )
