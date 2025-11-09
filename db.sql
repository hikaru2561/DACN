-- =================================================================
-- SCHEMA DATABASE ĐIỂM DANH ĐƠN GIẢN
-- Database: PostgreSQL 17
-- Yêu cầu: pgvector, uuid-ossp
-- =================================================================

-- Kích hoạt các extension cần thiết
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- =================================================================
-- BẢNG 1: EMPLOYEES (Nhân viên)
-- Lưu thông tin cơ bản của người cần điểm danh
-- =================================================================
CREATE TABLE IF NOT EXISTS employees (
    -- Dùng UUID làm khóa chính
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Mã nhân viên (ví dụ: 'NV001')
    employee_code VARCHAR(50) UNIQUE NOT NULL,
    
    full_name VARCHAR(100) NOT NULL,
    
    -- Trạng thái: true = đang làm (active), false = đã nghỉ
    is_active BOOLEAN DEFAULT true NOT NULL, 
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE employees IS 'Lưu thông tin nhân viên.';
COMMENT ON COLUMN employees.is_active IS 'Trạng thái đi làm (đang làm / đã nghỉ).';


-- =================================================================
-- BẢNG 2: FACE_PROFILES (Hồ sơ khuôn mặt)
-- Liên kết 1-1 với nhân viên, lưu vector trung bình
-- =================================================================
CREATE TABLE IF NOT EXISTS face_profiles (
    id SERIAL PRIMARY KEY,
    
    -- Khóa ngoại liên kết với bảng 'employees'
    employee_id UUID UNIQUE NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    
    -- Vector đặc trưng trung bình 512 chiều (từ ArcFace)
    avg_embedding vector(512) NOT NULL,
    
    -- Số lượng ảnh đã dùng để tính trung bình
    image_count INT NOT NULL,
    
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE face_profiles IS 'Lưu vector đặc trưng (ArcFace) trung bình cho mỗi nhân viên.';

-- TẠO INDEX HNSW (Rất quan trọng để tìm kiếm vector nhanh)
CREATE INDEX IF NOT EXISTS hnsw_avg_l2_idx
ON face_profiles
USING HNSW (avg_embedding vector_l2_ops);


-- =================================================================
-- TẠO KIỂU DỮ LIỆU ENUM (Định danh 'Vào' / 'Ra')
-- =================================================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'attendance_event_type') THEN
        CREATE TYPE attendance_event_type AS ENUM ('check_in', 'check_out');
    END IF;
END$$;


-- =================================================================
-- BẢNG 3: ATTENDANCE_LOGS (Nhật ký điểm danh)
-- Ghi lại MỌI LẦN quét mặt thành công
-- =================================================================
CREATE TABLE IF NOT EXISTS attendance_logs (
    -- Dùng BIGSERIAL vì bảng này sẽ rất lớn
    id BIGSERIAL PRIMARY KEY, 
    
    employee_id UUID NOT NULL REFERENCES employees(id),
    
    -- Thời gian chính xác camera ghi nhận
    check_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
    
    -- Kiểu sự kiện (Vào/Ra) - do ứng dụng Python của bạn quyết định
    event_type attendance_event_type NOT NULL,
    
    -- (Mở rộng) ID của thiết bị camera (ví dụ: 'CAM_CUA_TRUOC')
    source_terminal_id VARCHAR(50),
    
    -- (Mở rộng) Lưu lại độ tương đồng (khoảng cách L2)
    l2_distance DOUBLE PRECISION,
    
    -- (Mở rộng) Đường dẫn tới ảnh chụp nhanh lúc điểm danh
    snapshot_path TEXT 
);

COMMENT ON TABLE attendance_logs IS 'Lưu trữ TOÀN BỘ nhật ký quét mặt (chỉ vào/ra).';
COMMENT ON COLUMN attendance_logs.event_type IS 'Loại sự kiện (check_in, check_out).';

-- Tạo index cho các cột thường xuyên truy vấn
CREATE INDEX IF NOT EXISTS idx_logs_employee_id ON attendance_logs (employee_id);
CREATE INDEX IF NOT EXISTS idx_logs_check_time ON attendance_logs (check_time DESC);

-- =================================================================
-- KẾT THÚC SCHEMA
-- =================================================================