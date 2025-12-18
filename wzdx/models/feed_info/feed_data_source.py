# wzdx/feed_data_source.py
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from ..enums import LocationMethod

class FeedDataSource(BaseModel):
    """WZDx feed data source"""
    data_source_id: str = Field(alias="data_source_id")
    organization_name: Optional[str] = Field(None, alias="organization_name")
    contact_name: Optional[str] = Field(None, alias="contact_name")
    contact_email: Optional[str] = Field(None, alias="contact_email")
    update_frequency: Optional[int] = Field(None, alias="update_frequency")
    update_date: Optional[str] = Field(None, alias="update_date")
    location_method: Optional[LocationMethod] = Field(None, alias="location_method")
    lrs_type: Optional[str] = Field(None, alias="lrs_type")
    lrs_url: Optional[str] = Field(None, alias="lrs_url")