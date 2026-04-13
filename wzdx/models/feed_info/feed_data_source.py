from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class FeedDataSource(BaseModel):
    """
    The FeedDataSource object describes information about a specific data source used to build a data feed. A WZDx feed must contain at least one FeedDataSource, included as an entry in the data_sources array of the FeedInfo object.

    Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/objects/FeedDataSource.md
    """

    data_source_id: str = Field(
        alias="data_source_id",
        description="A unique identifier for the data source organization providing work zone data. It is recommended that this identifier is a Universally Unique Identifier (UUID) as defined in RFC 4122 to guarantee uniqueness between feeds and over time.",
    )
    organization_name: str = Field(
        alias="organization_name",
        description="The name of the organization for the authoritative source of the work zone data.",
    )
    update_date: Optional[datetime] = Field(
        default=None,
        alias="update_date",
        description="The UTC date and time when the data source was last updated.",
    )
    update_frequency: Optional[int] = Field(
        default=None,
        alias="update_frequency",
        description="The frequency in seconds at which the data source is updated.",
    )
    contact_name: Optional[str] = Field(
        default=None,
        alias="contact_name",
        description="The name of the individual or group responsible for the data source.",
    )
    contact_email: Optional[EmailStr] = Field(
        default=None,
        alias="contact_email",
        description="The email address of the individual or group responsible for the data source.",
    )
