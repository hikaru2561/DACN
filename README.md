# 🎓 HỆ THỐNG ĐIỂM DANH NHẬN DẠNG KHUÔN MẶT + KIỂM SOÁT RA VÀO

**Face Recognition Attendance & Access Control System**  
*HUTECH - Đồ Án Chuyên Ngành 2025*

---

## 📋 MỤC LỤC

1. [Tổng Quan](#-tổng-quan)
2. [Tính Năng](#-tính-năng)
3. [Kiến Trúc Hệ Thống](#️-kiến-trúc-hệ-thống)
4. [Công Nghệ Sử Dụng](#-công-nghệ-sử-dụng)
5. [Cài Đặt](#-cài-đặt)
6. [Sử Dụng](#-sử-dụng)
7. [Cấu Trúc Thư Mục](#-cấu-trúc-thư-mục)
8. [API Documentation](#-api-documentation)
9. [Thông Số Kỹ Thuật](#-thông-số-kỹ-thuật)

---

## 🎯 TỔNG QUAN

Hệ thống điểm danh tự động và kiểm soát ra vào sử dụng công nghệ nhận dạng khuôn mặt với camera ESP32-CAM, áp dụng Deep Learning (InsightFace) để nhận diện người dùng trong thời gian thực.

### Đặc điểm nổi bật

- ✅ **Liveness Detection**: Phát hiện người thật bằng nháy mắt (chống giả mạo)
- ✅ **Real-time Recognition**: Nhận diện tức thời với độ chính xác cao
- ✅ **Access Control**: Kiểm soát cửa ra vào tự động
- ✅ **Multi-user Management**: Quản lý sinh viên, giảng viên, lớp học, buổi học
- ✅ **Attendance Tracking**: Theo dõi điểm danh chi tiết
- ✅ **Video Streaming**: ESP32-CAM streaming với chất lượng cao
- ✅ **Modular Architecture**: Cấu trúc module hóa dễ bảo trì

---

## 🌟 TÍNH NĂNG

### 1. Kiểm Soát Ra Vào (Access Control)
- **Nhận diện khuôn mặt tức thời** (10-20ms/khuôn mặt)
- **Liveness Detection**: Yêu cầu nháy mắt 2 lần để xác thực người thật
- **Tự động mở khóa**: Kích hoạt relay khi xác thực thành công
- **OLED Display**: Hiển thị IP, tên người, trạng thái trên màn hình
- **Snapshot History**: Lưu ảnh lịch sử ra vào với timestamp
- **Access Logs**: Ghi nhận đầy đủ thông tin truy cập

### 2. Điểm Danh (Attendance)
- **Điểm danh tự động** qua camera
- **Quản lý buổi học**: Tạo và quản lý session điểm danh
- **Báo cáo**: Xuất báo cáo Excel/CSV chi tiết
- **Thống kê**: Tỷ lệ chuyên cần, xu hướng theo thời gian

### 3. Quản Lý Người Dùng
- **Chụp ảnh training**: Auto-capture với quality check (blur, face detection)
- **Face Embeddings**: Tạo và lưu vector đặc trưng khuôn mặt
- **Auto Training**: Tự động train model sau khi chụp ảnh
- **Brightness Adjustment**: Tự động điều chỉnh độ sáng (+30 units)

### 4. Dashboard & Monitoring
- **Live Video Stream**: Xem trực tiếp từ ESP32-CAM
- **Face Detection Overlay**: Vẽ bbox và hiển thị tên real-time
- **Access History**: Danh sách 15 lượt ra vào gần nhất
- **Statistics**: Thống kê trực quan

---

## 🏗️ KIẾN TRÚC HỆ THỐNG

### Kiến trúc 3-tier

```
┌───────────────────────────────────────────────────┐
│         ESP32-CAM (Hardware Layer)                │
│  • Camera Sensor: OV2640                          │
│  • MJPEG Streaming (Port 80)                      │
│  • Control API (Port 81)                          │
│  • OLED Display (128x64 SSD1306)                  │
│  • Relay Control (GPIO 12)                        │
└─────────────────┬─────────────────────────────────┘
                  │ HTTP Stream + REST API
┌─────────────────▼─────────────────────────────────┐
│      Desktop App (Application Layer)              │
│  • Python 3.12 + Tkinter GUI                      │
│  • InsightFace (Face Recognition)                 │
│  • MediaPipe (Face Detection + Face Mesh)         │
│  • Liveness Detection (Eye Blink)                 │
│  • API Client                                     │
└─────────────────┬─────────────────────────────────┘
                  │ REST API (FastAPI)
┌─────────────────▼─────────────────────────────────┐
│       Backend (API & Data Layer)                  │
│  • FastAPI Server (Port 8000)                     │
│  • PostgreSQL Database                            │
│  • SQLAlchemy ORM                                 │
│  • Pydantic Validation                            │
└───────────────────────────────────────────────────┘
```

### Luồng Xử Lý Chính

```
1. [Camera] → Stream MJPEG → [Desktop App]
2. [Desktop App] → Yêu cầu nháy mắt (Liveness)
3. [Desktop App] → Detect blink (MediaPipe Face Mesh)
4. [Desktop App] → Nhận diện khuôn mặt (InsightFace)
5. [Desktop App] → POST /api/control/open → [Backend]
6. [Backend] → GET http://ESP32_IP:81/open → [ESP32]
7. [ESP32] → Kích hoạt Relay → Mở cửa
8. [Desktop App] → POST /api/access-logs/ → [Backend]
9. [Backend] → Lưu log + snapshot path vào DB
```

---

## 🛠 CÔNG NGHỆ SỬ DỤNG

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Desktop Application
- **Python 3.12**
- **Tkinter** - GUI framework
- **InsightFace (Buffalo_L)** - Face recognition model
- **MediaPipe** - Face detection + Face Mesh
- **OpenCV** - Computer vision
- **PIL/Pillow** - Image processing
- **Requests** - HTTP client

### ESP32-CAM Firmware
- **Arduino IDE** / **PlatformIO**
- **ESP32 Arduino Core**
- **Adafruit SSD1306** - OLED library
- **Adafruit GFX** - Graphics library

### Hardware
- **ESP32-CAM** (AI-Thinker)
- **Camera**: OV2640 (2MP)
- **OLED**: SSD1306 128x64 I2C
- **Relay Module**: 5V
- **Flash LED**: GPIO 13

---

## 📦 CÀI ĐẶT

### 1. Yêu Cầu Hệ Thống

**Phần mềm:**
- Python 3.12+
- PostgreSQL 14+
- Arduino IDE 2.x / PlatformIO
- Git

**Phần cứng:**
- ESP32-CAM module
- OLED SSD1306 (128x64)
- Relay module 5V
- Nguồn 5V/2A

### 2. Clone Repository

```bash
git clone https://github.com/your-repo/DACN.git
cd DACN
```

### 3. Cài Đặt Backend

```bash
cd attendance_system/backend

# Tạo virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Cài đặt dependencies
pip install -r requirements.txt

# Cấu hình database
# Sửa file app/core/config.py với thông tin PostgreSQL

# Tạo database
python create_db.py

# Chạy server
cd app
python main.py
```

Backend sẽ chạy tại `http://localhost:8000`

### 4. Cài Đặt Desktop App

```bash
cd attendance_system/desktop

# Tạo virtual environment
python -m venv venv
.\venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Cấu hình
# Sửa file app/core/config.py:
# - API_BASE_URL = "http://localhost:8000/api"
# - stream_url = "http://ESP32_IP/stream"

# Chạy app
cd app
python main.py
```

### 5. Flash ESP32-CAM

1. Mở Arduino IDE
2. Cài đặt ESP32 Board:
   - File → Preferences → Additional Board URLs
   - Add: `https://dl.espressif.com/dl/package_esp32_index.json`
3. Tools → Board → ESP32 → AI Thinker ESP32-CAM
4. Cài thư viện:
   - Adafruit SSD1306
   - Adafruit GFX Library
5. Mở file `esp32-camera/CameraWebServer_AccessControl/CameraWebServer_AccessControl.ino`
6. Sửa WiFi SSID & Password
7. Upload (nhớ nối GPIO 0 với GND khi upload)

### 6. Kết Nối Phần Cứng

**ESP32-CAM Pinout:**

```
ESP32-CAM         → OLED SSD1306
GPIO 15 (SDA)     → SDA
GPIO 14 (SCL)     → SCL
3.3V              → VCC
GND               → GND

ESP32-CAM         → Relay Module
GPIO 12           → IN
5V                → VCC
GND               → GND

ESP32-CAM         → Flash LED
GPIO 13           → Anode (+)
GND               → Cathode (-)
```

**Lưu ý:** OLED chạy ở I2C clock 50kHz (giảm nhiễu)

---

## 🚀 SỬ DỤNG

### Khởi Động Hệ Thống

1. **Khởi động PostgreSQL**
2. **Chạy Backend:**
   ```bash
   cd attendance_system/backend/app
   python main.py
   ```
3. **Cấp điện cho ESP32-CAM** (tự động kết nối WiFi và hiện IP trên OLED)
4. **Chạy Desktop App:**
   ```bash
   cd attendance_system/desktop/app
   python main.py
   ```

### Quy Trình Sử Dụng

#### A. Thêm Người Dùng Mới

1. Mở Desktop App → **Quản lý người dùng**
2. Click **Thêm mới** → Nhập thông tin
3. Click **Chụp ảnh**
4. Hệ thống tự động chụp 20 ảnh (auto quality check)
5. Click **Train Model** → Hệ thống tự động train

#### B. Kiểm Soát Ra Vào

1. Dashboard hiển thị stream từ ESP32-CAM
2. Người dùng đứng trước camera
3. Hệ thống yêu cầu: **"NHAY MAT: 0/2"**
4. Nháy mắt 2 lần → **"✅ Liveness verified!"**
5. Hệ thống nhận diện khuôn mặt
6. Nếu match → Tự động:
   - Mở cửa (relay ON 5s)
   - Hiển thị tên trên OLED
   - Lưu snapshot vào `dataset/history/`
   - Ghi log vào database
7. Reset liveness → Lần sau phải nháy lại

#### C. Xem Lịch Sử

1. Dashboard → Phần **"Lịch sử ra vào"** (15 log gần nhất)
2. Hoặc click **"Lịch sử"** → Xem toàn bộ
3. Click vào log → Xem ảnh snapshot phóng to

---

## 📁 CẤU TRÚC THƯ MỤC

```
D:\HUTECH\DACN/
├── attendance_system/
│   ├── backend/                    # Backend API
│   │   ├── app/
│   │   │   ├── api/               # API endpoints
│   │   │   ├── core/              # Config, database
│   │   │   ├── models/            # SQLAlchemy models
│   │   │   ├── schemas/           # Pydantic schemas
│   │   │   └── main.py           # Entry point
│   │   ├── create_db.py          # Database setup
│   │   └── requirements.txt
│   │
│   └── desktop/                    # Desktop Application
│       ├── app/
│       │   ├── core/              # Config, API client, Face recognizer
│       │   ├── modules/
│       │   │   ├── dashboard/     # Main dashboard
│       │   │   ├── user_management/  # User CRUD + Capture
│       │   │   ├── history/       # Access history viewer
│       │   │   └── camera/        # Camera management
│       │   ├── ui/                # Login window
│       │   └── main.py           # Entry point
│       └── requirements.txt
│
├── esp32-camera/
│   └── CameraWebServer_AccessControl/
│       └── CameraWebServer_AccessControl.ino  # ESP32 firmware
│
├── dataset/
│   ├── raw/                       # Training photos (by user ID)
│   ├── history/                   # Access snapshots
│   └── face_embeddings.pkl       # Trained embeddings
│
└── README.md                      # This file
```

---

## 📡 API DOCUMENTATION

Backend API chạy tại: `http://localhost:8000`

### Endpoints Chính

#### Users
- `GET /api/users/` - Lấy danh sách người dùng
- `GET /api/users/{id}` - Lấy thông tin người dùng
- `POST /api/users/` - Tạo người dùng mới
- `PUT /api/users/{id}` - Cập nhật người dùng
- `DELETE /api/users/{id}` - Xóa người dùng

#### Access Logs
- `GET /api/access-logs/?limit=15` - Lấy lịch sử ra vào
- `POST /api/access-logs/` - Tạo log mới
- `DELETE /api/access-logs/{id}` - Xóa log

#### Control
- `POST /api/control/open` - Mở cửa (gọi ESP32)
- `GET /api/control/open` - Mở cửa (dạng GET)

#### Students, Teachers, Classes, Sessions, Subjects
- Tương tự pattern RESTful chuẩn

### ESP32 API

ESP32-CAM expose 2 HTTP servers:

**Stream Server (Port 80):**
- `GET /stream` - MJPEG video stream

**Control Server (Port 81):**
- `GET /open` - Mở khóa 5s
- `GET /control?var=face&val=Name` - Hiển thị tên lên OLED + mở khóa

---

## ⚙️ THÔNG SỐ KỸ THUẬT

### Face Recognition
- **Model**: InsightFace Buffalo_L (ArcFace)
- **Embedding Dimension**: 512
- **Similarity Metric**: Cosine Similarity
- **Threshold**: 0.7 (có thể điều chỉnh trong `config.py`)
- **Accuracy**: ~99.8% (LFW benchmark)
- **Speed**: 10-20ms/face (CPU Intel i5)

### Liveness Detection
- **Method**: Eye Aspect Ratio (EAR) tracking
- **Blinks Required**: 2
- **EAR Threshold**: 0.21
- **Face Mesh Model**: MediaPipe (468 landmarks)

### Camera Settings
- **Resolution**: SVGA 800x600 (ESP32) → 1024x768 (Desktop stream)
- **JPEG Quality**: 12 (balanced)
- **Frame Rate**: ~40-100 FPS (adaptive)
- **Brightness**: +1
- **Contrast**: +1
- **Sharpness**: +2 (max)
- **I2C Clock (OLED)**: 50kHz

### Dataset
- **Training Photos**: 20 ảnh/người
- **Photo Resolution**: 800x600
- **Blur Score Threshold**: >100 (Laplacian variance)
- **Face Detection**: Haar Cascade (fast)

---

## 🔧 CẤU HÌNH

### Desktop App (`desktop/app/core/config.py`)

```python
# API
API_BASE_URL = "http://localhost:8000/api"

# Camera
CAMERA_CONFIG = {
    "stream_url": "http://192.168.1.231/stream",  # Sửa theo IP ESP32
}

# Face Recognition
FACE_RECOGNITION_CONFIG = {
    "model_name": "buffalo_l",
    "similarity_threshold": 0.7,  # Điều chỉnh độ nhạy
    "confidence_threshold": 0.7,
}
```

### Backend (`backend/app/core/config.py`)

```python
# Database
DATABASE_URL = "postgresql://user:password@localhost/attendance_db"

# ESP32 IP (cho control API)
ESP32_IP = "192.168.1.231"  # Sửa theo IP thực tế
```

### ESP32 Firmware

```cpp
// WiFi
const char* ssid_1 = "K9";
const char* password_1 = "nk111111";
const char* ssid_2 = "TEAZONE_2.4G";
const char* password_2 = "88888888";

// GPIO
#define RELAY_PIN 12
#define FLASH_PIN 13
#define OLED_SDA 15
#define OLED_SCL 14
```

---

## 🐛 TROUBLESHOOTING

### Desktop App không kết nối được stream

1. Kiểm tra ESP32 đã kết nối WiFi chưa (xem OLED hoặc Serial Monitor)
2. Ping IP ESP32: `ping 192.168.1.231`
3. Mở browser test stream: `http://192.168.1.231/stream`
4. Sửa IP trong `config.py` nếu sai

### OLED bị pixelation/corruption

- **Nguyên nhân**: Nhiễu I2C hoặc nguồn không ổn định
- **Giải pháp**:
  - Dùng nguồn 5V/2A chất lượng tốt
  - Kiểm tra dây nối SDA/SCL (dây ngắn, chống nhiễu)
  - Code đã set I2C clock = 50kHz để giảm nhiễu
  - Khởi tạo Camera TRƯỚC OLED (tránh conflict)

### Liveness detection không hoạt động

- Kiểm tra `liveness_required = True` trong `dashboard_window.py`
- Đảm bảo ánh sáng đủ để MediaPipe detect landmarks
- Nháy mắt rõ ràng (đóng-mở nhanh)

### Nhận diện sai hoặc không nhận diện

- Tăng số ảnh training (>20 ảnh)
- Giảm `similarity_threshold` trong `config.py` (từ 0.7 → 0.6)
- Đảm bảo ảnh training đa dạng góc độ và ánh sáng
- Chạy lại training: Quản lý người dùng → Chọn user → Train Model

---

## 📝 CHANGELOG

### Version 2.0 (Hiện tại)
- ✅ Thêm Liveness Detection (blink detection)
- ✅ Tách UserManagement dùng chung stream với Dashboard
- ✅ Cải thiện capture window (brightness +30, face detection)
- ✅ Sửa lỗi thiếu `import os` trong dashboard
- ✅ Xóa logic `send_to_esp()` để tránh mở khóa sớm
- ✅ Tăng similarity threshold lên 0.7
- ✅ Fix lỗi 307 Redirect (thêm trailing slash)
- ✅ Fix lỗi 503 Service Unavailable (cập nhật ESP32_IP)
- ✅ Snapshot tự động lưu vào `dataset/history/`
- ✅ OLED hiển thị IP + tên + countdown

### Version 1.0 (Legacy)
- Hệ thống cơ bản với InsightFace
- Chưa có liveness detection

---

## 👥 CREDITS

**Phát triển bởi:** Nhóm DACN - HUTECH 2025

**Công nghệ chính:**
- InsightFace (Face Recognition)
- MediaPipe (Face Detection + Mesh)
- FastAPI (Backend)
- ESP32-CAM (Hardware)

---

## 📄 LICENSE

Educational Project - HUTECH University

---

## 🤝 CONTACT & SUPPORT

Nếu có vấn đề, hãy mở issue trên GitHub repository hoặc liên hệ qua email giảng viên hướng dẫn.

---

**Happy Coding! 🎉**
