"""
Application Configuration
"""
import os
from pathlib import Path
from .colors import COLORS
from .constants import *

# ============================================================================
# PROJECT PATHS
# ============================================================================

# Base directory của project chính (D:\HUTECH\DACN)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
# Base directory của attendance_system
BASE_DIR = PROJECT_ROOT / "attendance_system"

PATHS = {
    "project_root": PROJECT_ROOT,  # D:\HUTECH\DACN
    "base_dir": BASE_DIR,  # D:\HUTECH\DACN\attendance_system
    "desktop_dir": BASE_DIR / "desktop",
    "backend_dir": BASE_DIR / "backend",
    
    # Dataset nằm ở project root
    "dataset_dir": PROJECT_ROOT / "dataset",
    "raw_dir": PROJECT_ROOT / "dataset" / "raw",
    "history_dir": PROJECT_ROOT / "dataset" / "history",
    
    "models_dir": BASE_DIR / "models",
    "logs_dir": BASE_DIR / "logs",
    "temp_dir": BASE_DIR / "temp",
}

# Create directories if not exist
for path_name, path in PATHS.items():
    if isinstance(path, Path):
        path.mkdir(parents=True, exist_ok=True)

# ============================================================================
# API CONFIGURATION
# ============================================================================

API_CONFIG = {
    "base_url": "http://localhost:8000",
    "timeout": 30,  # seconds
}

# ============================================================================
# CAMERA CONFIGURATION
# ============================================================================

CAMERA_CONFIG = {
    # ESP32-CAM Stream URL
    "stream_url": "http://192.168.1.121/stream",
    
    # Backup camera URLs (nếu có nhiều camera)
    "backup_streams": [
        "http://192.168.1.170/stream",
        "http://192.168.1.171/stream",
    ],
    
    # Camera settings
    "resolution": (1024, 768),  # XGA Resolution - Khớp với ESP32
    "fps": 30,
    "buffer_size": 2048,  # Tăng buffer cho XGA
    
    # Reconnect settings
    "max_retries": 3,
    "retry_delay": 2,  # seconds
}

# ============================================================================
# FACE RECOGNITION CONFIGURATION
# ============================================================================

FACE_RECOGNITION_CONFIG = {
    # InsightFace model
    "model_name": "buffalo_l",
    "model_path": None,  # None = auto download
    
    # Recognition thresholds
    "similarity_threshold": 0.7,  # Ngưỡng độ tương đồng
    "confidence_threshold": 0.7,   # Ngưỡng confidence score
    
    # Face detection settings
    "det_size": (640, 640),
    "det_thresh": 0.5,
    
    # Embeddings storage
    "embeddings_file": "face_embeddings.pkl",
    "embeddings_backup": "face_embeddings_backup.pkl",
}

# ============================================================================
# ATTENDANCE CONFIGURATION
# ============================================================================

ATTENDANCE_CONFIG = {
    # Auto-save settings
    "auto_save": True,
    "auto_save_interval": 60,  # seconds
    
    # Attendance rules
    "late_threshold_minutes": 15,
    "early_leave_threshold_minutes": 15,
    
    # Duplicate check
    "prevent_duplicate_minutes": 5,  # Không cho điểm danh lại trong 5 phút
}

# ============================================================================
# STUDENT PHOTO CAPTURE CONFIGURATION
# ============================================================================

CAPTURE_CONFIG = {
    # Số lượng ảnh cần chụp cho mỗi sinh viên
    "target_photos": 20,
    
    # MediaPipe quality thresholds
    "min_quality_score": 0.65,
    "min_face_size": 100,  # pixels
    
    # Photo storage
    "dataset_path": str(PATHS["raw_dir"]),
    "photo_format": "jpg",
    "photo_quality": 95,  # JPEG quality (1-100)
    
    # Capture delay
    "capture_delay_ms": 500,  # Delay giữa các lần chụp
}

# ============================================================================
# UI CONFIGURATION
# ============================================================================

UI_CONFIG = {
    "colors": COLORS,
    "fonts": {
        "default": ("Segoe UI", 10),
        "bold": ("Segoe UI", 10, "bold"),
        "header": ("Segoe UI", 14, "bold"),
        "title": ("Segoe UI", 18, "bold"),
    },
    "window_sizes": WINDOW_SIZES,
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_camera_url():
    """Lấy URL camera chính"""
    return CAMERA_CONFIG["stream_url"]

def set_camera_url(url: str):
    """Cập nhật URL camera chính"""
    CAMERA_CONFIG["stream_url"] = url

def get_dataset_path(student_id: str = None):
    """Lấy đường dẫn thư mục dataset"""
    if student_id:
        return str(PATHS["raw_dir"] / student_id)
    return str(PATHS["raw_dir"])

def get_embeddings_path():
    """Lấy đường dẫn file embeddings"""
    return str(PATHS["dataset_dir"] / FACE_RECOGNITION_CONFIG["embeddings_file"])

def get_api_url(endpoint: str = ""):
    """Lấy URL đầy đủ cho API endpoint"""
    base = API_CONFIG["base_url"]
    if endpoint:
        return f"{base}/{endpoint.lstrip('/')}"
    return base
