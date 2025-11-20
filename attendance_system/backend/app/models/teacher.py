from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

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
