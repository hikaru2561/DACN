
#  Hệ Thống Điểm Danh Nhận Dạng Khuôn Mặt

Dự án này là một hệ thống điểm danh tự động, sử dụng camera ESP32-CAM để thu nhận hình ảnh và áp dụng các mô hình Deep Learning để nhận dạng sinh viên trong thời gian thực.

## 🎯 Mục Tiêu Hoàn Thiện

1.  **Hoàn thiện Giao diện Người dùng (UI):** Xây dựng đầy đủ các chức năng còn thiếu trong ứng dụng Desktop (Quản lý giảng viên, môn học, báo cáo thống kê).
2.  **Tích hợp API Backend:** Kết nối hoàn chỉnh các chức năng của ứng dụng Desktop với API để quản lý dữ liệu tập trung tại database.
3.  **Tối ưu Hiệu năng:** Cải thiện tốc độ nhận dạng, giảm độ trễ của stream và tối ưu hóa việc sử dụng tài nguyên.
4.  **Triển khai Thực tế:** Đóng gói ứng dụng, xây dựng trình cài đặt và hướng dẫn chi tiết để có thể triển khai trên các máy tính khác nhau.
5.  **Nâng cao Độ chính xác:** Nghiên cứu các phương pháp để cải thiện độ chính xác của mô hình trong các điều kiện ánh sáng yếu, góc mặt nghiêng, hoặc khi có vật cản.

---

## ⚙️ Quy Trình Kỹ Thuật Chi Tiết: Camera và Nhận Dạng Khuôn Mặt

Đây là luồng xử lý cốt lõi của hệ thống, từ lúc hình ảnh được ghi lại cho đến khi một sinh viên được nhận dạng.

### Tầng 1: Thu Nhận Hình Ảnh (Hardware - ESP32-CAM)

Thành phần chính là module **ESP32-CAM AI-Thinker** chạy firmware tùy chỉnh (`CameraWebServer_Optimized.ino`) được tối ưu cho tốc độ và chất lượng.

-   **Phương thức:** Module camera hoạt động như một web server, phát một luồng video (stream) theo định dạng MJPEG qua mạng WiFi.
-   **Công cụ:**
    -   **Hardware:** ESP32-CAM AI-Thinker.
    -   **Firmware:** Code C++ trên nền tảng Arduino.
-   **Cấu hình tối ưu (Smooth Mode):**
    -   **Độ phân giải:** `SVGA (800x600)` - Cân bằng giữa chi tiết và tốc độ.
    -   **Chất lượng JPEG:** `10` (thang 0-63, số càng nhỏ chất lượng càng cao) - Giảm dung lượng mỗi khung hình để tăng FPS.
    -   **Frame Buffer:** `2` - Sử dụng 2 bộ đệm giúp stream mượt mà, không bị "giật" hình.
    -   **Chế độ Grab:** `CAMERA_GRAB_WHEN_EMPTY` - Đảm bảo không bỏ sót khung hình nào, ưu tiên sự mượt mà.
    -   **Stream URL:** `http://192.168.243.176/stream` (địa chỉ IP của ESP32-CAM).
-   **Thư viện hỗ trợ:** `esp_camera.h`, `WiFi.h`, `esp_http_server.h`.

### Tầng 2: Chụp và Tiền Xử Lý Ảnh (Desktop App - `camera_capture_module.py`)

Đây là bước lấy dữ liệu đầu vào để "huấn luyện" cho hệ thống. Mục tiêu là thu thập 20 tấm ảnh khuôn mặt chất lượng cao cho mỗi sinh viên.

1.  **Đọc Stream từ ESP32-CAM:**
    -   **Phương thức:** Một luồng riêng (`ESP32StreamReader`) được khởi chạy để kết nối liên tục đến Stream URL của ESP32-CAM. Nó đọc dữ liệu MJPEG, giải mã thành từng khung hình (frame) và đưa vào bộ đệm.
    -   **Công cụ:** Python, `requests`, `OpenCV`.

2.  **Phát hiện Khuôn mặt (Face Detection):**
    -   **Phương thức:** Trên mỗi khung hình nhận được từ stream, hệ thống sử dụng mô hình **MediaPipe Face Detection** để xác định vị trí của các khuôn mặt.
    -   **Công cụ:** Thư viện `mediapipe` của Google.
    -   **Cấu hình:**
        -   `min_detection_confidence`: `0.6` (chỉ chấp nhận các phát hiện có độ tin cậy > 60%).
        -   `model_selection`: `1` (mô hình cho khoảng cách xa, phù hợp với camera giám sát).
    -   **Kết quả:** Trả về tọa độ `bounding box` (khung chữ nhật bao quanh khuôn mặt).

3.  **Kiểm tra Chất lượng Ảnh (`FaceQualityChecker`):**
    -   **Phương thức:** Đây là một bước cực kỳ quan trọng. Mỗi khuôn mặt được phát hiện sẽ được đánh giá chất lượng dựa trên 4 tiêu chí để đảm bảo dữ liệu training tốt. Một điểm tổng hợp (0-100) được tính toán.
    -   **Công cụ:** `OpenCV`, `Numpy`.
    -   **Các tiêu chí đánh giá:**
        -   **Độ sắc nét (Sharpness - 40% trọng số):** Tính toán bằng phương pháp `Laplacian variance`. Ảnh mờ sẽ có chỉ số thấp.
        -   **Độ sáng (Brightness - 25% trọng số):** Tính giá trị độ sáng trung bình của vùng mặt.
        -   **Kích thước (Size - 20% trọng số):** Khuôn mặt phải đủ lớn trong khung hình.
        -   **Độ tương phản (Contrast - 15% trọng số):** Tính độ lệch chuẩn của các pixel.
    -   **Ngưỡng chất lượng:** `MIN_QUALITY_SCORE = 65`. Chỉ những ảnh có điểm tổng hợp từ 65 trở lên mới được xem là hợp lệ.

4.  **Tự động Chụp và Lưu trữ:**
    -   **Phương thức:** Khi hệ thống tìm thấy một khuôn mặt đạt ngưỡng chất lượng, nó sẽ tự động cắt (crop) vùng mặt đó ra khỏi khung hình gốc và lưu lại.
    -   **Logic:**
        -   Chụp đủ `TARGET_PHOTOS = 20` ảnh chất lượng.
        -   Sau mỗi lần chụp, hệ thống sẽ tạm dừng `CAPTURE_COOLDOWN = 0.5` giây để tránh chụp các ảnh quá giống nhau.
    -   **Lưu trữ:**
        -   **Đường dẫn:** `dataset/processed/{mã_sinh_viên}/`.
        -   **Định dạng:** Ảnh được lưu là file `.jpg`.
        -   **Quan trọng:** Ảnh được lưu là **ảnh gốc đã crop**, **không resize** để giữ lại nhiều thông tin nhất có thể.

### Tầng 3: Xây dựng Cơ sở dữ liệu và Nhận dạng (Desktop App - `attendance_module.py`)

Đây là "bộ não" của hệ thống, nơi các mô hình Deep Learning thực hiện nhiệm vụ.

1.  **Xây dựng "Huấn luyện" (Build Embeddings):**
    -   **Phương thức:** Quá trình này không phải là "training" lại model, mà là dùng model đã được huấn luyện sẵn để trích xuất "đặc trưng" của từng sinh viên và lưu lại.
    -   **Công cụ:** Thư viện `insightface`, model `buffalo_l` (dựa trên kiến trúc ArcFace).
    -   **Quy trình:**
        1.  Hệ thống đọc 20 ảnh chất lượng cao đã lưu ở Tầng 2.
        2.  Với mỗi ảnh, hàm `rec_model.get_feat()` của InsightFace được gọi. Bên trong, thư viện sẽ tự động:
            -   Căn chỉnh khuôn mặt (face alignment).
            -   Resize ảnh về kích thước chuẩn `112x112` pixels.
            -   Chuẩn hóa (normalize) dữ liệu.
            -   Đưa vào mạng nơ-ron **ArcFace** để trích xuất đặc trưng.
        3.  **Kết quả:** Mỗi khuôn mặt được chuyển đổi thành một vector 512 chiều (gọi là **embedding**). Vector này là một chuỗi 512 con số, đại diện cho các đặc tính độc nhất của khuôn mặt đó.
    -   **Lưu trữ:** Toàn bộ embeddings của tất cả sinh viên được tổng hợp vào một file duy nhất: `dataset/face_embeddings.pkl`. File này hoạt động như một cơ sở dữ liệu vector.

2.  **Nhận dạng Thời gian thực (Real-time Recognition):**
    -   **Phương thức:** Khi chức năng điểm danh được bật, hệ thống lặp lại quy trình sau trên mỗi khung hình từ stream của ESP32-CAM.
    -   **Quy trình:**
        1.  **Phát hiện khuôn mặt:** Dùng **RetinaFace** (một phần của InsightFace) để tìm khuôn mặt trong khung hình.
        2.  **Trích xuất Embedding:** Với mỗi khuôn mặt phát hiện được, trích xuất vector embedding 512 chiều của nó (giống như bước "huấn luyện").
        3.  **So sánh và Tìm kiếm:**
            -   Lấy vector embedding vừa trích xuất.
            -   So sánh nó với **tất cả** các vector đã được lưu trong file `face_embeddings.pkl` bằng phép toán **Cosine Similarity**.
            -   Phép toán này đo góc giữa hai vector, trả về một giá trị từ -1 đến 1. Giá trị càng gần 1, hai khuôn mặt càng giống nhau.
        4.  **Xác định danh tính:**
            -   Nếu điểm tương đồng trung bình với một sinh viên nào đó trong CSDL vượt qua ngưỡng `SIMILARITY_THRESHOLD = 0.50`, hệ thống xác định đó là sinh viên đó.
            -   Tên và điểm số tương đồng sẽ được vẽ lên màn hình.
            -   Một cơ chế `RECOGNITION_COOLDOWN = 3.0` giây được áp dụng để tránh điểm danh liên tục cho cùng một người.

-   **Thư viện hỗ trợ:** `insightface`, `onnxruntime` (để chạy model), `numpy`, `opencv-python`, `pickle`.

---

## สรุป (Tóm tắt luồng)

```
1. ESP32-CAM: Phát video 800x600 qua WiFi.
   ↓
2. Desktop App (Lấy mẫu):
   - Đọc stream.
   - Dùng MediaPipe tìm mặt.
   - Dùng OpenCV chấm điểm chất lượng (sắc nét, sáng, ...).
   - Nếu điểm > 65, lưu ảnh gốc đã crop vào `dataset/processed/`.
   ↓
3. Desktop App (Training):
   - Đọc các ảnh đã lưu.
   - Dùng InsightFace (ArcFace) chuyển mỗi ảnh thành vector 512 chiều.
   - Lưu tất cả vector vào file `face_embeddings.pkl`.
   ↓
4. Desktop App (Điểm danh):
   - Đọc stream.
   - Dùng InsightFace tìm mặt và tạo vector cho mặt đó.
   - So sánh vector này với CSDL `face_embeddings.pkl` bằng Cosine Similarity.
   - Nếu điểm > 0.50 → Nhận dạng thành công!
```
