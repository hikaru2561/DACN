# Face Recognition Attendance System - Optimized

Hệ thống điểm danh bằng nhận diện khuôn mặt sử dụng FastAPI, PostgreSQL với pgvector, và OpenCV.

## 🚀 Tính năng chính

- **Face Detection**: Phát hiện khuôn mặt trong ảnh sử dụng OpenCV Haar Cascade
- **Face Recognition**: Nhận diện khuôn mặt với vector embedding 128D
- **User Registration**: Đăng ký người dùng với ảnh khuôn mặt
- **Attendance Check-in**: Điểm danh tự động bằng nhận diện khuôn mặt
- **Database Management**: Lưu trữ dữ liệu với PostgreSQL + pgvector
- **Web Interface**: Giao diện web đơn giản để test

## 📋 Yêu cầu hệ thống

- Python 3.8+
- PostgreSQL 12+ với extension pgvector
- OpenCV
- FastAPI
- Streamlit

## 🛠️ Cài đặt

### 1. Cài đặt PostgreSQL với pgvector

```bash
# Cài đặt PostgreSQL
# Tạo database
createdb face_attendance

# Cài đặt pgvector extension
psql -d face_attendance -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 2. Cài đặt Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình database

Chỉnh sửa file `core/config.py`:

```python
DATABASE_URL = "postgresql://postgres:your_password@localhost:5432/face_attendance"
```

### 4. Khởi tạo database

```bash
python reset_db_optimized.py
```

## 🚀 Chạy hệ thống

### Chạy API server

```bash
python run_optimized.py api
```

API sẽ chạy tại: http://localhost:8000
API Docs: http://localhost:8000/docs

### Chạy Web interface

```bash
python run_optimized.py web
```

Web interface sẽ chạy tại: http://localhost:8501

## 📁 Cấu trúc thư mục

```
server/
├── api/
│   └── main.py                    # FastAPI application
├── core/
│   └── config.py                  # Cấu hình hệ thống
├── database/
│   └── schema.sql                 # Database schema
├── models/
│   ├── database.py                # Database connection
│   ├── schemas.py                 # SQLAlchemy models
│   └── pydantic_models.py         # Pydantic models
├── services/
│   ├── database_service.py        # Database operations
│   └── face_recognition_improved.py # Face recognition service
├── uploads/
│   ├── faces/                     # Thư mục lưu ảnh khuôn mặt
│   └── attendance/                # Thư mục lưu ảnh điểm danh
├── web_app.py                     # Streamlit web interface
├── run.py                         # Script chạy hệ thống
├── reset_db.py                    # Script reset database
├── requirements.txt               # Dependencies
├── README.md                      # Documentation
└── SYSTEM_SUMMARY.md              # Tổng kết hệ thống
```

## 🔧 API Endpoints

### Face Detection
- `POST /api/v1/detect-faces` - Phát hiện khuôn mặt trong ảnh

### User Management
- `POST /api/v1/register` - Đăng ký người dùng mới
- `GET /api/v1/users` - Lấy danh sách người dùng

### Attendance
- `POST /api/v1/checkin` - Điểm danh bằng nhận diện khuôn mặt
- `GET /api/v1/attendance/logs` - Lấy lịch sử điểm danh
- `GET /api/v1/attendance/stats` - Thống kê điểm danh

### System
- `GET /api/v1/health` - Kiểm tra trạng thái hệ thống

## 🧪 Testing

Chạy test toàn bộ hệ thống:

```bash
python test_complete_flow.py
```

## 📊 Database Schema

### Users Table
- `id`: Primary key
- `name`: Tên người dùng
- `student_code`: Mã sinh viên (unique)
- `department`: Khoa/phòng ban
- `is_active`: Trạng thái hoạt động
- `created_at`: Thời gian tạo

### Face Embeddings Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `embedding`: Vector 128D (pgvector)
- `confidence`: Độ tin cậy
- `created_at`: Thời gian tạo

### Attendance Logs Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `timestamp`: Thời gian điểm danh
- `confidence`: Độ tin cậy nhận diện
- `device_id`: ID thiết bị

## 🔍 Face Recognition

Hệ thống sử dụng thuật toán cải tiến để tạo vector embedding 128D:

1. **Histogram Features** (16D): Phân bố màu sắc
2. **LBP Features** (16D): Local Binary Pattern
3. **Texture Features** (5D): Đặc trưng kết cấu
4. **HOG Features** (32D): Histogram of Oriented Gradients
5. **Gabor Features** (16D): Gabor filters
6. **Statistical Features** (8D): Thống kê cơ bản
7. **Edge Features** (16D): Đặc trưng cạnh
8. **Frequency Features** (16D): Miền tần số
9. **Additional Features** (3D): Các đặc trưng bổ sung

## 🎯 Sử dụng

1. **Đăng ký người dùng**: Upload ảnh khuôn mặt và thông tin cá nhân
2. **Điểm danh**: Upload ảnh để hệ thống nhận diện và điểm danh tự động
3. **Xem lịch sử**: Kiểm tra lịch sử điểm danh và thống kê

## 🔧 Troubleshooting

### Lỗi database connection
- Kiểm tra PostgreSQL đang chạy
- Kiểm tra password trong config.py
- Chạy `python reset_db_optimized.py` để reset database

### Lỗi face detection
- Đảm bảo ảnh có khuôn mặt rõ ràng
- Kiểm tra định dạng ảnh (JPG, PNG)
- Đảm bảo OpenCV được cài đặt đúng

### Lỗi vector similarity
- Kiểm tra pgvector extension đã được cài đặt
- Chạy lại `reset_db_optimized.py`

## 📝 Changelog

### Version 1.0 (Optimized)
- ✅ Database schema tối ưu
- ✅ Face recognition với vector 128D
- ✅ API endpoints hoàn chỉnh
- ✅ Web interface đơn giản
- ✅ Vector similarity search với pgvector
- ✅ Error handling và logging
- ✅ Test scripts hoàn chỉnh

## 👥 Tác giả

Hệ thống được phát triển cho dự án điểm danh bằng nhận diện khuôn mặt.

## 📄 License

Dự án học tập - HUTECH