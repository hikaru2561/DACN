# 🤖 Thông Tin Model Buffalo_L

## 📍 Vị Trí Model

### Đường dẫn chính
```
C:\Users\ASUS\.insightface\models\buffalo_l\
```

### Cấu trúc thư mục
```
C:\Users\ASUS\.insightface\
└── models\
    └── buffalo_l\                    # Model chính cho face recognition
        ├── 1k3d68.onnx              # 136.95 MB - 3D face alignment
        ├── 2d106det.onnx            # 4.80 MB - 2D face detection (106 landmarks)
        ├── det_10g.onnx             # 16.14 MB - Face detection (10G model)
        ├── genderage.onnx           # 1.26 MB - Gender & Age prediction
        └── w600k_r50.onnx           # 166.31 MB - Face recognition (ResNet-50)
```

---

## 📊 Chi Tiết Files

| File | Kích thước | Chức năng |
|------|-----------|-----------|
| **w600k_r50.onnx** | 166.31 MB | 🔥 **Face Recognition** - Model chính để extract 512D embeddings |
| **1k3d68.onnx** | 136.95 MB | 3D Face Alignment - Căn chỉnh khuôn mặt 3D |
| **det_10g.onnx** | 16.14 MB | Face Detection - Phát hiện khuôn mặt |
| **2d106det.onnx** | 4.80 MB | Face Detection - 106 landmarks detection |
| **genderage.onnx** | 1.26 MB | Gender & Age Prediction - Dự đoán giới tính và tuổi |

**Tổng kích thước**: ~325.46 MB

---

## 🔧 Cấu Hình Sử Dụng

### File config.py (Line 57)
```python
FACE_RECOGNITION_CONFIG = {
    "model_name": "buffalo_l",        # Tên model
    "ctx_id": 0,                      # CPU: 0, GPU: device_id
    "det_size": (640, 640),           # Detection size
    "similarity_threshold": 0.50,      # Ngưỡng similarity (50%)
}
```

### Model được load tự động
- InsightFace tự động tải model từ thư mục `~/.insightface/models/`
- Không cần copy model vào project
- Khi khởi tạo `FaceAnalysis(name='buffalo_l')`, library tự động tìm model

---

## 📥 Download Model (Nếu Chưa Có)

### Cách 1: Tự động download
```python
from insightface.app import FaceAnalysis

# Tự động download nếu chưa có
app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))
```

### Cách 2: Manual download
1. Truy cập: https://github.com/deepinsight/insightface/releases/tag/v0.7
2. Tải file: `buffalo_l.zip` (~325 MB)
3. Giải nén vào: `C:\Users\[Username]\.insightface\models\buffalo_l\`

### Cách 3: Download bằng script
```python
import insightface
from insightface.model_zoo import get_model

# Download buffalo_l model
model = insightface.model_zoo.get_model('buffalo_l')
```

---

## 🎯 Sử Dụng Trong Hệ Thống

### 1. Camera Capture Module (Duplicate Check)
```python
# File: camera_capture_module.py, Line ~85
class DuplicateChecker:
    def init_face_model(self):
        self.face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
        self.face_app.prepare(ctx_id=0, det_size=(640, 640))
        # → Load từ C:\Users\ASUS\.insightface\models\buffalo_l\
```

### 2. Build Embeddings (Training)
```python
# File: build_embeddings.py
app = FaceAnalysis(providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))
# → Extract 512D embeddings từ ảnh training
```

### 3. Live Recognition (Attendance)
```python
# File: attendance_live_module.py
self.face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
self.face_app.prepare(ctx_id=0, det_size=(640, 640))
# → So sánh embedding real-time với DB
```

---

## 🔍 Kiểm Tra Model

### Kiểm tra model có tồn tại không
```powershell
# PowerShell
Test-Path "C:\Users\$env:USERNAME\.insightface\models\buffalo_l"
# → True nếu có, False nếu không
```

### Liệt kê tất cả files
```powershell
Get-ChildItem "C:\Users\$env:USERNAME\.insightface\models\buffalo_l" -File
```

### Kiểm tra trong Python
```python
import os
from pathlib import Path

model_path = Path.home() / ".insightface" / "models" / "buffalo_l"
print(f"Model exists: {model_path.exists()}")
print(f"Model files: {list(model_path.glob('*.onnx'))}")
```

---

## ⚙️ Model Specifications

### buffalo_l (Large Model)
- **Architecture**: ArcFace (ResNet-50)
- **Training Dataset**: WebFace600K (~600K identities)
- **Embedding Size**: 512 dimensions
- **Accuracy**: ~99.8% (LFW benchmark)
- **Speed**: ~10-20ms per face (CPU), ~2-5ms (GPU)

### Các model khác trong InsightFace
| Model | Size | Accuracy | Speed |
|-------|------|----------|-------|
| buffalo_s | ~150MB | ~99.5% | Fast |
| **buffalo_l** | **~325MB** | **~99.8%** | **Medium** ⭐ |
| buffalo_sc | ~180MB | ~99.6% | Medium |

**Lý do chọn buffalo_l:**
- ✅ Cân bằng tốt giữa accuracy và speed
- ✅ Phù hợp với CPU inference
- ✅ Kích thước vừa phải (~325MB)
- ✅ Hiệu suất tốt cho attendance system

---

## 🚀 Tối Ưu Performance

### 1. CPU Optimization (Đang dùng)
```python
app = FaceAnalysis(providers=['CPUExecutionProvider'])
```
- Speed: ~10-20ms per face
- Phù hợp cho attendance (không cần real-time quá nhanh)

### 2. GPU Optimization (Nếu có GPU)
```python
app = FaceAnalysis(providers=['CUDAExecutionProvider'])
```
- Speed: ~2-5ms per face
- Cần: CUDA toolkit, GPU NVIDIA

### 3. Detection Size Tuning
```python
# Nhỏ hơn = nhanh hơn nhưng kém chính xác
app.prepare(ctx_id=0, det_size=(320, 320))  # Fast

# Vừa phải (đang dùng)
app.prepare(ctx_id=0, det_size=(640, 640))  # Balanced ⭐

# Lớn hơn = chậm hơn nhưng chính xác hơn
app.prepare(ctx_id=0, det_size=(1024, 1024))  # Accurate
```

---

## 🗑️ Xóa Model (Nếu Muốn Tải Lại)

### Xóa toàn bộ InsightFace cache
```powershell
Remove-Item -Path "C:\Users\$env:USERNAME\.insightface" -Recurse -Force
```

### Xóa chỉ buffalo_l
```powershell
Remove-Item -Path "C:\Users\$env:USERNAME\.insightface\models\buffalo_l" -Recurse -Force
```

### Tải lại sau khi xóa
```python
from insightface.app import FaceAnalysis

# Tự động download lại
app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=0)
```

---

## 📚 Tài Liệu Tham Khảo

- **InsightFace GitHub**: https://github.com/deepinsight/insightface
- **Model Zoo**: https://github.com/deepinsight/insightface/tree/master/model_zoo
- **Paper ArcFace**: https://arxiv.org/abs/1801.07698
- **ONNX Runtime**: https://onnxruntime.ai/

---

## 🔒 Backup Model (Optional)

Nếu muốn backup model để không phải tải lại:

### Backup
```powershell
# Nén model thành zip
Compress-Archive -Path "C:\Users\$env:USERNAME\.insightface\models\buffalo_l" `
                 -DestinationPath "D:\HUTECH\DACN\backups\buffalo_l_backup.zip"
```

### Restore
```powershell
# Giải nén model
Expand-Archive -Path "D:\HUTECH\DACN\backups\buffalo_l_backup.zip" `
               -DestinationPath "C:\Users\$env:USERNAME\.insightface\models\" -Force
```

---

**📍 Tóm lại**: Model buffalo_l nằm trong thư mục user home `~/.insightface/models/buffalo_l/`, được InsightFace tự động quản lý. Không cần copy vào project!
