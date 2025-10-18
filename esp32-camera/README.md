# 📸 ESP32-CAM Face Recognition System

## 🎯 Tổng quan

ESP32-CAM với giao diện web hiện đại cho hệ thống nhận dạng khuôn mặt. Hỗ trợ đăng ký và điểm danh người dùng thông qua camera streaming real-time.

## ✨ Tính năng

- 🎥 **Camera streaming** real-time với CORS support
- 🖥️ **Web interface** hiện đại với modal system
- 📸 **Image capture** với quality check
- 🔗 **API integration** với Python backend
- 📱 **Responsive design** cho mobile và desktop
- ⚡ **Fast processing** với optimized algorithms

## 🛠️ Phần cứng

### Required:
- ESP32-CAM module
- USB cable
- Breadboard và dây nối

### Optional:
- MicroSD card
- OLED display (SSD1306)
- Speaker + PAM8403

## 📦 Cài đặt

### 1. **Arduino IDE Setup**
```bash
# Cài đặt Arduino IDE 1.8.19+
# Cài đặt ESP32 board package
# Cài đặt thư viện (xem libraries.txt)
```

### 2. **Cấu hình**
```cpp
// Sửa trong CameraWebServer.ino:
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "http://YOUR_SERVER_IP:8000";
```

### 3. **Upload Code**
- Chọn board: **ESP32 Wrover Module**
- Upload code lên ESP32-CAM
- Mở Serial Monitor để xem IP

## 🚀 Sử dụng

### 1. **Truy cập Web Interface**
```
http://[ESP32_IP]
```

### 2. **Kết nối Server**
- Nhấn "🔗 Kết nối Server"
- Chờ camera stream khởi động

### 3. **Đăng ký người dùng**
- Nhấn "👤 Đăng ký"
- Chụp ảnh khuôn mặt
- Nhập thông tin
- Nhấn "✅ Đăng ký"

### 4. **Điểm danh**
- Nhấn "✅ Điểm danh"
- Chụp ảnh khuôn mặt
- Hệ thống tự động nhận diện

## 🎨 Giao diện

### Dashboard chính
- **Status panel**: Trạng thái hệ thống
- **Camera container**: Stream camera
- **Control buttons**: Các chức năng chính
- **Result panel**: Hiển thị kết quả

### Modal system
- **Đăng ký modal**: Form nhập thông tin
- **Điểm danh modal**: Auto processing
- **Quality check**: Kiểm tra chất lượng ảnh

## 🔧 API Endpoints

### ESP32-CAM Endpoints
- `GET /` - Dashboard chính
- `GET /stream` - Camera stream
- `GET /snapshot` - Ảnh chụp nhanh
- `GET /test-connection` - Test kết nối server
- `GET /users` - Lấy danh sách người dùng
- `GET /status` - Trạng thái hệ thống

### Server Integration
- `POST /api/v1/register` - Đăng ký người dùng
- `POST /api/v1/checkin` - Điểm danh
- `GET /api/v1/users` - Danh sách người dùng

## 🐛 Troubleshooting

### Camera Issues
- **Camera không hoạt động**: Kiểm tra kết nối hardware
- **Stream không hiển thị**: Kiểm tra CORS headers
- **Ảnh bị lỗi**: Kiểm tra chất lượng ánh sáng

### Network Issues
- **WiFi không kết nối**: Kiểm tra SSID/password
- **Server không kết nối**: Kiểm tra IP và port
- **CORS errors**: Kiểm tra browser console

### Performance Issues
- **Stream lag**: Giảm resolution hoặc FPS
- **Memory issues**: Restart ESP32
- **Slow response**: Kiểm tra network speed

## 📊 Specifications

- **Resolution**: 640x480 (VGA)
- **Frame Rate**: ~1-2 FPS
- **WiFi**: 802.11 b/g/n
- **Memory**: 4MB PSRAM
- **Storage**: MicroSD (optional)

## 🔒 Security

- **CORS headers** cho cross-origin access
- **Input validation** cho form data
- **Error handling** không tiết lộ thông tin nhạy cảm
- **Network security** trong mạng nội bộ

## 📚 Tài liệu

- [Libraries List](libraries.txt)
- [Wiring Diagram](wiring_diagram_oled_speaker.md)
- [Main Project README](../README.md)

---

**Version**: 2.0 Optimized  
**Last Updated**: 2024