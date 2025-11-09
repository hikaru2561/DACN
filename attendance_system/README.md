# Hệ thống Điểm Danh Khuôn Mặt - Attendance System

## 📋 Tổng quan

Hệ thống quản lý điểm danh tự động bằng nhận diện khuôn mặt, tích hợp:
- ✅ Face Recognition V2 (InsightFace + SVM/KNN)
- ✅ PostgreSQL Database
- ✅ Desktop Application (UI như trong ảnh bạn gửi)
- ✅ ESP32-CAM Integration

---

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────┐
│                      Desktop Application                     │
│  (Tkinter/PyQt5 - UI như trong ảnh)                         │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ Sinh viên│ │ Nhận diện│ │ Điểm danh│ │ Báo cáo  │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌──────────────────────┐
│   Backend API   │    │  Face Recognition V2 │
│  (Flask/FastAPI)│    │  (InsightFace + SVM) │
│                 │    │                      │
│  - CRUD APIs    │    │  - Detect faces      │
│  - Auth JWT     │    │  - Extract embeddings│
│  - Attendance   │    │  - Recognize         │
└────────┬────────┘    └──────────┬───────────┘
         │                        │
         ▼                        ▼
┌──────────────────────────────────────┐
│      PostgreSQL Database             │
│                                      │
│  Tables:                             │
│  - users, students, teachers         │
│  - subjects, classes, sessions       │
│  - attendance, face_encodings        │
│  - attendance_logs, camera_devices   │
└──────────────────────────────────────┘
         ▲
         │
         ▼
┌──────────────────┐
│   ESP32-CAM      │
│  (Video Stream)  │
└──────────────────┘
```

---

## 📁 Cấu trúc thư mục

```
attendance_system/
├── database/
│   ├── schema.sql           # ✅ Database schema (15 tables)
│   ├── sample_data.sql      # ✅ Dữ liệu mẫu
│   ├── ERD.md               # ✅ Database diagram
│   ├── SETUP.md             # ✅ Hướng dẫn setup
│   └── test_connection.py   # ✅ Test connection
│
├── backend/
│   ├── app.py               # ⏳ Flask/FastAPI app
│   ├── models/              # ⏳ Database models (SQLAlchemy)
│   ├── routes/              # ⏳ API endpoints
│   ├── auth/                # ⏳ JWT authentication
│   └── requirements.txt     # ⏳ Dependencies
│
├── frontend/
│   ├── main.py              # ⏳ Main desktop app
│   ├── ui/                  # ⏳ UI screens
│   │   ├── dashboard.py     # Dashboard chính
│   │   ├── students.py      # Quản lý sinh viên
│   │   ├── attendance.py    # Điểm danh
│   │   ├── recognition.py   # Nhận diện camera
│   │   └── reports.py       # Báo cáo
│   ├── utils/               # ⏳ Utilities
│   └── assets/              # ⏳ Icons, images
│
└── face_recognition/
    └── (Link to face_recognition_v2)
```

---

## 🗄️ Database Design

### Core Tables (15 bảng)

1. **users** - Authentication
2. **students** - Thông tin sinh viên
3. **face_encodings** - Embeddings 512D
4. **subjects** - Môn học
5. **teachers** - Giảng viên
6. **classes** - Lớp học môn
7. **class_enrollments** - Đăng ký học
8. **sessions** - Buổi học
9. **attendance** - Điểm danh
10. **attendance_logs** - Audit trail
11. **camera_devices** - ESP32-CAM
12. **recognition_logs** - Log nhận diện

### Features

- ✅ **Triggers**: Auto-update timestamps, auto-calculate attendance status
- ✅ **Views**: Attendance statistics, students with faces
- ✅ **Indexes**: Optimized for queries
- ✅ **ENUM types**: gender, attendance_status, user_role, session_status

---

## 🚀 Roadmap

### ✅ DONE - Database Layer

- [x] Design ERD với 15 bảng
- [x] Create `schema.sql` với triggers, views, indexes
- [x] Create `sample_data.sql` (dữ liệu từ ảnh bạn gửi)
- [x] Documentation (SETUP.md, ERD.md)
- [x] Test connection script

### ⏳ IN PROGRESS - Setup Database

**Bước tiếp theo của bạn:**

1. **Install PostgreSQL**
   ```powershell
   # Download từ postgresql.org
   # Install với pgAdmin 4
   ```

2. **Create Database**
   ```powershell
   psql -U postgres
   ```
   ```sql
   CREATE DATABASE attendance_system;
   \c attendance_system
   ```

3. **Import Schema**
   ```powershell
   cd D:\HUTECH\DACN\attendance_system\database
   psql -U postgres -d attendance_system -f schema.sql
   ```

4. **Import Sample Data**
   ```powershell
   psql -U postgres -d attendance_system -f sample_data.sql
   ```

5. **Test Connection**
   ```powershell
   python test_connection.py
   ```

### 🔜 NEXT - Backend API

- [ ] Setup Flask/FastAPI
- [ ] SQLAlchemy models
- [ ] CRUD endpoints
- [ ] JWT authentication
- [ ] Face recognition integration

### 🔜 FUTURE - Frontend Desktop App

- [ ] Tkinter/PyQt5 UI
- [ ] Dashboard như trong ảnh
- [ ] Quản lý sinh viên
- [ ] Nhận diện camera real-time
- [ ] Báo cáo & export

---

## 📊 Sample Data

Dữ liệu mẫu dựa trên ảnh bạn gửi:

### Sinh viên
- **Lê Quang Nhật** (ID: 1) - D12CNPM
- **Đỗ Mạnh Dũng** (ID: 2) - D13CNPM1
- **Mai Quốc Khánh** (ID: 3) - D12CNPM
- **NV01** (test) - D12CNPM

### Môn học
- Java (IT001)
- C++ (IT003)
- Database (IT002)

### Buổi học
- C++ class: 10 sessions (Apr 2021)
- Database class: 6 sessions

### Điểm danh
- Lê Quang Nhật: 11 records (mix: Vắng, Có mặt, Đi muộn)
- Status tự động tính dựa trên check_in_time

---

## 🔑 Default Accounts

**Admin:**
- Username: `admin`
- Password: `admin123`

**Teacher:**
- Username: `teacher1`
- Password: `teacher123`

**Student:**
- Username: `2011063561` (Lê Quang Nhật)
- Password: `student123`

---

## 📚 Next Steps

1. ✅ **Hoàn thành Database Setup** (chạy `schema.sql` và `sample_data.sql`)
2. ⏳ **Backend API** - Tạo REST API với Flask/FastAPI
3. ⏳ **Frontend UI** - Clone giao diện từ ảnh bạn gửi
4. ⏳ **Face Recognition Integration** - Link với `face_recognition_v2`
5. ⏳ **Testing** - End-to-end testing

---

Bạn muốn tôi tiếp tục với **bước nào**?

1. **Backend API** (Flask/FastAPI với SQLAlchemy)
2. **Frontend Desktop App** (Tkinter/PyQt5 - UI như ảnh)
3. **Face Recognition Integration** (Link v2 với database)

Hoặc bạn muốn tôi **hỗ trợ setup database** trước? 🚀
