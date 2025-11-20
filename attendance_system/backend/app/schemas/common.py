from pydantic import BaseModel
from typing import Optional, List
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
