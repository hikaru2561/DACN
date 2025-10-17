# Sơ đồ kết nối ESP32-CAM + OLED + Speaker

## Thiết bị cần thiết
- ESP32-CAM
- Màn hình OLED I2C 128x64 SSD1306
- Mini Speaker 3W
- Module khuếch đại âm thanh PAM8403
- Dây nối (Dupont)
- Breadboard (tùy chọn)

## Sơ đồ kết nối

### ESP32-CAM Pinout
```
ESP32-CAM:
┌─────────────────┐
│ 3V3  GND  GPIO0 │
│ GND   GPIO1     │
│ GPIO2 GPIO3     │
│ GND   GPIO4     │
│ GPIO5 GPIO6     │
│ GPIO7 GPIO8     │
│ GPIO9 GPIO10    │
│ GPIO11 GPIO12   │
│ GPIO13 GPIO14   │
│ GPIO15 GPIO16   │
│ GPIO17 GPIO18   │
│ GPIO19 GPIO21   │
│ GPIO22 GPIO23   │
│ GPIO25 GPIO26   │
│ GPIO27 GPIO32   │
│ GPIO33 GPIO35   │
│ GPIO36 GPIO39   │
└─────────────────┘
```

### Kết nối OLED (I2C)
```
ESP32-CAM    OLED SSD1306
---------    -------------
3V3    →     VCC
GND    →     GND
GPIO21 →     SDA
GPIO22 →     SCL
```

### Kết nối Speaker + PAM8403
```
ESP32-CAM    PAM8403    Speaker
---------    -------    -------
3V3    →     VCC
GND    →     GND
GPIO25 →     DIN (Data In)
GPIO26 →     BCLK (Bit Clock)
GPIO27 →     LRC (Left/Right Clock)
             L+   →     Speaker +
             L-   →     Speaker -
```

## Sơ đồ chi tiết

```
                    ESP32-CAM
                   ┌─────────┐
                   │ 3V3 GND │
                   │         │
                   │ GPIO21  │─── SDA ─── OLED
                   │ GPIO22  │─── SCL ─── OLED
                   │         │
                   │ GPIO25  │─── DIN ─── PAM8403
                   │ GPIO26  │─── BCLK ── PAM8403
                   │ GPIO27  │─── LRC ─── PAM8403
                   │         │
                   │ 3V3     │─── VCC ─── PAM8403
                   │ GND     │─── GND ─── PAM8403
                   └─────────┘
                            │
                            │
                    ┌───────▼───────┐
                    │   PAM8403     │
                    │   Amplifier   │
                    │               │
                    │ L+ ────┐      │
                    │ L- ────┘      │
                    └───────────────┘
                            │
                            │
                    ┌───────▼───────┐
                    │   Speaker     │
                    │     3W        │
                    └───────────────┘
```

## Lưu ý quan trọng

### 1. Nguồn điện
- ESP32-CAM: 3.3V
- OLED: 3.3V hoặc 5V (có thể dùng 3.3V)
- PAM8403: 3.3V - 5V (khuyến nghị 5V cho âm thanh tốt hơn)

### 2. I2C Address
- OLED mặc định: 0x3C
- Nếu không hiển thị, thử địa chỉ 0x3D

### 3. Audio Quality
- PAM8403 cần nguồn 5V để hoạt động tốt nhất
- Có thể dùng nguồn 3.3V nhưng âm thanh sẽ yếu hơn

### 4. Troubleshooting

#### OLED không hiển thị:
- Kiểm tra kết nối SDA/SCL
- Thử đổi địa chỉ I2C (0x3C hoặc 0x3D)
- Kiểm tra nguồn 3.3V

#### Speaker không phát âm:
- Kiểm tra kết nối I2S (DIN, BCLK, LRC)
- Kiểm tra nguồn PAM8403
- Kiểm tra kết nối Speaker (+/-)

#### Lỗi kết nối WiFi:
- Kiểm tra SSID và password
- Đảm bảo ESP32-CAM trong phạm vi WiFi

## Code cần thiết

### Libraries cần cài đặt:
1. **Adafruit SSD1306** - Cho OLED
2. **Adafruit GFX Library** - Cho OLED
3. **ESP32-audioI2S** - Cho Audio

### Cài đặt trong Arduino IDE:
```
Tools → Manage Libraries → Search:
- "Adafruit SSD1306"
- "Adafruit GFX Library" 
- "ESP32-audioI2S"
```

## Test kết nối

### 1. Test OLED:
```cpp
display.clearDisplay();
display.setTextSize(1);
display.setTextColor(WHITE);
display.setCursor(0,0);
display.println("Hello World!");
display.display();
```

### 2. Test Speaker:
```cpp
audio.setPinout(I2S_BCLK_PIN, I2S_LRC_PIN, I2S_DOUT_PIN);
audio.setVolume(10);
audio.connecttohost("http://translate.google.com/translate_tts?ie=UTF-8&q=Hello&tl=en&client=tw-ob");
```

## Kết quả mong đợi

1. **OLED hiển thị:**
   - "System Ready!"
   - "Check-in Success!" + tên người dùng
   - "Registration completed!"

2. **Speaker phát âm:**
   - "Bạn đã điểm danh thành công với người dùng [tên]"
   - "Điểm danh thất bại. Khuôn mặt không được nhận diện."
   - "Bạn đã đăng ký thành công với tên [tên]"
   - "Đăng ký thất bại. Vui lòng thử lại."

## Lưu ý bảo mật

- Thay đổi SSID và password WiFi
- Thay đổi IP server trong code
- Sử dụng HTTPS nếu có thể
- Bảo vệ thiết bị khỏi nước và bụi
