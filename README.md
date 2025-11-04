# 📸 Face Recognition Dataset Collection System# 🎯 Face Recognition Attendance System



Hệ thống thu thập dataset khuôn mặt sử dụng ESP32-CAM và Python client chạy trên PC.## 📋 Tổng quan



> **Version 2.0** - Simplified Architecture  Hệ thống điểm danh bằng nhận dạng khuôn mặt sử dụng ESP32-CAM và Python FastAPI. Hệ thống cho phép đăng ký người dùng mới và điểm danh tự động thông qua nhận dạng khuôn mặt.

> **Date**: October 31, 2025  

> **Author**: HUTECH Student## 🏗️ Kiến trúc hệ thống



---```

DACN/

## 🎯 Tổng quan├── 📁 esp32-camera/          # ESP32-CAM code và tài liệu

│   ├── CameraWebServer/      # Arduino code cho ESP32-CAM

Hệ thống mới được thiết kế đơn giản hơn với kiến trúc:│   ├── README.md            # Hướng dẫn ESP32-CAM

- **ESP32-CAM**: Chỉ stream video qua WiFi│   └── libraries.txt        # Danh sách thư viện Arduino

- **Python Client**: Chạy trên PC, nhận stream, detect face, capture và lưu dataset├── 📁 server/               # Python backend

- **Dataset**: Lưu ảnh khuôn mặt để training model sau này│   ├── api/                 # FastAPI endpoints

│   ├── core/                # Cấu hình hệ thống

## 🏗️ Kiến trúc hệ thống│   ├── database/            # Database schema

│   ├── models/              # SQLAlchemy models

```│   ├── services/            # Business logic

┌─────────────────┐         WiFi Stream          ┌─────────────────┐│   ├── uploads/             # Thư mục lưu ảnh

│   ESP32-CAM     │────────────────────────────►  │  Python Client  ││   ├── web_app.py           # Streamlit web interface

│                 │      (MJPEG/HTTP)             │    (on PC)      ││   ├── run.py               # Script chạy hệ thống

│ • Camera        │                               │                 ││   └── requirements.txt     # Python dependencies

│ • Stream Server │                               │ • Face Detection│├── 📁 docs/                 # Tài liệu API

│ • /stream       │                               │ • Capture       │└── README.md               # File này

│ • /capture      │                               │ • Save Dataset  │```

└─────────────────┘                               └─────────────────┘

                                                           │## 🚀 Tính năng chính

                                                           ▼

                                                  ┌─────────────────┐### ESP32-CAM

                                                  │   Dataset       │- ✅ **Web interface** hiện đại với modal system

                                                  │                 │- ✅ **Camera streaming** real-time

                                                  │ • user_1/       │- ✅ **Image capture** với quality check

                                                  │ • user_2/       │- ✅ **CORS support** cho cross-origin requests

                                                  │ • ...           │- ✅ **Responsive design** cho mobile và desktop

                                                  └─────────────────┘

```### Python Backend

- ✅ **FastAPI** với async support

## 📁 Cấu trúc thư mục- ✅ **PostgreSQL** với pgvector extension

- ✅ **Face recognition** sử dụng OpenCV

```- ✅ **128D embeddings** cho face matching

DACN/- ✅ **RESTful API** với proper error handling

├── esp32-camera/                   # ESP32-CAM code

│   ├── CameraWebServer/### Web Interface

│   │   └── CameraWebServer_Simple.ino  # Stream server code (NEW)- ✅ **Streamlit** dashboard

│   ├── libraries.txt- ✅ **Real-time statistics**

│   └── README.md- ✅ **User management**

│- ✅ **Attendance logs**

├── client/                         # Python client app (NEW)

│   ├── camera_client.py           # Main application## 🛠️ Cài đặt và chạy

│   ├── users.json                 # User metadata

│   ├── requirements.txt### 1. **ESP32-CAM Setup**

│   ├── README.md

│   └── utils/#### Hardware Requirements:

│       ├── image_quality.py       # Image quality checker- ESP32-CAM module

│       └── __init__.py- MicroSD card (optional)

│- USB cable

├── dataset/                        # Face images dataset (NEW)- Breadboard và dây nối

│   ├── user_1/

│   │   ├── user_1_1.jpg#### Software Setup:

│   │   ├── user_1_2.jpg```bash

│   │   └── ... (10 images)# 1. Cài đặt Arduino IDE

│   ├── user_2/# 2. Cài đặt ESP32 board package

│   └── ...# 3. Cài đặt thư viện (xem esp32-camera/libraries.txt)

│

├── models/                         # For future training (NEW)# 4. Cấu hình WiFi trong CameraWebServer.ino:

│const char* ssid = "YOUR_WIFI_SSID";

├── docs/                           # Documentationconst char* password = "YOUR_WIFI_PASSWORD";

│   ├── ARCHITECTURE.md            # System architectureconst char* serverUrl = "http://YOUR_SERVER_IP:8000";

│   └── SETUP.md                   # Setup guide

│# 5. Upload code lên ESP32-CAM

├── old_system/                     # Backup of old system```

│   └── server/                    # Old FastAPI server

│### 2. **Python Backend Setup**

└── README.md                       # This file

``````bash

# 1. Cài đặt Python 3.8+

## 🚀 Hướng dẫn cài đặt# 2. Cài đặt PostgreSQL với pgvector extension

# 3. Clone repository

### 1️⃣ Cấu hình ESP32-CAMcd server



#### Yêu cầu:# 4. Tạo virtual environment

- ESP32-CAM AI-Thinkerpython -m venv venv

- Arduino IDE 2.0+source venv/bin/activate  # Linux/Mac

- ESP32 Board Package# hoặc

venv\Scripts\activate     # Windows

#### Các bước:

# 5. Cài đặt dependencies

1. **Cài đặt Arduino IDE** và ESP32 board package:pip install -r requirements.txt

   - File → Preferences

   - Additional Board Manager URLs: # 6. Cấu hình database

     ```# Sửa server/core/config.py với thông tin database của bạn

     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json

     ```# 7. Khởi tạo database

   - Tools → Board → Boards Manager → Search "ESP32" → Installpython reset_db.py



2. **Mở file ESP32-CAM code**:# 8. Chạy API server

   ```python run.py api

   esp32-camera/CameraWebServer/CameraWebServer_Simple.ino

   ```# 9. Chạy web interface (terminal khác)

streamlit run web_app.py --server.port 8501

3. **Cấu hình WiFi**:```

   ```cpp

   const char* ssid = "YOUR_WIFI_SSID";### 3. **Database Setup**

   const char* password = "YOUR_WIFI_PASSWORD";

   ``````sql

-- Tạo database

4. **Upload code**:CREATE DATABASE face_attendance;

   - Tools → Board → "AI Thinker ESP32-CAM"

   - Tools → Port → Select your port-- Cài đặt pgvector extension

   - UploadCREATE EXTENSION vector;



5. **Lấy IP address**:-- Chạy schema

   - Mở Serial Monitor (115200 baud)\i server/database/schema.sql

   - Reset ESP32-CAM```

   - Ghi lại IP address hiển thị

## 📱 Cách sử dụng

### 2️⃣ Cài đặt Python Client

### 1. **Truy cập ESP32-CAM**

#### Yêu cầu:- Mở browser: `http://[ESP32_IP]`

- Python 3.8+- Nhấn "Kết nối Server"

- OpenCV- Chờ camera stream khởi động

- NumPy

### 2. **Đăng ký người dùng mới**

#### Các bước:- Nhấn "Đăng ký"

- Chụp ảnh khuôn mặt

1. **Di chuyển vào thư mục client**:- Nhập thông tin: Họ tên, Mã sinh viên

   ```bash- Nhấn "Đăng ký"

   cd client

   ```### 3. **Điểm danh**

- Nhấn "Điểm danh"

2. **Cài đặt dependencies**:- Chụp ảnh khuôn mặt

   ```bash- Hệ thống tự động nhận diện và điểm danh

   pip install -r requirements.txt

   ```### 4. **Quản lý qua Web Interface**

- Truy cập: `http://localhost:8501`

3. **Cấu hình IP của ESP32-CAM**:- Xem dashboard, thống kê, logs

   - Mở file `camera_client.py`

   - Sửa dòng:## 🔧 API Endpoints

     ```python

     ESP32_CAM_IP = "192.168.x.x"  # IP của ESP32-CAM### Health Check

     ``````http

GET /api/v1/health

4. **Chạy application**:```

   ```bash

   python camera_client.py### User Management

   ``````http

POST /api/v1/register

## 📖 Hướng dẫn sử dụngGET /api/v1/users

```

### Menu chức năng:

### Attendance

``````http

📋 MENUPOST /api/v1/checkin

1. 📺 View camera streamGET /api/v1/attendance/logs

2. 👤 Register new user (capture dataset)GET /api/v1/attendance/stats

3. 📊 View registered users```

4. ⚙️  Settings

5. ❌ Exit### Face Detection

``````http

POST /api/v1/detect-faces

### Đăng ký user mới:```



1. Chọn **option 2** từ menu## 📊 Database Schema

2. Nhập **Họ tên** và **Mã sinh viên**

3. Cửa sổ camera hiển thị:### Users Table

   - Video stream từ ESP32-CAM```sql

   - Bounding box quanh khuôn mặt được detectCREATE TABLE users (

   - Trạng thái capture    id SERIAL PRIMARY KEY,

4. Nhấn phím **'c'** để bắt đầu capture    name VARCHAR(100) NOT NULL,

5. Hệ thống tự động chụp **10 ảnh liên tục** (delay 0.5s)    student_code VARCHAR(20) UNIQUE NOT NULL,

6. Ảnh được lưu vào: `dataset/user_X/`    department VARCHAR(100),

7. Thông tin user lưu vào `users.json`    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### Phím tắt:);

```

- **'c'**: Bắt đầu capture (trong chế độ register)

- **'q'**: Thoát/Hủy### Face Embeddings Table

```sql

## 📊 Cấu trúc dữ liệuCREATE TABLE face_embeddings (

    id SERIAL PRIMARY KEY,

### Dataset structure:    user_id INTEGER REFERENCES users(id),

```    embedding VECTOR(128) NOT NULL,

dataset/    confidence FLOAT,

├── user_1/    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

│   ├── user_1_1.jpg    # Ảnh cropped khuôn mặt);

│   ├── user_1_2.jpg```

│   └── ... (10 ảnh)

└── user_2/### Attendance Logs Table

    └── ...```sql

```CREATE TABLE attendance_logs (

    id SERIAL PRIMARY KEY,

### Users metadata (users.json):    user_id INTEGER REFERENCES users(id),

```json    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

{    confidence FLOAT,

  "users": [    device_id VARCHAR(50)

    {);

      "user_id": 1,```

      "name": "Nguyễn Văn A",

      "student_code": "2021600001",## 🎨 Giao diện

      "folder_path": "dataset/user_1",

      "created_date": "2025-10-31 15:30:00",### ESP32-CAM Web Interface

      "num_images": 10- **Modern UI** với gradient và glassmorphism

    }- **Modal system** cho đăng ký và điểm danh

  ],- **Real-time camera stream**

  "last_user_id": 1- **Quality check** cho ảnh chụp

}- **Responsive design**

```

### Streamlit Dashboard

## 🔧 Cấu hình hệ thống- **Statistics overview**

- **User management**

### ESP32-CAM (trong .ino file):- **Attendance logs**

- **Real-time updates**

```cpp

const char* ssid = "YOUR_WIFI";## 🔒 Bảo mật

const char* password = "YOUR_PASSWORD";

- **CORS headers** cho cross-origin requests

// Camera quality- **Input validation** với Pydantic

config.frame_size = FRAMESIZE_VGA;     // 640x480- **SQL injection protection** với SQLAlchemy

config.jpeg_quality = 10;              // 0-63 (lower = higher quality)- **Error handling** không tiết lộ thông tin nhạy cảm

```

## 📈 Performance

### Python Client (trong camera_client.py):

- **Async FastAPI** cho high performance

```python- **Vector similarity search** với pgvector

ESP32_CAM_IP = "192.168.x.x"          # IP của ESP32-CAM- **Image optimization** cho ESP32-CAM

NUM_IMAGES_PER_USER = 10              # Số ảnh mỗi user- **Database indexing** cho fast queries

CAPTURE_DELAY = 0.5                   # Delay giữa các ảnh (giây)

## 🐛 Troubleshooting

# Face detection

FACE_CASCADE.detectMultiScale(### ESP32-CAM Issues

    gray,- **Camera không hoạt động**: Kiểm tra kết nối hardware

    scaleFactor=1.1,- **WiFi không kết nối**: Kiểm tra SSID/password

    minNeighbors=5,- **Stream không hiển thị**: Kiểm tra CORS headers

    minSize=(50, 50)

)### Backend Issues

```- **Database connection**: Kiểm tra PostgreSQL service

- **Face detection**: Kiểm tra chất lượng ảnh

## 🎯 Tính năng- **API errors**: Xem server logs



### ✅ Đã hoàn thành:### Common Solutions

- [x] ESP32-CAM stream server1. **Restart services**: ESP32, API server, database

- [x] Python client kết nối stream2. **Check logs**: Console, server logs

- [x] Face detection real-time3. **Verify network**: IP addresses, ports

- [x] Capture 10 ảnh liên tục4. **Test endpoints**: curl, Postman

- [x] Lưu dataset tự động

- [x] User metadata management## 📚 Tài liệu tham khảo

- [x] Image quality check

- [x] Console menu interface- [ESP32-CAM Documentation](esp32-camera/README.md)

- [API Documentation](docs/api_docs.md)

### 🔜 Tính năng tương lai:- [Arduino Libraries](esp32-camera/libraries.txt)

- [ ] GUI với Tkinter/PyQt

- [ ] Face recognition (matching)## 👥 Đóng góp

- [ ] Training face recognition model

- [ ] Attendance logging1. Fork repository

- [ ] Export/Import users2. Tạo feature branch

- [ ] Multi-language support3. Commit changes

4. Push to branch

## 🐛 Xử lý lỗi thường gặp5. Tạo Pull Request



### 1. Cannot connect to ESP32-CAM:## 📄 License

```

❌ Connection error: Cannot connect to ESP32-CAM streamMIT License - Xem file LICENSE để biết thêm chi tiết.

```

**Giải pháp:**## 🏆 Credits

- Kiểm tra ESP32-CAM đã bật nguồn

- Kiểm tra IP address đúng- **ESP32-CAM**: Espressif Systems

- Kiểm tra PC và ESP32-CAM cùng mạng WiFi- **FastAPI**: Sebastián Ramírez

- Thử truy cập `http://ESP_IP/` trên browser- **OpenCV**: Intel Corporation

- **PostgreSQL**: PostgreSQL Global Development Group

### 2. No face detected:- **Streamlit**: Streamlit Inc.

```

⚠️  No face detected in image---

```

**Giải pháp:****Version**: 2.0  

- Đảm bảo ánh sáng đủ**Last Updated**: 2024  

- Đưa khuôn mặt vào giữa khung hình**Author**: [Tên sinh viên]
- Giữ khoảng cách 30-80cm từ camera
- Không che khuất khuôn mặt

### 3. WiFi connection failed:
```
❌ WiFi connection failed!
```
**Giải pháp:**
- Kiểm tra SSID và password đúng
- Kiểm tra WiFi 2.4GHz (ESP32 không hỗ trợ 5GHz)
- Kiểm tra signal strength

## 📚 Tài liệu tham khảo

- [ESP32-CAM Setup Guide](docs/SETUP.md)
- [System Architecture](docs/ARCHITECTURE.md)
- [Python Client README](client/README.md)
- [Arduino ESP32](https://github.com/espressif/arduino-esp32)
- [OpenCV Documentation](https://docs.opencv.org/)

## 🔐 Bảo mật

⚠️ **Lưu ý bảo mật:**
- Hệ thống hiện tại không có authentication
- Chỉ sử dụng trong mạng nội bộ tin cậy
- Không expose ESP32-CAM ra internet công cộng
- Dataset chứa thông tin cá nhân, cần bảo vệ

## 📈 Performance

### ESP32-CAM:
- **Resolution**: 640x480 (VGA)
- **Frame rate**: 10-20 FPS
- **Latency**: < 500ms
- **WiFi range**: ~30m (indoor)

### Python Client:
- **Face detection**: ~30ms per frame
- **Capture speed**: 10 images in ~5 seconds
- **Storage**: ~50KB per image

## 🤝 Đóng góp

Dự án học tập tại HUTECH. Mọi đóng góp và góp ý xin gửi về repository.

## 📄 License

MIT License - Dự án học tập HUTECH

---

## 🆚 So sánh với phiên bản cũ

| Feature | Old System | New System |
|---------|-----------|------------|
| **Architecture** | ESP32 + FastAPI + PostgreSQL | ESP32 + Python Client |
| **Processing** | Server-side | Client-side (PC) |
| **Database** | PostgreSQL + pgvector | JSON file |
| **Face Recognition** | 128D embeddings | Dataset only (train later) |
| **Deployment** | Complex (3 components) | Simple (2 components) |
| **Setup Time** | ~30 minutes | ~10 minutes |
| **Dependencies** | 15+ packages | 3 packages |
| **Use Case** | Production system | Dataset collection |

## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra logs trong Serial Monitor (ESP32-CAM)
2. Kiểm tra logs trong Console (Python client)
3. Đọc hướng dẫn trong thư mục `docs/`
4. Kiểm tra file `users.json` có hợp lệ

---

**🎓 HUTECH - Face Recognition Dataset Collection System**  
**Version 2.0 - October 31, 2025**
