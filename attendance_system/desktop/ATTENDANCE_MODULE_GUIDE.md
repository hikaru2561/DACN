# ✅ Attendance Module - Hướng dẫn điểm danh tự động

## Tổng quan

Module điểm danh sinh viên tự động với nhận dạng khuôn mặt:
- Kết nối ESP32-CAM realtime stream
- Nhận dạng khuôn mặt với InsightFace
- So sánh embedding (Cosine Similarity)
- Tự động đánh dấu điểm danh
- Lưu kết quả vào database

## Cách sử dụng

### 1. Chuẩn bị dữ liệu

**Bước 1: Chụp ảnh sinh viên**
```
Desktop App → Quản lý Sinh viên → Chọn SV → 📷 Chụp ảnh
Chụp đủ 20 ảnh cho mỗi sinh viên
```

**Bước 2: Build Embeddings Database**
```
Desktop App → Điểm danh → 🔄 Rebuild DB
Hệ thống sẽ:
- Đọc tất cả ảnh từ dataset/processed/
- Trích xuất embeddings (512-dim vectors)
- Lưu vào face_embeddings.pkl
```

### 2. Bắt đầu điểm danh

```
1. Mở Desktop App → Điểm danh
2. (Optional) Chọn buổi học/lớp cụ thể
3. Nhấn "▶️ Bắt đầu điểm danh"
4. Sinh viên đứng trước camera
5. Hệ thống tự động nhận diện và đánh dấu
6. Nhấn "⏸️ Dừng" khi hoàn thành
7. Nhấn "💾 Lưu điểm danh" để lưu vào DB
```

### 3. Xem kết quả

**Bảng điểm danh realtime:**
```
STT | MSSV         | Họ tên            | Trạng thái
----|--------------|-------------------|------------
1   | 2280602549   | Nguyễn Kim Quang  | ✅
2   | 2280601234   | Trần Văn A        | ❌
```

**Chú thích:**
- ✅ = Có mặt (detected)
- ❌ = Vắng (chưa detect)

## Luồng nhận dạng

```
1. ESP32-CAM stream → Frame (640x480)
2. InsightFace detect faces → Bounding boxes
3. Crop khuôn mặt → Extract embedding (512-dim)
4. So sánh với database embeddings (Cosine Similarity)
5. Nếu Similarity ≥ 0.50 → Match → Đánh dấu điểm danh
6. Cooldown 3 giây (tránh trùng lặp)
```

## Cosine Similarity

### Công thức:

$$
\text{similarity}(A, B) = \frac{A \cdot B}{\|A\| \times \|B\|}
$$

Trong đó:
- $A$, $B$: Embedding vectors (512-dim)
- $A \cdot B$: Dot product
- $\|A\|$, $\|B\|$: L2 norms

### Ngưỡng:

| Similarity | Kết quả | Ý nghĩa |
|-----------|---------|---------|
| ≥ 0.50    | ✅ Match | Cùng người |
| 0.30 - 0.49 | ⚠️ Maybe | Có thể giống |
| < 0.30    | ❌ No match | Khác người |

**Mặc định:** `SIMILARITY_THRESHOLD = 0.50`

## Cấu hình

File: `attendance_module.py`

```python
class AttendanceConfig:
    ESP32_CAM_IP = "192.168.243.176"
    SIMILARITY_THRESHOLD = 0.50      # Ngưỡng nhận dạng
    RECOGNITION_COOLDOWN = 3.0       # Giây giữa 2 lần điểm danh
    EMBEDDINGS_FILE = "dataset/face_embeddings.pkl"
```

### Điều chỉnh threshold:

```python
# Nếu nhận dạng sai (false positive) → Tăng threshold
SIMILARITY_THRESHOLD = 0.60

# Nếu không nhận dạng được (false negative) → Giảm threshold
SIMILARITY_THRESHOLD = 0.45
```

## Xử lý lỗi

### ❌ "InsightFace not installed"

**Giải pháp:**
```powershell
pip install insightface
pip install onnxruntime
```

### ⚠️ "No embeddings file found"

**Nguyên nhân:**
- Chưa chụp ảnh sinh viên
- Chưa rebuild embeddings

**Giải pháp:**
```
1. Chụp ảnh cho sinh viên (Quản lý SV → 📷)
2. Nhấn "🔄 Rebuild DB" trong module điểm danh
```

### 🔴 "Unknown" (không nhận dạng được)

**Nguyên nhân:**
- Sinh viên chưa có ảnh trong DB
- Ảnh chất lượng kém
- Góc chụp khác với ảnh training

**Giải pháp:**
- Kiểm tra dataset/processed/{MSSV}/ có ảnh không
- Chụp lại ảnh với nhiều góc độ khác nhau
- Rebuild embeddings

### ⚠️ Nhận dạng sai người

**Nguyên nhân:**
- Threshold quá thấp
- 2 người giống nhau
- Ảnh training không đa dạng

**Giải pháp:**
```python
# Tăng threshold lên 0.60
SIMILARITY_THRESHOLD = 0.60

# Chụp thêm ảnh với nhiều biểu cảm khác nhau
# Rebuild embeddings
```

## Embeddings Database

### Cấu trúc file

File: `dataset/face_embeddings.pkl`

```python
{
    "2280602549": [
        np.array([0.123, -0.456, ...]),  # Embedding 1 (512-dim)
        np.array([0.234, -0.567, ...]),  # Embedding 2
        ...                               # 20 embeddings
    ],
    "2280601234": [...],
    ...
}
```

### Kích thước:

- Mỗi embedding: 512 floats = 2 KB
- 20 ảnh/sinh viên = 40 KB
- 100 sinh viên = 4 MB
- 1000 sinh viên = 40 MB

### Rebuild khi nào?

✅ **BẮT BUỘC rebuild:**
- Thêm sinh viên mới
- Chụp lại ảnh sinh viên
- Thay đổi dataset/processed/

⏰ **Thời gian rebuild:**
- 1 sinh viên (20 ảnh): ~2 giây
- 100 sinh viên: ~3 phút
- 1000 sinh viên: ~30 phút

## Performance

### FPS (Frames Per Second):

- ESP32-CAM stream: ~15-20 FPS
- InsightFace detection: ~10-15 FPS
- Display update: 30 FPS (limited)

### Độ trễ (Latency):

1. **Camera → Desktop:** ~100-200ms (WiFi)
2. **Face Detection:** ~50-80ms (CPU)
3. **Embedding extraction:** ~100-150ms (CPU)
4. **Database search:** ~5-10ms (100 students)
5. **Total:** ~300-450ms

### Optimization:

```python
# Giảm resolution stream (ESP32-CAM)
framesize = FRAMESIZE_VGA  # 640x480 (mặc định)
# framesize = FRAMESIZE_QVGA  # 320x240 (nhanh hơn)

# Giảm detection size (InsightFace)
det_size = (640, 640)  # Mặc định
# det_size = (320, 320)  # Nhanh hơn nhưng kém chính xác
```

## Cooldown System

**Vấn đề:** Cùng 1 sinh viên bị điểm danh nhiều lần trong vài giây

**Giải pháp:** Cooldown 3 giây

```python
last_recognition_time = {
    "2280602549": 1699356123.45,  # Timestamp
}

current_time = time.time()
if current_time - last_time >= RECOGNITION_COOLDOWN:
    mark_attendance(student_id)
    last_recognition_time[student_id] = current_time
```

## Giao diện

### Màu box trong video:

- 🟢 **GREEN**: Nhận dạng được (Similarity ≥ 0.50)
  ```
  Label: "2280602549 (0.82)"
  ```
  
- 🔴 **RED**: Không nhận dạng được
  ```
  Label: "Unknown"
  ```

### Bảng điểm danh:

- 🟢 **Light Green**: Có mặt
- 🔴 **Light Red**: Vắng
- 🟡 **Light Yellow**: Đi muộn (future)

## API Integration

### Lưu điểm danh vào DB:

```python
# POST /api/attendance
{
    "session_id": 1,
    "student_id": "2280602549",
    "status": "present",  # present/absent/late
    "timestamp": "2025-11-07T14:30:00"
}
```

### Lấy danh sách sinh viên trong lớp:

```python
# GET /api/sessions/{session_id}/students
[
    {
        "student_id": "2280602549",
        "full_name": "Nguyễn Kim Quang",
        "class_id": "DHKTPM17A"
    },
    ...
]
```

## Tips điểm danh hiệu quả

✅ **NÊN:**
- Rebuild embeddings trước mỗi buổi điểm danh
- Yêu cầu sinh viên đứng ổn định 2-3 giây
- Ánh sáng đầy đủ, không backlight
- Kiểm tra kết nối ESP32-CAM trước

❌ **KHÔNG NÊN:**
- Điểm danh quá nhanh (< 1 giây/người)
- Nhiều người cùng lúc (1 người/lần)
- Ánh sáng yếu hoặc quá sáng

## Troubleshooting

### Nhận dạng chậm

**Nguyên nhân:**
- Database quá lớn
- CPU yếu
- Stream lag

**Giải pháp:**
```python
# Giảm detection size
det_size = (320, 320)

# Giới hạn số sinh viên search
# (Chỉ search trong 1 lớp thay vì toàn trường)
```

### Không hiển thị video

**Nguyên nhân:**
- ESP32-CAM chưa kết nối
- IP sai

**Giải pháp:**
- Kiểm tra stream URL: http://192.168.243.176/stream
- Đổi IP trong AttendanceConfig

## Roadmap

- [ ] Lưu điểm danh vào database (API integration)
- [ ] Chọn lớp/buổi học trước khi điểm danh
- [ ] Hỗ trợ điểm danh nhiều người cùng lúc
- [ ] Export báo cáo điểm danh (Excel/PDF)
- [ ] Gửi email thông báo vắng mặt
- [ ] Dashboard thống kê tỷ lệ điểm danh

---

**Tác giả:** DACN Team  
**Phiên bản:** 1.0.0  
**Ngày cập nhật:** 07/11/2025
