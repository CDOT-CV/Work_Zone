from typing import Literal
from pydantic import BaseModel

class GeoJsonMultiPoint(BaseModel):
    """GeoJSON MultiPoint geometry"""
    type: Literal["MultiPoint"]
    coordinates: list[list[float]]  # Array of positions
