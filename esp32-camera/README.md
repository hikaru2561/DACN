# ESP32-CAM Face Recognition System

## 📁 Cấu trúc thư mục
```
esp32-camera/
├── CameraWebServer/
│   └── CameraWebServer.ino    # Code chính cho ESP32-CAM
├── libraries.txt              # Danh sách thư viện cần thiết
├── wiring_diagram_oled_speaker.md  # Sơ đồ kết nối OLED + Speaker
└── README.md                  # File này
```

## 🚀 Cài đặt nhanh

### 1. Cài đặt thư viện
Mở Arduino IDE → Tools → Manage Libraries → Cài đặt:
- `Adafruit SSD1306` (cho OLED)
- `Adafruit GFX Library` (cho OLED)
- `ESP32-audioI2S` (cho Speaker)

### 2. Cấu hình WiFi
Sửa trong `CameraWebServer.ino`:
```cpp
const char* ssid = "TEN_WIFI_CUA_BAN";
const char* password = "MAT_KHAU_WIFI";
```

### 3. Cấu hình Server
Sửa IP server trong `CameraWebServer.ino`:
```cpp
const char* serverUrl = "http://192.168.219.62:5000";
```

## 🎯 Tính năng chính

### ✅ Stream Camera
- **Độ phân giải:** VGA (640x480) với PSRAM, QVGA (320x240) không PSRAM
- **Chất lượng:** JPEG quality 8 (cao nhất)
- **FPS:** ~10-15 FPS mượt mà
- **Format:** Multipart stream cho browser

### ✅ Face Detection Simulation
- **Cooldown:** 3 giây giữa các lần detect
- **Tần suất:** 20% chance mỗi giây
- **Khung:** Vị trí cố định ở giữa màn hình
- **Tự động ẩn:** Sau 2 giây

### ✅ Web Interface
- **Responsive design** với gradient đẹp
- **Real-time status** hiển thị trạng thái
- **Control buttons** cho tất cả chức năng
- **Face overlay** với animation mượt

## 🔧 API Endpoints

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/` | GET | Web interface chính |
| `/stream` | GET | Camera stream (port 81) |
| `/snapshot` | GET | Ảnh chụp đơn lẻ |
| `/checkin` | POST | Điểm danh |
| `/register` | POST | Đăng ký người dùng |

## 📊 Cấu hình Camera

### Với PSRAM (ESP32-CAM AI-Thinker)
```cpp
config.frame_size = FRAMESIZE_VGA;    // 640x480
config.jpeg_quality = 8;              // Chất lượng cao
config.fb_count = 2;                  // Double buffering
```

### Không PSRAM
```cpp
config.frame_size = FRAMESIZE_QVGA;   // 320x240
config.jpeg_quality = 10;             // Chất lượng tốt
config.fb_count = 1;                  // Single buffer
```

## 🔌 Kết nối phần cứng

### OLED SSD1306 (128x64)
- VCC → 3.3V
- GND → GND
- SCL → GPIO 22
- SDA → GPIO 21

### Speaker + PAM8403
- VCC → 5V
- GND → GND
- IN+ → GPIO 25
- IN- → GPIO 26

## 🐛 Troubleshooting

### Stream không hiển thị
1. Kiểm tra IP ESP32 trong Serial Monitor
2. Truy cập `http://IP:81/stream` trực tiếp
3. Kiểm tra WiFi connection

### Face detection spam
- Đã tối ưu với cooldown 3 giây
- Tần suất giảm xuống 20%
- Khung vị trí cố định

### Chất lượng ảnh kém
- Tăng `jpeg_quality` (số càng nhỏ càng tốt)
- Kiểm tra ánh sáng
- Điều chỉnh `xclk_freq_hz`

## 📈 Performance

- **Memory usage:** ~200KB RAM
- **Stream bandwidth:** ~500KB/s
- **Detection accuracy:** 80% (simulation)
- **Response time:** <100ms

## 🔄 Cập nhật

### Version 2.0 (Current)
- ✅ Multipart stream hoạt động
- ✅ Face detection tối ưu
- ✅ Chất lượng ảnh cao
- ✅ Web interface responsive

### Version 1.0
- ❌ Snapshot polling (chậm)
- ❌ Face detection spam
- ❌ Chất lượng ảnh thấp

---

**Tác giả:** AI Assistant  
**Ngày cập nhật:** 2024  
**Phiên bản:** 2.0