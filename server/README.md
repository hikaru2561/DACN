# 🚀 Face Recognition Attendance System - Backend

## 🎯 Tổng quan

Backend Python cho hệ thống điểm danh bằng nhận dạng khuôn mặt. Sử dụng FastAPI, PostgreSQL với pgvector, và OpenCV để xử lý face recognition.

## ✨ Tính năng chính

- 🎭 **Face Detection**: Phát hiện khuôn mặt với OpenCV Haar Cascade
- 🧠 **Face Recognition**: Nhận diện với vector embedding 128D
- 👤 **User Registration**: Đăng ký người dùng với ảnh khuôn mặt
- ✅ **Attendance Check-in**: Điểm danh tự động
- 🗄️ **Database Management**: PostgreSQL + pgvector
- 🌐 **Web Interface**: Streamlit dashboard
- 📊 **Statistics**: Thống kê và báo cáo

## 🛠️ Yêu cầu hệ thống

- **Python**: 3.8+
- **PostgreSQL**: 12+ với extension pgvector
- **OpenCV**: 4.5+
- **FastAPI**: 0.68+
- **Streamlit**: 1.0+

## 📦 Cài đặt

### 1. **Database Setup**
```bash
# Cài đặt PostgreSQL
# Tạo database
createdb face_attendance

# Cài đặt pgvector extension
psql -d face_attendance -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 2. **Python Dependencies**
```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows

# Cài đặt dependencies
pip install -r requirements.txt
```

### 3. **Configuration**
```python
# Sửa server/core/config.py:
DATABASE_URL = "postgresql://postgres:your_password@localhost:5432/face_attendance"
```

### 4. **Initialize Database**
```bash
python reset_db.py
```

## 🚀 Chạy hệ thống

### API Server
```bash
python run.py api
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Web Interface
```bash
streamlit run web_app.py --server.port 8501
# Web: http://localhost:8501
```

### Cả hai cùng lúc
```bash
python run.py both
```

## 📁 Cấu trúc thư mục

```
server/
├── 📁 api/
│   └── main.py                    # FastAPI application
├── 📁 core/
│   └── config.py                  # System configuration
├── 📁 database/
│   └── schema.sql                 # Database schema
├── 📁 models/
│   ├── database.py                # Database connection
│   ├── schemas.py                 # SQLAlchemy models
│   └── pydantic_models.py         # Pydantic models
├── 📁 services/
│   ├── database_service.py        # Database operations
│   └── face_recognition_improved.py # Face recognition
├── 📁 uploads/
│   ├── faces/                     # Face images
│   └── attendance/                # Attendance images
├── web_app.py                     # Streamlit interface
├── run.py                         # Main runner script
├── reset_db.py                    # Database reset
└── requirements.txt               # Dependencies
```

## 🔧 API Endpoints

### System
- `GET /api/v1/health` - Health check

### Face Detection
- `POST /api/v1/detect-faces` - Detect faces in image

### User Management
- `POST /api/v1/register` - Register new user
- `GET /api/v1/users` - Get user list

### Attendance
- `POST /api/v1/checkin` - Check-in with face recognition
- `GET /api/v1/attendance/logs` - Get attendance history
- `GET /api/v1/attendance/stats` - Get attendance statistics

## 🧠 Face Recognition Algorithm

Hệ thống sử dụng thuật toán cải tiến để tạo vector embedding 128D:

1. **Histogram Features** (16D): Color distribution
2. **LBP Features** (16D): Local Binary Pattern
3. **Texture Features** (5D): Texture characteristics
4. **HOG Features** (32D): Histogram of Oriented Gradients
5. **Gabor Features** (16D): Gabor filters
6. **Statistical Features** (8D): Basic statistics
7. **Edge Features** (16D): Edge characteristics
8. **Frequency Features** (16D): Frequency domain
9. **Additional Features** (3D): Extra features

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

## 🎯 Sử dụng

### 1. **Đăng ký người dùng**
```bash
curl -X POST "http://localhost:8000/api/v1/register" \
  -F "file=@face_image.jpg" \
  -F "name=John Doe" \
  -F "student_code=ST001"
```

### 2. **Điểm danh**
```bash
curl -X POST "http://localhost:8000/api/v1/checkin" \
  -F "file=@checkin_image.jpg"
```

### 3. **Xem thống kê**
```bash
curl "http://localhost:8000/api/v1/attendance/stats"
```

## 🐛 Troubleshooting

### Database Issues
- **Connection failed**: Kiểm tra PostgreSQL service
- **pgvector error**: Cài đặt extension pgvector
- **Schema error**: Chạy `python reset_db.py`

### Face Detection Issues
- **No faces detected**: Kiểm tra chất lượng ảnh
- **Poor recognition**: Đảm bảo ảnh rõ nét, đủ sáng
- **Memory error**: Giảm image size

### API Issues
- **422 Unprocessable Entity**: Kiểm tra request format
- **500 Internal Error**: Xem server logs
- **CORS errors**: Kiểm tra ESP32-CAM CORS headers

## 📈 Performance

- **Face Detection**: ~200ms per image
- **Face Recognition**: ~300ms per image
- **Database Queries**: ~50ms average
- **API Response**: ~500ms total

## 🔒 Security

- **Input validation** với Pydantic
- **SQL injection protection** với SQLAlchemy
- **Error handling** không tiết lộ thông tin nhạy cảm
- **CORS support** cho cross-origin requests

## 📚 Tài liệu

- [API Documentation](http://localhost:8000/docs)
- [Main Project README](../README.md)
- [ESP32-CAM README](../esp32-camera/README.md)

---

**Version**: 2.0  
**Last Updated**: 2024