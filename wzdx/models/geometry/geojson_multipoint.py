from typing import Literal
from pydantic import BaseModel, Field


class GeoJsonMultiPoint(BaseModel):
    """GeoJSON MultiPoint geometry"""

    type: Literal["MultiPoint"] = Field(default="MultiPoint", alias="type")
    coordinates: list[list[float]] = Field(alias="coordinates")
