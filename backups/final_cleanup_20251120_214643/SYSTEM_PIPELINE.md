# Pipeline Hệ Thống Điểm Danh Nhận Diện Khuôn Mặt

Tài liệu này mô tả chi tiết luồng xử lý (pipeline) của hệ thống, từ lúc thu nhận hình ảnh từ camera đến khi ghi nhận kết quả điểm danh vào cơ sở dữ liệu.

## 1. Tổng Quan Hệ Thống

Hệ thống hoạt động theo mô hình **Client-Server**:
*   **Edge Device (ESP32-CAM)**: Thu thập hình ảnh và stream qua mạng nội bộ.
*   **Desktop Client (Python/Tkinter)**: Xử lý AI (Nhận diện khuôn mặt) và giao diện người dùng.
*   **Backend Server (FastAPI)**: Quản lý dữ liệu nghiệp vụ (Sinh viên, Lớp học, Lịch sử điểm danh).

## 2. Chi Tiết Pipeline Xử Lý

### Giai đoạn 1: Thu Nhận Hình Ảnh (Image Acquisition)
*   **Thiết bị**: ESP32-CAM.
*   **Giao thức**: HTTP Stream (MJPEG).
*   **Đường dẫn**: `http://<ESP32_IP>/stream` (Mặc định: `192.168.1.169`).
*   **Định dạng**: Các frame ảnh JPEG được gửi liên tục.
*   **Xử lý tại Client**: `ESP32StreamReader` sử dụng `requests` để đọc stream và `cv2.imdecode` để giải mã thành numpy array (BGR format).

### Giai đoạn 2: Phát Hiện & Tiền Xử Lý (Detection & Preprocessing)
*   **Thư viện**: `InsightFace` (với `FaceAnalysis` app).
*   **Model**: `buffalo_l` (mặc định của InsightFace) hoặc tương đương.
*   **Quy trình**:
    1.  **Input**: Frame ảnh gốc từ camera (Full Resolution).
    2.  **Detection**: Xác định vị trí khuôn mặt (Bounding Box) và 5 điểm mốc (Landmarks).
    3.  **Alignment**: Cắt và xoay khuôn mặt dựa trên 5 điểm mốc để chuẩn hóa góc nhìn.
    4.  **Output**: Ảnh khuôn mặt đã chuẩn hóa (thường là 112x112 pixel).

### Giai đoạn 3: Trích Xuất Đặc Trưng (Feature Extraction)
*   **Model**: ArcFace (nằm trong pipeline của InsightFace).
*   **Input**: Ảnh khuôn mặt đã chuẩn hóa.
*   **Output**: Vector đặc trưng (Embedding) kích thước **512 chiều**.
*   **Đặc điểm**: Vector này đại diện cho danh tính của người đó. Các khuôn mặt của cùng một người sẽ có vector gần giống nhau (khoảng cách nhỏ).

### Giai đoạn 4: Nhận Dạng (Recognition & Matching)
*   **Cơ sở dữ liệu Vector**: File `dataset/face_embeddings.pkl` chứa dictionary `{student_id: [list_of_embeddings]}`.
*   **Thuật toán**: **Cosine Similarity** (Độ tương đồng Cosine).
*   **Công thức**:
    ```python
    similarity = dot(A, B) / (norm(A) * norm(B))
    ```
*   **Ngưỡng (Threshold)**: `0.50` (Nếu similarity > 0.50 thì coi là trùng khớp).
*   **Logic so khớp**:
    1.  So sánh vector khuôn mặt hiện tại với TẤT CẢ vector trong database.
    2.  Tìm vector có độ tương đồng cao nhất (`best_match`).
    3.  Nếu `best_match > threshold` -> **Nhận diện thành công**.
    4.  Ngược lại -> **Unknown**.

### Giai đoạn 5: Xử Lý Nghiệp Vụ (Business Logic)
*   **Cooldown**: `3.0 giây` (Ngăn chặn việc điểm danh liên tục cho cùng một người trong thời gian ngắn).
*   **Ghi nhận**:
    1.  Lưu trạng thái vào RAM (`attendance_records`).
    2.  Hiển thị tên sinh viên và độ chính xác lên màn hình (Box màu xanh).
    3.  Gửi dữ liệu điểm danh về Backend API (khi nhấn "Lưu" hoặc tự động tùy cấu hình).

## 3. Sơ Đồ Luồng Dữ Liệu (Data Flow)

```mermaid
graph TD
    A[ESP32-CAM] -->|MJPEG Stream| B(Desktop App)
    B -->|Frame Decoding| C{Face Detection}
    C -->|No Face| B
    C -->|Face Detected| D[Alignment & Crop]
    D -->|Normalized Face| E[Feature Extraction (ArcFace)]
    E -->|512d Vector| F{Matching (Cosine Sim)}
    F -->|Score < 0.5| G[Unknown Label]
    F -->|Score >= 0.5| H[Identify Student ID]
    H -->|Check Cooldown| I{Can Log?}
    I -->|No| B
    I -->|Yes| J[Mark Present]
    J -->|API Request| K[FastAPI Backend]
    K -->|SQL Insert| L[(Database)]
```

## 4. Cấu Hình Quan Trọng (`attendance_module.py`)

| Tham số | Giá trị Mặc định | Mô tả |
| :--- | :--- | :--- |
| `ESP32_CAM_IP` | `192.168.1.169` | Địa chỉ IP của Camera |
| `SIMILARITY_THRESHOLD` | `0.50` | Ngưỡng nhận diện (0.0 - 1.0) |
| `RECOGNITION_COOLDOWN` | `3.0` | Thời gian chờ giữa 2 lần điểm danh (giây) |
| `DETECTION_SIZE` | `(640, 640)` | Kích thước ảnh đầu vào cho model detection |

## 5. Quản Lý Dữ Liệu Training
*   **Ảnh thô**: Lưu tại `dataset/processed/{student_id}/`.
*   **Embeddings**: Được tính toán trước (Pre-computed) và lưu tại `dataset/face_embeddings.pkl` để tăng tốc độ nhận diện thực tế (không cần chạy lại model qua hàng nghìn ảnh mỗi frame).
