from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..feed_info.feed_info import FeedInfo

from .field_device_feature import FieldDeviceFeature


class DeviceFeed(BaseModel):
    """
    The DeviceFeed object is the root (highest level) object of a WZDx Device Feed. There is one DeviceFeed object per feed GeoJSON document. The DeviceFeed is a [GeoJSON FeatureCollection](https://datatracker.ietf.org/doc/html/rfc7946#section-3.3) object.

    The DeviceFeed contains information (location, status, live data) about field devices deployed on the roadway in work zones.

    Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/objects/DeviceFeed.md
    """

    feed_info: FeedInfo = Field(
        alias="feed_info", description="Information about the data feed."
    )
    type: Literal["FeatureCollection"] = Field(
        default="FeatureCollection",
        alias="type",
        description="The GeoJSON object type. For WZDx, this must be the string FeatureCollection.",
    )
    features: list[FieldDeviceFeature] = Field(
        alias="features",
        description="An array of GeoJSON [Feature](https://datatracker.ietf.org/doc/html/rfc7946#section-3.2) objects which each represent a field device deployed in a work zone.",
    )
    bbox: Optional[list[float]] = Field(
        default=None,
        description="Information on the coordinate range for all FieldDeviceFeatures in the feed. The value must be an array of length 2n where n is the number of dimensions represented in the contained geometries, with all axes of the most southwesterly point followed by all axes of the more northeasterly point. The axes order of a bbox follows the axes order of geometries.",
    )
