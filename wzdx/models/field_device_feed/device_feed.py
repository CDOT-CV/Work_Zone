# device_feed/device_feed.py
from typing import Optional
from pydantic import BaseModel, Field

from ..feed_info.feed_info import FeedInfo

from .field_device_feature import FieldDeviceFeature

# Note: You'll need to implement FeedInfo from the wzdx package
# from ..wzdx import FeedInfo

class DeviceFeed(BaseModel):
    feed_info: FeedInfo = Field(alias="feed_info")
    type: str
    features: list[FieldDeviceFeature]
    bbox: Optional[list[float]] = None