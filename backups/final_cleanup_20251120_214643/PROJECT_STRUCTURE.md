# Cấu trúc Project - Face Recognition Attendance System

## 📊 Phân tích cấu trúc hiện tại

### ✅ Cấu trúc tốt (GIỮ LẠI):
```
DACN/
├── README.md                           # Documentation chính
├── SYSTEM_PIPELINE.md                  # System flow documentation
├── .gitignore                          # Git configuration
│
├── attendance_system/                  # ⭐ Core application
│   ├── backend/                        # FastAPI Backend
│   │   ├── main.py                     # API Server
│   │   ├── models.py                   # SQLAlchemy Models
│   │   ├── schemas.py                  # Pydantic Schemas
│   │   ├── database.py                 # Database Config
│   │   ├── .env                        # Environment variables
│   │   └── requirements.txt
│   │
│   ├── desktop/                        # Tkinter Desktop App
│   │   ├── main.py                     # Main Entry Point
│   │   ├── config.py                   # App Configuration
│   │   ├── api_client.py               # Backend API Client
│   │   │
│   │   ├── student_module_new.py       # Student Management
│   │   ├── teacher_module.py           # Teacher Management
│   │   ├── subject_module.py           # Subject Management
│   │   ├── class_module.py             # Class Management
│   │   ├── session_module.py           # Session Management
│   │   ├── camera_management_module.py # Camera Management
│   │   ├── report_module.py            # Reports & Statistics
│   │   │
│   │   ├── attendance_session_module.py    # Session Selection
│   │   ├── attendance_live_module.py       # Live Attendance (Real-time)
│   │   ├── attendance_module.py            # Attendance Recognition
│   │   ├── attendance_history_module.py    # Attendance History
│   │   │
│   │   ├── camera_capture_module.py    # Face Capture Tool
│   │   ├── build_embeddings.py         # Training Tool
│   │   └── requirements.txt
│   │
│   ├── database/                       # Database Scripts
│   │   └── schema.sql                  # Database Schema
│   │
│   └── backup_unused_files/            # ⚠️ Backup old files
│
├── client/                             # 📷 ESP32 Camera Clients
│   ├── capture_faces_mediapipe.py      # Face capture with MediaPipe
│   ├── capture_faces_xga.py            # Face capture XGA resolution
│   ├── view_stream_xga.py              # Stream viewer
│   └── requirements.txt
│
├── esp32-camera/                       # 🔧 ESP32 Firmware
│   ├── CameraWebServer/                # Arduino sketch
│   └── README.md
│
└── dataset/                            # 📁 Face images dataset
    ├── raw/                            # Original captures
    └── processed/                      # Preprocessed faces
```

---

## ⚠️ VẤN ĐỀ CẤN GIẢI QUYẾT

### 1. Thư mục trùng lặp:
- **`attendance_system/dataset/`** (trống) - XÓA
- **`dataset/`** (root) - GIỮ LẠI

### 2. Thư mục tạm thời:
- **`attendance_system/temp/`** - XÓA nếu trống
- **`attendance_system/logs/`** - XÓA nếu trống
- **`attendance_system/models/`** - XÓA nếu trống

### 3. File README trùng:
- `/README.md` (root) - GIỮ
- `/attendance_system/README.md` - XÓA (hoặc merge)
- `/attendance_system/desktop/README.md` - XÓA (hoặc merge)
- `/attendance_system/backend/README.md` - GIỮ (backend-specific)

### 4. File backup:
- **`attendance_system/backup_unused_files/`** - CÓ THỂ XÓA (đã commit)

### 5. File MODEL_INFO.md:
- **`attendance_system/MODEL_INFO.md`** - DI CHUYỂN lên ROOT hoặc `/docs`

---

## 🎯 KHUYẾN NGHỊ CẤU TRÚC MỚI

```
DACN/
├── README.md                           # Main documentation
├── SYSTEM_PIPELINE.md                  # System architecture
├── MODEL_INFO.md                       # ⬆️ MOVED from attendance_system/
├── .gitignore
│
├── docs/                               # 📚 NEW: All documentation
│   ├── api/                            # API documentation
│   ├── setup/                          # Installation guides
│   └── user-guide/                     # User manuals
│
├── attendance_system/
│   ├── backend/
│   │   ├── app/                        # ⭐ NEW: Organize by feature
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   │
│   │   │   ├── models/                 # Database models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── student.py
│   │   │   │   ├── teacher.py
│   │   │   │   └── ...
│   │   │   │
│   │   │   ├── schemas/                # Pydantic schemas
│   │   │   │   ├── __init__.py
│   │   │   │   ├── student.py
│   │   │   │   └── ...
│   │   │   │
│   │   │   ├── api/                    # API Routes
│   │   │   │   ├── __init__.py
│   │   │   │   ├── students.py
│   │   │   │   ├── teachers.py
│   │   │   │   └── ...
│   │   │   │
│   │   │   └── core/                   # Core utilities
│   │   │       ├── database.py
│   │   │       └── security.py
│   │   │
│   │   ├── tests/                      # ⭐ NEW: Backend tests
│   │   ├── requirements.txt
│   │   └── .env.example                # ⭐ NEW: Env template
│   │
│   ├── desktop/
│   │   ├── app/                        # ⭐ NEW: Organize modules
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   │
│   │   │   ├── modules/                # UI Modules
│   │   │   │   ├── __init__.py
│   │   │   │   ├── student/
│   │   │   │   ├── teacher/
│   │   │   │   ├── class/
│   │   │   │   ├── session/
│   │   │   │   ├── attendance/
│   │   │   │   ├── camera/
│   │   │   │   └── report/
│   │   │   │
│   │   │   ├── utils/                  # Utilities
│   │   │   │   ├── __init__.py
│   │   │   │   ├── api_client.py
│   │   │   │   └── helpers.py
│   │   │   │
│   │   │   └── assets/                 # Images, icons
│   │   │
│   │   ├── tests/                      # ⭐ NEW: Desktop tests
│   │   └── requirements.txt
│   │
│   └── database/
│       ├── schema.sql
│       ├── migrations/                 # ⭐ NEW: Migration scripts
│       └── seeds/                      # ⭐ NEW: Sample data
│
├── client/                             # ESP32 Camera clients
│   ├── mediapipe/
│   │   ├── capture_faces.py
│   │   └── requirements.txt
│   ├── xga/
│   │   ├── capture_faces.py
│   │   ├── view_stream.py
│   │   └── requirements.txt
│   └── README.md
│
├── esp32-camera/                       # ESP32 Firmware
│   └── CameraWebServer/
│
├── dataset/                            # Face dataset
│   ├── raw/
│   ├── processed/
│   └── embeddings/                     # ⭐ NEW: Store embeddings
│
├── scripts/                            # ⭐ NEW: Utility scripts
│   ├── setup.sh / setup.ps1
│   ├── start_backend.sh
│   └── backup.sh
│
└── .vscode/                            # VSCode settings
```

---

## 🔧 HÀNH ĐỘNG ĐỀ XUẤT

### Bước 1: Dọn dẹp file không cần thiết

```powershell
# XÓA thư mục trống hoặc backup cũ
Remove-Item -Recurse -Force "attendance_system/dataset"
Remove-Item -Recurse -Force "attendance_system/temp"
Remove-Item -Recurse -Force "attendance_system/logs"
Remove-Item -Recurse -Force "attendance_system/models"
Remove-Item -Recurse -Force "attendance_system/backup_unused_files"

# XÓA README trùng
Remove-Item "attendance_system/README.md"
Remove-Item "attendance_system/desktop/README.md"
```

### Bước 2: Di chuyển file documentation

```powershell
# Tạo thư mục docs
New-Item -ItemType Directory -Path "docs"

# Di chuyển MODEL_INFO
Move-Item "attendance_system/MODEL_INFO.md" "docs/MODEL_INFO.md"
```

### Bước 3: (TÙY CHỌN) Tổ chức lại code theo feature

Nếu muốn cấu trúc chuyên nghiệp hơn, có thể:
- Chia `backend/main.py` thành nhiều file trong `api/`
- Chia `models.py` và `schemas.py` theo từng model
- Tổ chức desktop modules theo feature folders

---

## 📝 GHI CHÚ

### Ưu tiên:
1. **Ngay lập tức**: Dọn dẹp file/folder trùng lặp và backup cũ
2. **Ngắn hạn**: Tổ chức documentation và README
3. **Dài hạn**: Refactor code theo feature-based structure

### Lợi ích:
- ✅ Code clean hơn, dễ maintain
- ✅ Dễ onboard developer mới
- ✅ Tách biệt concerns rõ ràng
- ✅ Chuẩn bị tốt cho scaling

### Rủi ro:
- ⚠️ Refactor lớn có thể gây lỗi
- ⚠️ Cần test kỹ sau khi di chuyển file
- ⚠️ Phải update import paths
