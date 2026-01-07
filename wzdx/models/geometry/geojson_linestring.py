from typing import Literal
from pydantic import BaseModel, Field


class GeoJsonLineString(BaseModel):
    """GeoJSON LineString geometry"""

    type: Literal["LineString"] = Field(
        default="LineString",
        alias="type",
        description="The GeoJSON object type. This MUST be the string LineString.",
    )
    coordinates: list[list[float]] = Field(
        alias="coordinates",
        description="A list of two or more positions that make up the LineString.",
    )
