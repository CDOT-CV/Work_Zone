from typing import Literal
from pydantic import BaseModel, Field


class GeoJsonPolygon(BaseModel):
    """GeoJSON Polygon geometry"""

    type: Literal["Polygon"] = Field(
        default="Polygon",
        alias="type",
        description="The GeoJSON object type. This MUST be the string Polygon.",
    )
    coordinates: list[list[list[float]]] = Field(
        alias="coordinates",
        description="A list of linear rings that make up the Polygon.",
    )
