"""
SQLAlchemy Models
Mapping Python classes to PostgreSQL tables
"""
from sqlalchemy import Column, Integer, String, Boolean, Date, Time, DateTime, Text, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import BYTEA
from datetime import datetime
import enum

from database import Base


# ============================================================================
# ENUMS
# ============================================================================

class GenderEnum(str, enum.Enum):
    """Giới tính"""
    MALE = "Nam"
    FEMALE = "Nữ"
    OTHER = "Khác"


class UserRoleEnum(str, enum.Enum):
    """Vai trò người dùng"""
    ADMIN = "Admin"
    TEACHER = "Teacher"
    STUDENT = "Student"


class AttendanceStatusEnum(str, enum.Enum):
    """Trạng thái điểm danh"""
    ABSENT = "Vắng"
    PRESENT = "Có mặt"
    LATE = "Đi muộn"
    EARLY_LEAVE = "Về sớm"
    EXCUSED = "Có phép"


class SessionStatusEnum(str, enum.Enum):
    """Trạng thái buổi học"""
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


# ============================================================================
# MODELS
# ============================================================================

class User(Base):
    """Bảng users - Tài khoản người dùng"""
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    role = Column(String(20), nullable=False)  # Admin, Teacher, Student
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="user", uselist=False)
    teacher = relationship("Teacher", back_populates="user", uselist=False)


class Student(Base):
    """Bảng students - Thông tin sinh viên"""
    __tablename__ = "students"
    
    student_id = Column(String(20), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    full_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date)
    gender = Column(String(10))
    phone = Column(String(15))
    email = Column(String(100))
    address = Column(Text)
    class_name = Column(String(50))
    major = Column(String(100))
    academic_year = Column(String(20))
    photo_path = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="student")
    face_encodings = relationship("FaceEncoding", back_populates="student")
    attendances = relationship("Attendance", back_populates="student")
    enrollments = relationship("ClassEnrollment", back_populates="student")


class Teacher(Base):
    """Bảng teachers - Thông tin giảng viên"""
    __tablename__ = "teachers"
    
    teacher_id = Column(String(20), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    full_name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone = Column(String(15))
    department = Column(String(100))
    photo_path = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="teacher")
    classes = relationship("Class", back_populates="teacher")


class Subject(Base):
    """Bảng subjects - Môn học"""
    __tablename__ = "subjects"
    
    subject_id = Column(String(20), primary_key=True)
    subject_name = Column(String(200), nullable=False)
    credits = Column(Integer, default=3)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    classes = relationship("Class", back_populates="subject")


class Class(Base):
    """Bảng classes - Lớp học môn"""
    __tablename__ = "classes"
    
    class_id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(String(20), ForeignKey("subjects.subject_id"))
    teacher_id = Column(String(20), ForeignKey("teachers.teacher_id"))
    class_name = Column(String(100), nullable=False)
    semester = Column(String(20))
    academic_year = Column(String(20))
    room = Column(String(50))
    max_students = Column(Integer, default=50)
    schedule_info = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subject = relationship("Subject", back_populates="classes")
    teacher = relationship("Teacher", back_populates="classes")
    sessions = relationship("Session", back_populates="class_obj")
    enrollments = relationship("ClassEnrollment", back_populates="class_obj")


class Session(Base):
    """Bảng sessions - Buổi học"""
    __tablename__ = "sessions"
    
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("classes.class_id", ondelete="CASCADE"))
    session_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    room = Column(String(50))
    status = Column(String(20), default="Scheduled")
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    class_obj = relationship("Class", back_populates="sessions")
    attendances = relationship("Attendance", back_populates="session")


class Attendance(Base):
    """Bảng attendance - Điểm danh"""
    __tablename__ = "attendance"
    
    attendance_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.session_id", ondelete="CASCADE"))
    student_id = Column(String(20), ForeignKey("students.student_id", ondelete="CASCADE"))
    check_in_time = Column(DateTime)
    check_out_time = Column(DateTime)
    status = Column(String(20), default="Vắng")
    confidence_score = Column(Float)
    photo_path = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="attendances")
    student = relationship("Student", back_populates="attendances")


class FaceEncoding(Base):
    """Bảng face_encodings - Mã hóa khuôn mặt"""
    __tablename__ = "face_encodings"
    
    face_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(20), ForeignKey("students.student_id", ondelete="CASCADE"))
    encoding = Column(BYTEA, nullable=False)  # 512D vector
    photo_path = Column(String(255))
    quality_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="face_encodings")


class ClassEnrollment(Base):
    """Bảng class_enrollments - Đăng ký lớp học"""
    __tablename__ = "class_enrollments"
    
    enrollment_id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("classes.class_id", ondelete="CASCADE"))
    student_id = Column(String(20), ForeignKey("students.student_id", ondelete="CASCADE"))
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)  # Thêm cột is_active
    
    # Relationships
    class_obj = relationship("Class", back_populates="enrollments")
    student = relationship("Student", back_populates="enrollments")


class CameraDevice(Base):
    """Bảng camera_devices - Thiết bị camera"""
    __tablename__ = "camera_devices"
    
    device_id = Column(Integer, primary_key=True, autoincrement=True)
    device_name = Column(String(100), nullable=False)
    device_code = Column(String(50), unique=True, nullable=False)
    stream_url = Column(String(255), nullable=False)
    location = Column(String(200))
    room = Column(String(50))
    is_active = Column(Boolean, default=True)
    last_heartbeat = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class RecognitionLog(Base):
    """Bảng recognition_logs - Log nhận diện"""
    __tablename__ = "recognition_logs"
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(20), ForeignKey("students.student_id"))
    device_id = Column(Integer, ForeignKey("camera_devices.device_id"))
    confidence_score = Column(Float)
    photo_path = Column(String(255))
    recognized_at = Column(DateTime, default=datetime.utcnow)
    is_successful = Column(Boolean, default=True)


class AttendanceLog(Base):
    """Bảng attendance_logs - Lịch sử thay đổi điểm danh"""
    __tablename__ = "attendance_logs"
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    attendance_id = Column(Integer, ForeignKey("attendance.attendance_id"))
    changed_by = Column(Integer, ForeignKey("users.user_id"))
    old_status = Column(String(20))
    new_status = Column(String(20))
    reason = Column(Text)
    changed_at = Column(DateTime, default=datetime.utcnow)
