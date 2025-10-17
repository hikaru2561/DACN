/*
 * Hệ thống Điểm danh bằng Nhận dạng Khuôn mặt
 * ESP32-CAM + OLED SSD1306 + Speaker + PAM8403
 * 
 * Tính năng:
 * - Chụp ảnh khuôn mặt và gửi lên server Python
 * - Hiển thị kết quả trên OLED 128x64
 * - Phát âm thanh thông báo tiếng Việt qua Speaker
 * - Web interface để quản lý và đăng ký
 * - Kết nối WiFi và HTTP API
 * 
 * Phần cứng:
 * - ESP32-CAM
 * - OLED SSD1306 128x64 (I2C: SDA=GPIO21, SCL=GPIO22)
 * - Speaker + PAM8403 (I2S: DIN=GPIO25, BCLK=GPIO26, LRC=GPIO27)
 * 
 * Tác giả: [Tên sinh viên]
 * Ngày: 2024
*/

#include "esp_camera.h"
#include <WiFi.h>
#include "esp_timer.h"
#include "img_converters.h"
#include "Arduino.h"
#include "fb_gfx.h"
#include "soc/soc.h"           // Disable brownout problems
#include "soc/rtc_cntl_reg.h"  // Disable brownout problems
#include "esp_http_server.h"
#include <HTTPClient.h>

// Select camera model
#define CAMERA_MODEL_AI_THINKER // Has PSRAM
//#define CAMERA_MODEL_ESP_EYE // Has PSRAM
//#define CAMERA_MODEL_ESP32S3_EYE // Has PSRAM
//#define CAMERA_MODEL_M5STACK_PSRAM // Has PSRAM
//#define CAMERA_MODEL_M5STACK_V2_PSRAM // M5Camera version B Has PSRAM
//#define CAMERA_MODEL_M5STACK_WIDE // Has PSRAM
//#define CAMERA_MODEL_M5STACK_ESP32CAM // No PSRAM
//#define CAMERA_MODEL_TTGO_T_JOURNAL // No PSRAM
//#define CAMERA_MODEL_WROVER_KIT // Has PSRAM

#include <ArduinoJson.h>

// Camera pin definitions for AI_THINKER
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
#else
  #error "Camera model not selected"
#endif
// #include <Wire.h>
// #include <Adafruit_GFX.h>
// #include <Adafruit_SSD1306.h>
// #include <Audio.h>

// ===================
// WiFi Configuration
// ===================
const char* ssid = "K9";           // Thay đổi SSID WiFi của bạn
const char* password = "nk111111";   // Thay đổi password WiFi của bạn

// ===================
// Server Configuration
// ===================
const char* serverUrl = "http://192.168.219.62:5000"; // Thay đổi IP của máy chủ Python (thay đổi IP này thành IP máy tính của bạn)

// ===================
// Camera Configuration
// ===================
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

// ===================
// OLED Configuration (COMMENTED FOR TESTING)
// ===================
// #define SCREEN_WIDTH 128
// #define SCREEN_HEIGHT 64
// #define OLED_RESET -1
// #define SCREEN_ADDRESS 0x3C
// Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// ===================
// Audio Configuration (COMMENTED FOR TESTING)
// ===================
// Audio audio;
// #define I2S_DOUT_PIN 25  // Data Out (SD)
// #define I2S_BCLK_PIN 26  // Bit Clock (SCK)
// #define I2S_LRC_PIN 27   // Left/Right Clock (WS)

// ===================
// Button Configuration (COMMENTED FOR TESTING)
// ===================
// #define BUTTON_PIN 4     // Nút điểm danh
// #define FLASH_PIN 2      // Nút đăng ký

// ===================
// Global Variables
// ===================
httpd_handle_t stream_httpd = NULL;
httpd_handle_t camera_httpd = NULL;
bool isStreaming = false;
unsigned long lastButtonPress = 0;
const unsigned long debounceDelay = 200;

// ===================
// Auto Face Detection Variables
// ===================
bool autoDetectionEnabled = false;
unsigned long faceDetectedTime = 0;
bool faceCurrentlyDetected = false;
const unsigned long faceDetectionDelay = 2500; // 2.5 seconds
unsigned long lastAutoCapture = 0;
const unsigned long autoCaptureCooldown = 5000; // 5 seconds cooldown

// ===================
// Base64 Encoding Function
// ===================
String base64_encode(uint8_t* data, size_t length) {
  const char* chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
  String result = "";
  int i = 0;
  int j = 0;
  uint8_t char_array_3[3];
  uint8_t char_array_4[4];

  while (i < length) {
    char_array_3[i % 3] = data[i];
    i++;
    if (i % 3 == 0) {
      char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
      char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
      char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
      char_array_4[3] = char_array_3[2] & 0x3f;

      for (j = 0; (j < 4); j++) {
        result += chars[char_array_4[j]];
      }
    }
  }

  if (i % 3) {
    for (j = i % 3; j < 3; j++) {
      char_array_3[j] = '\0';
    }

    char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
    char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
    char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
    char_array_4[3] = char_array_3[2] & 0x3f;

    for (j = 0; (j < i % 3 + 1); j++) {
      result += chars[char_array_4[j]];
    }

    while ((i % 3) != 0) {
      result += '=';
      i++;
    }
  }

  return result;
}

// ===================
// Text-to-Speech Function (COMMENTED FOR TESTING)
// ===================
/*
void playTTS(String text) {
  // Sử dụng Google Translate TTS (miễn phí)
  String url = "http://translate.google.com/translate_tts?ie=UTF-8&q=" + text + "&tl=vi&client=tw-ob";
  
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Playing TTS...");
  display.display();
  
  audio.connecttohost(url.c_str());
  
  // Chờ audio phát xong
  while (audio.isRunning()) {
    audio.loop();
    delay(10);
  }
  
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("TTS Complete");
  display.display();
  delay(1000);
}
*/

// ===================
// Simple Face Detection Function
// ===================
bool detectFaceInFrame(camera_fb_t * fb) {
  // Simple face detection based on image characteristics
  // This is a basic implementation - in real scenario, you'd use OpenCV or similar
  
  if (!fb || fb->len < 1000) return false;
  
  // Simple heuristic: check if image has enough contrast and brightness
  // This is a placeholder - real face detection would be more sophisticated
  uint8_t* buf = fb->buf;
  int totalPixels = fb->len;
  int brightPixels = 0;
  int darkPixels = 0;
  
  for (int i = 0; i < totalPixels; i += 10) { // Sample every 10th pixel
    if (buf[i] > 150) brightPixels++;
    else if (buf[i] < 100) darkPixels++;
  }
  
  // If we have good contrast (both bright and dark areas), assume face is present
  float contrast = (float)(brightPixels + darkPixels) / (totalPixels / 10);
  return contrast > 0.3; // Threshold for face detection
}

// ===================
// Auto Capture Function (COMMENTED FOR TESTING)
// ===================
/*
void performAutoCapture() {
  if (millis() - lastAutoCapture < autoCaptureCooldown) {
    return; // Still in cooldown period
  }
  
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Auto capturing...");
  display.display();
  
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Auto capture failed - camera error");
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Camera error!");
    display.display();
    return;
  }

  String imageData = base64_encode(fb->buf, fb->len);
  esp_camera_fb_return(fb);

  HTTPClient http;
  http.begin(serverUrl + String("/checkin"));
  http.addHeader("Content-Type", "application/json");
  
  String jsonData = "{\"image\":\"" + imageData + "\"}";
  int httpResponseCode = http.POST(jsonData);
  
  String response = http.getString();
  http.end();

  DynamicJsonDocument responseDoc(1024);
  deserializeJson(responseDoc, response);

  lastAutoCapture = millis();

  if (responseDoc["success"]) {
    String userName = responseDoc["user"]["name"];
    float confidence = responseDoc["user"]["confidence"];
    
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Auto Check-in!");
    display.println("Name: " + userName);
    display.print("Conf: ");
    display.println(confidence);
    display.display();
    
    String message = "Tự động điểm danh thành công với người dùng " + userName;
    playTTS(message);
  } else {
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Auto Check-in");
    display.println("Failed!");
    display.display();
    
    playTTS("Tự động điểm danh thất bại. Khuôn mặt không được nhận diện.");
  }
}
*/

// ===================
// HTTP Server Handlers
// ===================
static const char* PROGMEM INDEX_HTML = R"rawliteral(
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32-CAM Face Recognition System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            text-align: center; 
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        
        .title {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .subtitle {
            font-size: 1.2em;
            margin-bottom: 30px;
            opacity: 0.9;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 20px;
        }
        
        .left-panel {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .right-panel {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .camera-container {
            position: relative;
            background: rgba(0,0,0,0.3);
            border-radius: 15px;
            padding: 20px;
            min-height: 400px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        
        #stream {
            max-width: 100%;
            max-height: 400px;
            border-radius: 10px;
            box-shadow: 0 4px 15px 0 rgba(0,0,0,0.3);
            display: none;
        }
        
        .face-overlay {
            position: absolute;
            border: 3px solid #00ff00;
            border-radius: 5px;
            display: none;
            pointer-events: none;
            box-shadow: 0 0 10px rgba(0,255,0,0.5);
        }
        
        .captured-image {
            max-width: 100%;
            max-height: 200px;
            border-radius: 10px;
            box-shadow: 0 4px 15px 0 rgba(0,0,0,0.3);
            margin-top: 10px;
            display: none;
        }
        
        .status { 
            margin: 20px 0; 
            padding: 15px; 
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.3);
        }
        
        .status h3 {
            margin: 0 0 10px 0;
            color: #FFD700;
        }
        
        .button { 
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            border: none; 
            color: white; 
            padding: 12px 24px; 
            text-align: center; 
            text-decoration: none; 
            display: inline-block; 
            font-size: 16px; 
            margin: 5px; 
            cursor: pointer; 
            border-radius: 25px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px 0 rgba(31, 38, 135, 0.2);
            width: 100%;
        }
        
        .button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 6px 20px 0 rgba(31, 38, 135, 0.4);
        }
        
        .button:active {
            transform: translateY(0);
        }
        
        .button-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin: 10px 0;
        }
        
        .button-group.single {
            grid-template-columns: 1fr;
        }
        
        #result {
            margin: 20px 0;
            padding: 15px;
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            min-height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        }
        
        .camera-placeholder {
            color: #ccc;
            font-size: 1.2em;
            text-align: center;
        }
        
        .face-detection-info {
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0,0,0,0.7);
            color: #00ff00;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
            display: none;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .button-group {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">🎯 Face Recognition System</h1>
        <p class="subtitle">Hệ thống Điểm danh bằng Nhận dạng Khuôn mặt</p>
        
        <div class="status">
            <h3>📊 System Status</h3>
            <p><strong>Status:</strong> <span id="status">Ready</span></p>
            <p><strong>Server:</strong> <span id="server">Disconnected</span></p>
            <p><strong>WiFi:</strong> <span id="wifi">Connected</span></p>
        </div>
        
        <div class="main-content">
            <div class="left-panel">
                <div class="camera-container">
                    <div class="camera-placeholder" id="cameraPlaceholder">
                        📹 Nhấn "Start Camera" để bắt đầu
                    </div>
                    <img id="streamImg" alt="Camera Stream" style="width: 100%; height: 300px; object-fit: cover;">
                    <div class="face-overlay" id="faceOverlay"></div>
                    <div class="face-detection-info" id="faceDetectionInfo">
                        Khuôn mặt được phát hiện
                    </div>
                </div>
                
                <div class="button-group">
                    <button class="button" onclick="startStream()">📹 Start Camera</button>
                    <button class="button" onclick="stopStream()">⏹️ Stop Camera</button>
                </div>
                
                <div class="button-group">
                    <button class="button" onclick="checkin()">✅ Check-in (Điểm danh)</button>
                    <button class="button" onclick="register()">👤 Register (Đăng ký)</button>
                </div>
                
                <div class="button-group single">
                    <button class="button" onclick="toggleAutoDetection()" id="autoBtn">🤖 Enable Auto Detection</button>
                </div>
            </div>
            
            <div class="right-panel">
                <div id="result"></div>
                
                        <div class="button-group">
                            <button class="button" onclick="testConnection()">🔧 Test Server</button>
                            <button class="button" onclick="testStream()">📹 Test Stream</button>
                            <button class="button" onclick="testFaceDetection()">👤 Test Face Detection</button>
                            <button class="button" onclick="getUsers()">👥 View Users</button>
                        </div>
                
                <div class="button-group single">
                    <button class="button" onclick="getStatus()">📊 System Status</button>
                </div>
                
                <div id="capturedImageContainer" style="display: none;">
                    <h4>Ảnh vừa chụp:</h4>
                    <img id="capturedImage" class="captured-image" alt="Captured Image">
                </div>
            </div>
        </div>
    </div>
    
    <script>
      let streamInterval;
      let faceDetectionInterval;
      let isStreaming = false;
      let isUpdating = false;
      
      function startStream() {
        console.log('Starting stream...');
        const streamImg = document.getElementById('streamImg');
        const placeholder = document.getElementById('cameraPlaceholder');
        
        if (!streamImg) {
          console.error('Stream image element not found!');
          return;
        }
        
        if (!placeholder) {
          console.error('Placeholder element not found!');
          return;
        }
        
        console.log('Elements found, starting stream...');
        streamImg.style.display = 'block';  // Show img element
        placeholder.style.display = 'none';
        
        const streamUrl = 'http://' + window.location.hostname + ':81/stream';
        console.log('Stream URL:', streamUrl);
        
        // Set stream source directly - browser will handle multipart/x-mixed-replace
        streamImg.src = streamUrl;
        
        streamImg.onload = function() {
          console.log('Stream loaded successfully');
          document.getElementById('status').textContent = 'Streaming';
          document.getElementById('status').style.color = '#4ECDC4';
        };
        
        streamImg.onerror = function() {
          console.error('Stream failed to load, trying snapshot method');
          
          // Method 2: Use snapshot polling as fallback
          const snapshotUrl = 'http://' + window.location.hostname + ':81/snapshot';
          
          function updateSnapshot() {
            if (isStreaming && !isUpdating) {
              isUpdating = true;
              const img = new Image();
              img.onload = function() {
                streamImg.src = img.src;
                isUpdating = false;
              };
              img.onerror = function() {
                console.log('Snapshot request failed, retrying...');
                isUpdating = false;
              };
              img.src = snapshotUrl + '?t=' + new Date().getTime();
            }
          }
          
          // Start snapshot polling
          updateSnapshot();
          streamInterval = setInterval(updateSnapshot, 800); // Update every 800ms (1.25 FPS)
          
          document.getElementById('status').textContent = 'Streaming (snapshot)';
          document.getElementById('status').style.color = '#4ECDC4';
        };
        
        // No need for Method 3, using Method 1 (stream) and Method 2 (snapshot fallback)
        
        document.getElementById('status').textContent = 'Streaming';
        document.getElementById('status').style.color = '#4ECDC4';
        
        isStreaming = true;
        
        // Start real face detection
        startRealFaceDetection();
      }
      
      function stopStream() {
        const streamImg = document.getElementById('streamImg');
        const placeholder = document.getElementById('cameraPlaceholder');
        
        // Stop snapshot polling
        if (streamInterval) {
          clearInterval(streamInterval);
          streamInterval = null;
        }
        
        streamImg.style.display = 'none';
        placeholder.style.display = 'block';
        streamImg.src = '';
        
        document.getElementById('status').textContent = 'Stopped';
        document.getElementById('status').style.color = '#FF6B6B';
        
        isStreaming = false;
        stopFaceDetection();
      }
      
      function startFaceDetection() {
        if (faceDetectionInterval) clearInterval(faceDetectionInterval);
        
        let lastDetectionTime = 0;
        const detectionCooldown = 3000; // 3 giây cooldown để tránh spam
        
        // Face detection simulation DISABLED - waiting for real AI implementation
        // faceDetectionInterval = setInterval(() => {
        //   if (isStreaming) {
        //     const now = Date.now();
        //     // Chỉ detect nếu đã qua cooldown và random > 0.8 (giảm tần suất)
        //     if (now - lastDetectionTime > detectionCooldown && Math.random() > 0.8) {
        //       showFaceOverlay();
        //       lastDetectionTime = now;
        //       
        //       // Tự động ẩn sau 2 giây
        //       setTimeout(() => {
        //         hideFaceOverlay();
        //       }, 2000);
        //     } else {
        //       hideFaceOverlay();
        //     }
        //   }
        // }, 1000); // Check mỗi 1 giây thay vì 2 giây
      }
      
      function stopFaceDetection() {
        if (faceDetectionInterval) {
          clearInterval(faceDetectionInterval);
          faceDetectionInterval = null;
        }
        hideFaceOverlay();
      }
      
      // Real face detection function
      function startRealFaceDetection() {
        if (faceDetectionInterval) clearInterval(faceDetectionInterval);
        
        let lastDetectionTime = 0;
        const detectionCooldown = 3000; // 3 giây cooldown để tránh spam
        
        faceDetectionInterval = setInterval(() => {
          if (isStreaming) {
            const now = Date.now();
            if (now - lastDetectionTime > detectionCooldown) {
              detectFaceInStream();
              lastDetectionTime = now;
            }
          }
        }, 2000); // Check mỗi 2 giây
      }
      
      // Detect face in current stream frame
      function detectFaceInStream() {
        // Capture current stream frame
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const streamImg = document.getElementById('streamImg');
        
        canvas.width = streamImg.naturalWidth || 640;
        canvas.height = streamImg.naturalHeight || 480;
        
        ctx.drawImage(streamImg, 0, 0);
        
        // Convert to blob and send to server
        canvas.toBlob((blob) => {
          const formData = new FormData();
          formData.append('image', blob, 'frame.jpg');
          
          fetch('http://192.168.219.62:5000/detect-face', {
            method: 'POST',
            body: formData
          })
          .then(response => response.json())
          .then(data => {
            if (data.faces && data.faces.length > 0) {
              // Draw bounding boxes for detected faces
              drawFaceBoxes(data.faces, canvas.width, canvas.height);
            } else {
              hideFaceOverlay();
            }
          })
          .catch(error => {
            console.log('Face detection error:', error);
            hideFaceOverlay();
          });
        }, 'image/jpeg', 0.8);
      }
      
      // Draw bounding boxes for detected faces
      function drawFaceBoxes(faces, imgWidth, imgHeight) {
        const overlay = document.getElementById('faceOverlay');
        const info = document.getElementById('faceDetectionInfo');
        
        if (faces.length > 0) {
          const face = faces[0]; // Use first detected face
          
          // Convert server coordinates to display coordinates
          const containerWidth = 300; // Camera container width
          const containerHeight = 300; // Camera container height
          
          const scaleX = containerWidth / imgWidth;
          const scaleY = containerHeight / imgHeight;
          
          const x = face.x * scaleX;
          const y = face.y * scaleY;
          const width = face.width * scaleX;
          const height = face.height * scaleY;
          
          overlay.style.left = x + 'px';
          overlay.style.top = y + 'px';
          overlay.style.width = width + 'px';
          overlay.style.height = height + 'px';
          overlay.style.display = 'block';
          
          info.style.display = 'block';
          info.textContent = `Khuôn mặt được phát hiện (${faces.length})`;
          
          // Auto hide after 2 seconds
          setTimeout(() => {
            hideFaceOverlay();
          }, 2000);
        } else {
          hideFaceOverlay();
        }
      }
      
      // Manual face detection test function
      function testFaceDetection() {
        console.log('Testing face detection...');
        detectFaceInStream();
      }
      
      function showFaceOverlay() {
        const overlay = document.getElementById('faceOverlay');
        const info = document.getElementById('faceDetectionInfo');
        
        // Vị trí cố định ở giữa màn hình thay vì random
        const containerWidth = 300; // Width của camera container
        const containerHeight = 300; // Height của camera container
        
        // Tính toán vị trí trung tâm
        const faceWidth = 120; // Kích thước cố định cho khung mặt
        const faceHeight = 120;
        const x = (containerWidth - faceWidth) / 2;
        const y = (containerHeight - faceHeight) / 2;
        
        overlay.style.left = x + 'px';
        overlay.style.top = y + 'px';
        overlay.style.width = faceWidth + 'px';
        overlay.style.height = faceHeight + 'px';
        overlay.style.display = 'block';
        
        info.style.display = 'block';
        
        // Hide after 1 second
        setTimeout(() => {
          hideFaceOverlay();
        }, 1000);
      }
      
      function hideFaceOverlay() {
        document.getElementById('faceOverlay').style.display = 'none';
        document.getElementById('faceDetectionInfo').style.display = 'none';
      }
      
      function showCapturedImage(imageData) {
        const container = document.getElementById('capturedImageContainer');
        const img = document.getElementById('capturedImage');
        
        img.src = 'data:image/jpeg;base64,' + imageData;
        container.style.display = 'block';
        
        // Auto hide after 10 seconds
        setTimeout(() => {
          container.style.display = 'none';
        }, 10000);
      }
      
      function checkin() {
        document.getElementById('result').innerHTML = '<p><span class="loading"></span> Đang xử lý check-in...</p>';
        
        // Capture current frame for display and checkin
        const streamImg = document.getElementById('streamImg');
        if (streamImg.src) {
          // Create canvas to capture current frame
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          canvas.width = streamImg.naturalWidth || 640;
          canvas.height = streamImg.naturalHeight || 480;
          ctx.drawImage(streamImg, 0, 0);
          
          // Send to server for checkin
          canvas.toBlob((blob) => {
            const formData = new FormData();
            formData.append('image', blob, 'checkin.jpg');
            
            fetch('http://192.168.219.62:5000/checkin', {
              method: 'POST',
              body: formData
            })
            .then(response => response.json())
            .then(data => {
              if (data.success) {
                document.getElementById('result').innerHTML = 
                  '<p>✅ <strong>Check-in thành công!</strong><br>' +
                  'Tên: ' + data.user.name + '<br>' +
                  'Mã sinh viên: ' + data.user.student_code + '<br>' +
                  'Độ tin cậy: ' + (data.confidence * 100).toFixed(1) + '%<br>' +
                  'Thời gian: ' + new Date().toLocaleString() + '</p>';
                
                // Show captured image
                showCapturedImage(canvas.toDataURL('image/jpeg', 0.8));
              } else {
                document.getElementById('result').innerHTML = 
                  '<p>❌ <strong>Check-in thất bại!</strong><br>' + data.message + '</p>';
              }
            })
            .catch(error => {
              document.getElementById('result').innerHTML = 
                '<p>❌ <strong>Lỗi:</strong> ' + error + '</p>';
            });
          }, 'image/jpeg', 0.8);
        }
      }
      
      function register() {
        const name = prompt('Nhập tên của bạn:');
        const studentCode = prompt('Nhập mã sinh viên:');
        if (name && studentCode) {
          document.getElementById('result').innerHTML = '<p><span class="loading"></span> Đang xử lý đăng ký...</p>';
          
          // Capture current frame for display and registration
          const streamImg = document.getElementById('streamImg');
          if (streamImg.src) {
            // Create canvas to capture current frame
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = streamImg.naturalWidth || 640;
            canvas.height = streamImg.naturalHeight || 480;
            ctx.drawImage(streamImg, 0, 0);
            
            // Send to server for registration
            canvas.toBlob((blob) => {
              const formData = new FormData();
              formData.append('image', blob, 'register.jpg');
              formData.append('name', name);
              formData.append('student_code', studentCode);
              
              fetch('http://192.168.219.62:5000/register', {
                method: 'POST',
                body: formData
              })
              .then(response => response.json())
              .then(data => {
                if (data.success) {
                  document.getElementById('result').innerHTML = 
                    '<p>✅ <strong>Đăng ký thành công!</strong><br>' +
                    'Tên: ' + data.user.name + '<br>' +
                    'Mã SV: ' + data.user.student_code + '<br>' +
                    'ID: ' + data.user.user_id + '</p>';
                  
                  // Show captured image
                  showCapturedImage(canvas.toDataURL('image/jpeg', 0.8));
                } else {
                  document.getElementById('result').innerHTML = 
                    '<p>❌ <strong>Đăng ký thất bại:</strong> ' + data.message + '</p>';
                }
              })
              .catch(error => {
                document.getElementById('result').innerHTML = 
                  '<p>❌ <strong>Lỗi:</strong> ' + error + '</p>';
              });
            }, 'image/jpeg', 0.8);
          }
        }
      } 
                '<p>✅ <strong>Đăng ký thành công!</strong><br>' +
                'ID người dùng: ' + data.user_id + '<br>' +
                'Tên: ' + name + '<br>' +
                'Mã sinh viên: ' + studentCode + '</p>';
            } else {
              document.getElementById('result').innerHTML = 
                '<p>❌ <strong>Đăng ký thất bại!</strong><br>' + data.error + '</p>';
            }
          })
          .catch(error => {
            document.getElementById('result').innerHTML = 
              '<p>❌ <strong>Lỗi:</strong> ' + error + '</p>';
          });
        }
      }
      
      function testConnection() {
        document.getElementById('result').innerHTML = '<p><span class="loading"></span> Đang kiểm tra kết nối...</p>';
        fetch('/test-connection', {method: 'GET'})
          .then(response => response.json())
          .then(data => {
            document.getElementById('result').innerHTML = 
              '<p>🔧 <strong>Trạng thái Server:</strong><br>' +
              'Kết nối: ' + (data.connected ? '✅ Có' : '❌ Không') + '<br>' +
              'URL Server: ' + data.server_url + '<br>' +
              'Mã phản hồi: ' + data.response_code + '</p>';
            document.getElementById('server').textContent = data.connected ? 'Connected' : 'Disconnected';
            document.getElementById('server').style.color = data.connected ? '#4ECDC4' : '#FF6B6B';
          })
          .catch(error => {
            document.getElementById('result').innerHTML = 
              '<p>❌ <strong>Lỗi:</strong> ' + error + '</p>';
            document.getElementById('server').textContent = 'Error';
            document.getElementById('server').style.color = '#FF6B6B';
          });
      }
      
      function testStream() {
        document.getElementById('result').innerHTML = '<p><span class="loading"></span> Đang test stream...</p>';
        const streamUrl = 'http://' + window.location.hostname + ':81/stream';
        const snapshotUrl = 'http://' + window.location.hostname + ':81/snapshot';
        console.log('Testing stream URL:', streamUrl);
        console.log('Testing snapshot URL:', snapshotUrl);
        
        // Test snapshot first (simpler)
        fetch(snapshotUrl, {method: 'GET'})
          .then(response => {
            if (response.ok) {
              document.getElementById('result').innerHTML = 
                '<p>✅ <strong>Camera hoạt động!</strong><br>' +
                'Snapshot URL: ' + snapshotUrl + '<br>' +
                'Status: ' + response.status + '<br>' +
                'Content-Type: ' + response.headers.get('content-type') + '<br><br>' +
                'Stream URL: ' + streamUrl + '<br>' +
                'Có thể stream sẽ hoạt động!</p>';
            } else {
              document.getElementById('result').innerHTML = 
                '<p>❌ <strong>Camera lỗi!</strong><br>' +
                'Status: ' + response.status + '<br>' +
                'URL: ' + snapshotUrl + '</p>';
            }
          })
          .catch(error => {
            document.getElementById('result').innerHTML = 
              '<p>❌ <strong>Camera không kết nối được!</strong><br>' +
              'Lỗi: ' + error + '<br>' +
              'URL: ' + snapshotUrl + '</p>';
          });
      }
      
      function getUsers() {
        document.getElementById('result').innerHTML = '<p><span class="loading"></span> Đang tải danh sách người dùng...</p>';
        fetch('/users', {method: 'GET'})
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              let usersHtml = '<p>👥 <strong>Danh sách người dùng:</strong><br>';
              data.data.forEach(user => {
                usersHtml += '• ' + user.name + ' (' + user.student_code + ')<br>';
              });
              usersHtml += '<br>Tổng cộng: ' + data.count + ' người dùng</p>';
              document.getElementById('result').innerHTML = usersHtml;
            } else {
              document.getElementById('result').innerHTML = 
                '<p>❌ <strong>Lỗi:</strong> ' + data.error + '</p>';
            }
          })
          .catch(error => {
            document.getElementById('result').innerHTML = 
              '<p>❌ <strong>Lỗi:</strong> ' + error + '</p>';
          });
      }
      
      function toggleAutoDetection() {
        const button = document.getElementById('autoBtn');
        const isEnabled = button.textContent.includes('Disable');
        
        document.getElementById('result').innerHTML = '<p><span class="loading"></span> ' + (isEnabled ? 'Đang tắt' : 'Đang bật') + ' tự động phát hiện...</p>';
        
        fetch('/auto-detection', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({enabled: !isEnabled})
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            button.textContent = data.auto_detection_enabled ? '🤖 Tắt Tự động phát hiện' : '🤖 Bật Tự động phát hiện';
            button.style.background = data.auto_detection_enabled ? 
              'linear-gradient(45deg, #FF6B6B, #4ECDC4)' : 
              'linear-gradient(45deg, #4ECDC4, #45B7D1)';
            
            document.getElementById('result').innerHTML = 
              '<p>✅ <strong>' + data.message + '</strong><br>' +
              'Tự động phát hiện: ' + (data.auto_detection_enabled ? '🟢 BẬT' : '🔴 TẮT') + '</p>';
          } else {
            document.getElementById('result').innerHTML = 
              '<p>❌ <strong>Lỗi:</strong> ' + data.error + '</p>';
          }
        })
        .catch(error => {
          document.getElementById('result').innerHTML = 
            '<p>❌ <strong>Lỗi:</strong> ' + error + '</p>';
        });
      }
      
      function getStatus() {
        document.getElementById('result').innerHTML = '<p><span class="loading"></span> Đang lấy trạng thái hệ thống...</p>';
        fetch('/status', {method: 'GET'})
          .then(response => response.json())
          .then(data => {
            const uptime = Math.floor(data.uptime_ms / 1000);
            const hours = Math.floor(uptime / 3600);
            const minutes = Math.floor((uptime % 3600) / 60);
            const seconds = uptime % 60;
            
            document.getElementById('result').innerHTML = 
              '<p>📊 <strong>Trạng thái hệ thống:</strong><br>' +
              'Tự động phát hiện: ' + (data.auto_detection_enabled ? '🟢 BẬT' : '🔴 TẮT') + '<br>' +
              'Khuôn mặt phát hiện: ' + (data.face_currently_detected ? '🟢 CÓ' : '🔴 KHÔNG') + '<br>' +
              'WiFi: ' + (data.wifi_connected ? '🟢 Đã kết nối' : '🔴 Mất kết nối') + '<br>' +
              'IP: ' + data.wifi_ip + '<br>' +
              'Server: ' + data.server_url + '<br>' +
              'Thời gian hoạt động: ' + hours + 'h ' + minutes + 'm ' + seconds + 's</p>';
          })
          .catch(error => {
            document.getElementById('result').innerHTML = 
              '<p>❌ <strong>Lỗi:</strong> ' + error + '</p>';
          });
      }
      
      // Auto-refresh status every 30 seconds (DISABLED)
      // setInterval(testConnection, 30000);
    </script>
  </body>
</html>
)rawliteral";

static esp_err_t index_handler(httpd_req_t *req) {
  httpd_resp_set_type(req, "text/html");
  return httpd_resp_send(req, INDEX_HTML, strlen(INDEX_HTML));
}

static esp_err_t stream_handler(httpd_req_t *req) {
  camera_fb_t * fb = NULL;
  esp_err_t res = ESP_OK;
  size_t _jpg_buf_len = 0;
  uint8_t * _jpg_buf = NULL;
  char * part_buf[64];

  res = httpd_resp_set_type(req, "multipart/x-mixed-replace;boundary=123456789000000000000987654321");
  if(res != ESP_OK){
    return res;
  }
  
  while(true){
    
    fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      res = ESP_FAIL;
    } else {
      if(fb->format != PIXFORMAT_JPEG){
        bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
        esp_camera_fb_return(fb);
        fb = NULL;
        if(!jpeg_converted){
          Serial.println("JPEG compression failed");
          res = ESP_FAIL;
        }
      } else {
        _jpg_buf_len = fb->len;
        _jpg_buf = fb->buf;
      }
    }
    if(res == ESP_OK){
      size_t hlen = snprintf((char *)part_buf, 64, "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", _jpg_buf_len);
      res = httpd_resp_send_chunk(req, (const char *)part_buf, hlen);
    }
    if(res == ESP_OK){
      res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
    }
    if(res == ESP_OK){
      res = httpd_resp_send_chunk(req, "\r\n--123456789000000000000987654321\r\n", 40);
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
      break;
    }
  }
  return res;
}

static esp_err_t snapshot_handler(httpd_req_t *req) {
  camera_fb_t * fb = NULL;
  esp_err_t res = ESP_OK;
  
  Serial.println("Snapshot handler called");
  
  fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }
  
  // Add CORS headers
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Methods", "GET, POST, OPTIONS, HEAD");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Headers", "Content-Type");
  httpd_resp_set_hdr(req, "Access-Control-Max-Age", "3600");
  
  res = httpd_resp_set_type(req, "image/jpeg");
  if(res != ESP_OK){
    Serial.println("Failed to set response type");
    esp_camera_fb_return(fb);
    return res;
  }
  
  res = httpd_resp_send(req, (const char *)fb->buf, fb->len);
  esp_camera_fb_return(fb);
  
  if(res != ESP_OK){
    Serial.println("Failed to send response");
  } else {
    Serial.println("Snapshot sent successfully");
  }
  
  return res;
}

static esp_err_t cors_handler(httpd_req_t *req) {
  Serial.println("CORS handler called");
  
  // Add CORS headers
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Methods", "GET, POST, OPTIONS, HEAD");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Headers", "Content-Type");
  httpd_resp_set_hdr(req, "Access-Control-Max-Age", "3600");
  
  // Send empty response for OPTIONS request
  httpd_resp_send(req, NULL, 0);
  return ESP_OK;
}

static esp_err_t checkin_handler(httpd_req_t *req) {
  camera_fb_t * fb = NULL;
  esp_err_t res = ESP_OK;
  
  fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }

  String imageData = base64_encode(fb->buf, fb->len);
  esp_camera_fb_return(fb);

  HTTPClient http;
  http.begin(serverUrl + String("/checkin"));
  http.addHeader("Content-Type", "application/json");
  
  String jsonData = "{\"image\":\"" + imageData + "\"}";
  int httpResponseCode = http.POST(jsonData);
  
  String response = http.getString();
  http.end();

  DynamicJsonDocument responseDoc(1024);
  deserializeJson(responseDoc, response);

  if (responseDoc["success"]) {
    String userName = responseDoc["user"]["name"];
    float confidence = responseDoc["user"]["confidence"];
    
    // OLED display (COMMENTED FOR TESTING)
    /*
    display.clearDisplay();
    display.setCursor(0,0);
    display.println("Check-in Success!");
    display.println("Name: " + userName);
    display.print("Confidence: ");
    display.println(confidence);
    display.display();
    */
    
    Serial.println("Check-in Success! Name: " + userName + " Confidence: " + String(confidence));
    
    // TTS (COMMENTED FOR TESTING)
    /*
    String message = "Bạn đã điểm danh thành công với người dùng " + userName;
    playTTS(message);
    */
    
    httpd_resp_send(req, response.c_str(), response.length());
  } else {
    // OLED display (COMMENTED FOR TESTING)
    /*
    display.clearDisplay();
    display.setCursor(0,0);
    display.println("Check-in Failed!");
    display.println("Face not recognized");
    display.display();
    */
    
    Serial.println("Check-in Failed! Face not recognized");
    
    // TTS (COMMENTED FOR TESTING)
    /*
    playTTS("Điểm danh thất bại. Khuôn mặt không được nhận diện.");
    */
    
    httpd_resp_send(req, response.c_str(), response.length());
  }

  return ESP_OK;
}

static esp_err_t register_handler(httpd_req_t *req) {
  String body = "";
  char buf[1024];
  int ret, remaining = req->content_len;
  
  while (remaining > 0) {
    if ((ret = httpd_req_recv(req, buf, (remaining < sizeof(buf)) ? remaining : sizeof(buf))) <= 0) {
      if (ret == HTTPD_SOCK_ERR_TIMEOUT) {
        continue;
      }
      return ESP_FAIL;
    }
    remaining -= ret;
    body += String(buf).substring(0, ret);
  }

  DynamicJsonDocument doc(1024);
  deserializeJson(doc, body);
  
  String name = doc["name"];
  String studentCode = doc["student_code"];

  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }

  String imageData = base64_encode(fb->buf, fb->len);
  esp_camera_fb_return(fb);

  HTTPClient http;
  http.begin(serverUrl + String("/register"));
  http.addHeader("Content-Type", "application/json");
  
  String jsonData = "{\"name\":\"" + name + "\",\"student_code\":\"" + studentCode + "\",\"image\":\"" + imageData + "\"}";
  int httpResponseCode = http.POST(jsonData);
  
  String response = http.getString();
  http.end();

  if (httpResponseCode > 0) {
    DynamicJsonDocument responseDoc(1024);
    deserializeJson(responseDoc, response);
    
    // OLED display (COMMENTED FOR TESTING)
    /*
    display.clearDisplay();
    display.setCursor(0,0);
    display.println("Registration");
    display.println("completed!");
    display.display();
    */
    
    Serial.println("Registration completed! Name: " + name + " Student Code: " + studentCode);
    
    // TTS (COMMENTED FOR TESTING)
    /*
    String message = "Bạn đã đăng ký thành công với tên " + name;
    playTTS(message);
    */
    
    httpd_resp_send(req, response.c_str(), response.length());
  } else {
    // OLED display (COMMENTED FOR TESTING)
    /*
    display.clearDisplay();
    display.setCursor(0,0);
    display.println("Registration");
    display.println("failed!");
    display.display();
    */
    
    Serial.println("Registration failed!");
    
    // TTS (COMMENTED FOR TESTING)
    /*
    playTTS("Đăng ký thất bại. Vui lòng thử lại.");
    */
    
    httpd_resp_send_500(req);
  }

  return ESP_OK;
}

static esp_err_t test_connection_handler(httpd_req_t *req) {
  HTTPClient http;
  http.begin(serverUrl + String("/health"));
  int httpResponseCode = http.GET();
  
  DynamicJsonDocument responseDoc(512);
  responseDoc["connected"] = (httpResponseCode == 200);
  responseDoc["server_url"] = serverUrl;
  responseDoc["response_code"] = httpResponseCode;
  
  String response;
  serializeJson(responseDoc, response);
  http.end();
  
  httpd_resp_set_type(req, "application/json");
  return httpd_resp_send(req, response.c_str(), response.length());
}

static esp_err_t users_handler(httpd_req_t *req) {
  HTTPClient http;
  http.begin(serverUrl + String("/users"));
  int httpResponseCode = http.GET();
  
  String response = http.getString();
  http.end();
  
  httpd_resp_set_type(req, "application/json");
  return httpd_resp_send(req, response.c_str(), response.length());
}

static esp_err_t auto_detection_handler(httpd_req_t *req) {
  String body = "";
  char buf[1024];
  int ret, remaining = req->content_len;
  
  while (remaining > 0) {
    if ((ret = httpd_req_recv(req, buf, (remaining < sizeof(buf)) ? remaining : sizeof(buf))) <= 0) {
      if (ret == HTTPD_SOCK_ERR_TIMEOUT) {
        continue;
      }
      return ESP_FAIL;
    }
    remaining -= ret;
    body += String(buf).substring(0, ret);
  }

  DynamicJsonDocument doc(1024);
  deserializeJson(doc, body);
  
  bool enabled = doc["enabled"];
  autoDetectionEnabled = enabled;
  
  DynamicJsonDocument responseDoc(512);
  responseDoc["success"] = true;
  responseDoc["auto_detection_enabled"] = autoDetectionEnabled;
  responseDoc["message"] = autoDetectionEnabled ? "Auto detection enabled" : "Auto detection disabled";
  
  String response;
  serializeJson(responseDoc, response);
  
  httpd_resp_set_type(req, "application/json");
  return httpd_resp_send(req, response.c_str(), response.length());
}

static esp_err_t status_handler(httpd_req_t *req) {
  DynamicJsonDocument responseDoc(512);
  responseDoc["auto_detection_enabled"] = autoDetectionEnabled;
  responseDoc["face_currently_detected"] = faceCurrentlyDetected;
  responseDoc["wifi_connected"] = (WiFi.status() == WL_CONNECTED);
  responseDoc["wifi_ip"] = WiFi.localIP().toString();
  responseDoc["server_url"] = serverUrl;
  responseDoc["uptime_ms"] = millis();
  
  String response;
  serializeJson(responseDoc, response);
  
  httpd_resp_set_type(req, "application/json");
  return httpd_resp_send(req, response.c_str(), response.length());
}

void startCameraServer(){
  // Start stream server on port 81
  httpd_config_t stream_config = HTTPD_DEFAULT_CONFIG();
  stream_config.server_port = 81;
  stream_config.ctrl_port = 81;
  stream_config.max_open_sockets = 7;
  stream_config.max_resp_headers = 8;
  stream_config.backlog_conn = 5;
  stream_config.lru_purge_enable = true;

  httpd_uri_t stream_uri = {
    .uri       = "/stream",
    .method    = HTTP_GET,
    .handler   = stream_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t snapshot_uri = {
    .uri       = "/snapshot",
    .method    = HTTP_GET,
    .handler   = snapshot_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t stream_options_uri = {
    .uri       = "/stream",
    .method    = HTTP_OPTIONS,
    .handler   = cors_handler,
    .user_ctx  = NULL
  };

  Serial.println("Attempting to start stream server on port 81...");
  esp_err_t stream_err = httpd_start(&stream_httpd, &stream_config);
  if (stream_err == ESP_OK) {
    httpd_register_uri_handler(stream_httpd, &stream_uri);
    httpd_register_uri_handler(stream_httpd, &snapshot_uri);
    httpd_register_uri_handler(stream_httpd, &stream_options_uri);
    Serial.println("✅ Stream server started successfully on port 81");
  } else {
    Serial.printf("❌ Failed to start stream server on port 81. Error: 0x%x\n", stream_err);
    Serial.println("Trying port 82...");
    stream_config.server_port = 82;
    stream_config.ctrl_port = 82;
    stream_err = httpd_start(&stream_httpd, &stream_config);
    if (stream_err == ESP_OK) {
      httpd_register_uri_handler(stream_httpd, &stream_uri);
      Serial.println("✅ Stream server started successfully on port 82");
    } else {
      Serial.printf("❌ Failed to start stream server on port 82. Error: 0x%x\n", stream_err);
    }
  }

  // Start main server on port 80
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 80;

  httpd_uri_t index_uri = {
    .uri       = "/",
    .method    = HTTP_GET,
    .handler   = index_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t checkin_uri = {
    .uri       = "/checkin",
    .method    = HTTP_POST,
    .handler   = checkin_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t register_uri = {
    .uri       = "/register",
    .method    = HTTP_POST,
    .handler   = register_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t test_connection_uri = {
    .uri       = "/test-connection",
    .method    = HTTP_GET,
    .handler   = test_connection_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t users_uri = {
    .uri       = "/users",
    .method    = HTTP_GET,
    .handler   = users_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t auto_detection_uri = {
    .uri       = "/auto-detection",
    .method    = HTTP_POST,
    .handler   = auto_detection_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t status_uri = {
    .uri       = "/status",
    .method    = HTTP_GET,
    .handler   = status_handler,
    .user_ctx  = NULL
  };

  Serial.println("Attempting to start main server on port 80...");
  esp_err_t main_err = httpd_start(&camera_httpd, &config);
  if (main_err == ESP_OK) {
    httpd_register_uri_handler(camera_httpd, &index_uri);
    httpd_register_uri_handler(camera_httpd, &checkin_uri);
    httpd_register_uri_handler(camera_httpd, &register_uri);
    httpd_register_uri_handler(camera_httpd, &test_connection_uri);
    httpd_register_uri_handler(camera_httpd, &users_uri);
    httpd_register_uri_handler(camera_httpd, &auto_detection_uri);
    httpd_register_uri_handler(camera_httpd, &status_uri);
    Serial.println("✅ Main server started successfully on port 80");
  } else {
    Serial.printf("❌ Failed to start main server on port 80. Error: 0x%x\n", main_err);
  }
}

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
  
  Serial.begin(115200);
  Serial.setDebugOutput(false);
  
  // Initialize OLED (COMMENTED FOR TESTING)
  /*
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0,0);
  display.println("Initializing...");
  display.display();
  */

  // Initialize Audio (COMMENTED FOR TESTING)
  /*
  audio.setPinout(I2S_BCLK_PIN, I2S_LRC_PIN, I2S_DOUT_PIN);
  audio.setVolume(10);
  */

  // Initialize buttons (COMMENTED FOR TESTING)
  /*
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(FLASH_PIN, INPUT_PULLUP);
  */

  // Camera configuration from original example
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
  
  if(psramFound()){
    config.frame_size = FRAMESIZE_VGA;  // 640x480 - chất lượng tốt hơn
    config.jpeg_quality = 8;  // Chất lượng cao hơn (1-63, số càng nhỏ càng tốt)
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_QVGA;  // 320x240 - giữ nguyên cho board không có PSRAM
    config.jpeg_quality = 10;  // Chất lượng tốt hơn
    config.fb_count = 1;
  }

  Serial.println("Initializing camera...");
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("❌ Camera init failed with error 0x%x\n", err);
    // OLED display (COMMENTED FOR TESTING)
    /*
    display.clearDisplay();
    display.setCursor(0,0);
    display.println("Camera init failed!");
    display.display();
    */
    return;
  } else {
    Serial.println("✅ Camera initialized successfully");
    
    // Get camera sensor info
    sensor_t * s = esp_camera_sensor_get();
    if (s != NULL) {
      Serial.printf("Camera sensor initialized successfully\n");
      Serial.printf("Camera resolution: %d\n", s->status.framesize);
      Serial.printf("Camera quality: %d\n", s->status.quality);
    }
  }

  // WiFi connection
  WiFi.begin(ssid, password);
  // OLED display (COMMENTED FOR TESTING)
  /*
  display.clearDisplay();
  display.setCursor(0,0);
  display.println("Connecting to WiFi...");
  display.display();
  */
  
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    // display.print(".");
    // display.display();
  }
  
  // OLED display (COMMENTED FOR TESTING)
  /*
  display.clearDisplay();
  display.setCursor(0,0);
  display.println("WiFi connected!");
  display.print("IP: ");
  display.println(WiFi.localIP());
  display.display();
  */
  
  Serial.println("\nWiFi connected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  startCameraServer();
  
  // OLED display (COMMENTED FOR TESTING)
  /*
  display.clearDisplay();
  display.setCursor(0,0);
  display.println("System Ready!");
  display.println("Press button to");
  display.println("check-in");
  display.println("Web: http://" + WiFi.localIP().toString());
  display.display();
  */
  
  Serial.println("System Ready!");
  Serial.println("Web interface: http://" + WiFi.localIP().toString());
  Serial.println("Use web interface to test API");
}

void loop() {
  // Button functionality (COMMENTED FOR TESTING)
  // All interactions now through web interface
  /*
  // Check button press for check-in
  if (digitalRead(BUTTON_PIN) == LOW && millis() - lastButtonPress > debounceDelay) {
    lastButtonPress = millis();
    
  display.clearDisplay();
  display.setCursor(0,0);
    display.println("Taking photo...");
  display.display();
  
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
      Serial.println("Camera capture failed");
      display.clearDisplay();
      display.setCursor(0,0);
      display.println("Camera error!");
      display.display();
    return;
  }
  
    String imageData = base64_encode(fb->buf, fb->len);
    esp_camera_fb_return(fb);

  HTTPClient http;
    http.begin(serverUrl + String("/checkin"));
  http.addHeader("Content-Type", "application/json");
  
    String jsonData = "{\"image\":\"" + imageData + "\"}";
    int httpResponseCode = http.POST(jsonData);
    
    String response = http.getString();
    http.end();

    DynamicJsonDocument responseDoc(1024);
    deserializeJson(responseDoc, response);
    
    if (responseDoc["success"]) {
      String userName = responseDoc["user"]["name"];
      float confidence = responseDoc["user"]["confidence"];
      
      display.clearDisplay();
      display.setCursor(0,0);
      display.println("Check-in Success!");
      display.println("Name: " + userName);
      display.print("Confidence: ");
      display.println(confidence);
      display.display();
      
      String message = "Bạn đã điểm danh thành công với người dùng " + userName;
      playTTS(message);
    } else {
      display.clearDisplay();
      display.setCursor(0,0);
      display.println("Check-in Failed!");
      display.println("Face not recognized");
      display.display();
      
      playTTS("Điểm danh thất bại. Khuôn mặt không được nhận diện.");
    }
  }

  // Check flash button for registration
  if (digitalRead(FLASH_PIN) == LOW && millis() - lastButtonPress > debounceDelay) {
    lastButtonPress = millis();
    
  display.clearDisplay();
  display.setCursor(0,0);
    display.println("Registration mode");
    display.println("Use web interface");
  display.display();
  
    playTTS("Chế độ đăng ký. Vui lòng sử dụng giao diện web.");
  }
  */

  delay(100);
}