from typing import Literal
from pydantic import BaseModel

class GeoJsonPolygon(BaseModel):
    """GeoJSON Polygon geometry"""
    type: Literal["Polygon"]
    coordinates: list[list[list[float]]]  # Array of linear rings
