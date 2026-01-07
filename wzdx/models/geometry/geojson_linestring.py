from typing import Literal
from pydantic import BaseModel, Field


class GeoJsonLineString(BaseModel):
    """GeoJSON LineString geometry"""

    type: Literal["LineString"] = Field(default="LineString", alias="type")
    coordinates: list[list[float]] = Field(alias="coordinates")
