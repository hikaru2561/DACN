from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base

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
