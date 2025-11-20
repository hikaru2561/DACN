from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from .common import UserRoleEnum

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRoleEnum


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    user_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
