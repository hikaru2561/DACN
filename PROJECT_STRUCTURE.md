# 📁 Cấu trúc Project - Attendance System

**Ngày cập nhật:** November 7, 2025  
**Trạng thái:** ✅ Đã dọn dẹp và tối ưu

---

## 🎯 Tổng quan

```
d:\HUTECH\DACN\
├── 📂 attendance_system/       ✅ Main Application
├── 📂 dataset/                 ✅ Face Images & Embeddings
├── 📂 client/                  📝 Standalone Capture Tools
├── 📂 esp32-camera/            📡 ESP32-CAM Firmware
├── 📂 archive/                 📦 Old Dataset (Backup)
└── 📄 Documentation Files
```

---

## 📂 Chi tiết cấu trúc

### 1. **attendance_system/** - Ứng dụng chính

```
attendance_system/
├── backend/                    # FastAPI Server
│   ├── main.py                 # Entry point
│   ├── database.py             # SQLAlchemy setup
│   ├── models.py               # ORM models
│   ├── schemas.py              # Pydantic schemas
│   ├── requirements.txt        # Python dependencies
│   └── database/
│       ├── schema.sql          # PostgreSQL schema
│       ├── insert_sample_data.sql
│       └── create_database.py
│
└── desktop/                    # Tkinter Desktop App
    ├── main.py                 # Entry point + Login + Dashboard
    ├── student_module_new.py   # Student CRUD + Camera
    ├── camera_capture_module.py # ESP32-CAM + MediaPipe
    ├── attendance_module.py    # InsightFace Recognition
    ├── build_embeddings.py     # Standalone training script
    ├── api_client.py           # REST API client
    ├── requirements.txt        # Python dependencies
    └── *.md                    # Module guides
```

**Ports:**
- Backend API: `http://localhost:8000`
- PostgreSQL: `localhost:5432/attendance_system`

**Key Features:**
- ✅ Login & Dashboard (8 modules)
- ✅ Student Management (CRUD + Camera + Training)
- ✅ Face Recognition (InsightFace + Real-time)
- ⏳ Teacher/Subject/Class Modules (TODO)
- ⏳ Session Management (TODO)
- ⏳ Reports & Statistics (TODO)

---

### 2. **dataset/** - Dữ liệu nhận dạng

```
dataset/
├── processed/                  # Face images
│   └── {student_id}/          # e.g., 2280602549/
│       ├── {id}_timestamp_q65.jpg  (20 photos)
│       └── ...
│
└── face_embeddings.pkl         # 512-dim embeddings
    Structure: {
        "2280602549": [emb1, emb2, ..., emb20],
        ...
    }
```

**Image Format:**
- **Type:** BGR crop (kích thước tự nhiên từ MediaPipe detection)
- **Content:** Ảnh GỐC - KHÔNG resize, KHÔNG preprocessing
- **Quality:** Score ≥ 65/100
- **Count:** 20 photos/person

**Training:**
- InsightFace tự động: detect → align → resize 112x112 → extract embedding
- Output: 512-dim vector (L2-normalized)

---

### 3. **client/** - Công cụ chụp ảnh standalone

```
client/
├── capture_faces_mediapipe.py  # MediaPipe capture tool
├── capture_faces_xga.py        # XGA capture tool
├── view_stream_xga.py          # Stream viewer
└── requirements.txt
```

**Mục đích:**
- Chụp ảnh độc lập (không cần Desktop App)
- Testing & debugging
- Đã tích hợp vào Desktop App → Client chỉ còn backup

**Note:** Các file debug/test đã được xóa.

---

### 4. **esp32-camera/** - Firmware cho ESP32-CAM

```
esp32-camera/
├── README.md
└── CameraWebServer/
    └── CameraWebServer_Optimized/
        └── CameraWebServer_Optimized.ino
```

**Config:**
- IP: `192.168.243.176`
- Stream: `http://192.168.243.176/stream`
- Format: MJPEG (640x480)
- Frame rate: 15-20 FPS

**Optimizations:**
- XGA mode with FLUSH
- PSRAM enabled
- Quality: 12 (0-63, lower = better)

---

### 5. **archive/** - Dataset backup cũ

```
archive/
├── Dataset.csv
├── Faces/
└── Original Images/
    ├── Akshay Kumar/
    ├── Alexandra Daddario/
    └── ... (31 persons)
```

**Mục đích:**
- Backup dataset ban đầu
- Reference cho testing
- **Không sử dụng trong production**

---

### 6. **📄 Documentation**

**Root level:**
- `README_NEW.md` - Hướng dẫn chính ✅
- `MODEL_ARCHITECTURE.md` - Kiến trúc model chi tiết ✅
- `STREAM_OPTIMIZATION_MODES.md` - ESP32-CAM optimization ✅
- `PROJECT_STRUCTURE.md` - File này ✅
- `cleanup_old_files.ps1` - Script dọn dẹp
- `db.sql` - Database schema

**Desktop app docs:**
- `QUICK_START.md` - Quick start guide
- `CAMERA_MODULE_GUIDE.md` - Camera module usage
- `ATTENDANCE_MODULE_GUIDE.md` - Attendance module usage

---

## 🔧 Dependencies

### Backend (FastAPI)
```
fastapi==0.115.6
uvicorn==0.32.1
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
pydantic==2.10.3
python-dotenv==1.0.1
```

### Desktop (Tkinter)
```
insightface==0.7.3
onnxruntime==1.16.3
opencv-python==4.8.1.78
mediapipe==0.10.21
numpy==1.26.4
protobuf==4.25.5
Pillow==10.2.0
requests==2.32.3
```

**Python Version:** 3.12.0

---

## 🗂️ Các file ĐÃ XÓA (dọn dẹp)

### ❌ Removed from `client/`
- ~~`compare_histeq_vs_clahe.py`~~ - Debug preprocessing
- ~~`debug_compare_preprocessing.py`~~ - Debug tool
- ~~`debug_preprocessing.py`~~ - Debug tool
- ~~`debug_test_similarity.py`~~ - Debug tool
- ~~`direct_face_comparison.py`~~ - Test tool
- ~~`face_recognition_system.py`~~ - Old version
- ~~`insightface_onnx.py`~~ - Test script
- ~~`test.py`~~ - Test script
- ~~`test_crop_accuracy.py`~~ - Test script
- ~~`view_preprocessing_result.py`~~ - Debug viewer
- ~~`live.py`~~ - Old stream viewer
- ~~`models/`~~ - InsightFace cache (auto-download)

### ❌ Removed from root
- ~~`face_recognition_v2/`~~ - Old version (replaced by attendance_system)
- ~~`cleanup_project.ps1`~~ - Old cleanup script
- ~~`README.md`~~ - Old readme (replaced by README_NEW.md)
- ~~`archive.zip`~~ - Redundant (folder exists)

### ❌ Python cache
- ~~`__pycache__/`~~ - Auto-generated (deleted)
- ~~`*.pyc`~~ - Bytecode files

---

## 📊 Kích thước Project

```
Total:              ~200 MB
├── attendance_system/  ~50 MB   (code + docs)
├── dataset/            ~2 MB    (per student, 20 photos)
├── archive/            ~140 MB  (backup dataset)
└── esp32-camera/       ~5 MB    (firmware)
```

**InsightFace models** (auto-download khi chạy lần đầu):
- `buffalo_l`: ~140 MB
- Location: `~/.insightface/models/`

---

## 🚀 Workflow

### 1. Setup Database
```bash
cd attendance_system/backend/database
python create_database.py
python run_schema.py
python run_sample_data.py
```

### 2. Start Backend (Optional)
```bash
cd attendance_system/backend
python main.py
# API: http://localhost:8000
```

### 3. Run Desktop App
```bash
cd attendance_system/desktop
python main.py
```

### 4. Capture Photos
```
Desktop App → Quản lý Sinh viên
→ Click student → 📷 Lấy ảnh sinh viên
→ Auto-capture 20 photos (Q ≥ 65)
```

### 5. Training
```
Desktop App → Quản lý Sinh viên
→ Click student → 🔄 Training Data
→ InsightFace extracts embeddings
→ Saved to dataset/face_embeddings.pkl
```

### 6. Recognition
```
Desktop App → Dashboard → Điểm danh
→ ▶️ Bắt đầu điểm danh
→ ESP32-CAM stream → Real-time recognition
```

---

## 🎯 Next Steps (TODO)

- [ ] Teacher/Subject/Class Modules
- [ ] Session Management
- [ ] API Integration for Attendance
- [ ] Reports & Statistics (Charts, Export Excel)
- [ ] Improve accuracy (collect more photos, fine-tune threshold)

---

## 📞 Support

**Issues:**
- Check console output for errors
- Verify ESP32-CAM connection (ping 192.168.243.176)
- Ensure PostgreSQL is running
- Check Python dependencies

**Performance:**
- Recognition: ~35-45ms/frame (CPU)
- Training: ~1-2s/student (20 photos)
- Stream FPS: 15-20 (ESP32-CAM)

---

**Last Updated:** November 7, 2025  
**Project Status:** ✅ Production Ready (Core features)
