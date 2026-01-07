from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

from .field_device_type import FieldDeviceType
from .field_device_status import FieldDeviceStatus
from ..enums import Direction


class FieldDeviceCoreDetails(BaseModel):
    """
    The FieldDeviceCoreDetails object represents the core details—both configuration and current state—of a field device that are shared by all types of field devices.
    The FieldDeviceCoreDetails object cannot occur directly in a data feed and does not represent a field device on its own. It is used as the value of the core_details
    property on every specific type of field device, each represented by its own object.

    Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/objects/FieldDeviceCoreDetails.md
    """

    device_type: FieldDeviceType = Field(
        alias="device_type", description="The type of field device."
    )
    data_source_id: str = Field(
        alias="data_source_id",
        description="Identifies the data source from which the field device data originates.",
    )
    device_status: FieldDeviceStatus = Field(
        alias="device_status",
        description="The operational status of the field device. The value of this property indicates if the device is ok or in an error or warning state.",
    )
    update_date: datetime = Field(
        alias="update_date",
        description="The UTC time and date when the field device information was updated.",
    )
    has_automatic_location: bool = Field(
        alias="has_automatic_location",
        description="A yes/no value indicating if the field device location (parent FieldDeviceFeature's geometry) is determined automatically from an onboard GPS (true) or manually set/overridden (false).",
    )
    road_direction: Optional[Direction] = Field(
        None,
        alias="road_direction",
        description="The direction of the road that the field device is on. This value indicates the direction of the traffic flow of the road, not a real heading angle.",
    )
    road_names: Optional[list[str]] = Field(
        None,
        alias="road_names",
        description="A list of publicly known names of the road on which the device is located. This may include the road number designated by a jurisdiction such as a county, state or interstate (e.g. I-5, VT 133).",
    )
    name: Optional[str] = Field(
        None, alias="name", description="A human-readable name for the field device."
    )
    description: Optional[str] = Field(
        None, alias="description", description="A description of the field device."
    )
    status_messages: Optional[list[str]] = Field(
        None,
        alias="status_messages",
        description="A list of messages associated with the device's status, if applicable. Used to provide additional information about the status such as specific warning or error messages.",
    )
    is_moving: Optional[bool] = Field(
        None,
        alias="is_moving",
        description="A yes/no value indicating if the device is actively moving (not statically placed) as part of a mobile work zone operation.",
    )
    road_event_ids: Optional[list[str]] = Field(
        None,
        alias="road_event_ids",
        description="A list of one or more IDs of a RoadEventFeature that the device is associated with.",
    )
    milepost: Optional[float] = Field(
        None,
        alias="milepost",
        description="The linear distance measured against a milepost marker along a roadway where the device is located.",
    )
    make: Optional[str] = Field(
        None, alias="make", description="The make or manufacturer of the device."
    )
    model: Optional[str] = Field(
        None, alias="model", description="The model of the device."
    )
    serial_number: Optional[str] = Field(
        None, alias="serial_number", description="The serial number of the device."
    )
    firmware_version: Optional[str] = Field(
        None,
        alias="firmware_version",
        description="The version of firmware the device is using to operate.",
    )
    velocity_kph: Optional[float] = Field(
        None,
        alias="velocity_kph",
        description="The velocity of the device in kilometers per hour.",
    )
