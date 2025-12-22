# device_feed/properties/camera.py
from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from ..field_device_core_details import FieldDeviceCoreDetails

class CameraCoreDetails(FieldDeviceCoreDetails):
    device_type: Literal["camera"] = "camera"

class Camera(BaseModel):
    core_details: CameraCoreDetails = Field(alias="core_details")
    image_url: Optional[HttpUrl] = Field(None, alias="image_url")
    image_timestamp: Optional[datetime] = Field(None, alias="image_timestamp")
