from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, model_validator
from ..field_device_core_details import FieldDeviceCoreDetails


class CameraCoreDetails(FieldDeviceCoreDetails):
    device_type: Literal["camera"] = "camera"


class Camera(BaseModel):
    """
    The Camera object describes a camera device deployed in the field, capable of capturing still images.

    The Camera is a type of field device; it has a core_details property which contains the :class:`FieldDeviceCoreDetails` and exists within a :class:`FieldDeviceFeature`.

    Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/objects/Camera.md
    """

    core_details: CameraCoreDetails = Field(
        alias="core_details",
        description="The core details of the field device that are shared by all types of field devices, not specific to cameras.",
    )
    image_url: Optional[HttpUrl] = Field(
        None,
        alias="image_url",
        description="A URL pointing to an image file for the camera image still.",
    )
    image_timestamp: Optional[datetime] = Field(
        None,
        alias="image_timestamp",
        description="The UTC date and time when the image was captured.",
    )

    @model_validator(mode="after")
    def validate_image_timestamp(self) -> "Camera":
        """Validate that image_timestamp is provided when image_url is set."""
        if self.image_url is not None and self.image_timestamp is None:
            raise ValueError("image_timestamp is required when image_url is provided")
        return self
