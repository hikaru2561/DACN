-- ==============================================================
-- DATABASE SCHEMA: FACE ACCESS CONTROL SYSTEM
-- ==============================================================

-- 1. Bảng Users (Người dùng được phép ra vào)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    user_code VARCHAR(50) UNIQUE NOT NULL, -- Mã nhân viên/thẻ
    role VARCHAR(20) DEFAULT 'user',       -- 'admin', 'user', 'guest'
    department VARCHAR(100),               -- Phòng ban
    avatar_path VARCHAR(255),              -- Đường dẫn ảnh đại diện
    is_active BOOLEAN DEFAULT TRUE,        -- Còn hoạt động hay không
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Bảng Access Logs (Lịch sử ra vào)
CREATE TABLE access_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Thông tin nhận diện
    similarity_score FLOAT,                -- Độ chính xác (ví dụ: 0.75)
    snapshot_path VARCHAR(255),            -- Ảnh chụp lúc mở cửa
    
    -- Trạng thái
    status VARCHAR(20) NOT NULL,           -- 'GRANTED' (Mở), 'DENIED' (Chặn), 'UNKNOWN' (Người lạ)
    note TEXT                              -- Ghi chú thêm
);

-- 3. Bảng System Settings (Cấu hình hệ thống)
CREATE TABLE system_settings (
    key VARCHAR(50) PRIMARY KEY,
    value TEXT,
    description TEXT
);

-- Dữ liệu mẫu (Seed Data)
INSERT INTO system_settings (key, value, description) VALUES 
('threshold', '0.50', 'Ngưỡng nhận diện khuôn mặt'),
('door_open_time', '5', 'Thời gian mở cửa (giây)'),
('camera_ip', '192.168.1.192', 'IP của ESP32-CAM');

-- Index để tìm kiếm nhanh
CREATE INDEX idx_users_code ON users(user_code);
CREATE INDEX idx_logs_timestamp ON access_logs(timestamp);
