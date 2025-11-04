# 📸 ESP32-CAM Face Recognition System

Hệ thống nhận diện khuôn mặt sử dụng ESP32-CAM và Python

---

## 📁 Cấu trúc thư mục

```
DACN/
├── esp32-camera/
│   └── CameraWebServer/
│       └── CameraWebServer_Optimized/
│           └── CameraWebServer_Optimized.ino    # Code ESP32-CAM
├── client/
│   ├── view_stream_v2.py                        # Xem stream từ ESP32-CAM  
│   └── requirements.txt                         # Python dependencies
├── dataset/                                     # Dataset ảnh khuôn mặt
└── README.md
```

---

## 🚀 Quick Start

### 1. Setup ESP32-CAM

**Hardware:**
- ESP32-CAM AI-Thinker
- FTDI/USB-to-Serial programmer
- Jumper wires

**Upload Code:**
```
1. Mở Arduino IDE
2. File → Open → CameraWebServer_Optimized.ino
3. Tools → Board → AI Thinker ESP32-CAM
4. Tools → Port → Chọn COM port
5. QUAN TRỌNG: Nối GPIO 0 → GND khi upload
6. Click Upload
7. Sau upload: Ngắt GPIO 0, nhấn Reset
```

**WiFi Config:**
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
```

---

### 2. Setup Python Client

**Install dependencies:**
```bash
cd client
pip install -r requirements.txt
```

**Run Stream Viewer:**
```bash
python view_stream_v2.py
```

---

## 🎥 Camera Settings (Optimized)

Current settings đã được tối ưu cho:
- ✅ Giảm noise (AGC Gain: 3)
- ✅ Giảm lag (JPEG Quality: 12)
- ✅ Cân bằng sáng tối (Gamma ON)
- ✅ High resolution (SVGA 800x600)

**Key Settings:**
```cpp
Brightness: 0 (neutral)
Contrast: +1
Saturation: -1 (reduce color noise)
Sharpness: +2 (MAX)
AGC Gain: 3 (low noise)
Gain Ceiling: 8x
JPEG Quality: 12 (balance quality/speed)
Resolution: SVGA 800x600
```

---

## 📊 Quality Metrics

Target quality sau tối ưu:
- Brightness: 100-180 ✅
- Sharpness: >100 ✅
- Contrast: >50 ✅
- Overall Score: 60-70/100 ✅

---

## 🔧 Troubleshooting

### ESP32-CAM không kết nối WiFi
- Kiểm tra SSID/password
- Kiểm tra nguồn điện (5V/2A)
- Xem Serial Monitor (115200 baud)

### Stream bị lag
- Đã tối ưu: JPEG Quality = 12
- Frame buffer = 2
- Giảm số client kết nối đồng thời

### Ảnh bị noise
- Đã tối ưu: AGC Gain = 3
- Gain Ceiling = 8x
- Thêm ánh sáng môi trường

---

## 📡 ESP32-CAM Endpoints

Sau khi kết nối WiFi thành công, truy cập:

- **Stream:** `http://ESP_IP/stream`
- **Capture:** `http://ESP_IP/capture`
- **Web Interface:** `http://ESP_IP/`

---

## 🎯 Next Steps (Tùy chọn)

Để phát triển thêm:
1. Face detection & capture (OpenCV)
2. Face recognition training (DeepFace)
3. Vector storage (PostgreSQL pgvector)
4. Real-time recognition

---

## 🛠️ Tech Stack

- **Hardware:** ESP32-CAM AI-Thinker
- **Camera:** OV2640 2MP
- **Backend:** Arduino C++
- **Frontend:** Python + OpenCV
- **Stream Protocol:** MJPEG over HTTP

---

## 📝 Notes

- ESP32-CAM đang chạy ở **SVGA 800x600** resolution
- JPEG quality = **12** (cân bằng giữa quality và speed)
- AGC Gain = **3** (giảm noise tối đa)
- Frame buffer = **2** (smooth streaming)

---

## 📄 License

MIT License - HUTECH Student Project

---

**Author:** HUTECH Student  
**Date:** November 4, 2025  
**Version:** Clean & Optimized
