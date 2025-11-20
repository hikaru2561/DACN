# Database Schema - Attendance System

## 📊 Entity Relationship Diagram (ERD)

```
┌─────────────┐
│    users    │
│─────────────│
│ user_id (PK)│──┐
│ username    │  │
│ password    │  │
│ email       │  │
│ role        │  │
└─────────────┘  │
                 │
      ┌──────────┼──────────┐
      │          │          │
      ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ students │ │ teachers │ │  admin   │
│──────────│ │──────────│ └──────────┘
│student_id│ │teacher_id│
│user_id(FK│ │user_id(FK│
│full_name │ │full_name │
│class_name│ │department│
│photo_path│ │          │
└────┬─────┘ └────┬─────┘
     │            │
     │            │
     ▼            ▼
┌─────────────┐ ┌──────────┐
│face_encodings│ │ subjects │
│─────────────│ │──────────│
│encoding_id  │ │subject_id│
│student_id(FK)│ │name      │
│embedding    │ │credits   │
│image_path   │ └────┬─────┘
└─────────────┘      │
                     │
                     ▼
              ┌──────────────┐
              │   classes    │
              │──────────────│
              │ class_id (PK)│──┐
              │ subject_id(FK)│  │
              │ teacher_id(FK)│  │
              │ class_name   │  │
              │ semester     │  │
              └──────┬───────┘  │
                     │          │
         ┌───────────┼──────────┘
         │           │
         ▼           ▼
┌──────────────┐ ┌─────────┐
│class_enrollmt│ │sessions │
│──────────────│ │─────────│
│enrollment_id │ │session_id│──┐
│class_id (FK) │ │class_id  │  │
│student_id(FK)│ │date      │  │
└──────────────┘ │start_time│  │
                 │end_time  │  │
                 │status    │  │
                 └──────────┘  │
                               │
                               ▼
                      ┌───────────────┐
                      │  attendance   │
                      │───────────────│
                      │attendance_id  │
                      │session_id (FK)│
                      │student_id (FK)│
                      │check_in_time  │
                      │check_out_time │
                      │status         │
                      │confidence     │
                      └───────────────┘
```

## 🗂️ Tables Description

### Core Tables

1. **users** - Authentication & Authorization
   - Primary: user_id
   - Stores: username, password_hash, role (Admin/Teacher/Student)

2. **students** - Student Information
   - Primary: student_id (e.g., D12CNPM1)
   - Foreign: user_id
   - Stores: full info, class, photo_path

3. **face_encodings** - Face Recognition Data
   - Primary: encoding_id
   - Foreign: student_id
   - Stores: 512D embedding (BYTEA), image_path, quality

4. **subjects** - Course Catalog
   - Primary: subject_id (e.g., IT001)
   - Stores: name, credits

5. **teachers** - Teacher Information
   - Primary: teacher_id
   - Foreign: user_id
   - Stores: full info, department

6. **classes** - Course Sections
   - Primary: class_id
   - Foreign: subject_id, teacher_id
   - Stores: semester, room, schedule

7. **class_enrollments** - Student Enrollment
   - Links: students ↔ classes (many-to-many)

8. **sessions** - Specific Class Meetings
   - Primary: session_id
   - Foreign: class_id
   - Stores: date, start_time, end_time, status

9. **attendance** - Attendance Records
   - Primary: attendance_id
   - Foreign: session_id, student_id
   - Stores: check_in/out times, status, confidence

### Support Tables

10. **attendance_logs** - Audit Trail
11. **camera_devices** - ESP32-CAM Management
12. **recognition_logs** - Face Recognition Logs

## 🔑 Key Relationships

- `users` 1:1 → `students` (một user là một sinh viên)
- `users` 1:1 → `teachers` (một user là một giảng viên)
- `students` 1:N → `face_encodings` (một sinh viên nhiều ảnh)
- `classes` N:M → `students` (through `class_enrollments`)
- `classes` 1:N → `sessions` (một lớp nhiều buổi học)
- `sessions` 1:N → `attendance` (một buổi học nhiều điểm danh)

## 📐 Business Rules

1. **Attendance Status** (tự động tính):
   - `Có mặt`: Check-in <= start_time + 15 phút
   - `Đi muộn`: Check-in > start_time + 15 phút
   - `Vắng`: Không check-in

2. **Face Recognition**:
   - Mỗi sinh viên >= 20 ảnh training
   - Confidence score >= 0.6 để điểm danh tự động
   - < 0.6 cần xác nhận thủ công

3. **Class Enrollment**:
   - Unique constraint: (class_id, student_id)
   - Cannot enroll if class is full (max_students)

4. **Session**:
   - Cannot create session if class is inactive
   - Status flow: Scheduled → In Progress → Completed

## 🔧 Features

### Triggers
- `update_updated_at_column`: Tự động cập nhật timestamp
- `calculate_attendance_status`: Tự động tính trạng thái điểm danh

### Views
- `v_students_with_faces`: Sinh viên + số lượng ảnh
- `v_attendance_statistics`: Thống kê tỷ lệ điểm danh theo lớp

### Indexes
- Composite indexes cho queries phức tạp
- Foreign key indexes cho JOIN performance

## 📊 Sample Queries

```sql
-- 1. Lấy danh sách sinh viên trong lớp
SELECT s.student_id, s.full_name, s.class_name
FROM class_enrollments ce
JOIN students s ON ce.student_id = s.student_id
WHERE ce.class_id = 1;

-- 2. Thống kê điểm danh của sinh viên
SELECT 
    s.full_name,
    COUNT(a.attendance_id) as total,
    COUNT(CASE WHEN a.status = 'Có mặt' THEN 1 END) as present,
    COUNT(CASE WHEN a.status = 'Vắng' THEN 1 END) as absent,
    ROUND(
        COUNT(CASE WHEN a.status = 'Có mặt' THEN 1 END)::NUMERIC / 
        COUNT(a.attendance_id) * 100, 2
    ) as attendance_rate
FROM students s
JOIN attendance a ON s.student_id = a.student_id
WHERE s.student_id = 'D12CNPM1'
GROUP BY s.student_id, s.full_name;

-- 3. Điểm danh theo buổi học
SELECT 
    s.full_name,
    a.check_in_time,
    a.status,
    a.confidence_score
FROM attendance a
JOIN students s ON a.student_id = s.student_id
WHERE a.session_id = 1
ORDER BY a.check_in_time;
```
