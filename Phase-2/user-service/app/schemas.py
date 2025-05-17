from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True 