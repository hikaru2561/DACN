"""
Application Constants
"""
from pathlib import Path

# Application info
APP_NAME = "Attendance Management System"
APP_VERSION = "1.0.0"

# Paths
APP_ROOT = Path(__file__).parent.parent.parent
DATASET_ROOT = APP_ROOT.parent.parent / "dataset"
DATASET_PROCESSED = DATASET_ROOT / "processed"
EMBEDDINGS_FILE = DATASET_ROOT / "face_embeddings.pkl"

# API
API_BASE_URL = "http://localhost:8000"

# Window sizes
WINDOW_SIZES = {
    "main": "1000x700",
    "management": "1400x800",
    "attendance": "1400x800",
}
