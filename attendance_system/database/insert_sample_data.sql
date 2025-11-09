-- ============================================================================
-- SAMPLE DATA - MÔN HỌC, GIÁO VIÊN, LỚP HỌC, TIẾT HỌC
-- ============================================================================
-- Version: 1.0
-- Date: 2025-11-07
-- NOTE: Không thêm dữ liệu sinh viên - chỉ thêm môn học, giáo viên, lớp, tiết
-- ============================================================================

-- ============================================================================
-- 1. GIÁO VIÊN (Teachers)
-- ============================================================================

-- Thêm user accounts cho giáo viên
INSERT INTO users (username, password_hash, email, role) VALUES
('gv_pham_van_b', crypt('teacher123', gen_salt('bf')), 'phamvanb@hutech.edu.vn', 'Teacher'),
('gv_tran_thi_c', crypt('teacher123', gen_salt('bf')), 'tranthic@hutech.edu.vn', 'Teacher'),
('gv_le_van_d', crypt('teacher123', gen_salt('bf')), 'levand@hutech.edu.vn', 'Teacher'),
('gv_nguyen_thi_e', crypt('teacher123', gen_salt('bf')), 'nguyenthie@hutech.edu.vn', 'Teacher');

-- Thêm thông tin giáo viên
INSERT INTO teachers (teacher_id, user_id, full_name, email, phone, department) VALUES
('GV002', (SELECT user_id FROM users WHERE username = 'gv_pham_van_b'), 'Phạm Văn B', 'phamvanb@hutech.edu.vn', '0909123456', 'Công nghệ phần mềm'),
('GV003', (SELECT user_id FROM users WHERE username = 'gv_tran_thi_c'), 'Trần Thị C', 'tranthic@hutech.edu.vn', '0909123457', 'Công nghệ phần mềm'),
('GV004', (SELECT user_id FROM users WHERE username = 'gv_le_van_d'), 'Lê Văn D', 'levand@hutech.edu.vn', '0909123458', 'Công nghệ phần mềm'),
('GV005', (SELECT user_id FROM users WHERE username = 'gv_nguyen_thi_e'), 'Nguyễn Thị E', 'nguyenthie@hutech.edu.vn', '0909123459', 'Công nghệ phần mềm');

-- ============================================================================
-- 2. MÔN HỌC (Subjects)
-- ============================================================================

INSERT INTO subjects (subject_id, subject_name, credits, description) VALUES
('IT101', 'Lập trình C++', 3, 'Lập trình hướng đối tượng với C++'),
('IT102', 'Lập trình Java', 3, 'Lập trình hướng đối tượng với Java'),
('IT201', 'Cơ sở dữ liệu', 3, 'Thiết kế và quản trị cơ sở dữ liệu quan hệ'),
('IT202', 'Cấu trúc dữ liệu và giải thuật', 3, 'Các cấu trúc dữ liệu cơ bản và giải thuật'),
('IT301', 'Phát triển ứng dụng Web', 3, 'HTML, CSS, JavaScript, Backend'),
('IT302', 'Công nghệ phần mềm', 3, 'Quy trình phát triển phần mềm'),
('IT401', 'Trí tuệ nhân tạo', 3, 'Machine Learning, Deep Learning cơ bản'),
('IT402', 'Đồ án chuyên ngành', 4, 'Dự án tốt nghiệp');

-- ============================================================================
-- 3. LỚP HỌC (Classes) 
-- ============================================================================
-- NOTE: class_id là SERIAL (auto-increment), không cần chỉ định

INSERT INTO classes (class_name, subject_id, teacher_id, semester, academic_year, room, schedule_info, max_students, is_active) VALUES
-- Học kỳ 1, năm 2024-2025
('D12CNPM - Lập trình C++', 'IT101', 'GV004', '1', '2024-2025', 'A101', 'Thứ 2, 7:00-9:30', 50, TRUE),
('D12CNPM - Lập trình Java', 'IT102', 'GV002', '1', '2024-2025', 'A102', 'Thứ 3, 13:00-15:30', 50, TRUE),
('D12CNPM - Cơ sở dữ liệu', 'IT201', 'GV003', '1', '2024-2025', 'A103', 'Thứ 4, 7:00-9:30', 50, TRUE),

('D13CNPM1 - Lập trình C++', 'IT101', 'GV004', '1', '2024-2025', 'A201', 'Thứ 2, 13:00-15:30', 45, TRUE),
('D13CNPM1 - Cấu trúc dữ liệu', 'IT202', 'GV002', '1', '2024-2025', 'A202', 'Thứ 5, 7:00-9:30', 45, TRUE),

-- Học kỳ 2, năm 2024-2025
('D12CNPM - Phát triển Web', 'IT301', 'GV005', '2', '2024-2025', 'B101', 'Thứ 3, 7:00-9:30', 50, FALSE),
('D12CNPM - Công nghệ phần mềm', 'IT302', 'GV002', '2', '2024-2025', 'B102', 'Thứ 5, 13:00-15:30', 50, FALSE),

('D13CNPM1 - Lập trình Java', 'IT102', 'GV002', '2', '2024-2025', 'B201', 'Thứ 4, 13:00-15:30', 45, FALSE);

-- ============================================================================
-- 4. TIẾT HỌC (Sessions)
-- ============================================================================
-- NOTE: Dùng subquery để lấy class_id dựa vào class_name

-- Tiết học cho lớp D12CNPM - Lập trình C++ (15 buổi)
INSERT INTO sessions (class_id, session_date, start_time, end_time, room, status, notes) VALUES
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình C++'), '2024-09-02', '07:00:00', '09:30:00', 'A101', 'Completed', 'Buổi 1: Giới thiệu môn học, Cài đặt môi trường'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình C++'), '2024-09-09', '07:00:00', '09:30:00', 'A101', 'Completed', 'Buổi 2: Cú pháp C++ cơ bản, Biến và kiểu dữ liệu'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình C++'), '2024-09-16', '07:00:00', '09:30:00', 'A101', 'Completed', 'Buổi 3: Cấu trúc điều khiển: if-else, switch'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình C++'), '2024-09-23', '07:00:00', '09:30:00', 'A101', 'Completed', 'Buổi 4: Vòng lặp: for, while, do-while'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình C++'), '2024-09-30', '07:00:00', '09:30:00', 'A101', 'Completed', 'Buổi 5: Hàm và tham số'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình C++'), '2024-10-07', '07:00:00', '09:30:00', 'A101', 'Completed', 'Buổi 6: Mảng và con trỏ'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình C++'), '2024-10-14', '07:00:00', '09:30:00', 'A101', 'Completed', 'Buổi 7: Chuỗi ký tự trong C++'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình C++'), '2024-10-21', '07:00:00', '09:30:00', 'A101', 'Completed', 'Buổi 8: Kiểm tra giữa kỳ'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình C++'), '2024-10-28', '07:00:00', '09:30:00', 'A101', 'Completed', 'Buổi 9: Lập trình hướng đối tượng - Class'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình C++'), '2024-11-04', '07:00:00', '09:30:00', 'A101', 'Completed', 'Buổi 10: Constructor và Destructor'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình C++'), '2024-11-11', '07:00:00', '09:30:00', 'A101', 'Scheduled', 'Buổi 11: Kế thừa (Inheritance)'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình C++'), '2024-11-18', '07:00:00', '09:30:00', 'A101', 'Scheduled', 'Buổi 12: Đa hình (Polymorphism)'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình C++'), '2024-11-25', '07:00:00', '09:30:00', 'A101', 'Scheduled', 'Buổi 13: Template và STL'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình C++'), '2024-12-02', '07:00:00', '09:30:00', 'A101', 'Scheduled', 'Buổi 14: Xử lý ngoại lệ (Exception)'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình C++'), '2024-12-09', '07:00:00', '09:30:00', 'A101', 'Scheduled', 'Buổi 15: Ôn tập và thi cuối kỳ');

-- Tiết học cho lớp D12CNPM - Lập trình Java
INSERT INTO sessions (class_id, session_date, start_time, end_time, room, status, notes) VALUES
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình Java'), '2024-09-03', '13:00:00', '15:30:00', 'A102', 'Completed', 'Buổi 1: Giới thiệu Java, JDK, IDE'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình Java'), '2024-09-10', '13:00:00', '15:30:00', 'A102', 'Completed', 'Buổi 2: Cú pháp Java cơ bản'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình Java'), '2024-09-17', '13:00:00', '15:30:00', 'A102', 'Completed', 'Buổi 3: OOP trong Java - Class và Object'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình Java'), '2024-09-24', '13:00:00', '15:30:00', 'A102', 'Completed', 'Buổi 4: Encapsulation và Access Modifiers'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình Java'), '2024-10-01', '13:00:00', '15:30:00', 'A102', 'Completed', 'Buổi 5: Inheritance trong Java'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình Java'), '2024-10-08', '13:00:00', '15:30:00', 'A102', 'Completed', 'Buổi 6: Polymorphism và Interface'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình Java'), '2024-10-15', '13:00:00', '15:30:00', 'A102', 'Completed', 'Buổi 7: Abstract Class và Interface'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình Java'), '2024-10-22', '13:00:00', '15:30:00', 'A102', 'Completed', 'Buổi 8: Kiểm tra giữa kỳ'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình Java'), '2024-10-29', '13:00:00', '15:30:00', 'A102', 'Completed', 'Buổi 9: Collections Framework'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình Java'), '2024-11-05', '13:00:00', '15:30:00', 'A102', 'Scheduled', 'Buổi 10: Exception Handling'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình Java'), '2024-11-12', '13:00:00', '15:30:00', 'A102', 'Scheduled', 'Buổi 11: File I/O'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình Java'), '2024-11-19', '13:00:00', '15:30:00', 'A102', 'Scheduled', 'Buổi 12: Multithreading'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình Java'), '2024-11-26', '13:00:00', '15:30:00', 'A102', 'Scheduled', 'Buổi 13: JDBC Database Connection'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình Java'), '2024-12-03', '13:00:00', '15:30:00', 'A102', 'Scheduled', 'Buổi 14: Java Swing GUI'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Lập trình Java'), '2024-12-10', '13:00:00', '15:30:00', 'A102', 'Scheduled', 'Buổi 15: Ôn tập và thi cuối kỳ');

-- Tiết học cho lớp D12CNPM - Cơ sở dữ liệu
INSERT INTO sessions (class_id, session_date, start_time, end_time, room, status, notes) VALUES
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Cơ sở dữ liệu'), '2024-09-04', '07:00:00', '09:30:00', 'A103', 'Completed', 'Buổi 1: Giới thiệu CSDL, Mô hình dữ liệu'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Cơ sở dữ liệu'), '2024-09-11', '07:00:00', '09:30:00', 'A103', 'Completed', 'Buổi 2: Mô hình quan hệ (Relational Model)'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Cơ sở dữ liệu'), '2024-09-18', '07:00:00', '09:30:00', 'A103', 'Completed', 'Buổi 3: SQL cơ bản - SELECT, WHERE'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Cơ sở dữ liệu'), '2024-09-25', '07:00:00', '09:30:00', 'A103', 'Completed', 'Buổi 4: SQL - JOIN, UNION'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Cơ sở dữ liệu'), '2024-10-02', '07:00:00', '09:30:00', 'A103', 'Completed', 'Buổi 5: SQL - GROUP BY, Aggregate Functions'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Cơ sở dữ liệu'), '2024-10-09', '07:00:00', '09:30:00', 'A103', 'Completed', 'Buổi 6: Thiết kế CSDL - ERD'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Cơ sở dữ liệu'), '2024-10-16', '07:00:00', '09:30:00', 'A103', 'Completed', 'Buổi 7: Chuẩn hóa CSDL (1NF, 2NF, 3NF)'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Cơ sở dữ liệu'), '2024-10-23', '07:00:00', '09:30:00', 'A103', 'Completed', 'Buổi 8: Kiểm tra giữa kỳ'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Cơ sở dữ liệu'), '2024-10-30', '07:00:00', '09:30:00', 'A103', 'Completed', 'Buổi 9: Triggers và Stored Procedures'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Cơ sở dữ liệu'), '2024-11-06', '07:00:00', '09:30:00', 'A103', 'Scheduled', 'Buổi 10: Transactions và ACID'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Cơ sở dữ liệu'), '2024-11-13', '07:00:00', '09:30:00', 'A103', 'Scheduled', 'Buổi 11: Indexing và Optimization'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Cơ sở dữ liệu'), '2024-11-20', '07:00:00', '09:30:00', 'A103', 'Scheduled', 'Buổi 12: PostgreSQL Advanced Features'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Cơ sở dữ liệu'), '2024-11-27', '07:00:00', '09:30:00', 'A103', 'Scheduled', 'Buổi 13: NoSQL Introduction'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Cơ sở dữ liệu'), '2024-12-04', '07:00:00', '09:30:00', 'A103', 'Scheduled', 'Buổi 14: Database Security'),
((SELECT class_id FROM classes WHERE class_name = 'D12CNPM - Cơ sở dữ liệu'), '2024-12-11', '07:00:00', '09:30:00', 'A103', 'Scheduled', 'Buổi 15: Ôn tập và thi cuối kỳ');

-- Tiết học cho lớp D13CNPM1 - Lập trình C++ (vài buổi đầu)
INSERT INTO sessions (class_id, session_date, start_time, end_time, room, status, notes) VALUES
((SELECT class_id FROM classes WHERE class_name = 'D13CNPM1 - Lập trình C++'), '2024-09-02', '13:00:00', '15:30:00', 'A201', 'Completed', 'Buổi 1: Giới thiệu môn học'),
((SELECT class_id FROM classes WHERE class_name = 'D13CNPM1 - Lập trình C++'), '2024-09-09', '13:00:00', '15:30:00', 'A201', 'Completed', 'Buổi 2: Cú pháp C++ cơ bản'),
((SELECT class_id FROM classes WHERE class_name = 'D13CNPM1 - Lập trình C++'), '2024-09-16', '13:00:00', '15:30:00', 'A201', 'Completed', 'Buổi 3: Cấu trúc điều khiển'),
((SELECT class_id FROM classes WHERE class_name = 'D13CNPM1 - Lập trình C++'), '2024-09-23', '13:00:00', '15:30:00', 'A201', 'Completed', 'Buổi 4: Vòng lặp'),
((SELECT class_id FROM classes WHERE class_name = 'D13CNPM1 - Lập trình C++'), '2024-09-30', '13:00:00', '15:30:00', 'A201', 'Completed', 'Buổi 5: Hàm và tham số'),
((SELECT class_id FROM classes WHERE class_name = 'D13CNPM1 - Lập trình C++'), '2024-10-07', '13:00:00', '15:30:00', 'A201', 'Scheduled', 'Buổi 6: Mảng và con trỏ');

-- Tiết học cho lớp D13CNPM1 - Cấu trúc dữ liệu
INSERT INTO sessions (class_id, session_date, start_time, end_time, room, status, notes) VALUES
((SELECT class_id FROM classes WHERE class_name = 'D13CNPM1 - Cấu trúc dữ liệu'), '2024-09-05', '07:00:00', '09:30:00', 'A202', 'Completed', 'Buổi 1: Giới thiệu cấu trúc dữ liệu'),
((SELECT class_id FROM classes WHERE class_name = 'D13CNPM1 - Cấu trúc dữ liệu'), '2024-09-12', '07:00:00', '09:30:00', 'A202', 'Completed', 'Buổi 2: Array và Linked List'),
((SELECT class_id FROM classes WHERE class_name = 'D13CNPM1 - Cấu trúc dữ liệu'), '2024-09-19', '07:00:00', '09:30:00', 'A202', 'Completed', 'Buổi 3: Stack và Queue'),
((SELECT class_id FROM classes WHERE class_name = 'D13CNPM1 - Cấu trúc dữ liệu'), '2024-09-26', '07:00:00', '09:30:00', 'A202', 'Completed', 'Buổi 4: Tree - Binary Tree'),
((SELECT class_id FROM classes WHERE class_name = 'D13CNPM1 - Cấu trúc dữ liệu'), '2024-10-03', '07:00:00', '09:30:00', 'A202', 'Scheduled', 'Buổi 5: Binary Search Tree');

-- ============================================================================
-- 5. CAMERA DEVICES (Thiết bị camera cho hệ thống)
-- ============================================================================

INSERT INTO camera_devices (device_name, device_code, stream_url, location, room, is_active) VALUES
('Camera phòng A101', 'CAM-A101', 'http://192.168.1.101:81/stream', 'Phòng học A101', 'A101', TRUE),
('Camera phòng A102', 'CAM-A102', 'http://192.168.1.102:81/stream', 'Phòng học A102', 'A102', TRUE),
('Camera phòng A103', 'CAM-A103', 'http://192.168.1.103:81/stream', 'Phòng học A103', 'A103', TRUE),
('Camera phòng A201', 'CAM-A201', 'http://192.168.1.201:81/stream', 'Phòng học A201', 'A201', TRUE),
('Camera phòng A202', 'CAM-A202', 'http://192.168.1.202:81/stream', 'Phòng học A202', 'A202', TRUE),
('Camera phòng B101', 'CAM-B101', 'http://192.168.1.111:81/stream', 'Phòng học B101', 'B101', FALSE),
('Camera Laptop', 'CAM-LAPTOP', '0', 'Camera laptop cho demo', 'Mobile', TRUE);

-- ============================================================================
-- END OF SAMPLE DATA
-- ============================================================================

-- Verify data
SELECT '=== TEACHERS ===' as info;
SELECT teacher_id, full_name, department FROM teachers ORDER BY teacher_id;

SELECT '=== SUBJECTS ===' as info;
SELECT subject_id, subject_name, credits FROM subjects ORDER BY subject_id;

SELECT '=== CLASSES ===' as info;
SELECT class_id, class_name, semester, academic_year FROM classes ORDER BY class_id;

SELECT '=== SESSIONS COUNT ===' as info;
SELECT c.class_name, COUNT(s.session_id) as total_sessions 
FROM classes c
LEFT JOIN sessions s ON c.class_id = s.class_id
GROUP BY c.class_name
ORDER BY c.class_name;

SELECT '=== CAMERA DEVICES ===' as info;
SELECT device_name, location, is_active FROM camera_devices ORDER BY device_id;
