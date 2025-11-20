from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import BYTEA
from datetime import datetime
from app.core.database import Base

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
