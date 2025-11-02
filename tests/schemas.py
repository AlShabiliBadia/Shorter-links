from pydantic import BaseModel, HttpUrl, EmailStr
from datetime import datetime

class UserDisplay(BaseModel):
    id: int
    username: str
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

    def model_post_init(self, __context):
        assert self.token_type == "bearer"

class URLInfo(BaseModel):
    id: int
    target_url: HttpUrl
    short_url: HttpUrl
    clicks: int
    created_at: datetime

class URLStats(BaseModel):
    target_url: HttpUrl
    short_code: str
    clicks: int

class ErrorResponse(BaseModel):
    detail: str