from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

from .field_device_type import FieldDeviceType
from .field_device_status import FieldDeviceStatus
from ..enums import Direction

class FieldDeviceCoreDetails(BaseModel):
    device_type: FieldDeviceType = Field(None, alias="device_type")
    data_source_id: str = Field(None, alias="data_source_id")
    device_status: FieldDeviceStatus = Field(None, alias="device_status")
    update_date: datetime = Field(None, alias="update_date")
    has_automatic_location: bool = Field(None, alias="has_automatic_location")
    road_direction: Optional[Direction] = Field(None, alias="road_direction")
    road_names: Optional[list[str]] = Field(None, alias="road_names")
    name: Optional[str] = None
    description: Optional[str] = None
    status_messages: Optional[list[str]] = Field(None, alias="status_messages")
    is_moving: Optional[bool] = Field(None, alias="is_moving")
    road_event_ids: Optional[list[str]] = Field(None, alias="road_event_ids")
    milepost: Optional[float] = None
    make: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = Field(None, alias="serial_number")
    firmware_version: Optional[str] = Field(None, alias="firmware_version")
    velocity_kph: Optional[float] = Field(None, alias="velocity_kph")
