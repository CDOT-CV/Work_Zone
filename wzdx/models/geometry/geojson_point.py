from typing import Literal
from pydantic import BaseModel, Field


class GeoJsonPoint(BaseModel):
    """GeoJSON Point geometry"""

    type: Literal["Point"] = Field(
        default="Point",
        alias="type",
        description="The GeoJSON object type. This MUST be the string Point.",
    )
    coordinates: list[float] = Field(
        alias="coordinates",
        description="A single position that makes up the Point.",
    )
