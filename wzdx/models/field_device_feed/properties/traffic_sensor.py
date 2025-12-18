# device_feed/properties/traffic_sensor.py
from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..field_device_core_details import FieldDeviceCoreDetails

class TrafficSensorLaneData(BaseModel):
    lane_order: int = Field(alias="lane_order")
    average_speed_kph: Optional[float] = Field(None, alias="average_speed_kph")
    volume_vph: Optional[int] = Field(None, alias="volume_vph")
    occupancy_percent: Optional[float] = Field(None, alias="occupancy_percent")

class TrafficSensorCoreDetails(FieldDeviceCoreDetails):
    device_type: Literal["traffic-sensor"] = "traffic-sensor"

class TrafficSensor(BaseModel):
    core_details: TrafficSensorCoreDetails = Field(alias="core_details")
    collection_interval_start_date: Optional[str] = Field(
        None, alias="collection_interval_start_date"
    )
    collection_interval_end_date: Optional[str] = Field(
        None, alias="collection_interval_end_date"
    )
    lane_data: Optional[list[TrafficSensorLaneData]] = Field(None, alias="lane_data")