from datetime import datetime
from pydantic import BaseModel, EmailStr, HttpUrl, field_validator
from typing import Optional, Literal


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class EndpointBase(BaseModel):
    name: str
    url: HttpUrl
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"] = "GET"
    expected_status: int = 200
    interval_seconds: int = 60
    is_active: bool = True

    @field_validator("interval_seconds")
    @classmethod
    def validate_interval(cls, v: int) -> int:
        if v < 15:
            raise ValueError("interval_seconds must be at least 15 seconds")
        return v


class EndpointCreate(EndpointBase):
    pass


class EndpointUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    method: Optional[Literal["GET", "POST", "PUT", "DELETE", "PATCH"]] = None
    expected_status: Optional[int] = None
    interval_seconds: Optional[int] = None
    is_active: Optional[bool] = None


class EndpointOut(EndpointBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class HealthLogOut(BaseModel):
    id: int
    endpoint_id: int
    status_code: int
    success: bool
    latency_ms: float
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


