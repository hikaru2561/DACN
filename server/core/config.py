"""
Configuration settings for Face Recognition Attendance System
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:Nguyenquang%402561@localhost:5432/face_attendance"
    
    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379"
    
    # Face Recognition
    FACE_MODEL_NAME: str = "buffalo_l"  # InsightFace model
    FACE_DETECTION_THRESHOLD: float = 0.6
    FACE_RECOGNITION_THRESHOLD: float = 0.4
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload
    MAX_FILE_SIZE: int = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png"}
    UPLOAD_FOLDER: str = "uploads"
    
    # ESP32 Integration
    ESP32_CAM_IP: str = "192.168.219.176"
    ESP32_CAM_PORT: int = 80
    
    # Performance
    MAX_WORKERS: int = 4
    CACHE_TTL: int = 3600  # 1 hour
    
    # Web Interface
    WEB_HOST: str = "0.0.0.0"
    WEB_PORT: int = 8501
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Create directories
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(f"{settings.UPLOAD_FOLDER}/faces", exist_ok=True)
os.makedirs(f"{settings.UPLOAD_FOLDER}/attendance", exist_ok=True)
