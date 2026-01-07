from typing import Annotated, Union

from pydantic import Field
from .geojson_point import GeoJsonPoint
from .geojson_linestring import GeoJsonLineString
from .geojson_multipoint import GeoJsonMultiPoint
from .geojson_polygon import GeoJsonPolygon

GeoJsonGeometry = Annotated[
    Union[
        GeoJsonPoint,
        GeoJsonLineString,
        GeoJsonMultiPoint,
        GeoJsonPolygon,
    ],
    Field(discriminator="type"),
]
