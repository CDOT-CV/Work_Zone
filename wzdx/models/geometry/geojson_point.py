from typing import Literal
from pydantic import BaseModel, Field


class GeoJsonPoint(BaseModel):
    """GeoJSON Point geometry"""

    type: Literal["Point"] = Field(default="Point", alias="type")
    coordinates: list[float] = Field(
        alias="coordinates"
    )  # [longitude, latitude] or [longitude, latitude, elevation]
