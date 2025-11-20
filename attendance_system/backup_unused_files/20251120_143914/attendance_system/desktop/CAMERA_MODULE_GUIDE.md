# 📸 Camera Capture Module - Hướng dẫn sử dụng

## Tổng quan

Module chụp ảnh khuôn mặt sinh viên với các tính năng:
- Kết nối ESP32-CAM qua WiFi stream
- Phát hiện khuôn mặt tự động (MediaPipe)
- Đánh giá chất lượng ảnh (Brightness, Sharpness, Contrast)
- Tự động chụp 20 ảnh chất lượng cao
- Tiền xử lý ảnh (112x112 grayscale + CLAHE)

## Cách sử dụng

### 1. Chuẩn bị ESP32-CAM

```
1. Kết nối ESP32-CAM vào WiFi
2. Ghi nhớ IP address (mặc định: 192.168.243.176)
3. Upload code CameraWebServer_Optimized.ino
4. Mở Serial Monitor kiểm tra stream URL: http://<IP>/stream
```

### 2. Chụp ảnh từ Desktop App

```
1. Mở Desktop App → Quản lý Sinh viên
2. Chọn sinh viên cần chụp ảnh
3. Nhấn nút "📷 Chụp ảnh"
4. Cửa sổ Camera tự động mở
5. Đứng trước camera, hướng mặt thẳng
6. Hệ thống tự động chụp 20 ảnh (màu xanh = chất lượng tốt)
7. Đợi đến khi đủ 20 ảnh → Hoàn thành
```

### 3. Lưu ảnh

Ảnh được lưu tại:
```
dataset/processed/{MSSV}/
  ├── 2280602549_20250107_143052_123_q85.jpg
  ├── 2280602549_20250107_143053_456_q92.jpg
  └── ... (20 ảnh)
```

**Format filename:** `{MSSV}_{timestamp}_{quality}.jpg`
- `MSSV`: Mã số sinh viên
- `timestamp`: YYYYmmdd_HHMMSs_ms
- `quality`: q{score} (0-100)

## Chất lượng ảnh

### Indicators trên màn hình:

- 🟢 **GREEN BOX (GOOD)**: Quality ≥ 65 → Ảnh tốt, sẽ được lưu
- 🟡 **YELLOW BOX (OK)**: Quality 40-64 → Ảnh tạm được
- 🔴 **RED BOX (POOR)**: Quality < 40 → Ảnh kém, không lưu

### Tiêu chí đánh giá (0-100):

1. **Brightness (25%)**: Độ sáng (80-180 tốt nhất)
2. **Sharpness (40%)**: Độ nét (Laplacian variance)
3. **Contrast (15%)**: Độ tương phản
4. **Size (20%)**: Kích thước khuôn mặt (100-400px tốt nhất)

## Cấu hình

File: `camera_capture_module.py`

```python
class CaptureConfig:
    ESP32_CAM_IP = "192.168.243.176"  # Đổi IP của bạn
    TARGET_PHOTOS = 20                # Số ảnh cần chụp
    FACE_OUTPUT_SIZE = (112, 112)     # Kích thước ảnh đầu ra
    MIN_QUALITY_SCORE = 65            # Điểm tối thiểu để lưu
    CAPTURE_COOLDOWN = 0.5            # Giây giữa các lần chụp
```

## Xử lý lỗi

### ❌ "Không thể kết nối ESP32-CAM"

**Nguyên nhân:**
- ESP32-CAM chưa bật
- IP sai
- Không cùng mạng WiFi

**Giải pháp:**
```
1. Kiểm tra ESP32-CAM đang hoạt động (LED sáng)
2. Mở trình duyệt, truy cập http://192.168.243.176/stream
3. Nếu không được → Kiểm tra IP trong Serial Monitor
4. Đổi IP trong CaptureConfig.ESP32_CAM_IP
```

### ⚠️ "MediaPipe not installed"

**Giải pháp:**
```powershell
cd d:\HUTECH\DACN\attendance_system\desktop
pip install mediapipe
```

### 📷 Không phát hiện khuôn mặt

**Nguyên nhân:**
- Ánh sáng kém
- Khuôn mặt quá xa/gần
- Góc nghiêng

**Giải pháp:**
- Đứng cách camera 50-100cm
- Hướng mặt thẳng vào camera
- Tăng ánh sáng phòng

## Tips chụp ảnh tốt

✅ **NÊN:**
- Đứng trước camera ổn định
- Ánh sáng đầy đủ (không quá sáng/tối)
- Mặt thẳng, không đeo kính/khẩu trang
- Thử nhiều góc nhìn khác nhau (nghiêng nhẹ trái/phải)

❌ **KHÔNG NÊN:**
- Di chuyển quá nhanh
- Che mặt bằng tay/vật dụng
- Ánh sáng quá mạnh phía sau (backlight)
- Đứng quá xa camera

## Luồng xử lý

```
1. User chọn sinh viên → Click "Chụp ảnh"
2. CameraCaptureWindow khởi tạo
3. ESP32StreamReader kết nối stream
4. FaceProcessor phát hiện khuôn mặt (MediaPipe)
5. FaceQualityChecker đánh giá chất lượng
6. Nếu Quality ≥ 65 → Lưu ảnh
7. Lặp lại cho đến khi đủ 20 ảnh
8. Preprocess: Resize 112x112 + Grayscale + CLAHE
9. Lưu vào dataset/processed/{MSSV}/
```

## API Reference

### CameraCaptureWindow

```python
CameraCaptureWindow(parent, student_id, student_name)
```

**Parameters:**
- `parent`: Cửa sổ cha (Tkinter root)
- `student_id`: MSSV (str)
- `student_name`: Họ tên (str)

**Methods:**
- `start_capture()`: Bắt đầu chụp
- `toggle_auto()`: Tạm dừng/tiếp tục
- `save_photo(face_img, quality_info)`: Lưu 1 ảnh
- `on_closing()`: Đóng cửa sổ

### FaceProcessor

```python
processor = FaceProcessor()
detections = processor.detect_faces(frame)
face_crop, bbox = processor.crop_face(frame, detection)
face_processed = processor.preprocess_face(face_img)
```

### FaceQualityChecker

```python
quality = FaceQualityChecker.calculate_overall_quality(face_img)
# Returns: {'overall': 85.3, 'brightness': 90, 'sharpness': 82, ...}
```

## Roadmap

- [ ] Hỗ trợ webcam local (không cần ESP32-CAM)
- [ ] Chụp thủ công (click button thay vì auto)
- [ ] Preview ảnh đã chụp trước khi lưu
- [ ] Chụp lại ảnh kém chất lượng
- [ ] Export ảnh ra folder khác

---

**Tác giả:** DACN Team  
**Phiên bản:** 1.0.0  
**Ngày cập nhật:** 07/11/2025
