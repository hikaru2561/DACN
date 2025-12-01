from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    full_name: str
    is_active: Optional[bool] = True

# Properties to receive via API on creation
class UserCreate(UserBase):
    pass

# Properties to receive via API on update
class UserUpdate(UserBase):
    full_name: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    avatar_path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Additional properties to return via API
class User(UserInDBBase):
    pass
