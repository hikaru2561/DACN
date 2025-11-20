# 📷 Hướng dẫn Quản lý Cấu hình Camera

## 🎯 Tổng quan

File `config.py` chứa tất cả các cấu hình hệ thống, bao gồm URL camera, database, API, và các thông số nhận diện khuôn mặt.

## 🔧 Cách cập nhật URL Camera

### Phương pháp 1: Sử dụng Config Manager (Giao diện)

```bash
python config_manager.py
```

- Mở cửa sổ quản lý cấu hình
- Thay đổi URL trong mục "📷 Cấu hình Camera"
- Click "💾 Lưu cấu hình"
- Khởi động lại ứng dụng

### Phương pháp 2: Script nhanh (Command line)

```bash
python update_camera.py
```

Nhập URL mới khi được hỏi:
```
URL mới: http://192.168.1.169/stream
```

### Phương pháp 3: Chỉnh sửa trực tiếp file config.py

Mở file `config.py` và tìm dòng:

```python
CAMERA_CONFIG = {
    # ESP32-CAM Stream URL
    "stream_url": "http://192.168.1.169/stream",
    ...
}
```

Thay đổi URL và lưu file.

## 📋 Các cấu hình quan trọng

### Camera
- `stream_url`: URL stream từ ESP32-CAM
- `resolution`: Độ phân giải camera (mặc định: 640x480)
- `fps`: Số khung hình/giây
- `max_retries`: Số lần thử kết nối lại

### Nhận diện khuôn mặt
- `similarity_threshold`: Ngưỡng độ tương đồng (0.0-1.0, mặc định: 0.50)
- `confidence_threshold`: Ngưỡng độ tin cậy (0.0-1.0, mặc định: 0.6)

### Điểm danh
- `late_threshold_minutes`: Số phút để tính đi muộn (mặc định: 15)
- `prevent_duplicate_minutes`: Chặn điểm danh trùng trong X phút (mặc định: 5)

### Chụp ảnh sinh viên
- `target_photos`: Số ảnh cần chụp mỗi sinh viên (mặc định: 20)
- `min_quality_score`: Điểm chất lượng tối thiểu (0.0-1.0, mặc định: 0.7)

## 🌐 Tìm địa chỉ IP ESP32-CAM

### Windows:
```bash
arp -a
```

### Linux/Mac:
```bash
arp -a | grep -i "esp32"
```

### Hoặc kiểm tra trên Serial Monitor của ESP32:
- Mở Arduino IDE
- Tools → Serial Monitor
- ESP32 sẽ in ra IP khi khởi động

## 🔍 Test kết nối Camera

Sau khi cập nhật URL, test kết nối:

```python
python -c "import requests; print(requests.get('http://192.168.1.169/stream', stream=True, timeout=5).status_code)"
```

Nếu hiển thị `200` → Kết nối thành công!

## ⚡ Quick Commands

### Xem cấu hình hiện tại:
```bash
python -c "from config import CAMERA_CONFIG; print(CAMERA_CONFIG['stream_url'])"
```

### Thay đổi nhanh:
```bash
python update_camera.py
```

### Mở Config Manager:
```bash
python config_manager.py
```

## 🆘 Troubleshooting

### Camera không kết nối được:
1. Kiểm tra ESP32 đã bật chưa
2. Kiểm tra cùng mạng WiFi với máy tính
3. Ping địa chỉ IP: `ping 192.168.1.169`
4. Kiểm tra URL trong browser: `http://192.168.1.169/stream`

### Cấu hình không áp dụng:
- **Khởi động lại ứng dụng** sau khi thay đổi config
- Kiểm tra file `config.py` đã lưu đúng chưa

### Lỗi import config:
```bash
# Chạy từ thư mục desktop
cd attendance_system/desktop
python main.py
```

## 📝 Lưu ý

- ⚠️ **Luôn khởi động lại ứng dụng** sau khi thay đổi config
- 💾 Backup file `config.py` trước khi sửa
- 🔒 Không commit password database lên Git
- 📱 ESP32-CAM phải cùng mạng với máy tính

## 🔗 Liên kết hữu ích

- [ESP32-CAM Setup Guide](https://randomnerdtutorials.com/esp32-cam-video-streaming-face-recognition-arduino-ide/)
- [InsightFace Documentation](https://github.com/deepinsight/insightface)
- [MediaPipe Face Detection](https://google.github.io/mediapipe/solutions/face_detection.html)

---

💡 **Tip**: Lưu địa chỉ IP tĩnh cho ESP32-CAM trong router để không phải cập nhật URL mỗi lần khởi động lại!
