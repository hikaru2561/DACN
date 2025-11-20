# 📘 TÀI LIỆU TOÀN DIỆN DỰ ÁN - HỆ THỐNG ĐIỂM DANH NHẬN DẠNG KHUÔN MẶT
**(Comprehensive Project Documentation - Face Recognition Attendance System)**

---

## 📑 MỤC LỤC

1.  [Tổng Quan Dự Án](#1-tổng-quan-dự-án)
2.  [Kiến Trúc Hệ Thống](#2-kiến-trúc-hệ-thống)
3.  [Quy Trình Kỹ Thuật (System Pipeline)](#3-quy-trình-kỹ-thuật-system-pipeline)
4.  [Cấu Trúc Dự Án (Project Structure)](#4-cấu-trúc-dự-án-project-structure)
5.  [Chi Tiết Model AI (Buffalo_L)](#5-chi-tiết-model-ai-buffalo_l)
6.  [Hướng Dẫn Cài Đặt & Sử Dụng](#6-hướng-dẫn-cài-đặt--sử-dụng)
7.  [Hướng Dẫn ESP32-CAM](#7-hướng-dẫn-esp32-cam)
8.  [API Documentation](#8-api-documentation)
9.  [Đánh Giá & Roadmap](#9-đánh-giá--roadmap)

---

## 1. 🎯 TỔNG QUAN DỰ ÁN

**Tên dự án:** Face Recognition Attendance System (Hệ thống Điểm danh Nhận dạng Khuôn mặt)
**Phiên bản:** 1.0.0 (Professional Refactored)

### 1.1. Giới thiệu
Dự án này là một giải pháp điểm danh tự động, hiện đại, sử dụng camera ESP32-CAM để thu nhận hình ảnh và áp dụng các mô hình Deep Learning tiên tiến để nhận dạng sinh viên trong thời gian thực. Hệ thống bao gồm một ứng dụng Desktop quản lý toàn diện và một Backend API mạnh mẽ.

### 1.2. Tính năng chính
*   **Điểm danh tự động:** Nhận diện khuôn mặt từ luồng video trực tiếp (ESP32-CAM).
*   **Quản lý toàn diện:** Sinh viên, Giảng viên, Môn học, Lớp học, Buổi học.
*   **Báo cáo & Thống kê:** Xem lịch sử điểm danh, xuất báo cáo, thống kê tỷ lệ chuyên cần.
*   **Quản lý Camera:** Thêm, sửa, xóa, xem trạng thái các thiết bị camera.
*   **Chất lượng cao:** Kiểm tra chất lượng ảnh đầu vào (độ sáng, sắc nét, góc mặt) trước khi training.

---

## 2. 🏗️ KIẾN TRÚC HỆ THỐNG

Hệ thống được xây dựng theo mô hình Client-Server với 3 tầng chính:

### 2.1. Tầng Phần Cứng (Hardware Layer)
*   **Thiết bị:** ESP32-CAM AI-Thinker.
*   **Vai trò:** Thu thập hình ảnh/video stream và gửi về Desktop App qua WiFi.
*   **Giao thức:** HTTP Stream (MJPEG).

### 2.2. Tầng Ứng Dụng (Application Layer - Desktop)
*   **Công nghệ:** Python, Tkinter (GUI).
*   **Vai trò:**
    *   Giao diện người dùng (Quản lý, Điểm danh, Báo cáo).
    *   Xử lý ảnh & AI (Face Detection, Recognition).
    *   Giao tiếp với Backend API.
*   **Thư viện AI:** InsightFace (ArcFace), MediaPipe, OpenCV.

### 2.3. Tầng Backend & Dữ Liệu (Backend & Data Layer)
*   **Công nghệ:** Python, FastAPI.
*   **Cơ sở dữ liệu:** PostgreSQL.
*   **Vai trò:**
    *   Cung cấp RESTful API cho Desktop App.
    *   Lưu trữ thông tin người dùng, sinh viên, lớp học, lịch sử điểm danh.
    *   Xử lý logic nghiệp vụ và thống kê.

---

## 3. ⚙️ QUY TRÌNH KỸ THUẬT (SYSTEM PIPELINE)

Quy trình cốt lõi từ lúc thu nhận hình ảnh đến khi nhận dạng thành công:

### 3.1. Thu Nhận Hình Ảnh (ESP32-CAM)
*   Camera phát luồng video MJPEG (800x600 resolution).
*   Firmware tối ưu cho tốc độ và độ trễ thấp.

### 3.2. Tiền Xử Lý & Thu Thập Dữ Liệu (Data Collection)
1.  **Đọc Stream:** Desktop App kết nối và đọc từng frame hình.
2.  **Phát hiện mặt (Face Detection):** Sử dụng **MediaPipe** để tìm vị trí khuôn mặt.
3.  **Kiểm tra chất lượng (Quality Check):** Đánh giá ảnh dựa trên:
    *   Độ sắc nét (Sharpness - Laplacian variance).
    *   Độ sáng (Brightness).
    *   Kích thước (Size).
    *   Độ tương phản (Contrast).
    *   *Chỉ lưu ảnh nếu điểm chất lượng > 65.*
4.  **Lưu trữ:** Lưu ảnh gốc (crop) vào `dataset/processed/{student_id}/`.

### 3.3. Trích Xuất Đặc Trưng (Feature Extraction / "Training")
1.  **Input:** Đọc 20 ảnh chất lượng cao của mỗi sinh viên.
2.  **Model:** Sử dụng **InsightFace (ArcFace)**.
3.  **Process:**
    *   Face Alignment (Căn chỉnh).
    *   Normalization (Chuẩn hóa).
    *   Embedding Extraction (Trích xuất vector 512 chiều).
4.  **Output:** Lưu toàn bộ embeddings vào file `dataset/face_embeddings.pkl`.

### 3.4. Nhận Dạng Thời Gian Thực (Real-time Recognition)
1.  **Input:** Frame hình từ Camera Stream.
2.  **Detection:** Tìm khuôn mặt bằng RetinaFace/MediaPipe.
3.  **Embedding:** Trích xuất vector 512 chiều cho khuôn mặt vừa tìm thấy.
4.  **Matching:** So sánh vector này với CSDL `face_embeddings.pkl` bằng **Cosine Similarity**.
5.  **Decision:** Nếu độ tương đồng > `0.50` (Threshold) -> **Nhận dạng thành công**.

---

## 4. 📂 CẤU TRÚC DỰ ÁN (PROJECT STRUCTURE)

Dự án được tổ chức theo cấu trúc chuyên nghiệp, phân tách rõ ràng giữa Backend và Desktop.

```
DACN/
├── attendance_system/
│   │
│   ├── backend/                        # ⭐ BACKEND (FastAPI)
│   │   ├── app/
│   │   │   ├── api/                    # API Routes (Endpoints)
│   │   │   ├── core/                   # Config, Database connection
│   │   │   ├── models/                 # SQLAlchemy Models (DB Schema)
│   │   │   ├── schemas/                # Pydantic Schemas (Validation)
│   │   │   └── main.py                 # Entry point (New structure)
│   │   ├── main.py                     # Entry point (Old - running)
│   │   └── ...
│   │
│   ├── desktop/                        # ⭐ DESKTOP (Tkinter)
│   │   ├── app/
│   │   │   ├── core/                   # API Client, Constants, Config
│   │   │   ├── modules/                # Feature Modules
│   │   │   │   ├── student/            # Quản lý sinh viên
│   │   │   │   ├── teacher/            # Quản lý giảng viên
│   │   │   │   ├── attendance/         # Điểm danh & Lịch sử
│   │   │   │   ├── camera/             # Quản lý Camera
│   │   │   │   └── ...                 # (Subject, Class, Session, Report)
│   │   │   └── main.py                 # Entry point
│   │   └── ...
│   │
│   └── database/                       # Database Scripts
│       └── schema.sql                  # SQL tạo bảng
│
├── client/                             # Scripts cho ESP32/Client test
├── dataset/                            # Dữ liệu ảnh & Embeddings
├── docs/                               # Tài liệu dự án
└── ...
```

---

## 5. 🤖 CHI TIẾT MODEL AI (BUFFALO_L)

Hệ thống sử dụng bộ model `buffalo_l` của InsightFace.

### 5.1. Thông tin Model
*   **Vị trí:** `C:\Users\[User]\.insightface\models\buffalo_l\`
*   **Tổng kích thước:** ~325 MB
*   **Thành phần:**
    *   `w600k_r50.onnx` (166 MB): **Face Recognition** (ArcFace ResNet-50).
    *   `1k3d68.onnx` (137 MB): **3D Face Alignment**.
    *   `det_10g.onnx` (16 MB): **Face Detection**.
    *   `genderage.onnx` (1.2 MB): **Gender & Age**.

### 5.2. Tại sao chọn Buffalo_L?
*   **Độ chính xác:** ~99.8% trên tập LFW benchmark.
*   **Tốc độ:** ~10-20ms/face trên CPU (phù hợp với laptop thông thường).
*   **Kích thước:** Vừa phải, cân bằng giữa hiệu năng và tài nguyên.

### 5.3. Cấu hình trong Code
```python
FACE_RECOGNITION_CONFIG = {
    "model_name": "buffalo_l",
    "ctx_id": 0,              # 0 = CPU
    "det_size": (640, 640),   # Kích thước detection (càng lớn càng chính xác nhưng chậm)
    "similarity_threshold": 0.50
}
```

---

## 6. 🚀 HƯỚNG DẪN CÀI ĐẶT & SỬ DỤNG

### 6.1. Yêu cầu hệ thống
*   Python 3.8+
*   PostgreSQL
*   Webcam hoặc ESP32-CAM

### 6.2. Cài đặt Backend
1.  Di chuyển vào thư mục backend: `cd attendance_system/backend`
2.  Cài đặt thư viện: `pip install -r requirements.txt`
3.  Cấu hình Database:
    *   Tạo database `attendance_db` trong PostgreSQL.
    *   Chạy script `database/schema.sql` để tạo bảng.
    *   Cập nhật `DATABASE_URL` trong `.env` hoặc `app/core/config.py`.
4.  Chạy Server: `python main.py` (Server sẽ chạy tại `http://localhost:8000`).

### 6.3. Cài đặt Desktop App
1.  Di chuyển vào thư mục desktop: `cd attendance_system/desktop`
2.  Cài đặt thư viện: `pip install -r requirements.txt`
3.  Chạy ứng dụng: `python -m app.main`

### 6.4. Sử dụng
1.  **Đăng nhập:** Sử dụng tài khoản Admin (mặc định `admin`/`admin` nếu đã seed data).
2.  **Quản lý:** Thêm Giảng viên, Môn học, Lớp học, Sinh viên.
3.  **Thu thập dữ liệu:** Vào module Sinh viên -> Chọn sinh viên -> Chụp ảnh (20 tấm).
4.  **Training:** Nhấn nút "Training Data" để tạo embeddings.
5.  **Điểm danh:** Vào module Điểm danh -> Chọn Lớp/Buổi học -> Bắt đầu điểm danh.

---

## 7. 📸 HƯỚNG DẪN ESP32-CAM

### 7.1. Cài đặt Firmware
1.  Sử dụng **Arduino IDE**.
2.  Mở project trong thư mục `esp32-camera/`.
3.  Cấu hình WiFi và Server IP trong `CameraWebServer.ino`:
    ```cpp
    const char* ssid = "YOUR_WIFI_SSID";
    const char* password = "YOUR_WIFI_PASSWORD";
    ```
4.  Upload code lên board **ESP32 Wrover Module**.

### 7.2. Sử dụng
*   Mở Serial Monitor để xem IP của ESP32.
*   Truy cập IP đó trên trình duyệt để xem giao diện web.
*   Stream URL: `http://[ESP32_IP]/stream` (dùng để nhập vào Desktop App).

---

## 8. 🔌 API DOCUMENTATION

Backend cung cấp đầy đủ các API RESTful. Truy cập `http://localhost:8000/docs` (Swagger UI) để xem chi tiết và test trực tiếp.

Các nhóm API chính:
*   `/api/students`: CRUD sinh viên.
*   `/api/teachers`: CRUD giảng viên.
*   `/api/subjects`: CRUD môn học.
*   `/api/classes`: Quản lý lớp học & ghi danh.
*   `/api/sessions`: Quản lý buổi học.
*   `/api/attendance`: Ghi nhận & xem lịch sử điểm danh.
*   `/api/cameras`: Quản lý thiết bị camera.
*   `/api/reports`: Thống kê báo cáo.

---

## 9. 📊 ĐÁNH GIÁ & ROADMAP

### 9.1. Trạng thái hiện tại (Professional Grade - 82/100)
*   ✅ **Cấu trúc:** Xuất sắc, module hóa cao.
*   ✅ **Tính năng:** Đầy đủ các chức năng cốt lõi.
*   ✅ **Tài liệu:** Rất chi tiết và đầy đủ.
*   ⚠️ **Testing:** Chưa có Unit Test/Integration Test.
*   ⚠️ **Security:** Cần bổ sung Authentication (JWT).

### 9.2. Kế hoạch phát triển (Roadmap)
*   **Ngắn hạn (2 tuần):**
    *   Viết Unit Tests (pytest).
    *   Thêm xác thực người dùng (JWT Authentication).
    *   Hoàn thiện migration code Backend sang cấu trúc mới (`app/`).
*   **Trung hạn (1 tháng):**
    *   Docker hóa ứng dụng (Backend + DB).
    *   Thiết lập CI/CD Pipeline.
    *   Tối ưu hóa hiệu năng nhận diện.
*   **Dài hạn:**
    *   Phát triển Web Dashboard (React/Vue).
    *   Mở rộng hỗ trợ nhiều camera cùng lúc.

---
*Tài liệu được tổng hợp tự động ngày 20/11/2025.*
