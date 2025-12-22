# wzdx/feed_info.py
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from .feed_data_source import FeedDataSource
from datetime import datetime

class FeedInfoIconeCustom(BaseModel):
    """Custom iCone properties"""
    # Add iCone custom fields here based on FeedInfoIconeCustom.java
    pass

class FeedInfo(BaseModel):
    """
    WZDx feed info metadata.
    
    See: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/objects/FeedInfo.md
    """
    publisher: str = None
    version: str = None
    license: Optional[str] = None
    data_sources: list[FeedDataSource] = Field(None, alias="data_sources")
    update_date: datetime = Field(None, alias="update_date")
    update_frequency: Optional[int] = Field(None, alias="update_frequency")
    contact_name: Optional[str] = Field(None, alias="contact_name")
    contact_email: Optional[EmailStr] = Field(None, alias="contact_email")
