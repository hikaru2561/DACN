/*
 * ESP32-CAM + OLED + Serial Debug
 */

#include "esp_camera.h"
#include <WiFi.h>
#include "esp_http_server.h"
#include "img_converters.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Preferences.h>

#define RELAY_PIN 12
#define FLASH_PIN 13
#define LED_BUILTIN 33
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define OLED_SDA 15
#define OLED_SCL 14

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
Preferences preferences;

#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27
#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22

httpd_handle_t stream_httpd = NULL;
httpd_handle_t control_httpd = NULL;
unsigned long unlock_time = 0;
bool is_unlocked = false;
String user_name = "";

void configure_camera_quality(sensor_t *s) {
  // --- Cân chỉnh ánh sáng & Màu sắc ---
  s->set_brightness(s, 1);     // Tăng sáng nhẹ (Module này thường hơi tối)
  s->set_contrast(s, 0);       // Giữ nguyên độ tương phản để giữ chi tiết
  s->set_saturation(s, 0);     // Màu sắc tự nhiên
  s->set_special_effect(s, 0); // Không dùng hiệu ứng màu
  s->set_whitebal(s, 1);       // Bật cân bằng trắng (White Balance)
  s->set_awb_gain(s, 1);       // Bật Auto White Balance Gain (Rất quan trọng cho HDF3MP)
  s->set_wb_mode(s, 0);        // Chế độ Auto (0) hoạt động tốt nhất ngoài trời/trong nhà

  // --- Phơi sáng (Exposure) ---
  s->set_exposure_ctrl(s, 1);  // Bật kiểm soát phơi sáng
  s->set_aec2(s, 1);           // Bật DSP làm việc
  s->set_ae_level(s, 0);       // Mức bù phơi sáng (0 là mặc định)
  s->set_aec_value(s, 300);    // Giới hạn AEC (có thể tăng lên 400-600 nếu phòng tối)
  s->set_gain_ctrl(s, 1);      // Bật Gain Control (ISO)
  
  // --- Xử lý ảnh & Khắc phục lỗi quang học (QUAN TRỌNG CHO HDF3MP) ---
  s->set_lenc(s, 1);           // BẬT Lens Correction: BẮT BUỘC cho ống kính góc rộng để khử tối góc
  s->set_bpc(s, 0);            // Tắt Black Pixel Correction (để giảm noise giả)
  s->set_wpc(s, 1);            // Bật White Pixel Correction: Khử điểm chết sáng (hot pixels)
  s->set_raw_gma(s, 1);        // Bật Gamma Correction: Giúp ảnh có chiều sâu hơn
  
  // --- Độ nét & Ổn định độ phân giải ---
  s->set_sharpness(s, 1);      // Độ nét: 1 là vừa đủ, cao quá sẽ bị nhiễu hạt (grainy)
  s->set_dcw(s, 1);            // BẬT Downsize Crop Window: Giúp sensor scale về XGA chính xác hơn
}

static esp_err_t stream_handler(httpd_req_t *req) {
  camera_fb_t *fb = NULL;
  esp_err_t res = ESP_OK;
  size_t _jpg_buf_len = 0;
  uint8_t *_jpg_buf = NULL;
  char *part_buf[64];
  res = httpd_resp_set_type(req, "multipart/x-mixed-replace; boundary=frame");
  if (res != ESP_OK) return res;
  while (true) {
    fb = esp_camera_fb_get();
    if (!fb) {
      res = ESP_FAIL;
    } else {
      if (fb->format != PIXFORMAT_JPEG) {
        bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
        esp_camera_fb_return(fb);
        fb = NULL;
        if (!jpeg_converted) res = ESP_FAIL;
      } else {
        _jpg_buf_len = fb->len;
        _jpg_buf = fb->buf;
      }
    }
    if (res == ESP_OK) {
      size_t hlen = snprintf((char *)part_buf, 64, "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", _jpg_buf_len);
      res = httpd_resp_send_chunk(req, (const char *)part_buf, hlen);
    }
    if (res == ESP_OK) {
      res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
    }
    if (res == ESP_OK) {
      res = httpd_resp_send_chunk(req, "\r\n--frame\r\n", 11);
    }
    if (fb) {
      esp_camera_fb_return(fb);
      fb = NULL;
      _jpg_buf = NULL;
    } else if (_jpg_buf) {
      free(_jpg_buf);
      _jpg_buf = NULL;
    }
    if (res != ESP_OK) break;
    delay(1);
  }
  return res;
}

static esp_err_t control_handler(httpd_req_t *req) {
  char buf[100];
  if (httpd_req_get_url_query_str(req, buf, sizeof(buf)) == ESP_OK) {
    char var[32];
    char val[64];
    if (httpd_query_key_value(buf, "var", var, sizeof(var)) == ESP_OK &&
        httpd_query_key_value(buf, "val", val, sizeof(val)) == ESP_OK) {
      if (strcmp(var, "face") == 0) {
        user_name = String(val);
        user_name.replace("%20", " ");
        is_unlocked = true;
        unlock_time = millis() + 5000;
        digitalWrite(RELAY_PIN, HIGH);
        digitalWrite(FLASH_PIN, HIGH);
        Serial.print("✓ Access: ");
        Serial.println(user_name);
      }
    }
  }
  httpd_resp_send(req, "OK", 2);
  return ESP_OK;
}

static esp_err_t open_handler(httpd_req_t *req) {
  is_unlocked = true;
  unlock_time = millis() + 5000;
  user_name = "Manual";
  digitalWrite(RELAY_PIN, HIGH);
  digitalWrite(FLASH_PIN, HIGH);
  Serial.println("✓ Manual Open");
  httpd_resp_send(req, "OK", 2);
  return ESP_OK;
}

void startServers() {
  httpd_config_t stream_config = HTTPD_DEFAULT_CONFIG();
  stream_config.server_port = 80;
  stream_config.ctrl_port = 32768;
  httpd_uri_t stream_uri = {.uri = "/stream", .method = HTTP_GET, .handler = stream_handler, .user_ctx = NULL};
  if (httpd_start(&stream_httpd, &stream_config) == ESP_OK) {
    httpd_register_uri_handler(stream_httpd, &stream_uri);
    Serial.println("✓ Stream: Port 80");
  }
  httpd_config_t control_config = HTTPD_DEFAULT_CONFIG();
  control_config.server_port = 81;
  control_config.ctrl_port = 32769;
  httpd_uri_t control_uri = {.uri = "/control", .method = HTTP_GET, .handler = control_handler, .user_ctx = NULL};
  httpd_uri_t open_uri = {.uri = "/open", .method = HTTP_GET, .handler = open_handler, .user_ctx = NULL};
  if (httpd_start(&control_httpd, &control_config) == ESP_OK) {
    httpd_register_uri_handler(control_httpd, &control_uri);
    httpd_register_uri_handler(control_httpd, &open_uri);
    Serial.println("✓ Control: Port 81");
  }
}

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
  Serial.begin(115200);
  Serial.println("\n\n=== ESP32-CAM STARTING ===");
  
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(FLASH_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(FLASH_PIN, LOW);
  digitalWrite(LED_BUILTIN, HIGH);

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  if (psramFound()) {
    config.frame_size = FRAMESIZE_XGA;  // 1024x768 - XGA Resolution
    config.jpeg_quality = 14;            // Chất lượng cao hơn (số nhỏ = chất lượng cao)
    config.fb_count = 2;
    config.grab_mode = CAMERA_GRAB_LATEST;
    Serial.println("✓ PSRAM found - XGA Mode");
  } else {
    config.frame_size = FRAMESIZE_SVGA;  // 1024x768 - Vẫn dùng XGA
    config.jpeg_quality = 12;
    config.fb_count = 1;
    Serial.println("⚠ No PSRAM - XGA Mode (Limited)");
  }
  
  // Khởi tạo Camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("❌ Camera FAIL: 0x%x\n", err);
    return;
  }
  Serial.println("✓ Camera OK");
  
  // Lấy con trỏ điều khiển sensor
  sensor_t *s = esp_camera_sensor_get();
  
  // --- BẮT BUỘC: Ép lại độ phân giải tại đây ---
  s->set_framesize(s, FRAMESIZE_XGA); 
  // ---------------------------------------------
  
  // Gọi hàm cấu hình chất lượng mới
  configure_camera_quality(s);
  
  // Đợi sensor ổn định cài đặt mới
  delay(200);

  Wire.begin(OLED_SDA, OLED_SCL);
  Wire.setClock(50000);
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("❌ OLED FAIL");
  } else {
    Serial.println("✓ OLED OK");
    display.clearDisplay();
    display.display();
    delay(50);
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(WHITE);
    display.setCursor(0, 0);
    display.println("Connecting...");
    display.display();
  }

  const char *ssid_1 = "K9";
  const char *password_1 = "nk111111";
  const char *ssid_2 = "TEAZONE_2.4G";
  const char *password_2 = "88888888";

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  preferences.begin("wifi_cfg", false);
  String last_ssid = preferences.getString("ssid", "");
  preferences.end();
  bool connected = false;
  
  Serial.println("\n=== WiFi Connection ===");
  
  if (last_ssid.length() > 0) {
    Serial.print("Trying saved: ");
    Serial.println(last_ssid);
    const char *password = (last_ssid == ssid_1) ? password_1 : password_2;
    WiFi.begin(last_ssid.c_str(), password);
    unsigned long start = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - start < 10000) {
      delay(500);
      Serial.print(".");
    }
    if (WiFi.status() == WL_CONNECTED) {
      connected = true;
      Serial.println("\n✓ Connected!");
    } else {
      WiFi.disconnect();
      Serial.println("\n✗ Failed");
    }
  }
  
  while (!connected) {
    Serial.print("Trying: ");
    Serial.println(ssid_1);
    WiFi.begin(ssid_1, password_1);
    unsigned long start = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - start < 10000) {
      delay(500);
      Serial.print(".");
    }
    if (WiFi.status() == WL_CONNECTED) {
      connected = true;
      preferences.begin("wifi_cfg", false);
      preferences.putString("ssid", ssid_1);
      preferences.end();
      Serial.println("\n✓ Connected!");
      break;
    }
    WiFi.disconnect();
    Serial.println("\n✗ Failed");
    delay(1000);
    
    Serial.print("Trying: ");
    Serial.println(ssid_2);
    WiFi.begin(ssid_2, password_2);
    start = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - start < 10000) {
      delay(500);
      Serial.print(".");
    }
    if (WiFi.status() == WL_CONNECTED) {
      connected = true;
      preferences.begin("wifi_cfg", false);
      preferences.putString("ssid", ssid_2);
      preferences.end();
      Serial.println("\n✓ Connected!");
      break;
    }
    WiFi.disconnect();
    Serial.println("\n✗ Failed");
    delay(1000);
  }

  Serial.println("\n=== System Ready ===");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.print("Stream URL: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/stream");
  Serial.print("Control Port: 81\n");
  Serial.println("====================\n");

  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("IP:");
  display.setTextSize(2);
  display.println(WiFi.localIP());
  display.display();
  
  startServers();
}

void loop() {
  if (is_unlocked) {
    unsigned long current_time = millis();
    if (current_time < unlock_time) {
      int remaining = (unlock_time - current_time) / 1000;
      display.clearDisplay();
      display.setTextSize(1);
      display.setCursor(0, 0);
      display.println("ACCESS OK");
      display.setTextSize(2);
      display.setCursor(0, 12);
      String name = user_name;
      if (name.length() > 10) name = name.substring(0, 10);
      display.println(name);
      display.setTextSize(1);
      display.setCursor(0, 40);
      display.print("Lock: ");
      display.print(remaining + 1);
      display.println("s");
      display.display();
    } else {
      is_unlocked = false;
      digitalWrite(RELAY_PIN, LOW);
      digitalWrite(FLASH_PIN, LOW);
      display.clearDisplay();
      display.setTextSize(1);
      display.setCursor(0, 0);
      display.println("IP:");
      display.setTextSize(2);
      display.println(WiFi.localIP());
      display.display();
      user_name = "";
    }
  }
  delay(100);
}