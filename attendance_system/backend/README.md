# Backend API - Attendance Management System

FastAPI REST API cho hệ thống quản lý điểm danh khuôn mặt.

## 🚀 Setup

### 1. Cài đặt dependencies

```bash
cd attendance_system/backend
pip install -r requirements.txt
```

### 2. Cấu hình database

File `.env` đã được tạo sẵn với config mặc định:
```
DATABASE_URL=postgresql://postgres:Nguyenquang@2561@localhost:5432/attendance_system
```

### 3. Chạy server

```bash
python main.py
```

Hoặc dùng uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server sẽ chạy tại:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Students (Sinh viên)
- `GET /api/students` - Lấy danh sách sinh viên
- `GET /api/students/{student_id}` - Lấy thông tin sinh viên
- `POST /api/students` - Tạo sinh viên mới
- `PUT /api/students/{student_id}` - Cập nhật sinh viên
- `DELETE /api/students/{student_id}` - Xóa sinh viên

### Teachers (Giảng viên)
- `GET /api/teachers` - Lấy danh sách giảng viên
- `GET /api/teachers/{teacher_id}` - Lấy thông tin giảng viên

### Subjects (Môn học)
- `GET /api/subjects` - Lấy danh sách môn học

### Classes (Lớp học)
- `GET /api/classes` - Lấy danh sách lớp học
- `GET /api/classes/{class_id}` - Lấy thông tin lớp học

### Sessions (Buổi học)
- `GET /api/sessions` - Lấy danh sách buổi học
- `GET /api/sessions/{session_id}` - Lấy thông tin buổi học
- Query: `?class_id=1` để lọc theo lớp

### Attendance (Điểm danh)
- `GET /api/attendance` - Lấy danh sách điểm danh
- `POST /api/attendance` - Tạo bản ghi điểm danh
- Query: `?session_id=1` hoặc `?student_id=SV001`

### Cameras (Camera)
- `GET /api/cameras` - Lấy danh sách camera
- Query: `?is_active=true` để lọc camera đang hoạt động

## 🧪 Test API

### Sử dụng Swagger UI
Truy cập http://localhost:8000/docs để test trực tiếp

### Sử dụng curl

```bash
# Health check
curl http://localhost:8000/health

# Lấy danh sách sinh viên
curl http://localhost:8000/api/students

# Lấy danh sách giảng viên
curl http://localhost:8000/api/teachers

# Lấy danh sách lớp học
curl http://localhost:8000/api/classes

# Lấy buổi học của lớp 33
curl http://localhost:8000/api/sessions?class_id=33

# Tạo sinh viên mới
curl -X POST http://localhost:8000/api/students \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "SV001",
    "full_name": "Nguyễn Văn A",
    "email": "sva@hutech.edu.vn",
    "phone": "0909123456",
    "class_name": "D12CNPM",
    "major": "Công nghệ phần mềm"
  }'
```

## 📁 Cấu trúc

```
backend/
├── main.py           # FastAPI app + endpoints
├── models.py         # SQLAlchemy models
├── schemas.py        # Pydantic schemas
├── database.py       # Database connection
├── requirements.txt  # Dependencies
├── .env             # Environment variables
└── README.md        # This file
```

## 🔐 Authentication (Coming soon)

JWT authentication sẽ được thêm vào để bảo vệ API endpoints.

## 📊 Database Schema

Database được tạo bởi `attendance_system/database/schema.sql`:
- 12 tables: users, students, teachers, subjects, classes, sessions, attendance, face_encodings, etc.
- 2 views: v_students_with_faces, v_attendance_statistics  
- 4 triggers: auto timestamps, calculate attendance status

## 🐛 Troubleshooting

### Lỗi kết nối database
```
Database connection failed: could not connect to server
```
→ Kiểm tra PostgreSQL đã chạy và config trong `.env` đúng

### Lỗi import
```
ModuleNotFoundError: No module named 'fastapi'
```
→ Chạy `pip install -r requirements.txt`

## 🚧 TODO

- [ ] JWT Authentication & Authorization
- [ ] File upload cho ảnh sinh viên
- [ ] Face recognition endpoints
- [ ] Statistics & Reports endpoints
- [ ] Pagination cho list endpoints
- [ ] Error handling improvements
- [ ] Rate limiting
- [ ] API documentation improvements
