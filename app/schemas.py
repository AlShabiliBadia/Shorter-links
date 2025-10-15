from pydantic import BaseModel, Field, HttpUrl, ConfigDict, EmailStr, model_validator
import datetime


class URLCreate(BaseModel):
    target_url: HttpUrl


class URLInfo(BaseModel):
    id: int = Field(alias='url_id') 
    target_url: HttpUrl
    short_url: str
    clicks: int
    created_at: datetime.datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserAccount(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    password_confirmation: str


    @model_validator(mode="after")
    def password_must_match(self):
        if self.password != self.password_confirmation:
            raise ValueError("Password and Password confirmation are not matching.")
        return self

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserDisplay(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)