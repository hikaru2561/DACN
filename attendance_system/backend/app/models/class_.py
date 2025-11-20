from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

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


class ClassEnrollment(Base):
    """Bảng class_enrollments - Đăng ký lớp học"""
    __tablename__ = "class_enrollments"
    
    enrollment_id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("classes.class_id", ondelete="CASCADE"))
    student_id = Column(String(20), ForeignKey("students.student_id", ondelete="CASCADE"))
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    class_obj = relationship("Class", back_populates="enrollments")
    student = relationship("Student", back_populates="enrollments")
