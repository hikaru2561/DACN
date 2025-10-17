"""
Pydantic models - Optimized Version
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

# User schemas - Minimal
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    student_code: str = Field(..., min_length=1, max_length=20)
    department: Optional[str] = Field(None, max_length=50)

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Face detection schemas
class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int

class FaceInfo(BaseModel):
    bbox: BoundingBox
    embedding: List[float]
    confidence: float

class FaceDetectionResponse(BaseModel):
    faces: List[FaceInfo]
    count: int
    timestamp: datetime

# Recognition schemas
class RecognitionResponse(BaseModel):
    success: bool
    user: Optional[UserResponse] = None
    confidence: Optional[float] = None
    timestamp: Optional[datetime] = None
    message: Optional[str] = None

# Attendance schemas
class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    timestamp: datetime
    confidence: Optional[float] = None
    device_id: Optional[str] = None
    
    class Config:
        from_attributes = True

# Statistics schemas
class DailyStats(BaseModel):
    date: str
    count: int

class StatsResponse(BaseModel):
    total_attendance: int
    unique_users: int
    daily_breakdown: List[DailyStats]
    period_days: int

# Health check schema
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str

# Error schemas
class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
