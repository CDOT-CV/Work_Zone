# wzdx/geometry/geojson_linestring.py
from typing import Literal
from pydantic import BaseModel

class GeoJsonLineString(BaseModel):
    """GeoJSON LineString geometry"""
    type: Literal["LineString"]
    coordinates: list[list[float]]  # Array of positions