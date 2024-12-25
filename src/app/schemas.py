from pydantic import BaseModel
from typing import List, Optional


class UserBase(BaseModel):
    name: str
    email: Optional[str] = None
    mobile: Optional[str] = None
    telegram_chat_id: Optional[int] = None
    active: Optional[int] = 0  # Default to active


class UserCreate(UserBase):
    name: str
    email: str
    mobile: str
    telegram_chat_id: int


class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True


class MarketBase(BaseModel):
    name: str


class MarketCreate(MarketBase):
    pass


class MarketResponse(MarketBase):
    id: int

    class Config:
        orm_mode = True


class PairBase(BaseModel):
    market_id: int
    name: str


class PairCreate(PairBase):
    pass


class PairResponse(PairBase):
    id: int

    class Config:
        orm_mode = True


class TimeframeBase(BaseModel):
    name: str
    minutes: int


class TimeframeCreate(TimeframeBase):
    pass


class TimeframeResponse(TimeframeBase):
    id: int

    class Config:
        orm_mode = True


class NotificationBase(BaseModel):
    user_id: int
    message: str
    method: str  # e.g., "telegram", "sms", "email"


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    id: int

    class Config:
        orm_mode = True
