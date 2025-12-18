# device_feed/field_device_core_details.py
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

from .field_device_type import FieldDeviceType
from .field_device_status import FieldDeviceStatus

class FieldDeviceCoreDetails(BaseModel):
    device_type: Optional[FieldDeviceType] = Field(None, alias="device_type")
    road_event_id: Optional[str] = Field(None, alias="road_event_id")
    data_source_id: Optional[str] = Field(None, alias="data_source_id")
    road_names: Optional[list[str]] = Field(None, alias="road_names")
    name: Optional[str] = None
    description: Optional[str] = None
    device_status: Optional[FieldDeviceStatus] = Field(None, alias="device_status")
    update_date: Optional[datetime] = Field(None, alias="update_date")
    has_automatic_location: Optional[bool] = Field(None, alias="has_automatic_location")
    velocity_kph: Optional[float] = Field(None, alias="velocity_kph")
    is_moving: Optional[bool] = Field(None, alias="is_moving")
    road_direction: Optional[str] = Field(None, alias="road_direction")
    make: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = Field(None, alias="serial_number")
    firmware_version: Optional[str] = Field(None, alias="firmware_version")
    milepost: Optional[float] = None