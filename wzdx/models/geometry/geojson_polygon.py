from typing import Literal
from pydantic import BaseModel, Field


class GeoJsonPolygon(BaseModel):
    """GeoJSON Polygon geometry"""

    type: Literal["Polygon"] = Field(default="Polygon", alias="type")
    coordinates: list[list[list[float]]] = Field(
        alias="coordinates"
    )  # Array of linear rings
