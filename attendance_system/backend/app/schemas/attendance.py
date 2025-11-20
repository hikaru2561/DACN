from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .common import AttendanceStatusEnum

class AttendanceBase(BaseModel):
    session_id: int
    student_id: str


class AttendanceCreate(AttendanceBase):
    check_in_time: Optional[datetime] = None
    status: AttendanceStatusEnum = AttendanceStatusEnum.ABSENT
    confidence_score: Optional[float] = None


class AttendanceUpdate(BaseModel):
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    status: Optional[AttendanceStatusEnum] = None
    notes: Optional[str] = None


class AttendanceResponse(AttendanceBase):
    attendance_id: int
    check_in_time: Optional[datetime]
    check_out_time: Optional[datetime]
    status: AttendanceStatusEnum
    confidence_score: Optional[float]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
