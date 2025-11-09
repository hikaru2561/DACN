# 🎯 HƯỚNG DẪN SỬ DỤNG HỆ THỐNG

## Tóm tắt

Bạn đã hoàn thành 2 module quan trọng:
1. **📷 Camera Capture Module** - Chụp ảnh khuôn mặt sinh viên
2. **✅ Attendance Module** - Điểm danh tự động bằng nhận dạng khuôn mặt

---

## 🚀 Quy trình sử dụng hoàn chỉnh

### BƯỚC 1: Chụp ảnh sinh viên

```
1. Mở Desktop App (D:/Python/python.exe main.py)
2. Đăng nhập (admin/admin123)
3. Click "Quản lý Sinh viên"
4. Chọn sinh viên cần chụp ảnh
5. Click "📷 Chụp ảnh"
6. Đứng trước ESP32-CAM, đợi tự động chụp 20 ảnh
7. Hoàn thành → Ảnh lưu tại dataset/processed/{MSSV}/
```

### BƯỚC 2: Build Embeddings Database

```
1. Click "Điểm danh" từ Dashboard
2. Click "🔄 Rebuild DB"
3. Đợi hệ thống xử lý tất cả ảnh (2-5 phút)
4. Hoàn thành → face_embeddings.pkl được tạo
```

### BƯỚC 3: Điểm danh

```
1. Click "▶️ Bắt đầu điểm danh"
2. Sinh viên đứng trước camera lần lượt
3. Hệ thống tự động nhận diện và đánh dấu ✅
4. Xem realtime trong bảng bên phải
5. Nhấn "⏸️ Dừng" khi xong
6. Nhấn "💾 Lưu điểm danh" (hiện tại chưa lưu DB)
```

---

## 📂 Cấu trúc thư mục

```
attendance_system/desktop/
├── main.py                          # Entry point
├── student_module.py                # Quản lý sinh viên
├── camera_capture_module.py         # 📷 Chụp ảnh
├── attendance_module.py             # ✅ Điểm danh
├── api_client.py                    # REST API wrapper
├── requirements.txt                 # Dependencies
├── CAMERA_MODULE_GUIDE.md           # Hướng dẫn Camera
├── ATTENDANCE_MODULE_GUIDE.md       # Hướng dẫn Attendance
└── README.md                        # Module overview

dataset/
├── processed/                       # Ảnh đã xử lý
│   ├── 2280602549/                 # Folder theo MSSV
│   │   ├── 2280602549_..._q85.jpg
│   │   └── ... (20 ảnh)
│   └── ...
└── face_embeddings.pkl              # Embeddings DB
```

---

## ⚙️ Cài đặt

### Dependencies mới:

```powershell
cd d:\HUTECH\DACN\attendance_system\desktop
pip install opencv-python mediapipe onnxruntime
pip install insightface  # Optional - để nhận dạng khuôn mặt
```

### ESP32-CAM Setup:

```
1. Flash code: esp32-camera/CameraWebServer/CameraWebServer_Optimized/
2. Kết nối WiFi
3. Ghi nhớ IP: 192.168.243.176
4. Test stream: http://192.168.243.176/stream
```

---

## 🎯 Các module đã hoàn thành

### ✅ Camera Capture Module

**Features:**
- ESP32-CAM WiFi stream
- MediaPipe face detection
- Quality scoring (Brightness, Sharpness, Contrast)
- Auto capture 20 high-quality photos
- CLAHE preprocessing (112x112 grayscale)

**Files:**
- `camera_capture_module.py` (750 lines)
- `CAMERA_MODULE_GUIDE.md` (documentation)

**How to use:**
```python
from camera_capture_module import CameraCaptureWindow

# Mở cửa sổ chụp ảnh
CameraCaptureWindow(parent, "2280602549", "Nguyễn Kim Quang")
```

### ✅ Attendance Module

**Features:**
- Realtime face recognition (InsightFace)
- Cosine Similarity matching (threshold: 0.50)
- Auto attendance marking
- Cooldown system (3 seconds)
- Embeddings database (pickle)

**Files:**
- `attendance_module.py` (850 lines)
- `ATTENDANCE_MODULE_GUIDE.md` (documentation)

**How to use:**
```python
from attendance_module import AttendanceModule

# Mở module điểm danh
AttendanceModule(parent, api_client, session_id=None)
```

---

## 🔧 Configuration

### Camera Capture:

```python
# camera_capture_module.py
class CaptureConfig:
    ESP32_CAM_IP = "192.168.243.176"  # ⚠️ ĐỔI IP CỦA BẠN
    TARGET_PHOTOS = 20                # Số ảnh cần chụp
    MIN_QUALITY_SCORE = 65            # Ngưỡng chất lượng
    FACE_OUTPUT_SIZE = (112, 112)     # Kích thước ảnh
```

### Attendance:

```python
# attendance_module.py
class AttendanceConfig:
    ESP32_CAM_IP = "192.168.243.176"
    SIMILARITY_THRESHOLD = 0.50       # Ngưỡng nhận dạng
    RECOGNITION_COOLDOWN = 3.0        # Cooldown (giây)
```

---

## 🐛 Troubleshooting

### ❌ Không kết nối được ESP32-CAM

**Kiểm tra:**
```
1. ESP32-CAM đang bật (LED sáng)
2. Mở http://192.168.243.176/stream trong Chrome
3. Nếu không được → Kiểm tra IP trong Serial Monitor
4. Đổi IP trong CaptureConfig.ESP32_CAM_IP
```

### ⚠️ MediaPipe/InsightFace not installed

```powershell
pip install mediapipe
pip install insightface onnxruntime
```

### 🔴 "Unknown" - Không nhận dạng được

**Nguyên nhân:**
- Sinh viên chưa có ảnh trong dataset
- Chưa rebuild embeddings

**Giải pháp:**
```
1. Chụp ảnh cho sinh viên (Student Module → 📷)
2. Rebuild embeddings (Attendance Module → 🔄 Rebuild DB)
```

### ⚠️ Nhận dạng sai người

**Tăng threshold:**
```python
SIMILARITY_THRESHOLD = 0.60  # Từ 0.50 → 0.60
```

---

## 📊 Performance

### Camera Capture:
- **Detection:** ~15-20 FPS (MediaPipe CPU)
- **Quality check:** ~50ms/face
- **Save time:** ~10ms/photo
- **Total time:** ~20-30 giây cho 20 ảnh

### Attendance:
- **Stream FPS:** ~15-20 FPS (ESP32-CAM)
- **Face detection:** ~50-80ms (InsightFace CPU)
- **Embedding extraction:** ~100-150ms
- **Database search:** ~5-10ms (100 students)
- **Total latency:** ~300-450ms

---

## 📝 Code Statistics

| Module | Lines | Classes | Functions |
|--------|-------|---------|-----------|
| camera_capture_module.py | 750 | 5 | 15+ |
| attendance_module.py | 850 | 4 | 12+ |
| student_module.py | 734 | 2 | 20+ |
| main.py | 621 | 2 | 15+ |
| api_client.py | 309 | 1 | 25+ |
| **TOTAL** | **3,264** | **14** | **87+** |

---

## 🎨 UI Design

### Color Scheme:
```python
PRIMARY = "#2196F3"    # Blue
SUCCESS = "#4CAF50"    # Green
DANGER = "#F44336"     # Red
WARNING = "#FF9800"    # Orange
INFO = "#00BCD4"       # Cyan
```

### Fonts:
- **Header:** Segoe UI, 14pt Bold
- **Body:** Segoe UI, 10-11pt
- **Code:** Consolas, 9pt

---

## 🚧 Next Steps (Pending)

### HIGH PRIORITY:
- [ ] API Integration for Attendance (POST /api/attendance)
- [ ] Session Management Module (chọn lớp/buổi học)
- [ ] Teacher/Subject/Class CRUD modules

### MEDIUM PRIORITY:
- [ ] Reports & Statistics (charts, export Excel)
- [ ] Email notifications (vắng mặt)
- [ ] Webcam support (không cần ESP32-CAM)

### LOW PRIORITY:
- [ ] Multi-face attendance (nhiều người cùng lúc)
- [ ] Mobile app (React Native/Flutter)
- [ ] Cloud deployment

---

## 📚 Documentation

- **CAMERA_MODULE_GUIDE.md**: Chi tiết về Camera Capture
- **ATTENDANCE_MODULE_GUIDE.md**: Chi tiết về Attendance
- **README.md**: Tổng quan module (file này)

---

## 🎉 Kết luận

Bạn đã hoàn thành **hệ thống điểm danh tự động** với:
- ✅ Database (PostgreSQL 15 tables)
- ✅ Backend API (FastAPI 14 endpoints)
- ✅ Desktop UI (Tkinter + Material Design)
- ✅ Student Management (CRUD + Search)
- ✅ Camera Capture (ESP32-CAM + MediaPipe)
- ✅ Face Recognition (InsightFace + Cosine Similarity)

**Để test ngay:**
```powershell
# Terminal 1: Backend
cd d:\HUTECH\DACN\attendance_system\backend
D:/Python/python.exe main.py

# Terminal 2: Desktop App
cd d:\HUTECH\DACN\attendance_system\desktop
D:/Python/python.exe main.py
```

**Login:** admin / admin123

---

**Tác giả:** DACN Team  
**Phiên bản:** 1.0.0  
**Ngày:** 07/11/2025  
**GitHub:** hikaru2561/DACN
