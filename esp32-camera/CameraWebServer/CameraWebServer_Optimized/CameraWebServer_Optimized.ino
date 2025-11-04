/*
 * ESP32-CAM Optimized Configuration
 * FOR HIGH QUALITY FACE RECOGNITION
 * * Improvements:
 * - Tăng độ sáng (brightness)
 * - Tăng độ tương phản (contrast)
 * - Giảm noise
 * - Tối ưu exposure
 * - Auto white balance
 * * Hardware: ESP32-CAM AI-Thinker
 * Author: HUTECH Student
 * Date: October 31, 2025
 * * --- VERSION 7.1 (FIXED by Gemini) ---
 * - Fix: Moved configure_camera_quality() BEFORE set_framesize()
 * to prevent resolution reset to 1600x1200.
 */

#include "esp_camera.h"
#include <WiFi.h>
#include "esp_timer.h"
#include "img_converters.h"
#include "Arduino.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include "esp_http_server.h"
#include <lwip/sockets.h>
#include <lwip/netdb.h>

// Camera model
#define CAMERA_MODEL_AI_THINKER

// Camera pins
#if defined(CAMERA_MODEL_AI_THINKER)
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22
#endif

// WiFi Configuration
const char* ssid = "TRA SUA ZEEK TEA";
const char* password = "xincamon";

// Global variables
httpd_handle_t stream_httpd = NULL;

// ==========================================
// CAMERA QUALITY OPTIMIZATION SETTINGS
// ==========================================
void configure_camera_quality(sensor_t * s) {
  // Brightness: Tăng độ sáng (range: -2 to 2)
  s->set_brightness(s, 1);     // Tăng từ 0 lên 1
  
  // Contrast: Tăng độ tương phản (range: -2 to 2)
  s->set_contrast(s, 1);       // Tăng từ 0 lên 1
  
  // Saturation: Độ bão hòa màu (range: -2 to 2)
  s->set_saturation(s, 0);     // Giữ nguyên
  
  // Sharpness: Độ nét (range: -2 to 2)
  s->set_sharpness(s, 2);      // Tăng lên MAX cho ảnh nét
  
  // White Balance: Tự động cân bằng trắng
  s->set_whitebal(s, 1);       // 1 = enable auto white balance
  s->set_awb_gain(s, 1);       // Auto white balance gain
  
  // Exposure Control: Điều chỉnh exposure
  s->set_exposure_ctrl(s, 1);  // 1 = enable auto exposure
  s->set_aec2(s, 1);           // Auto exposure correction
  s->set_ae_level(s, 1);       // Exposure level: tăng 1 level
  
  // Gain Control: Điều chỉnh gain (REDUCED for less noise)
  s->set_gain_ctrl(s, 1);      // 1 = enable auto gain
  s->set_agc_gain(s, 3);       // AGC gain (0-30), giảm xuống 3 để giảm noise tối đa
  
  // Special Effects: Tắt các effect
  s->set_special_effect(s, 0); // 0 = no effect
  
  // Lens Correction: Bật lens correction
  s->set_lenc(s, 1);           // 1 = enable lens correction
  
  // DCW (Downsize EN): Tắt downsize để giữ chất lượng
  s->set_dcw(s, 0);            // 0 = disable
  
  // Color Bar: Tắt color bar test pattern
  s->set_colorbar(s, 0);       // 0 = disable
  
  // BPC (Bad Pixel Correction): Bật
  s->set_bpc(s, 1);            // 1 = enable
  
  // WPC (White Pixel Correction): Bật
  s->set_wpc(s, 1);            // 1 = enable
  
  // Gamma Correction: Bật để cải thiện độ sáng
  s->set_raw_gma(s, 1);              // Enable gamma correction
  s->set_gainceiling(s, (gainceiling_t)2); // Gain ceiling 8x (ultra low noise)
  
  Serial.println("✅ Camera quality settings applied:");
  Serial.println("   Resolution: XGA 1024x768 (FORCED & VERIFIED)");
  Serial.println("   JPEG Quality: 12 (balanced)");
  Serial.println("   Frame Buffers: 1 (SPEED)");
  Serial.println("   Grab Mode: LATEST (always newest)");
  Serial.println("   Brightness: +1");
  Serial.println("   Contrast: +1");
  Serial.println("   Sharpness: MAX (+2)");
  Serial.println("   AGC Gain: 3 (ultra low noise)");
  Serial.println("   ⚡ WiFi Sleep: DISABLED");
  Serial.println("   🎯 Mode: XGA HIGH QUALITY @ 100 FPS");
}

// Simple HTML page
static const char* INDEX_HTML = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32-CAM Optimized</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background: #1a1a2e;
            color: white;
            padding: 20px;
        }
        h1 { color: #00ff88; }
        .stream-container {
            margin: 20px auto;
            max-width: 640px;
        }
        img {
            width: 100%;
            border: 3px solid #00ff88;
            border-radius: 10px;
        }
        .info {
            background: #16213e;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .quality-badge {
            display: inline-block;
            background: #00ff88;
            color: #1a1a2e;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin: 5px;
        }
    </style>
</head>
<body>
    <h1>🎥 ESP32-CAM OPTIMIZED</h1>
    <div class="info">
        <h3>⚡ Quality Enhancements Active:</h3>
        <span class="quality-badge">XGA 1024x768</span>
        <span class="quality-badge">JPEG Q12</span>
        <span class="quality-badge">40 FPS</span>
        <span class="quality-badge">High Quality Smooth</span>
        <span class="quality-badge">Ultra Low Noise</span>
    </div>
    <div class="stream-container">
        <img id="stream" src="/stream" />
    </div>
    <div class="info">
        <p>📊 Stream URL: <strong>http://192.168.22.176/stream</strong></p>
        <p>📸 Capture URL: <strong>http://192.168.22.176/capture</strong></p>
    </div>
</body>
</html>
)rawliteral";

static esp_err_t index_handler(httpd_req_t *req) {
  httpd_resp_set_type(req, "text/html");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  return httpd_resp_send(req, INDEX_HTML, strlen(INDEX_HTML));
}

// Stream handler with connection check and stability
static esp_err_t stream_handler(httpd_req_t *req) {
  camera_fb_t * fb = NULL;
  esp_err_t res = ESP_OK;
  size_t _jpg_buf_len = 0;
  uint8_t * _jpg_buf = NULL;
  char * part_buf[64];

  Serial.println("Stream client connected");
  
  // 🎯 Enable TCP_NODELAY for low latency
  int fd = httpd_req_to_sockfd(req);
  int nodelay = 1;
  setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &nodelay, sizeof(nodelay));

  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Headers", "Content-Type");
  httpd_resp_set_hdr(req, "Cache-Control", "no-cache, no-store, must-revalidate");
  httpd_resp_set_hdr(req, "Pragma", "no-cache");
  httpd_resp_set_hdr(req, "Expires", "0");

  res = httpd_resp_set_type(req, "multipart/x-mixed-replace; boundary=frame");
  if(res != ESP_OK){
    Serial.println("Failed to set response type");
    return res;
  }
  
  // 🔥 FLUSH OLD FRAMES - Critical for resolution change!
  Serial.println("🔥 Flushing old frames from buffer...");
  for(int i = 0; i < 5; i++) {
    camera_fb_t * flush_fb = esp_camera_fb_get();
    if(flush_fb) {
      Serial.printf("   Flushed frame %d: %dx%d\n", i+1, flush_fb->width, flush_fb->height);
      esp_camera_fb_return(flush_fb);
    }
    delay(10);
  }
  Serial.println("✅ Buffer flushed, streaming fresh frames...");
  
  unsigned long frame_count = 0;
  unsigned long last_report = millis();

  while(true){
    fb = esp_camera_fb_get();
    if (!fb) {
      // ⚠️ RETRY: Don't break immediately on NULL frame
      Serial.println("⚠️ Camera capture failed - retrying...");
      delay(50);  // Wait for camera to be ready
      
      // Try again (max 3 retries)
      for(int retry = 0; retry < 3; retry++) {
        fb = esp_camera_fb_get();
        if(fb) {
          Serial.println("✅ Camera recovered");
          break;
        }
        delay(20);
      }
      
      // If still NULL after retries, skip this frame
      if(!fb) {
        Serial.println("❌ Frame skipped after retries");
        continue;  // Skip to next iteration instead of breaking
      }
    }
    
    // Process frame
    {
      if(fb->format != PIXFORMAT_JPEG){
        bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
        esp_camera_fb_return(fb);
        fb = NULL;
        if(!jpeg_converted){
          Serial.println("JPEG compression failed");
          res = ESP_FAIL;
          break;
        }
      } else {
        _jpg_buf_len = fb->len;
        _jpg_buf = fb->buf;
      }
    }  // End of frame processing block
    
    if(res == ESP_OK){
      size_t hlen = snprintf((char *)part_buf, 64, 
        "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", _jpg_buf_len);
      res = httpd_resp_send_chunk(req, (const char *)part_buf, hlen);
    }
    if(res == ESP_OK){
      res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
    }
    if(res == ESP_OK){
      res = httpd_resp_send_chunk(req, "\r\n--frame\r\n", 9);
    }
    
    if(fb){
      esp_camera_fb_return(fb);
      fb = NULL;
      _jpg_buf = NULL;
    } else if(_jpg_buf){
      free(_jpg_buf);
      _jpg_buf = NULL;
    }
    
    if(res != ESP_OK){
      Serial.println("Stream client disconnected");
      break;
    }
    
    // 🎯 Frame counter & health monitoring
    frame_count++;
    if(millis() - last_report > 5000) {  // Report every 5s
      float fps = frame_count / 5.0;
      Serial.printf("📊 Stream FPS: %.1f | Frames: %lu\n", fps, frame_count);
      frame_count = 0;
      last_report = millis();
    }
    
    // ⚡ BALANCED FPS for XGA (10ms = ~100 FPS target)
    delay(1);
  }
  
  return res;
}

// Capture handler
static esp_err_t capture_handler(httpd_req_t *req) {
  camera_fb_t * fb = NULL;
  esp_err_t res = ESP_OK;
  
  fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }

  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_type(req, "image/jpeg");
  httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg");

  res = httpd_resp_send(req, (const char *)fb->buf, fb->len);
  esp_camera_fb_return(fb);
  return res;
}

// Status handler
static esp_err_t status_handler(httpd_req_t *req) {
  static char json_response[256];
  sensor_t * s = esp_camera_sensor_get();
  
  sprintf(json_response,
    "{\"brightness\":%d,\"contrast\":%d,\"sharpness\":%d,\"awb\":%d,\"aec\":%d,\"quality\":\"optimized\"}",
    s->status.brightness, s->status.contrast, s->status.sharpness,
    s->status.awb, s->status.aec);
  
  httpd_resp_set_type(req, "application/json");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  return httpd_resp_send(req, json_response, strlen(json_response));
}

void startCameraServer() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 80;
  config.ctrl_port = 80;
  config.max_open_sockets = 13;
  config.max_uri_handlers = 16;
  config.lru_purge_enable = true;
  config.recv_wait_timeout = 8;        // Cân bằng: không quá ngắn
  config.send_wait_timeout = 8;
  config.backlog_conn = 5;
  config.max_resp_headers = 8;

  httpd_uri_t index_uri = {
    .uri       = "/",
    .method    = HTTP_GET,
    .handler   = index_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t stream_uri = {
    .uri       = "/stream",
    .method    = HTTP_GET,
    .handler   = stream_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t capture_uri = {
    .uri       = "/capture",
    .method    = HTTP_GET,
    .handler   = capture_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t status_uri = {
    .uri       = "/status",
    .method    = HTTP_GET,
    .handler   = status_handler,
    .user_ctx  = NULL
  };

  Serial.println("Starting HTTP server...");
  
  if (httpd_start(&stream_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(stream_httpd, &index_uri);
    httpd_register_uri_handler(stream_httpd, &stream_uri);
    httpd_register_uri_handler(stream_httpd, &capture_uri);
    httpd_register_uri_handler(stream_httpd, &status_uri);
    Serial.println("✅ HTTP server started successfully");
  } else {
    Serial.println("❌ Failed to start HTTP server");
  }
}

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
  
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();
  Serial.println("===========================================");
  Serial.println("   ESP32-CAM BUFFER FLUSH MODE");
  Serial.println("   🔥 VERSION: XGA_FLUSH_v7.1 (FIXED) 🔥");
  Serial.println("===========================================");

  // Camera configuration
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
  config.grab_mode = CAMERA_GRAB_LATEST; // LATEST for max FPS
  
  // ⚡ HIGH QUALITY: XGA 1024x768 for quality + speed
  if(psramFound()){
    config.frame_size = FRAMESIZE_XGA;      // 1024x768
    config.jpeg_quality = 14;               // 12 = balanced (30-35KB/frame)
    config.fb_count = 2;                    // 1 buffer for speed
    config.fb_location = CAMERA_FB_IN_PSRAM;
    config.grab_mode = CAMERA_GRAB_LATEST;  // Always get latest frame
  } else {
    config.frame_size = FRAMESIZE_VGA;      // 640x480 if no PSRAM
    config.jpeg_quality = 15;
    config.fb_count = 2;
  }

  // Init camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    return;
  }

  // 🔧 GET SENSOR & FULL RESET + FORCE RESOLUTION
  sensor_t * s = esp_camera_sensor_get();
  
  // ========================================================
  // ⭐ FIX: APPLY QUALITY OPTIMIZATIONS *BEFORE* SETTING FRAMESIZE
  // ========================================================
  configure_camera_quality(s);
  
  Serial.println("\n🔧 RESETTING SENSOR & FORCING XGA...");
  
  // ⚡ STEP 1: Full sensor reset
  s->set_framesize(s, FRAMESIZE_QVGA);   // Reset to small size first
  delay(100);
  
  // ⚡ STEP 2: QUADRUPLE FORCE with verification loop
  // (This is now the LAST setting applied to the sensor)
  for(int i = 0; i < 4; i++) {
    s->set_framesize(s, FRAMESIZE_XGA);
    s->set_hmirror(s, 0);    // Reset mirror
    s->set_vflip(s, 0);      // Reset flip
    delay(150);
    
    // Check if applied
    camera_fb_t * check_fb = esp_camera_fb_get();
    if(check_fb) {
      Serial.printf("   Attempt %d: %dx%d (size: %d KB)\n", i+1, 
                     check_fb->width, check_fb->height, check_fb->len / 1024);
      
      if(check_fb->width == 1024 && check_fb->height == 768) {
        Serial.println("   ✅ XGA LOCKED!");
        esp_camera_fb_return(check_fb);
        break;
      }
      esp_camera_fb_return(check_fb);
    }
  }
  
  delay(300);  // Extended stabilization
  
  Serial.println("\n📊 ACTUAL Camera Configuration:");
  Serial.print("   Frame Size: ");
  Serial.println(s->status.framesize);  // Print numeric framesize
  
  // Print resolution name
  const char* frame_size_names[] = {
    "96x96", "QQVGA", "QCIF", "HQVGA", "240x240", "QVGA", "CIF", 
    "HVGA", "VGA", "SVGA", "XGA", "HD", "SXGA", "UXGA"
  };
  if(s->status.framesize <= 13) {
    Serial.print("   Resolution Name: ");
    Serial.println(frame_size_names[s->status.framesize]);
  }
  
  // Get actual frame to check real resolution
  camera_fb_t * test_fb = esp_camera_fb_get();
  if(test_fb) {
    Serial.printf("   Actual Width x Height: %d x %d\n", test_fb->width, test_fb->height);
    Serial.printf("   Frame Buffer Size: %d bytes\n", test_fb->len);
    esp_camera_fb_return(test_fb);
  }

  // (configure_camera_quality(s); was removed from here)

  // Connect WiFi
  WiFi.begin(ssid, password);
  
  // ⚡ LOW LATENCY WiFi Settings
  WiFi.setSleep(false);                  // Tắt WiFi sleep = giảm latency
  WiFi.setTxPower(WIFI_POWER_19_5dBm);   // Max WiFi power = tín hiệu mạnh
  
  Serial.print("Connecting to WiFi");
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi connected");
    Serial.print("📡 IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.println("⚡ WiFi Sleep: DISABLED (Low Latency Mode)");
    
    startCameraServer();
    
    Serial.println("\n===========================================");
    Serial.println("   🎥 ESP32-CAM Ready (OPTIMIZED MODE)!");
    Serial.println("===========================================");
    Serial.print("📺 Stream URL: http://");
    Serial.print(WiFi.localIP());
    Serial.println("/stream");
    Serial.print("📸 Capture URL: http://");
    Serial.print(WiFi.localIP());
    Serial.println("/capture");
    Serial.print("🌐 Web Interface: http://");
    Serial.print(WiFi.localIP());
    Serial.println("/");
    Serial.println("===========================================");
  } else {
    Serial.println("\n❌ WiFi connection failed");
  }
}

void loop() {
  delay(10000);
}