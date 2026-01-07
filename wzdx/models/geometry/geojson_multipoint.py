from typing import Literal
from pydantic import BaseModel, Field


class GeoJsonMultiPoint(BaseModel):
    """GeoJSON MultiPoint geometry"""

    type: Literal["MultiPoint"] = Field(
        default="MultiPoint",
        alias="type",
        description="The GeoJSON object type. This MUST be the string MultiPoint.",
    )
    coordinates: list[list[float]] = Field(
        alias="coordinates",
        description="A list of positions that make up the MultiPoint.",
    )
