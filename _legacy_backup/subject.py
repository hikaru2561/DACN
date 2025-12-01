from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

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
