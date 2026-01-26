from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class FeedDataSource(BaseModel):
    """WZDx feed data source"""
    data_source_id: str = Field(alias="data_source_id")
    organization_name: str = Field(None, alias="organization_name")
    update_date: Optional[datetime] = Field(None, alias="update_date")
    update_frequency: Optional[int] = Field(None, alias="update_frequency")
    contact_name: Optional[str] = Field(None, alias="contact_name")
    contact_email: Optional[str] = Field(None, alias="contact_email")
