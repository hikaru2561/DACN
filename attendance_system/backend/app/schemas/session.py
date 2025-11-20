from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional
from .common import SessionStatusEnum

class SessionBase(BaseModel):
    class_id: int
    session_date: date
    start_time: time
    end_time: time
    room: Optional[str] = None
    notes: Optional[str] = None


class SessionCreate(SessionBase):
    status: SessionStatusEnum = SessionStatusEnum.SCHEDULED


class SessionUpdate(BaseModel):
    session_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    room: Optional[str] = None
    status: Optional[SessionStatusEnum] = None
    notes: Optional[str] = None


class SessionResponse(SessionBase):
    session_id: int
    status: SessionStatusEnum
    created_at: datetime
    attendance_count: Optional[int] = 0  # Số sinh viên đã điểm danh
    
    class Config:
        from_attributes = True
