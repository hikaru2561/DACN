# 🎓 BÁO CÁO SƠ BỘ ĐỒ ÁN CHUYÊN NGÀNH
## ĐỀ TÀI: HỆ THỐNG ĐIỂM DANH TỰ ĐỘNG NHẬN DIỆN KHUÔN MẶT (FACE RECOGNITION ATTENDANCE SYSTEM)

---

## 1. 🎯 TỔNG QUAN & LÝ DO CHỌN ĐỀ TÀI

### 1.1. Đặt vấn đề
- Việc điểm danh thủ công tại các trường đại học tốn nhiều thời gian và dễ xảy ra sai sót/gian lận.
- Các giải pháp thẻ từ hay vân tay yêu cầu tiếp xúc vật lý và có thể gây ùn tắc.
- Nhu cầu về một hệ thống tự động hóa, chính xác và hiện đại trong kỷ nguyên số.

### 1.2. Mục tiêu đề tài
- Xây dựng hệ thống điểm danh **tự động hoàn toàn** sử dụng Camera AI.
- Đảm bảo độ chính xác cao (>99%) và tốc độ nhận diện nhanh (Real-time).
- Quản lý tập trung dữ liệu sinh viên, lớp học và lịch sử ra vào.
- Tối ưu hóa chi phí phần cứng bằng việc sử dụng **ESP32-CAM**.

---

## 2. 🏗️ GIẢI PHÁP CÔNG NGHỆ & KIẾN TRÚC

### 2.1. Mô hình tổng thể (3-Tier Architecture)
Hệ thống hoạt động theo mô hình 3 tầng tách biệt, đảm bảo hiệu năng và dễ dàng mở rộng:

1.  **Tầng Thu Thập (Hardware Layer):**
    *   **Thiết bị:** ESP32-CAM (AI-Thinker).
    *   **Chức năng:** Stream video chất lượng cao (XGA 1024x768) qua WiFi.
    *   **Giao thức:** MJPEG Stream, HTTP REST.

2.  **Tầng Ứng Dụng (Application Layer - Desktop App):**
    *   **Ngôn ngữ:** Python 3.8+.
    *   **Giao diện:** Tkinter (Modern UI).
    *   **AI Core:** InsightFace (Model Buffalo_L) cho nhận diện, MediaPipe cho phát hiện khuôn mặt.
    *   **Chức năng:** Xử lý hình ảnh, hiển thị thông tin, quản lý sinh viên.

3.  **Tầng Dữ Liệu & API (Backend Layer):**
    *   **Framework:** FastAPI (High performance).
    *   **Database:** PostgreSQL (Lưu trữ dữ liệu lớn, ổn định).
    *   **ORM:** SQLAlchemy & Pydantic.

### 2.2. Công nghệ AI nổi bật
- **Model:** InsightFace (Buffalo_L).
- **Thuật toán:** ArcFace (State-of-the-art trong nhận diện khuôn mặt).
- **Độ chính xác:** ~99.8% trên tập dữ liệu chuẩn LFW.
- **Quy trình xử lý:**
    1.  Phát hiện mặt (Detection).
    2.  Căn chỉnh mặt 3D (Alignment).
    3.  Trích xuất đặc trưng (Feature Extraction -> 512D Vector).
    4.  So khớp (Cosine Similarity Matching).

---

## 3. ✨ TÍNH NĂNG ĐÃ HOÀN THIỆN

### 3.1. Quản lý Sinh viên & Dữ liệu
- ✅ Thêm/Sửa/Xóa thông tin sinh viên chi tiết.
- ✅ **Thu thập dữ liệu thông minh:** Tự động chụp 20 ảnh chất lượng cao, lọc ảnh mờ/tối/nghiêng.
- ✅ **Training nhanh:** Tạo vector đặc trưng chỉ trong vài giây.

### 3.2. Điểm danh Thời gian thực
- ✅ Kết nối luồng video từ ESP32-CAM (Low latency).
- ✅ Nhận diện đa khuôn mặt cùng lúc.
- ✅ Hiển thị thông tin sinh viên ngay lập tức trên màn hình.
- ✅ Ghi nhận thời gian vào/ra chính xác.

### 3.3. Quản lý Lớp học & Báo cáo
- ✅ Quản lý Môn học, Lớp học, Buổi học.
- ✅ Xem lịch sử điểm danh trực quan.
- ✅ Xuất báo cáo thống kê (Dự kiến).

---

## 4. 📊 KẾT QUẢ THỰC NGHIỆM (SƠ BỘ)

### 4.1. Hiệu năng Phần cứng (ESP32-CAM)
- **Độ phân giải:** 1024x768 (XGA).
- **Tốc độ khung hình:** 40-100 FPS (Adaptive).
- **Chất lượng ảnh:** Sắc nét, đã tối ưu độ sáng và tương phản.

### 4.2. Hiệu năng Nhận diện
- **Tốc độ xử lý:** ~15-20ms/khuôn mặt (trên CPU Laptop).
- **Độ chính xác:** Nhận diện đúng hầu hết các trường hợp góc nghiêng nhẹ, đeo kính.
- **Ngưỡng tin cậy:** 0.50 (Cosine Similarity).

---

## 5. 🚀 KẾ HOẠCH PHÁT TRIỂN TIẾP THEO

### Giai đoạn 1 (Hoàn thiện - Hiện tại)
- [x] Tái cấu trúc mã nguồn (Refactoring) sang dạng Modular chuyên nghiệp.
- [x] Kết nối ổn định Database PostgreSQL.
- [x] Tối ưu hóa Firmware ESP32-CAM.

### Giai đoạn 2 (Nâng cao - Sắp tới)
- [ ] Tích hợp bảo mật (Đăng nhập, Phân quyền).
- [ ] Xây dựng Web Dashboard cho giảng viên xem báo cáo từ xa.
- [ ] Đóng gói ứng dụng (File .exe) để dễ dàng cài đặt.

---

## 6. 📝 KẾT LUẬN
Đồ án đã xây dựng thành công một hệ thống điểm danh hoàn chỉnh từ phần cứng đến phần mềm. Hệ thống đáp ứng tốt các yêu cầu về tốc độ, độ chính xác và tính ổn định, sẵn sàng cho việc thử nghiệm thực tế tại lớp học.

---
*Người thực hiện: [Tên của bạn]*
*Lớp/MSSV: [Thông tin của bạn]*
*Ngày báo cáo: 21/11/2025*
