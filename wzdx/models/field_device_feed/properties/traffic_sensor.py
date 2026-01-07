from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..field_device_core_details import FieldDeviceCoreDetails


class TrafficSensorLaneData(BaseModel):
    """
    The TrafficSensorLaneData object describes data for a single lane measured by a :class:`TrafficSensor` deployed on the roadway.

    Note this structure allows a single :class:`TrafficSensor` to provide data across lanes on multiple road events.

    Description: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/objects/TrafficSensorLaneData.md
    """

    lane_order: int = Field(
        alias="lane_order",
        description="The lane's position in sequence on the roadway. If road_event_id is provided, the value of this property corresponds to the associated road event's Lane's order property.",
    )
    road_event_id: Optional[str] = Field(
        None,
        alias="road_event_id",
        description="The ID of a RoadEventFeature which the measured lane occurs in, if applicable.",
    )
    average_speed_kph: Optional[float] = Field(
        None,
        alias="average_speed_kph",
        description="The average speed of traffic in the lane over the collection interval (in kilometers per hour).",
    )
    volume_vph: Optional[float] = Field(
        None,
        alias="volume_vph",
        description="The rate of vehicles passing by the sensor in the lane during the collection interval (in vehicles per hour).",
    )
    occupancy_percent: Optional[float] = Field(
        None,
        alias="occupancy_percent",
        description="The percent of time the lane monitored by the sensor was occupied by a vehicle over the collection interval.",
    )


class TrafficSensorCoreDetails(FieldDeviceCoreDetails):
    device_type: Literal["traffic-sensor"] = "traffic-sensor"


class TrafficSensor(BaseModel):
    """
    The TrafficSensor object describes a traffic sensor deployed on a roadway which captures traffic metrics (e.g. speed, volume, occupancy) over a collection interval. The TrafficSensor can describe lane-level traffic data if available and if associated with a road event (e.g. :class:`WorkZoneRoadEvent`).

    The TrafficSensor is a type of field device; it has a core_details property which contains the :class:`FieldDeviceCoreDetails` and exists within a :class:`FieldDeviceFeature`.

    Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/objects/TrafficSensor.md
    """

    core_details: TrafficSensorCoreDetails = Field(
        alias="core_details",
        description="The core details of the field device shared by all field devices types, not specific to traffic sensors.",
    )
    collection_interval_start_date: str = Field(
        alias="collection_interval_start_date",
        description="The UTC date and time where the TrafficSensor data began being collected at. The averages and totals contained in the TrafficSensor data apply to the inclusive interval of collection_interval_start_date to collection_interval_end_date.",
    )
    collection_interval_end_date: str = Field(
        alias="collection_interval_end_date",
        description="The UTC date and time where the TrafficSensor collection interval ended. The averages and totals contained in the TrafficSensor data apply to the inclusive interval of collection_interval_start_date to collection_interval_end_date.",
    )
    average_speed_kph: Optional[float] = Field(
        None,
        alias="average_speed_kph",
        description="The average speed of vehicles across all lanes over the collection interval in kilometers per hour.",
    )
    volume_vph: Optional[float] = Field(
        None,
        alias="volume_vph",
        description="The rate of vehicles passing by the sensor during the collection interval in vehicles per hour.",
    )
    occupancy_percent: Optional[float] = Field(
        None,
        alias="occupancy_percent",
        description="The percent of time the roadway section monitored by the sensor was occupied by a vehicle over the collection interval.",
    )
    lane_data: Optional[list[TrafficSensorLaneData]] = Field(
        None,
        alias="lane_data",
        description="A list of objects each describing traffic data for a specific lane.",
    )
