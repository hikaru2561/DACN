# 🎯 Face Recognition Attendance System

## 📋 Tổng quan

Hệ thống điểm danh bằng nhận dạng khuôn mặt sử dụng ESP32-CAM và Python FastAPI. Hệ thống cho phép đăng ký người dùng mới và điểm danh tự động thông qua nhận dạng khuôn mặt.

## 🏗️ Kiến trúc hệ thống

```
DACN/
├── 📁 esp32-camera/          # ESP32-CAM code và tài liệu
│   ├── CameraWebServer/      # Arduino code cho ESP32-CAM
│   ├── README.md            # Hướng dẫn ESP32-CAM
│   └── libraries.txt        # Danh sách thư viện Arduino
├── 📁 server/               # Python backend
│   ├── api/                 # FastAPI endpoints
│   ├── core/                # Cấu hình hệ thống
│   ├── database/            # Database schema
│   ├── models/              # SQLAlchemy models
│   ├── services/            # Business logic
│   ├── uploads/             # Thư mục lưu ảnh
│   ├── web_app.py           # Streamlit web interface
│   ├── run.py               # Script chạy hệ thống
│   └── requirements.txt     # Python dependencies
├── 📁 docs/                 # Tài liệu API
└── README.md               # File này
```

## 🚀 Tính năng chính

### ESP32-CAM
- ✅ **Web interface** hiện đại với modal system
- ✅ **Camera streaming** real-time
- ✅ **Image capture** với quality check
- ✅ **CORS support** cho cross-origin requests
- ✅ **Responsive design** cho mobile và desktop

### Python Backend
- ✅ **FastAPI** với async support
- ✅ **PostgreSQL** với pgvector extension
- ✅ **Face recognition** sử dụng OpenCV
- ✅ **128D embeddings** cho face matching
- ✅ **RESTful API** với proper error handling

### Web Interface
- ✅ **Streamlit** dashboard
- ✅ **Real-time statistics**
- ✅ **User management**
- ✅ **Attendance logs**

## 🛠️ Cài đặt và chạy

### 1. **ESP32-CAM Setup**

#### Hardware Requirements:
- ESP32-CAM module
- MicroSD card (optional)
- USB cable
- Breadboard và dây nối

#### Software Setup:
```bash
# 1. Cài đặt Arduino IDE
# 2. Cài đặt ESP32 board package
# 3. Cài đặt thư viện (xem esp32-camera/libraries.txt)

# 4. Cấu hình WiFi trong CameraWebServer.ino:
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "http://YOUR_SERVER_IP:8000";

# 5. Upload code lên ESP32-CAM
```

### 2. **Python Backend Setup**

```bash
# 1. Cài đặt Python 3.8+
# 2. Cài đặt PostgreSQL với pgvector extension
# 3. Clone repository
cd server

# 4. Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows

# 5. Cài đặt dependencies
pip install -r requirements.txt

# 6. Cấu hình database
# Sửa server/core/config.py với thông tin database của bạn

# 7. Khởi tạo database
python reset_db.py

# 8. Chạy API server
python run.py api

# 9. Chạy web interface (terminal khác)
streamlit run web_app.py --server.port 8501
```

### 3. **Database Setup**

```sql
-- Tạo database
CREATE DATABASE face_attendance;

-- Cài đặt pgvector extension
CREATE EXTENSION vector;

-- Chạy schema
\i server/database/schema.sql
```

## 📱 Cách sử dụng

### 1. **Truy cập ESP32-CAM**
- Mở browser: `http://[ESP32_IP]`
- Nhấn "Kết nối Server"
- Chờ camera stream khởi động

### 2. **Đăng ký người dùng mới**
- Nhấn "Đăng ký"
- Chụp ảnh khuôn mặt
- Nhập thông tin: Họ tên, Mã sinh viên
- Nhấn "Đăng ký"

### 3. **Điểm danh**
- Nhấn "Điểm danh"
- Chụp ảnh khuôn mặt
- Hệ thống tự động nhận diện và điểm danh

### 4. **Quản lý qua Web Interface**
- Truy cập: `http://localhost:8501`
- Xem dashboard, thống kê, logs

## 🔧 API Endpoints

### Health Check
```http
GET /api/v1/health
```

### User Management
```http
POST /api/v1/register
GET /api/v1/users
```

### Attendance
```http
POST /api/v1/checkin
GET /api/v1/attendance/logs
GET /api/v1/attendance/stats
```

### Face Detection
```http
POST /api/v1/detect-faces
```

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    student_code VARCHAR(20) UNIQUE NOT NULL,
    department VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Face Embeddings Table
```sql
CREATE TABLE face_embeddings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    embedding VECTOR(128) NOT NULL,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Attendance Logs Table
```sql
CREATE TABLE attendance_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence FLOAT,
    device_id VARCHAR(50)
);
```

## 🎨 Giao diện

### ESP32-CAM Web Interface
- **Modern UI** với gradient và glassmorphism
- **Modal system** cho đăng ký và điểm danh
- **Real-time camera stream**
- **Quality check** cho ảnh chụp
- **Responsive design**

### Streamlit Dashboard
- **Statistics overview**
- **User management**
- **Attendance logs**
- **Real-time updates**

## 🔒 Bảo mật

- **CORS headers** cho cross-origin requests
- **Input validation** với Pydantic
- **SQL injection protection** với SQLAlchemy
- **Error handling** không tiết lộ thông tin nhạy cảm

## 📈 Performance

- **Async FastAPI** cho high performance
- **Vector similarity search** với pgvector
- **Image optimization** cho ESP32-CAM
- **Database indexing** cho fast queries

## 🐛 Troubleshooting

### ESP32-CAM Issues
- **Camera không hoạt động**: Kiểm tra kết nối hardware
- **WiFi không kết nối**: Kiểm tra SSID/password
- **Stream không hiển thị**: Kiểm tra CORS headers

### Backend Issues
- **Database connection**: Kiểm tra PostgreSQL service
- **Face detection**: Kiểm tra chất lượng ảnh
- **API errors**: Xem server logs

### Common Solutions
1. **Restart services**: ESP32, API server, database
2. **Check logs**: Console, server logs
3. **Verify network**: IP addresses, ports
4. **Test endpoints**: curl, Postman

## 📚 Tài liệu tham khảo

- [ESP32-CAM Documentation](esp32-camera/README.md)
- [API Documentation](docs/api_docs.md)
- [Arduino Libraries](esp32-camera/libraries.txt)

## 👥 Đóng góp

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## 📄 License

MIT License - Xem file LICENSE để biết thêm chi tiết.

## 🏆 Credits

- **ESP32-CAM**: Espressif Systems
- **FastAPI**: Sebastián Ramírez
- **OpenCV**: Intel Corporation
- **PostgreSQL**: PostgreSQL Global Development Group
- **Streamlit**: Streamlit Inc.

---

**Version**: 2.0  
**Last Updated**: 2024  
**Author**: [Tên sinh viên]