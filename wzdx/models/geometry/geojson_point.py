# wzdx/geometry/geojson_point.py
from typing import Literal
from pydantic import BaseModel

class GeoJsonPoint(BaseModel):
    """GeoJSON Point geometry"""
    type: Literal["Point"]
    coordinates: list[float]  # [longitude, latitude] or [longitude, latitude, elevation]