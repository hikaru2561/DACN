from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional
from .common import GenderEnum

class StudentBase(BaseModel):
    student_id: str
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    class_name: Optional[str] = None
    major: Optional[str] = None
    academic_year: Optional[str] = None


class StudentCreate(StudentBase):
    user_id: Optional[int] = None


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    class_name: Optional[str] = None
    major: Optional[str] = None
    academic_year: Optional[str] = None
    is_active: Optional[bool] = None


class StudentResponse(StudentBase):
    user_id: Optional[int]
    photo_path: Optional[str]
    is_active: bool
    created_at: datetime
    face_count: Optional[int] = 0  # Số lượng ảnh khuôn mặt
    
    class Config:
        from_attributes = True
