# Desktop Application - User Guide

## 📦 Cài đặt

### 1. Cài đặt Dependencies

```powershell
cd d:\HUTECH\DACN\attendance_system\desktop
pip install -r requirements.txt
```

### 2. Khởi động Backend API

**Cách 1: Sử dụng Python trực tiếp**
```powershell
cd d:\HUTECH\DACN\attendance_system\backend
python main.py
```

**Cách 2: Chạy backend ẩn (background)**
```powershell
Start-Process -FilePath "python" -ArgumentList "d:\HUTECH\DACN\attendance_system\backend\main.py" -WindowStyle Hidden
```

Backend sẽ chạy tại: http://localhost:8000

### 3. Chạy Desktop App

```powershell
cd d:\HUTECH\DACN\attendance_system\desktop
python main.py
```

---

## 🖥️ Giao diện

### Màn hình đăng nhập

- **Username**: `admin`
- **Password**: `admin123`

Ứng dụng sẽ tự động kiểm tra kết nối API khi mở:
- ✅ **Xanh**: Kết nối thành công
- ❌ **Đỏ**: Không kết nối được (kiểm tra Backend)

### Dashboard (Trang chính)

Dashboard có 8 module chính với giao diện card hiện đại:

| Module | Màu sắc | Chức năng | Trạng thái |
|--------|---------|-----------|------------|
| 👨‍🎓 Sinh viên | Blue | Quản lý danh sách, thêm/sửa/xóa sinh viên, chụp ảnh | ✅ Hoàn thành |
| 👨‍🏫 Giảng viên | Green | Quản lý danh sách giảng viên | 🚧 Đang phát triển |
| 📚 Môn học | Orange | Quản lý danh sách môn học | 🚧 Đang phát triển |
| 🏫 Lớp học | Cyan | Quản lý lớp học, phân công giảng viên | 🚧 Đang phát triển |
| 📅 Buổi học | Purple | Lên lịch buổi học, xem thống kê | 🚧 Đang phát triển |
| ✅ Điểm danh | Green | Điểm danh tự động qua camera | 🚧 Đang phát triển |
| 📷 Camera | Red | Quản lý thiết bị camera | 🚧 Đang phát triển |
| 📊 Báo cáo | Gray | Thống kê, xuất báo cáo Excel/CSV | 🚧 Đang phát triển |

**Hover Effects**: Card sẽ đổi màu khi di chuột qua để tăng tính tương tác.

---

## 📋 Module Quản lý Sinh viên

### Tính năng chính

✅ **Danh sách sinh viên**
- Hiển thị bảng với các cột: STT, MSSV, Họ tên, Giới tính, Ngày sinh, Email, SĐT, Số ảnh
- Alternating row colors (xen kẽ trắng/xám) để dễ đọc
- Header màu xanh với font chữ in hoa rõ ràng

✅ **Tìm kiếm**
- Search box với icon 🔍
- Tìm theo MSSV hoặc Họ tên
- Real-time search (tự động lọc khi gõ)
- Hiển thị số kết quả tìm được

✅ **Thêm sinh viên mới**
- Form dialog với validation
- Các trường: MSSV (*), Họ tên (*), Giới tính, Ngày sinh, Email, SĐT
- Validation:
  * MSSV: Bắt buộc, chỉ chứa chữ in hoa và số
  * Họ tên: Bắt buộc
  * Email: Format email hợp lệ
  * Ngày sinh: Format YYYY-MM-DD

✅ **Sửa thông tin**
- Double-click vào row hoặc nút ✏️ Sửa
- MSSV không thể sửa (readonly)
- Form tương tự Add với dữ liệu được điền sẵn

✅ **Xóa sinh viên**
- Nút 🗑️ Xóa với confirmation dialog
- Hiển thị MSSV và tên để xác nhận

✅ **Chụp ảnh khuôn mặt**
- Nút � Chụp ảnh
- Sẽ tích hợp với ESP32-CAM module (Coming soon)

✅ **Làm mới**
- Nút 🔄 để reload dữ liệu từ API

### Shortcuts

- **Double-click**: Sửa sinh viên
- **Enter**: Trong form - Lưu
- **Esc**: Đóng dialog

---

## �🔧 Cấu trúc code

```
attendance_system/desktop/
├── main.py              # Entry point, Login & Dashboard
├── api_client.py        # REST API client
├── student_module.py    # Module quản lý sinh viên (NEW)
├── requirements.txt     # Dependencies
└── README.md           # This file
```

### Các file chính

#### `api_client.py`
REST API client để kết nối với Backend:

```python
from api_client import APIClient

client = APIClient()

# Health check
client.health_check()  # True/False

# Students
students = client.get_students()
student = client.get_student("SV001")
client.create_student({"student_id": "SV001", ...})
client.update_student("SV001", {...})
client.delete_student("SV001")

# Teachers
teachers = client.get_teachers()

# Classes
classes = client.get_classes(is_active=True)

# Sessions
sessions = client.get_sessions(class_id=1)

# Attendance
attendance = client.get_attendance(session_id=1)
client.create_attendance({...})

# Cameras
cameras = client.get_cameras(is_active=True)
```

#### `main.py`
Ứng dụng Tkinter chính:

**Classes:**
- `LoginWindow`: Màn hình đăng nhập với auto health check
- `MainApplication`: Dashboard với 8 module cards + hover effects
- `start_app()`: Entry point

**Color Scheme:**
```python
COLORS = {
    "primary": "#2196F3",        # Blue
    "primary_dark": "#1976D2",   # Dark Blue
    "success": "#4CAF50",        # Green
    "success_dark": "#388E3C",   # Dark Green
    "danger": "#F44336",         # Red
    "danger_dark": "#D32F2F",    # Dark Red
    "warning": "#FF9800",        # Orange
    "info": "#00BCD4",           # Cyan
    "purple": "#9C27B0",         # Purple
    "deep_orange": "#FF5722",    # Deep Orange
    "blue_grey": "#607D8B",      # Blue Grey
    "light": "#FAFAFA",          # Light background
    "white": "#FFFFFF",
    "text": "#212121",
    "text_secondary": "#757575",
    "border": "#E0E0E0",
}
```

#### `student_module.py` ⭐ NEW
Module quản lý sinh viên:

**Classes:**
- `StudentModule`: Main window với Treeview table
- `StudentFormDialog`: Add/Edit form dialog

**Features:**
- Treeview với alternating row colors
- Real-time search
- CRUD operations với API integration
- Form validation
- Status bar hiển thị số lượng/kết quả

---

## 🚀 Phát triển tiếp

### Module tiếp theo: Camera Integration

**Mục tiêu**: Tích hợp ESP32-CAM để chụp ảnh khuôn mặt sinh viên

**Workflow**:
1. Click nút "📷 Chụp ảnh" trong Student Module
2. Mở window mới với video stream từ ESP32-CAM
3. Detect face với MediaPipe
4. Auto-capture 20 ảnh chất lượng cao
5. Preprocess: CLAHE + resize 112x112
6. Lưu vào folder `dataset/processed/{student_id}/`
7. Extract embeddings với InsightFace
8. Lưu vào database `face_encodings` table

**Tech Stack**:
- ESP32-CAM: Video streaming
- MediaPipe: Face detection
- OpenCV: Image processing
- InsightFace ONNX: Embedding extraction (512D)
- PostgreSQL: Vector storage

---

## 📝 Notes

### Dependencies
- **requests**: HTTP client để gọi API
- **Pillow**: Xử lý ảnh
- **pandas**: Xử lý data cho reports
- **openpyxl**: Export Excel
- **matplotlib**: Vẽ biểu đồ
- **tkinter**: GUI framework (built-in Python)

### Authentication
Hiện tại đang dùng **hardcoded credentials** (`admin/admin123`).

**TODO**: Implement JWT authentication
- Backend: Tạo endpoint `POST /api/login` trả về token
- Desktop: Lưu token vào session, gửi trong header `Authorization: Bearer <token>`

### Database Connection
Backend kết nối PostgreSQL:
- Host: `localhost:5432`
- Database: `attendance_system`
- User: `postgres`
- Password: `Nguyenquang@2561`

### Design Principles
1. **Material Design Colors**: Sử dụng palette chuẩn Material Design
2. **Hover Effects**: Interactive cards với state changes
3. **Alternating Row Colors**: Treeview dễ đọc hơn
4. **Consistent Spacing**: Padding/Margin đồng nhất
5. **Clear Typography**: Segoe UI font, hierarchy rõ ràng
6. **Icon Usage**: Emoji icons cho buttons/headers

---

## 🐛 Troubleshooting

### Backend không chạy
```powershell
# Check nếu port 8000 đang được sử dụng
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F

# Restart backend
cd attendance_system\backend
python main.py
```

### Desktop app không kết nối được API
1. Kiểm tra backend đang chạy: http://localhost:8000/docs
2. Kiểm tra firewall
3. Check console output trong Desktop app
4. Xem status label trong Login screen

### Treeview không hiển thị data
1. Check console log để xem API response
2. Verify database có data (qua Swagger UI)
3. Kiểm tra status bar ở Student Module

### Form validation fail
- MSSV: Phải là chữ IN HOA + số (VD: SV001, 2280602549)
- Email: Phải có @ và domain (VD: student@gmail.com)
- Ngày sinh: Format YYYY-MM-DD (VD: 2004-01-09)

---

## 📚 API Documentation

Xem Swagger UI: http://localhost:8000/docs

Hoặc ReDoc: http://localhost:8000/redoc

### Key Endpoints

**Students**
- `GET /api/students` - Lấy danh sách
- `GET /api/students/{id}` - Lấy 1 sinh viên
- `POST /api/students` - Thêm mới
- `PUT /api/students/{id}` - Cập nhật
- `DELETE /api/students/{id}` - Xóa

**Teachers**
- `GET /api/teachers` - Lấy danh sách
- `GET /api/teachers/{id}` - Lấy 1 giảng viên

**Classes**
- `GET /api/classes` - Lấy danh sách (filter: `is_active`)

**Sessions**
- `GET /api/sessions` - Lấy danh sách (filter: `class_id`)

**Attendance**
- `GET /api/attendance` - Lấy danh sách (filter: `session_id`, `student_id`)
- `POST /api/attendance` - Đánh dấu điểm danh

---

## 🎯 Roadmap

### ✅ Phase 1: Core UI (Completed)
- [x] Login screen
- [x] Dashboard with 8 modules
- [x] Student Management Module
- [x] API Integration

### 🚧 Phase 2: Data Management (In Progress)
- [ ] Teacher Management Module
- [ ] Subject Management Module
- [ ] Class Management Module
- [ ] Session Management Module

### 📅 Phase 3: Face Recognition (Planned)
- [ ] Camera Integration
- [ ] Face Capture Module
- [ ] Face Recognition Engine
- [ ] Attendance Marking Module

### 📊 Phase 4: Analytics (Planned)
- [ ] Reports & Statistics
- [ ] Excel/CSV Export
- [ ] Charts & Visualizations

---

## 👨‍💻 Developers

**HUTECH - DACN Team**
- Database: PostgreSQL 17.6
- Backend: FastAPI + SQLAlchemy
- Frontend: Tkinter (Python)
- Face Recognition: InsightFace + MediaPipe

**Version**: 1.0.0  
**Last Updated**: 2025-11-07
