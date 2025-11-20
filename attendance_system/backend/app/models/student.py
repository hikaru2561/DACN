"""
Student Model
TODO: Copy from _models_old.py and adapt
"""
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


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
    
    # TODO: Add relationships when other models are created
    # user = relationship("User", back_populates="student")
    # face_encodings = relationship("FaceEncoding", back_populates="student")
    # attendances = relationship("Attendance", back_populates="student")
    # enrollments = relationship("ClassEnrollment", back_populates="student")
