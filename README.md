# 🎯 Face Recognition Attendance System - ESP32-CAM Module

Hệ thống điểm danh bằng nhận dạng khuôn mặt sử dụng ESP32-CAM với giao diện web tích hợp.

## 📁 Cấu trúc dự án

```
DACN/
├── esp32-camera/              # Module ESP32-CAM
│   ├── CameraWebServer/       # Code Arduino cho ESP32
│   │   └── CameraWebServer.ino # File chính
│   ├── libraries.txt          # Danh sách thư viện cần thiết
│   ├── README.md              # Hướng dẫn ESP32
│   └── wiring_diagram_oled_speaker.md # Sơ đồ nối dây
├── example/                   # Code mẫu gốc
│   ├── CameraWebServer.ino    # Example từ Arduino
│   └── ...                    # Các file hỗ trợ
├── docs/                      # Tài liệu
│   └── api_docs.md           # API documentation
├── PROJECT_SUMMARY.md         # Tóm tắt dự án
├── workflow.txt              # Kế hoạch thực hiện
└── README.md                 # File này
```

## 🛠️ Tính năng ESP32-CAM

### ✅ Đã hoàn thành:
- **Camera streaming** với độ phân giải tối ưu
- **Web interface** hiện đại với giao diện tiếng Việt
- **Face detection** thời gian thực
- **Auto capture** khi phát hiện khuôn mặt
- **API integration** với server Python
- **OLED display** hiển thị thông tin
- **Speaker notification** với TTS
- **WiFi management** tự động kết nối
- **Error handling** và monitoring

### 🔧 Hardware cần thiết:
- ESP32-CAM module
- OLED I2C 128x64 SSD1306
- Mini Speaker với PAM8403 amplifier
- Breadboard và dây nối
- Nguồn 5V/2A

## 🚀 Cách sử dụng

### 1. Chuẩn bị phần cứng
- Kết nối ESP32-CAM theo sơ đồ trong `wiring_diagram_oled_speaker.md`
- Cấp nguồn 5V cho module

### 2. Cài đặt code
- Mở `esp32-camera/CameraWebServer/CameraWebServer.ino` trong Arduino IDE
- Cài đặt các thư viện trong `libraries.txt`
- Cấu hình WiFi credentials trong code
- Upload code lên ESP32-CAM

### 3. Kết nối và sử dụng
- ESP32 sẽ tạo WiFi hotspot hoặc kết nối WiFi
- Mở browser và truy cập IP của ESP32
- Sử dụng giao diện web để:
  - Xem camera stream
  - Test kết nối server
  - Đăng ký người dùng mới
  - Điểm danh bằng khuôn mặt

## 📋 API Endpoints

ESP32-CAM cung cấp các endpoint sau:

- `GET /` - Giao diện web chính
- `GET /stream` - Camera stream (port 81)
- `POST /checkin` - Điểm danh
- `POST /register` - Đăng ký người dùng
- `GET /status` - Trạng thái hệ thống
- `GET /health` - Health check

## 🔧 Cấu hình

### WiFi Settings
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
```

### Server Settings
```cpp
const char* serverUrl = "http://YOUR_SERVER_IP:5000";
```

### Camera Settings
```cpp
config.frame_size = FRAMESIZE_QVGA;  // 320x240
config.jpeg_quality = 12;            // Quality 0-63
```

## 📊 Tính năng nâng cao

### Real-time Face Detection
- Phát hiện khuôn mặt trong stream
- Vẽ bounding box tự động
- Auto capture khi khuôn mặt ổn định

### Voice Notifications
- Thông báo bằng giọng nói
- TTS integration
- Custom messages cho từng trường hợp

### OLED Display
- Hiển thị trạng thái hệ thống
- Thông tin người dùng
- Debug information

### Error Handling
- WiFi reconnection
- Memory monitoring
- Watchdog timer
- Restart reason detection

## 🐛 Troubleshooting

### ESP32 không kết nối WiFi
- Kiểm tra SSID và password
- Đảm bảo WiFi 2.4GHz
- Reset ESP32 và thử lại

### Camera không hiển thị
- Kiểm tra kết nối camera
- Thử giảm độ phân giải
- Kiểm tra nguồn điện

### Server không phản hồi
- Kiểm tra IP server trong code
- Đảm bảo server đang chạy
- Kiểm tra firewall

## 📚 Tài liệu tham khảo

- [ESP32-CAM Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/camera.html)
- [Arduino IDE Setup](https://docs.arduino.cc/software/ide-v2)
- [WiFi Library](https://github.com/espressif/arduino-esp32)

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push và tạo Pull Request

## 📄 License

MIT License - Xem file LICENSE để biết thêm chi tiết.

---

**Phát triển bởi: [Tên sinh viên]**  
**Trường: HUTECH**  
**Năm: 2024**