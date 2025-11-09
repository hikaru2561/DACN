"""
Pydantic Schemas
Request/Response validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import date, time, datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class GenderEnum(str, Enum):
    MALE = "Nam"
    FEMALE = "Nữ"
    OTHER = "Khác"


class UserRoleEnum(str, Enum):
    ADMIN = "Admin"
    TEACHER = "Teacher"
    STUDENT = "Student"


class AttendanceStatusEnum(str, Enum):
    ABSENT = "Vắng"
    PRESENT = "Có mặt"
    LATE = "Đi muộn"
    EARLY_LEAVE = "Về sớm"
    EXCUSED = "Có phép"


class SessionStatusEnum(str, Enum):
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


# ============================================================================
# USER SCHEMAS
# ============================================================================

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


# ============================================================================
# STUDENT SCHEMAS
# ============================================================================

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


# ============================================================================
# TEACHER SCHEMAS
# ============================================================================

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


# ============================================================================
# SUBJECT SCHEMAS
# ============================================================================

class SubjectBase(BaseModel):
    subject_id: str
    subject_name: str
    credits: int = 3
    description: Optional[str] = None


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    subject_name: Optional[str] = None
    credits: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SubjectResponse(SubjectBase):
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# CLASS SCHEMAS
# ============================================================================

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


# ============================================================================
# SESSION SCHEMAS
# ============================================================================

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


# ============================================================================
# ATTENDANCE SCHEMAS
# ============================================================================

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


# ============================================================================
# CAMERA SCHEMAS
# ============================================================================

class CameraDeviceBase(BaseModel):
    device_name: str
    device_code: str
    stream_url: str
    location: Optional[str] = None
    room: Optional[str] = None


class CameraDeviceCreate(CameraDeviceBase):
    pass


class CameraDeviceUpdate(BaseModel):
    device_name: Optional[str] = None
    stream_url: Optional[str] = None
    location: Optional[str] = None
    room: Optional[str] = None
    is_active: Optional[bool] = None


class CameraDeviceResponse(CameraDeviceBase):
    device_id: int
    is_active: bool
    last_heartbeat: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# STATISTICS SCHEMAS
# ============================================================================

class AttendanceStatistics(BaseModel):
    """Thống kê điểm danh của một sinh viên trong một lớp"""
    student_id: str
    student_name: str
    total_sessions: int
    attended: int
    late: int
    absent: int
    excused: int
    attendance_rate: float


class ClassStatistics(BaseModel):
    """Thống kê của một lớp học"""
    class_id: int
    class_name: str
    total_students: int
    total_sessions: int
    average_attendance_rate: float


# ============================================================================
# RESPONSE WRAPPERS
# ============================================================================

class SuccessResponse(BaseModel):
    """Thành công response"""
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Lỗi response"""
    success: bool = False
    message: str
    detail: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Paginated response"""
    success: bool = True
    data: List
    total: int
    page: int
    page_size: int
    total_pages: int
