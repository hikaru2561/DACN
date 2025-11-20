from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class ClassBase(BaseModel):
    class_name: str
    subject_id: str
    teacher_id: str
    semester: Optional[str] = None
    academic_year: Optional[str] = None
    room: Optional[str] = None
    max_students: int = 50
    schedule_info: Optional[str] = None


class ClassCreate(ClassBase):
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ClassUpdate(BaseModel):
    class_name: Optional[str] = None
    teacher_id: Optional[str] = None
    room: Optional[str] = None
    max_students: Optional[int] = None
    schedule_info: Optional[str] = None
    is_active: Optional[bool] = None


class ClassResponse(ClassBase):
    class_id: int
    start_date: Optional[date]
    end_date: Optional[date]
    is_active: bool
    created_at: datetime
    student_count: Optional[int] = 0  # Số sinh viên đã đăng ký
    
    class Config:
        from_attributes = True
