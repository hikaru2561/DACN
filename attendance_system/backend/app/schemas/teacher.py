from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class TeacherBase(BaseModel):
    teacher_id: str
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None


class TeacherCreate(TeacherBase):
    user_id: Optional[int] = None


class TeacherUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None


class TeacherResponse(TeacherBase):
    user_id: Optional[int]
    photo_path: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
