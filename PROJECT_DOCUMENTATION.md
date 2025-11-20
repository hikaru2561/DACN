# 📘 HỆ THỐNG ĐIỂM DANH NHẬN DẠNG KHUÔN MẶT
**Face Recognition Attendance System - HUTECH DACN Project**

*Phiên bản 2.0 - Professional Architecture (Refactored 21/11/2025)*

---

## 📑 MỤC LỤC

1. [Tổng Quan](#1-tổng-quan)
2. [Kiến Trúc Hệ Thống](#2-kiến-trúc-hệ-thống)
3. [Cấu Trúc Dự Án](#3-cấu-trúc-dự-án)
4. [Công Nghệ & Model AI](#4-công-nghệ--model-ai)
5. [Hướng Dẫn Sử Dụng](#5-hướng-dẫn-sử-dụng)
6. [API Documentation](#6-api-documentation)
7. [Triển Khai & Bảo Trì](#7-triển-khai--bảo-trì)

---

## 1. 🎯 TỔNG QUAN

### Giới thiệu
Hệ thống điểm danh tự động sử dụng công nghệ nhận dạng khuôn mặt (Face Recognition) với camera ESP32-CAM, áp dụng Deep Learning (InsightFace) để nhận diện sinh viên trong thời gian thực.

### Tính năng chính
- ✅ **Điểm danh tự động** qua camera ESP32-CAM
- ✅ **Quản lý toàn diện**: Sinh viên, Giảng viên, Môn học, Lớp học, Buổi học
- ✅ **Báo cáo & Thống kê**: Lịch sử điểm danh, tỷ lệ chuyên cần
- ✅ **Quản lý Camera**: Multi-camera support
- ✅ **Quality Check**: Kiểm tra chất lượng ảnh (độ sáng, sắc nét, góc mặt)
- ✅ **Modular Architecture**: Dễ bảo trì và mở rộng

### Thông số kỹ thuật
- **Độ chính xác nhận dạng**: ~99.8% (LFW benchmark)
- **Tốc độ nhận dạng**: ~10-20ms/face (CPU)
- **Ngưỡng nhận dạng**: 0.50 (Cosine Similarity)
- **Số ảnh training**: 20 ảnh/sinh viên
- **Camera Resolution**: **XGA 1024x768** (optimized)
- **JPEG Quality**: 12-15 (balanced quality/size)
- **Frame Rate**: ~40-100 FPS (adaptive)
- **WiFi**: 2.4GHz (sleep disabled for low latency)

### ESP32-CAM Hardware Specs
- **Module**: ESP32-CAM AI-Thinker
- **Camera Sensor**: OV2640
- **Resolution**: XGA 1024x768 pixels
- **Frame Buffers**: 2 (PSRAM)
- **Grab Mode**: CAMERA_GRAB_LATEST (always newest frame)
- **WiFi Mode**: No sleep (max performance)
- **Stream Protocol**: MJPEG over HTTP

### Camera Quality Optimizations
```cpp
Brightness: +1        // Enhanced lighting
Contrast: +1          // Better detail
Sharpness: +2 (MAX)   // Maximum sharpness
AGC Gain: 3           // Ultra low noise
Auto White Balance: ON
Auto Exposure: ON
Lens Correction: ON
Bad Pixel Correction: ON
```

---

## 2. 🏗️ KIẾN TRÚC HỆ THỐNG

### Mô hình 3-tier

```
┌─────────────────────────────────────────────┐
│         ESP32-CAM (Hardware Layer)          │
│  • Camera Module                            │
│  • WiFi Streaming (MJPEG)                   │
│  • HTTP Server                              │
└──────────────────┬──────────────────────────┘
                   │ Video Stream
┌──────────────────▼──────────────────────────┐
│      Desktop App (Application Layer)        │
│  • Python + Tkinter GUI                     │
│  • Face Detection (MediaPipe)               │
│  • Face Recognition (InsightFace)           │
│  • API Client                               │
└──────────────────┬──────────────────────────┘
                   │ REST API
┌──────────────────▼──────────────────────────┐
│       Backend (API & Data Layer)            │
│  • FastAPI Server                           │
│  • PostgreSQL Database                      │
│  • Business Logic                           │
└─────────────────────────────────────────────┘
```

### Tech Stack

**Backend:**
- FastAPI (Web Framework)
- PostgreSQL (Database)
- SQLAlchemy (ORM)
- Pydantic (Validation)
- Uvicorn (ASGI Server)

**Desktop:**
- Python 3.8+
- Tkinter (GUI)
- InsightFace (Face Recognition)
- MediaPipe (Face Detection)
- OpenCV (Image Processing)
- Pillow (Image Handling)

**Hardware:**
- ESP32-CAM AI-Thinker
- OV2640 Camera Sensor

---

## 3. 📂 CẤU TRÚC DỰ ÁN

### Tổng quan

```
D:\HUTECH\DACN\
├── attendance_system/
│   ├── backend/              # Backend API Server
│   │   ├── app/
│   │   │   ├── api/          # API Routes (modular)
│   │   │   ├── core/         # Config, Database
│   │   │   ├── models/       # SQLAlchemy Models
│   │   │   ├── schemas/      # Pydantic Schemas
│   │   │   └── main.py       # Entry Point
│   │   ├── .env              # Environment Variables
│   │   └── requirements.txt
│   │
│   ├── desktop/              # Desktop Application
│   │   ├── app/
│   │   │   ├── ui/           # UI Components
│   │   │   ├── core/         # API Client, Config
│   │   │   ├── modules/      # Feature Modules
│   │   │   └── main.py       # Entry Point
│   │   └── requirements.txt
│   │
│   └── database/             # Database Scripts
│       └── schema.sql
│
├── dataset/                  # Training Data
│   ├── processed/            # Student Photos
│   └── face_embeddings.pkl   # AI Model Data
│
├── esp32-camera/             # ESP32 Firmware
└── docs/                     # Documentation
```

### Backend Structure (Modular)

```
backend/app/
├── api/                      # API Endpoints
│   ├── students.py
│   ├── teachers.py
│   ├── subjects.py
│   ├── classes.py
│   ├── sessions.py
│   ├── attendance.py
│   ├── cameras.py
│   ├── reports.py
│   └── __init__.py
│
├── core/                     # Core Utilities
│   ├── config.py             # Settings (Pydantic)
│   ├── database.py           # DB Connection
│   └── __init__.py
│
├── models/                   # Database Models
│   ├── user.py
│   ├── student.py
│   ├── teacher.py
│   ├── subject.py
│   ├── class_.py
│   ├── session.py
│   ├── attendance.py
│   ├── camera.py
│   └── __init__.py
│
├── schemas/                  # API Schemas
│   ├── common.py
│   ├── student.py
│   ├── teacher.py
│   ├── subject.py
│   ├── class_.py
│   ├── session.py
│   ├── attendance.py
│   ├── camera.py
│   ├── stats.py
│   └── __init__.py
│
└── main.py                   # Application Entry
```

### Desktop Structure (Modular)

```
desktop/app/
├── ui/                       # UI Layer
│   ├── login_window.py
│   └── dashboard_window.py
│
├── core/                     # Core Components
│   ├── api_client.py         # API Communication
│   ├── config.py             # Application Config
│   ├── colors.py             # UI Colors
│   └── constants.py
│
├── modules/                  # Feature Modules
│   ├── student/
│   │   └── student_window.py
│   ├── teacher/
│   │   └── teacher_window.py
│   ├── subject/
│   │   └── subject_window.py
│   ├── class_/
│   │   └── class_window.py
│   ├── session/
│   │   └── session_window.py
│   ├── attendance/
│   │   ├── session_selection.py
│   │   ├── live_attendance.py
│   │   ├── history.py
│   │   └── recognition.py
│   ├── camera/
│   │   ├── camera_window.py
│   │   └── capture.py
│   └── report/
│       └── report_window.py
│
└── main.py                   # Application Entry
```

---

## 4. 🤖 CÔNG NGHỆ & MODEL AI

### InsightFace - Buffalo_L Model

**Thông tin:**
- **Model**: `buffalo_l` (@ ~/.insightface/models/buffalo_l/)
- **Kích thước**: ~325 MB
- **Components**:
  - `w600k_r50.onnx` (166 MB): Face Recognition (ArcFace ResNet-50)
  - `det_10g.onnx` (16 MB): Face Detection (RetinaFace)
  - `1k3d68.onnx` (137 MB): 3D Face Alignment
  - `genderage.onnx` (1.2 MB): Gender & Age Detection

**Cấu hình:**
```python
FACE_RECOGNITION_CONFIG = {
    "model_name": "buffalo_l",
    "det_size": (640, 640),
    "similarity_threshold": 0.50,
    "providers": ['CPUExecutionProvider']
}
```

### Pipeline Nhận dạng

```
1. Capture Image (ESP32-CAM)
   ↓
2. Face Detection (RetinaFace/MediaPipe)
   ↓
3. Face Alignment (3D Landmarks)
   ↓
4. Feature Extraction (ArcFace → 512D Vector)
   ↓
5. Cosine Similarity Matching
   ↓
6. Recognition Decision (Threshold > 0.50)
```

### Quality Check Pipeline

```python
Quality Score = (
    Brightness * 0.25 +
    Sharpness * 0.40 +
    Size * 0.20 +
    Contrast * 0.15
)

Minimum Score: 65/100
```

---

## 5. 🚀 HƯỚNG DẪN SỬ DỤNG

### Cài đặt & Chạy Backend

```bash
# Di chuyển vào thư mục backend
cd attendance_system/backend

# Cài đặt dependencies
pip install -r requirements.txt

# Cấu hình database trong .env
DATABASE_URL=postgresql://user:pass@localhost:5432/attendance_db

# Chạy server
python -m app.main
# hoặc
cd app && python main.py

# Truy cập Swagger UI
http://localhost:8000/docs
```

### Cài đặt & Chạy Desktop

```bash
# Di chuyển vào thư mục desktop
cd attendance_system/desktop

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy ứng dụng
python -m app.main
# hoặc
cd app && python main.py
```

### Workflow Sử Dụng

**1. Setup Ban Đầu:**
- Chạy Backend server
- Tạo database và chạy schema.sql
- Cấu hình ESP32-CAM (xem phần ESP32)

**2. Quản Lý Dữ Liệu:**
- Đăng nhập Desktop App (admin/admin123)
- Thêm Giảng viên, Môn học, Lớp học
- Thêm Sinh viên và gán vào lớp

**3. Thu Thập Dữ Liệu:**
- Vào module "Quản lý Sinh viên"
- Chọn sinh viên → Click "📷 Lấy ảnh"
- Hệ thống tự động chụp 20 ảnh chất lượng cao
- Click "Training Data" để tạo embeddings

**4. Điểm Danh:**
- Vào module "Điểm danh Lớp học"
- Chọn buổi học
- Hệ thống tự động nhận diện và ghi nhận

**5. Báo Cáo:**
- Vào module "Lịch sử Điểm danh"
- Xem thống kê, xuất báo cáo

### ESP32-CAM Setup Guide

**Hardware Requirements:**
- ESP32-CAM AI-Thinker module
- USB-to-TTL programmer (FTDI/CH340)
- Jumper wires

**Firmware Upload:**
```bash
# 1. Open Arduino IDE
# 2. Install ESP32 board support
# 3. Select board: "AI Thinker ESP32-CAM"
# 4. Open: esp32-camera/CameraWebServer_Optimized.ino
```

**WiFi Configuration:**
```cpp
// Edit in firmware (lines 53-54):
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_PASSWORD";
```

**Camera Settings (Pre-configured):**
```cpp
Resolution: XGA 1024x768
JPEG Quality: 12-15
Frame Buffers: 2
FPS Target: 40-100
Optimizations: All enabled (see firmware)
```

**Wiring for Upload:**
```
ESP32-CAM  →  FTDI Adapter
---------     -------------
5V         →  5V (VCC)
GND        →  GND
U0T (TX)   →  RX
U0R (RX)   →  TX
IO0        →  GND (for upload mode)
```

**Upload Steps:**
1. Connect wiring as above (IO0 to GND)
2. Press ESP32-CAM reset button
3. Upload firmware via Arduino IDE
4. Remove IO0-GND connection
5. Press reset button
6. Check Serial Monitor for IP address

**URLs sau khi upload:**
- Web Interface: `http://[ESP32_IP]/`
- Stream: `http://[ESP32_IP]/stream`
- Capture: `http://[ESP32_IP]/capture`
- Status: `http://[ESP32_IP]/status`

**Desktop App Configuration:**
```python
# Update in desktop/app/core/config.py:
CAMERA_CONFIG = {
    "stream_url": "http://192.168.x.x/stream",  # Your ESP32 IP
    ...
}
```

**Troubleshooting:**
- **Camera not init**: Check wiring, flash mode
- **Brown-out reset**: Use external 5V power (>2A)
- **WiFi fails**: Check SSID/password, signal strength
- **Low FPS**: Reduce JPEG quality or resolution
- **Stream lag**: Enable "WiFi sleep disabled" in firmware



---

## 6. 🔌 API DOCUMENTATION

### Endpoints

**Students API** (`/api/students`)
- `GET /` - Lấy danh sách sinh viên
- `GET /{id}` - Lấy thông tin sinh viên
- `POST /` - Tạo sinh viên mới
- `PUT /{id}` - Cập nhật sinh viên
- `DELETE /{id}` - Xóa sinh viên

**Similar structure for:**
- `/api/teachers` - Giảng viên
- `/api/subjects` - Môn học
- `/api/classes` - Lớp học
- `/api/sessions` - Buổi học
- `/api/attendance` - Điểm danh
- `/api/cameras` - Camera
- `/api/reports` - Báo cáo

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 7. 🛠️ TRIỂN KHAI & BẢO TRÌ

### Production Checklist

**Backend:**
- [ ] Configure production DATABASE_URL
- [ ] Set up environment variables (.env)
- [ ] Enable HTTPS (SSL certificate)
- [ ] Add JWT authentication
- [ ] Set up logging and monitoring
- [ ] Configure CORS properly
- [ ] Add rate limiting
- [ ] Database backup strategy

**Desktop:**
- [ ] Build executable (PyInstaller)
- [ ] Package dependencies
- [ ] Create installer
- [ ] Add auto-update mechanism
- [ ] Error logging to file
- [ ] User manual documentation

**ESP32-CAM:**
- [ ] Configure static IP
- [ ] Set up authentication
- [ ] Firmware version management
- [ ] Fallback camera support

### Bảo Trì Thường Xuyên

**Hàng tuần:**
- Backup database (attendance records)
- Check log files for errors
- Monitor API response times

**Hàng tháng:**
- Update dependencies (security patches)
- Clean up old logs
- Review and optimize slow queries
- Backup embeddings file

**Hàng quý:**
- Re-train models if needed
- Update documentation
- Performance optimization
- Security audit

### Troubleshooting

**Lỗi thường gặp:**

1. **Backend không khởi động:**
   - Check DATABASE_URL in .env
   - Verify PostgreSQL is running
   - Check port 8000 availability

2. **Desktop không kết nối API:**
   - Verify backend is running
   - Check API_CONFIG.base_url
   - Test with curl/Postman

3. **ESP32-CAM không stream:**
   - Check WiFi connection
   - Verify IP address
   - Test stream URL in browser
   - Check camera module connection

4. **Nhận dạng kém:**
   - Retrain with more photos
   - Check lighting conditions
   - Verify quality threshold
   - Update embeddings file

---

## 📊 THỐNG KÊ DỰ ÁN

**Lines of Code**: ~15,000+
**Files Created**: 50+
**Modules**: 9 feature modules
**API Endpoints**: 40+
**Database Tables**: 10
**Refactoring Status**: ✅ Complete

**Team:**
- Project Lead: [Your Name]
- Institution: HUTECH
- Year: 2025

---

**Cập nhật lần cuối**: 21/11/2025
**Phiên bản**: 2.0 (Professional Architecture)
**License**: Educational Project
