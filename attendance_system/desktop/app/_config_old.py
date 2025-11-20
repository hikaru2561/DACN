"""
Configuration File - Quản lý tập trung các cấu hình hệ thống
"""
import os

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "attendance_system",
    "user": "postgres",
    "password": "your_password"  # Thay đổi password của bạn
}

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
    "stream_url": "http://192.168.1.169/stream",
    
    # Backup camera URLs (nếu có nhiều camera)
    "backup_streams": [
        "http://192.168.1.170/stream",
        "http://192.168.1.171/stream",
    ],
    
    # Camera settings
    "resolution": (640, 480),
    "fps": 30,
    "buffer_size": 1024,
    
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
    "similarity_threshold": 0.50,  # Ngưỡng độ tương đồng (càng cao càng strict)
    "confidence_threshold": 0.6,   # Ngưỡng confidence score
    
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
    "late_threshold_minutes": 15,  # Đi muộn nếu > 15 phút
    "early_leave_threshold_minutes": 15,  # Về sớm nếu < 15 phút trước khi kết thúc
    
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
    "min_quality_score": 0.65,  # 🔥 GIẢM XUỐNG 55% để dễ chụp hơn (trước: 0.7)
    "min_face_size": 100,  # pixels
    
    # Photo storage
    "dataset_path": os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset", "processed"),
    "photo_format": "jpg",
    "photo_quality": 95,  # JPEG quality (1-100)
    
    # Capture delay
    "capture_delay_ms": 500,  # Delay giữa các lần chụp
}

# ============================================================================
# UI CONFIGURATION
# ============================================================================

UI_CONFIG = {
    # Color scheme
    "colors": {
        "primary": "#2C3E50",
        "secondary": "#34495E",
        "success": "#27AE60",
        "danger": "#E74C3C",
        "warning": "#F39C12",
        "info": "#3498DB",
        "light": "#ECF0F1",
        "dark": "#2C3E50",
        "white": "#FFFFFF",
        "text": "#2C3E50",
        "red": "#E74C3C",  # Màu đỏ cho header điểm danh
        
        # Buttons
        "btn_save": "#3498DB",
        "btn_edit": "#F39C12",
        "btn_delete": "#E74C3C",
        "btn_new": "#27AE60",
        "btn_cancel": "#95A5A6",
        "btn_capture": "#5DADE2",
        "btn_training": "#16A085",
        "btn_students": "#9B59B6",
    },
    
    # Window sizes
    "main_window_size": "1024x768",
    "student_window_size": "1600x900",
    "attendance_window_size": "1400x800",
    
    # Fonts
    "font_family": "Segoe UI",
    "font_sizes": {
        "title": 20,
        "header": 16,
        "normal": 11,
        "small": 9,
    }
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING_CONFIG = {
    "enabled": True,
    "log_file": "attendance_system.log",
    "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "max_file_size": 10 * 1024 * 1024,  # 10 MB
    "backup_count": 5,
}

# ============================================================================
# SYSTEM PATHS
# ============================================================================

# Base directory của project chính (D:\HUTECH\DACN)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Base directory của attendance_system
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

PATHS = {
    "project_root": PROJECT_ROOT,  # D:\HUTECH\DACN
    "base_dir": BASE_DIR,  # D:\HUTECH\DACN\attendance_system
    "desktop_dir": os.path.join(BASE_DIR, "desktop"),
    "backend_dir": os.path.join(BASE_DIR, "backend"),
    
    # Dataset nằm ở project root, không phải trong attendance_system
    "dataset_dir": os.path.join(PROJECT_ROOT, "dataset"),
    "processed_dir": os.path.join(PROJECT_ROOT, "dataset", "processed"),
    
    "models_dir": os.path.join(BASE_DIR, "models"),
    "logs_dir": os.path.join(BASE_DIR, "logs"),
    "temp_dir": os.path.join(BASE_DIR, "temp"),
}

# Create directories if not exist
for path in PATHS.values():
    if isinstance(path, str):
        os.makedirs(path, exist_ok=True)

# ============================================================================
# DEVELOPMENT / PRODUCTION MODE
# ============================================================================

ENVIRONMENT = "development"  # "development" hoặc "production"

DEBUG = ENVIRONMENT == "development"

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
        return os.path.join(PATHS["processed_dir"], student_id)
    return PATHS["processed_dir"]

def get_embeddings_path():
    """Lấy đường dẫn file embeddings"""
    # File embeddings nằm ở D:\HUTECH\DACN\dataset\face_embeddings.pkl
    return os.path.join(PATHS["dataset_dir"], FACE_RECOGNITION_CONFIG["embeddings_file"])

def get_api_url(endpoint: str = ""):
    """Lấy URL đầy đủ cho API endpoint"""
    base = API_CONFIG["base_url"]
    if endpoint:
        return f"{base}/{endpoint.lstrip('/')}"
    return base

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Kiểm tra tính hợp lệ của config"""
    errors = []
    
    # Check camera URL
    if not CAMERA_CONFIG["stream_url"]:
        errors.append("Camera stream URL is not configured")
    
    # Check dataset path exists
    if not os.path.exists(PATHS["dataset_dir"]):
        errors.append(f"Dataset directory not found: {PATHS['dataset_dir']}")
    
    # Check API URL
    if not API_CONFIG["base_url"]:
        errors.append("API base URL is not configured")
    
    if errors:
        print("⚠️ Configuration Warnings:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True

# ============================================================================
# AUTO-VALIDATE ON IMPORT
# ============================================================================

if __name__ != "__main__":
    validate_config()

# ============================================================================
# CONFIG EXPORT
# ============================================================================

__all__ = [
    'DATABASE_CONFIG',
    'API_CONFIG',
    'CAMERA_CONFIG',
    'FACE_RECOGNITION_CONFIG',
    'ATTENDANCE_CONFIG',
    'CAPTURE_CONFIG',
    'UI_CONFIG',
    'LOGGING_CONFIG',
    'PATHS',
    'ENVIRONMENT',
    'DEBUG',
    'get_camera_url',
    'set_camera_url',
    'get_dataset_path',
    'get_embeddings_path',
    'get_api_url',
    'validate_config',
]
