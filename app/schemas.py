from pydantic import BaseModel, HttpUrl, ConfigDict
import datetime


class URLCreate(BaseModel):
    target_url: HttpUrl


class URLInfo(BaseModel):
    id: int
    target_url: HttpUrl
    short_url: str
    clicks: int
    created_at: datetime.datetime
    
    model_config = ConfigDict(from_attributes=True)