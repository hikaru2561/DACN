-- ============================================================================
-- HỆ THỐNG QUẢN LÝ ĐIỂM DANH KHUÔN MẶT - POSTGRESQL DATABASE SCHEMA
-- ============================================================================
-- Version: 1.0
-- Date: 2025-11-07
-- Author: HUTECH DACN
-- ============================================================================
-- NOTE: Database "attendance_system" must be created before running this schema
-- Use create_database.py to create the database first
-- ============================================================================

-- ============================================================================
-- EXTENSIONS
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- Password hashing

-- ============================================================================
-- ENUM TYPES
-- ============================================================================

-- Giới tính
CREATE TYPE gender_enum AS ENUM ('Nam', 'Nữ', 'Khác');

-- Loại điểm danh
CREATE TYPE attendance_status_enum AS ENUM (
    'Vắng',           -- Absent
    'Có mặt',         -- Present
    'Đi muộn',        -- Late
    'Về sớm',         -- Leave early
    'Có phép'         -- Excused
);

-- Vai trò người dùng
CREATE TYPE user_role_enum AS ENUM ('Admin', 'Teacher', 'Student');

-- Trạng thái buổi học
CREATE TYPE session_status_enum AS ENUM ('Scheduled', 'In Progress', 'Completed', 'Cancelled');

-- ============================================================================
-- TABLE: users (Người dùng hệ thống - Authentication)
-- ============================================================================
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- Bcrypt hash
    email VARCHAR(100) UNIQUE NOT NULL,
    role user_role_enum NOT NULL DEFAULT 'Student',
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE users IS 'Bảng quản lý người dùng và authentication';

-- ============================================================================
-- TABLE: students (Sinh viên)
-- ============================================================================
CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY,  -- VD: D12CNPM1, SV001
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    full_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    gender gender_enum,
    national_id VARCHAR(20) UNIQUE,  -- CMND/CCCD
    phone VARCHAR(15),
    email VARCHAR(100),
    address TEXT,
    class_name VARCHAR(50),  -- Lớp học (VD: D12CNPM1)
    major VARCHAR(100),      -- Chuyên ngành
    academic_year VARCHAR(20), -- Năm học (VD: 2020-2021)
    photo_path VARCHAR(255), -- Đường dẫn ảnh đại diện
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE students IS 'Thông tin sinh viên';

-- ============================================================================
-- TABLE: face_encodings (Dữ liệu khuôn mặt)
-- ============================================================================
CREATE TABLE face_encodings (
    encoding_id SERIAL PRIMARY KEY,
    student_id VARCHAR(20) REFERENCES students(student_id) ON DELETE CASCADE,
    embedding BYTEA NOT NULL,  -- 512D vector (pickle/numpy saved as bytes)
    image_path VARCHAR(255),   -- Đường dẫn ảnh gốc
    quality_score FLOAT,       -- Quality score khi capture
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE  -- Cho phép vô hiệu hóa encoding cũ
);

COMMENT ON TABLE face_encodings IS 'Embeddings khuôn mặt của sinh viên (512D vectors)';
CREATE INDEX idx_face_student ON face_encodings(student_id);

-- ============================================================================
-- TABLE: subjects (Môn học)
-- ============================================================================
CREATE TABLE subjects (
    subject_id VARCHAR(20) PRIMARY KEY,  -- VD: IT001, MATH101
    subject_name VARCHAR(200) NOT NULL,
    credits INTEGER DEFAULT 3,  -- Số tín chỉ
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE subjects IS 'Danh sách môn học';

-- ============================================================================
-- TABLE: teachers (Giảng viên)
-- ============================================================================
CREATE TABLE teachers (
    teacher_id VARCHAR(20) PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(15),
    department VARCHAR(100),  -- Khoa
    photo_path VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE teachers IS 'Thông tin giảng viên';

-- ============================================================================
-- TABLE: classes (Lớp học môn - Teaching assignments)
-- ============================================================================
CREATE TABLE classes (
    class_id SERIAL PRIMARY KEY,
    subject_id VARCHAR(20) REFERENCES subjects(subject_id),
    teacher_id VARCHAR(20) REFERENCES teachers(teacher_id),
    class_name VARCHAR(100) NOT NULL,  -- Tên lớp học phần (VD: D12CNPM1 - Java)
    semester VARCHAR(20),    -- Học kỳ (VD: HK1 2024-2025)
    academic_year VARCHAR(20),
    room VARCHAR(50),        -- Phòng học
    max_students INTEGER DEFAULT 50,
    schedule_info TEXT,      -- Thông tin lịch học (JSON hoặc text)
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE classes IS 'Lớp học môn (phân công giảng dạy)';

-- ============================================================================
-- TABLE: class_enrollments (Đăng ký học)
-- ============================================================================
CREATE TABLE class_enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    class_id INTEGER REFERENCES classes(class_id) ON DELETE CASCADE,
    student_id VARCHAR(20) REFERENCES students(student_id) ON DELETE CASCADE,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(class_id, student_id)  -- Mỗi sinh viên chỉ đăng ký 1 lần
);

COMMENT ON TABLE class_enrollments IS 'Sinh viên đăng ký lớp học môn';
CREATE INDEX idx_enrollment_class ON class_enrollments(class_id);
CREATE INDEX idx_enrollment_student ON class_enrollments(student_id);

-- ============================================================================
-- TABLE: sessions (Buổi học)
-- ============================================================================
CREATE TABLE sessions (
    session_id SERIAL PRIMARY KEY,
    class_id INTEGER REFERENCES classes(class_id) ON DELETE CASCADE,
    session_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    room VARCHAR(50),
    status session_status_enum DEFAULT 'Scheduled',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE sessions IS 'Các buổi học cụ thể của lớp học môn';
CREATE INDEX idx_session_class ON sessions(class_id);
CREATE INDEX idx_session_date ON sessions(session_date);

-- ============================================================================
-- TABLE: attendance (Điểm danh)
-- ============================================================================
CREATE TABLE attendance (
    attendance_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(session_id) ON DELETE CASCADE,
    student_id VARCHAR(20) REFERENCES students(student_id) ON DELETE CASCADE,
    check_in_time TIMESTAMP,
    check_out_time TIMESTAMP,
    status attendance_status_enum DEFAULT 'Vắng',
    confidence_score FLOAT,  -- Confidence của face recognition
    photo_path VARCHAR(255), -- Ảnh khi điểm danh (optional)
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, student_id)  -- Mỗi sinh viên chỉ điểm danh 1 lần/buổi
);

COMMENT ON TABLE attendance IS 'Bảng điểm danh sinh viên';
CREATE INDEX idx_attendance_session ON attendance(session_id);
CREATE INDEX idx_attendance_student ON attendance(student_id);
CREATE INDEX idx_attendance_date ON attendance(created_at);

-- ============================================================================
-- TABLE: attendance_logs (Lịch sử điểm danh - Audit trail)
-- ============================================================================
CREATE TABLE attendance_logs (
    log_id SERIAL PRIMARY KEY,
    attendance_id INTEGER REFERENCES attendance(attendance_id) ON DELETE CASCADE,
    action VARCHAR(50),  -- 'CHECK_IN', 'CHECK_OUT', 'UPDATE', 'MANUAL_MARK'
    old_status attendance_status_enum,
    new_status attendance_status_enum,
    changed_by INTEGER REFERENCES users(user_id),  -- Ai thay đổi
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

COMMENT ON TABLE attendance_logs IS 'Lịch sử thay đổi điểm danh (audit log)';

-- ============================================================================
-- TABLE: camera_devices (ESP32-CAM devices)
-- ============================================================================
CREATE TABLE camera_devices (
    device_id SERIAL PRIMARY KEY,
    device_name VARCHAR(100) NOT NULL,
    device_code VARCHAR(50) UNIQUE NOT NULL,  -- VD: CAM-ROOM-A101
    stream_url VARCHAR(255) NOT NULL,
    location VARCHAR(200),  -- Vị trí lắp đặt
    room VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    last_heartbeat TIMESTAMP,  -- Lần ping cuối
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE camera_devices IS 'Danh sách thiết bị camera ESP32-CAM';

-- ============================================================================
-- TABLE: recognition_logs (Log nhận diện)
-- ============================================================================
CREATE TABLE recognition_logs (
    log_id SERIAL PRIMARY KEY,
    student_id VARCHAR(20) REFERENCES students(student_id),
    device_id INTEGER REFERENCES camera_devices(device_id),
    confidence_score FLOAT,
    photo_path VARCHAR(255),
    recognized_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_successful BOOLEAN DEFAULT TRUE
);

COMMENT ON TABLE recognition_logs IS 'Log tất cả lần nhận diện khuôn mặt';
CREATE INDEX idx_recog_student ON recognition_logs(student_id);
CREATE INDEX idx_recog_time ON recognition_logs(recognized_at);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function: Tự động cập nhật updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers cho các bảng cần updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_students_updated_at BEFORE UPDATE ON students
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_attendance_updated_at BEFORE UPDATE ON attendance
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function: Tự động tính trạng thái điểm danh dựa trên thời gian
CREATE OR REPLACE FUNCTION calculate_attendance_status()
RETURNS TRIGGER AS $$
DECLARE
    session_start_time TIME;
    late_threshold INTEGER := 15;  -- Phút (đi muộn nếu > 15 phút)
BEGIN
    -- Lấy thời gian bắt đầu buổi học
    SELECT start_time INTO session_start_time
    FROM sessions WHERE session_id = NEW.session_id;
    
    -- Nếu check_in_time NULL → Vắng
    IF NEW.check_in_time IS NULL THEN
        NEW.status := 'Vắng';
    -- Nếu check_in muộn hơn session_start > 15 phút → Đi muộn
    ELSIF EXTRACT(EPOCH FROM (NEW.check_in_time::time - session_start_time)) / 60 > late_threshold THEN
        NEW.status := 'Đi muộn';
    ELSE
        NEW.status := 'Có mặt';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER auto_calculate_attendance_status
    BEFORE INSERT OR UPDATE ON attendance
    FOR EACH ROW
    EXECUTE FUNCTION calculate_attendance_status();

-- ============================================================================
-- VIEWS (Prepared queries for common use cases)
-- ============================================================================

-- View: Danh sách sinh viên với số lượng face encodings
CREATE OR REPLACE VIEW v_students_with_faces AS
SELECT 
    s.student_id,
    s.full_name,
    s.class_name,
    s.email,
    s.phone,
    COUNT(f.encoding_id) as face_count,
    s.is_active
FROM students s
LEFT JOIN face_encodings f ON s.student_id = f.student_id AND f.is_active = TRUE
GROUP BY s.student_id;

-- View: Thống kê điểm danh theo lớp học
CREATE OR REPLACE VIEW v_attendance_statistics AS
SELECT 
    c.class_id,
    c.class_name,
    sub.subject_name,
    t.full_name as teacher_name,
    COUNT(DISTINCT s.session_id) as total_sessions,
    COUNT(DISTINCT ce.student_id) as total_students,
    COUNT(a.attendance_id) as total_attendance_records,
    ROUND(
        COUNT(CASE WHEN a.status = 'Có mặt' THEN 1 END)::NUMERIC / 
        NULLIF(COUNT(a.attendance_id), 0) * 100, 
        2
    ) as attendance_rate
FROM classes c
LEFT JOIN subjects sub ON c.subject_id = sub.subject_id
LEFT JOIN teachers t ON c.teacher_id = t.teacher_id
LEFT JOIN sessions s ON c.class_id = s.class_id
LEFT JOIN class_enrollments ce ON c.class_id = ce.class_id
LEFT JOIN attendance a ON s.session_id = a.session_id
GROUP BY c.class_id, c.class_name, sub.subject_name, t.full_name;

-- ============================================================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================================================

-- Insert admin user
INSERT INTO users (username, password_hash, email, role) VALUES
('admin', crypt('admin123', gen_salt('bf')), 'admin@hutech.edu.vn', 'Admin');

-- Insert sample teacher
INSERT INTO users (username, password_hash, email, role) VALUES
('teacher1', crypt('teacher123', gen_salt('bf')), 'teacher1@hutech.edu.vn', 'Teacher');

INSERT INTO teachers (teacher_id, user_id, full_name, email, department) VALUES
('GV001', 2, 'Nguyễn Văn A', 'teacher1@hutech.edu.vn', 'Công nghệ phần mềm');

-- Insert sample subject
INSERT INTO subjects (subject_id, subject_name, credits) VALUES
('IT001', 'Lập trình Java', 3),
('IT002', 'Cơ sở dữ liệu', 3);

-- ============================================================================
-- INDEXES for Performance
-- ============================================================================

-- Composite indexes cho queries thường dùng
CREATE INDEX idx_attendance_session_student ON attendance(session_id, student_id);
CREATE INDEX idx_sessions_class_date ON sessions(class_id, session_date);

-- ============================================================================
-- GRANTS (Permissions)
-- ============================================================================

-- Tạo role cho application
CREATE ROLE attendance_app WITH LOGIN PASSWORD 'your_secure_password_here';
GRANT CONNECT ON DATABASE attendance_system TO attendance_app;
GRANT USAGE ON SCHEMA public TO attendance_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO attendance_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO attendance_app;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

-- Verify tables
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
