from pydantic import BaseModel

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
