from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from .feed_data_source import FeedDataSource
from datetime import datetime


class FeedInfo(BaseModel):
    """
    The FeedInfo object describes WZDx feed header information such as metadata, contact information, and data sources. There is one FeedInfo per WZDx GeoJSON document.

    Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/objects/FeedInfo.md
    """

    publisher: str = Field(
        alias="publisher",
        description="The organization responsible for publishing the feed.",
    )
    version: str = Field(
        alias="version",
        description="The WZDx specification version used to create the data feed in major.minor format. Note this mandates that all data in a WZDx feed complies to a single version of WZDx.",
    )
    license: Optional[str] = Field(
        default=None,
        alias="license",
        description='The URL of the license that applies to the data in the WZDx feed. This must be the string "https://creativecommons.org/publicdomain/zero/1.0/"',
    )
    data_sources: list[FeedDataSource] = Field(
        alias="data_sources",
        description="A list of specific data sources for the road event data in the feed.",
    )
    update_date: datetime = Field(
        alias="update_date",
        description="The UTC date and time when the GeoJSON file (representing the instance of the feed) was generated.",
    )
    update_frequency: Optional[int] = Field(
        default=None,
        alias="update_frequency",
        description="The frequency in seconds at which the data feed is updated.",
    )
    contact_name: Optional[str] = Field(
        default=None,
        alias="contact_name",
        description="The name of the individual or group responsible for the data feed.",
    )
    contact_email: Optional[EmailStr] = Field(
        default=None,
        alias="contact_email",
        description="The email address of the individual or group responsible for the data feed.",
    )
