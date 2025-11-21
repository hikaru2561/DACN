# 🔬 PHÂN TÍCH KỸ THUẬT CHUYÊN SÂU (TECHNICAL DEEP DIVE)
## ESP32-CAM & INSIGHTFACE AI MODEL

---

## 1. 📷 ESP32-CAM: CẤU HÌNH & TỐI ƯU HÓA PHẦN CỨNG

### 1.1. Thông số Phần cứng (Hardware Specifications)
*   **Module:** ESP32-CAM (AI-Thinker).
*   **Vi điều khiển (MCU):** ESP32-S SoC (System on Chip).
    *   Core: Dual-core 32-bit LX6 Xtensa.
    *   Xung nhịp: 240 MHz.
    *   SRAM: 520 KB.
    *   **PSRAM (Quan trọng):** 4 MB (External Pseudo Static RAM) - *Bắt buộc để xử lý ảnh độ phân giải cao.*
*   **Cảm biến Camera:** OV2640.
    *   Độ phân giải tối đa: 2 Megapixels (1600x1200).
    *   Định dạng đầu ra: JPEG, BMP, YUV.

### 1.2. Cấu hình Firmware (Optimized Version)
Dựa trên firmware `CameraWebServer_Optimized.ino` đang sử dụng:

#### A. Cấu hình Độ phân giải & Bộ nhớ
```cpp
config.frame_size = FRAMESIZE_XGA;      // 1024x768 pixels
config.jpeg_quality = 15;               // Scale 0-63 (Thấp hơn = Nét hơn). 12-15 là mức cân bằng tốt nhất.
config.fb_count = 2;                    // Số lượng Frame Buffer trong PSRAM.
config.grab_mode = CAMERA_GRAB_LATEST;  // Luôn lấy frame mới nhất, bỏ qua frame cũ đang chờ.
```
*   **Tại sao XGA (1024x768)?** Đây là điểm ngọt (sweet spot) giữa độ chi tiết để nhận diện khuôn mặt ở xa và băng thông WiFi. VGA (640x480) quá mờ, UXGA (1600x1200) quá lag.
*   **Double Buffering (`fb_count = 2`):** Cho phép camera ghi frame mới vào buffer 2 trong khi hệ thống đang gửi frame từ buffer 1 đi. Tăng FPS đáng kể.

#### B. Tinh chỉnh Cảm biến (Sensor Tuning)
Các thiết lập này can thiệp trực tiếp vào thanh ghi (registers) của cảm biến OV2640:

| Tham số | Giá trị | Tác dụng |
| :--- | :--- | :--- |
| **Brightness** | `+1` | Tăng độ sáng tổng thể, giúp nhận diện tốt hơn trong phòng tối. |
| **Contrast** | `+1` | Tăng độ tương phản, làm nổi bật các đường nét khuôn mặt. |
| **Sharpness** | `+2` (Max) | Tăng độ sắc nét cạnh, giúp thuật toán phát hiện biên (edge detection) tốt hơn. |
| **AGC Gain** | `3` (0-30) | Giới hạn khuếch đại tín hiệu ở mức thấp để **giảm nhiễu hạt (noise)**. |
| **Auto White Balance** | `Enable` | Tự động cân bằng trắng, giúp màu da chính xác dưới ánh đèn huỳnh quang/LED. |
| **Lens Correction** | `Enable` | Khắc phục hiện tượng méo hình do thấu kính góc rộng. |

#### C. Tối ưu hóa WiFi & Đường truyền
```cpp
WiFi.setSleep(false);                // TẮT chế độ tiết kiệm năng lượng của WiFi.
WiFi.setTxPower(WIFI_POWER_19_5dBm); // Tăng công suất phát lên mức tối đa.
setsockopt(..., TCP_NODELAY, ...);   // Tắt thuật toán Nagle, gửi gói tin ngay lập tức (giảm độ trễ).
```
*   **Kết quả:** Giảm độ trễ (latency) từ ~500ms xuống <100ms, giúp trải nghiệm mượt mà.

---

## 2. 🧠 AI MODEL: INSIGHTFACE (BUFFALO_L)

Dự án sử dụng thư viện **InsightFace** với bộ model **`buffalo_l`**. Đây là một pipeline gồm nhiều model chuyên biệt phối hợp với nhau.

### 2.1. Kiến trúc Tổng quan
Pipeline xử lý một hình ảnh qua các bước:
`Input Image` -> **Detection (RetinaFace)** -> **Alignment (Landmarks)** -> **Recognition (ArcFace)** -> `512D Vector`

### 2.2. Chi tiết từng Model thành phần

#### A. Face Detection (Phát hiện khuôn mặt)
*   **Tên Model:** `det_10g.onnx`
*   **Kiến trúc:** **RetinaFace** (ResNet-50 backbone).
*   **Chức năng:** Tìm vị trí (bounding box) của tất cả khuôn mặt trong ảnh.
*   **Đặc điểm kỹ thuật:**
    *   **Input Size:** 640x640 (Auto resize).
    *   **Khả năng:** Phát hiện mặt rất nhỏ, mặt nghiêng, bị che khuất một phần.
    *   **Single-stage detector:** Tốc độ cực nhanh so với các thuật toán cũ (như MTCNN).

#### B. Face Alignment (Căn chỉnh khuôn mặt)
*   **Tên Model:** `1k3d68.onnx`
*   **Chức năng:** Xác định **5 điểm mốc chính** (2 mắt, đầu mũi, 2 khóe miệng) hoặc 68 điểm chi tiết 2D/3D.
*   **Tác dụng:** Dùng để xoay và cắt (crop) khuôn mặt về góc thẳng (frontalization) trước khi đưa vào nhận diện. Bước này cực kỳ quan trọng để tăng độ chính xác.

#### C. Face Recognition (Nhận diện/Trích xuất đặc trưng)
*   **Tên Model:** `w600k_r50.onnx`
*   **Kiến trúc:** **ResNet-50** (Residual Network 50 layers).
*   **Loss Function:** **ArcFace (Additive Angular Margin Loss)**.
    *   *Đây là "vũ khí bí mật" giúp InsightFace vượt trội hơn FaceNet hay Dlib.*
    *   ArcFace tối ưu hóa khoảng cách góc trên mặt cầu siêu chiều, giúp phân biệt các khuôn mặt giống nhau tốt hơn.
*   **Input:** Ảnh mặt đã căn chỉnh (112x112 pixels).
*   **Output:** Vector đặc trưng **512 chiều** (512-dimensional embedding).
*   **Dữ liệu huấn luyện:** WebFace600K (600,000 identities).

#### D. Gender & Age (Giới tính & Tuổi)
*   **Tên Model:** `genderage.onnx`
*   **Chức năng:** Dự đoán giới tính và độ tuổi (Tính năng phụ trợ).

### 2.3. Tại sao chọn InsightFace (Buffalo_L)?

| Tiêu chí | InsightFace (Buffalo_L) | Dlib (ResNet-34) | FaceNet |
| :--- | :--- | :--- | :--- |
| **Độ chính xác (LFW)** | **99.83%** | 99.38% | 99.63% |
| **Backbone** | ResNet-50 | ResNet-34 | Inception-ResNet |
| **Kích thước Vector** | 512 | 128 | 128/512 |
| **Tốc độ (CPU)** | ~20ms | ~100ms (Rất chậm) | ~50ms |
| **Khả năng chống nhiễu**| Rất tốt (Góc nghiêng, tối) | Trung bình | Khá |

### 2.4. Cơ chế So khớp (Matching Mechanism)
Hệ thống sử dụng **Cosine Similarity** (Độ tương đồng Cosine) để so sánh hai vector 512 chiều.

*   Công thức: $Similarity = \cos(\theta) = \frac{A \cdot B}{\|A\| \|B\|}$
*   **Ngưỡng (Threshold):** `0.50`
    *   Nếu Similarity > 0.50: Cùng một người.
    *   Nếu Similarity < 0.50: Người lạ.

---

## 3. 📊 TỔNG KẾT THÔNG SỐ DỰ ÁN

### Cấu hình Camera (ESP32-CAM)
*   **Resolution:** 1024x768 (XGA)
*   **FPS:** 40-100 (Adaptive)
*   **Stream:** MJPEG over HTTP
*   **Latency:** < 100ms

### Cấu hình AI (Desktop App)
*   **Detection Model:** RetinaFace (ResNet50)
*   **Recognition Model:** ArcFace (ResNet50)
*   **Embedding Size:** 512 floats
*   **Input Size:** 640x640 (Detection), 112x112 (Recognition)
*   **Inference Time:** ~30-50ms tổng cộng (trên CPU Intel Core i5/i7 gen 10+)

---
*Tài liệu được biên soạn ngày 21/11/2025 cho Đồ án Chuyên ngành.*
