from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..geometry.geojson_geometry import GeoJsonGeometry
from .properties.field_device_properties import FieldDeviceProperties


class FieldDeviceFeature(BaseModel):
    """
    The FieldDeviceFeature object is a GeoJSON Feature representing a deployed field device. This object contains the specific details of the field device, similar to how the RoadEventFeature object in a WZDx Feed contains the road event object (WorkZoneRoadEvent or DetourRoadEvent.

    Currently, only point devices are supported.

    Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/objects/FieldDeviceFeature.md
    """

    id: str = Field(
        alias="id",
        description="A unique identifier issued by the data feed provider to identify the field device. It is recommended that this identifier is a Universally Unique Identifier (UUID) as defined in RFC 4122 to guarantee uniqueness between feeds and over time.",
    )
    type: Literal["Feature"] = Field(
        default="Feature",
        alias="type",
        description="The GeoJSON object type. This MUST be the string Feature.",
    )
    properties: FieldDeviceProperties = Field(
        alias="properties",
        description="The specific details of the field device.",
    )
    geometry: GeoJsonGeometry = Field(
        alias="geometry",
        description="The geometry of the field device, indicating its location. The Geometry object's type property MUST be Point.",
    )
    bbox: Optional[list[float]] = Field(
        default=None,
        alias="bbox",
        description="Information on the coordinate range for this field device. Must be an array of length 2n where n is the number of dimensions represented in the geometry property, with all axes of the most southwesterly point followed by all axes of the more northeasterly point. The axes order of a bbox follows the axes order of the geometry.",
    )
