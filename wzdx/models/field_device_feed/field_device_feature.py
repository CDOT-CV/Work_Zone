from typing import Optional
from pydantic import BaseModel

from ..geometry.geojson_geometry import GeoJsonGeometry
from .properties.field_device_properties import FieldDeviceProperties


class FieldDeviceFeature(BaseModel):
    id: str
    type: str
    properties: FieldDeviceProperties
    geometry: GeoJsonGeometry
    bbox: Optional[list[float]] = None

    # Custom Fields
    route_details_start: Optional[dict] = None
    route_details_end: Optional[dict] = None
