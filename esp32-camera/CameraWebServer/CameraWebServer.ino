/*
 * Hệ thống Điểm danh bằng Nhận dạng Khuôn mặt
 * ESP32-CAM Web Interface
 * 
 * Tính năng:
 * - Chụp ảnh khuôn mặt và gửi lên server Python
 * - Web interface để quản lý và đăng ký
 * - Kết nối WiFi và HTTP API
 * - Camera streaming và snapshot
 * 
 * Phần cứng:
 * - ESP32-CAM AI-Thinker
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

// ===================
// WiFi Configuration
// ===================
const char* ssid = "K09";           // Thay đổi SSID WiFi của bạn
const char* password = "nk111111";   // Thay đổi password WiFi của bạn

// ===================
// Server Configuration
// ===================
const char* serverUrl = "http://192.168.216.62:8000"; // Thay đổi IP của máy chủ Python (thay đổi IP này thành IP máy tính của bạn)


// ===================
// Global Variables
// ===================
httpd_handle_t stream_httpd = NULL;
httpd_handle_t camera_httpd = NULL;

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
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4c93 100%);
            background-attachment: fixed;
            color: white;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 25px 0 rgba(31, 38, 135, 0.3);
            border: 1px solid rgba(255,255,255,0.15);
            animation: fadeInUp 0.8s ease-out;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .title {
            font-size: 2.8em;
            margin-bottom: 15px;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
            color: #E6B800;
            font-weight: 600;
        }
        
        .subtitle {
            font-size: 1.3em;
            margin-bottom: 40px;
            opacity: 0.95;
            font-weight: 300;
            letter-spacing: 1px;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            margin-top: 30px;
            align-items: start;
        }
        
        .left-panel {
            display: flex;
            flex-direction: column;
            gap: 25px;
        }
        
        .right-panel {
            display: flex;
            flex-direction: column;
            gap: 25px;
        }
        
        .camera-container {
            position: relative;
            background: rgba(0,0,0,0.6);
            border-radius: 20px;
            padding: 25px;
            min-height: 450px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border: 2px solid rgba(255,255,255,0.08);
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
            transition: all 0.3s ease;
        }
        
        .camera-container:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        }
        
        .camera-stream {
            max-width: 100%;
            max-height: 450px;
            border-radius: 15px;
            box-shadow: 0 8px 25px 0 rgba(0,0,0,0.4);
            display: none;
            transition: all 0.3s ease;
            border: 3px solid rgba(255,255,255,0.2);
        }
        
        .camera-stream:hover {
            transform: scale(1.02);
            box-shadow: 0 12px 35px 0 rgba(0,0,0,0.5);
        }
        
        .captured-image {
            max-width: 100%;
            max-height: 200px;
            border-radius: 15px;
            box-shadow: 0 8px 25px 0 rgba(0,0,0,0.4);
            margin-top: 10px;
            display: none;
            border: 3px solid rgba(255,255,255,0.2);
        }
        
        #capturedImageContainer {
            background: rgba(255,255,255,0.08);
            border-radius: 15px;
            padding: 15px;
            margin: 0;
            border: 1px solid rgba(255,255,255,0.15);
            backdrop-filter: blur(8px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        
        #capturedImageContainer h4 {
            margin: 0 0 10px 0;
            color: #D4AF37;
            font-size: 1.1em;
            text-align: center;
            font-weight: 500;
        }
        
        .status { 
            margin: 0; 
            padding: 20px; 
            background: rgba(255,255,255,0.08);
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.15);
            backdrop-filter: blur(8px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        
        .status h3 {
            margin: 0 0 15px 0;
            color: #D4AF37;
            font-size: 1.2em;
            text-align: center;
            font-weight: 500;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .status-item:last-child {
            border-bottom: none;
        }
        
        .status-label {
            font-weight: 500;
            color: rgba(255,255,255,0.9);
        }
        
        .status-value {
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        
        #result {
            margin: 20px 0;
            padding: 20px;
            background: rgba(0,0,0,0.3);
            border-radius: 15px;
            border: 2px solid rgba(255,255,255,0.1);
            min-height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }
        
        #result.success {
            background: rgba(76, 175, 80, 0.2);
            border-color: rgba(76, 175, 80, 0.5);
            color: #4CAF50;
        }
        
        #result.error {
            background: rgba(244, 67, 54, 0.2);
            border-color: rgba(244, 67, 54, 0.5);
            color: #f44336;
        }
        
        #result.loading {
            background: rgba(33, 150, 243, 0.2);
            border-color: rgba(33, 150, 243, 0.5);
            color: #2196F3;
        }
        
        #result p {
            margin: 0;
            text-align: center;
            font-size: 16px;
            line-height: 1.5;
        }
        
        #result strong {
            font-weight: 700;
            font-size: 18px;
        }
        
        #result small {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .button { 
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            border: none; 
            color: white; 
            padding: 15px 30px; 
            text-align: center; 
            text-decoration: none; 
            display: inline-block; 
            font-size: 16px; 
            font-weight: 600;
            margin: 8px; 
            cursor: pointer; 
            border-radius: 30px;
            transition: all 0.3s ease;
            box-shadow: 0 6px 20px 0 rgba(31, 38, 135, 0.3);
            width: 100%;
            position: relative;
            overflow: hidden;
        }
        
        .button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .button:hover::before {
            left: 100%;
        }
        
        .button:hover { 
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 10px 30px 0 rgba(31, 38, 135, 0.5);
        }
        
        .button:active {
            transform: translateY(0);
        }
        
        .camera-settings {
            background: rgba(255,255,255,0.08);
            border-radius: 15px;
            padding: 20px;
            margin: 0;
            border: 1px solid rgba(255,255,255,0.15);
            backdrop-filter: blur(8px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        
        .camera-settings h3 {
            margin: 0 0 20px 0;
            color: #D4AF37;
            font-size: 1.2em;
            text-align: center;
            font-weight: 500;
        }
        
        .setting-group {
            margin-bottom: 15px;
        }
        
        .setting-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #fff;
        }
        
        .setting-group input[type="range"] {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: rgba(255,255,255,0.2);
            outline: none;
            -webkit-appearance: none;
        }
        
        .setting-group input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            cursor: pointer;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }
        
        .setting-group input[type="range"]::-moz-range-thumb {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            cursor: pointer;
            border: none;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }
        
        .button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
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
        
        .button-group.triple {
            grid-template-columns: 1fr 1fr 1fr;
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
        
        .loading {
            display: inline-block;
            width: 25px;
            height: 25px;
            border: 3px solid rgba(255,255,255,0.3);
            border-top: 3px solid #FFD700;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            max-width: 400px;
            background: rgba(0,0,0,0.9);
            border-radius: 10px;
            padding: 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        }
        
        .notification.show {
            transform: translateX(0);
        }
        
        .notification-content {
            display: flex;
            align-items: center;
            padding: 15px;
            color: white;
        }
        
        .notification-icon {
            font-size: 20px;
            margin-right: 10px;
        }
        
        .notification-message {
            flex: 1;
            font-size: 14px;
            line-height: 1.4;
        }
        
        .notification-close {
            background: none;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
            padding: 0;
            margin-left: 10px;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: background 0.2s;
        }
        
        .notification-close:hover {
            background: rgba(255,255,255,0.2);
        }
        
        .notification-success {
            border-left: 4px solid #4CAF50;
        }
        
        .notification-error {
            border-left: 4px solid #f44336;
        }
        
        .notification-info {
            border-left: 4px solid #2196F3;
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.8);
        }
        
        .modal-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 5% auto;
            padding: 30px;
            border-radius: 15px;
            width: 90%;
            max-width: 500px;
            color: white;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .close {
            color: white;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .close:hover {
            opacity: 0.7;
        }
        
        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .form-group input {
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
        }
        
        .capture-controls {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin: 20px 0;
        }
        
        .capture-btn {
            background: linear-gradient(45deg, #4ECDC4, #45B7D1);
            border: none;
            color: white;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 18px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .capture-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px 0 rgba(31, 38, 135, 0.4);
        }
        
        .capture-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        @media (max-width: 1200px) {
            .container {
                max-width: 95%;
                padding: 20px;
            }
            
            .title {
                font-size: 2.5em;
            }
        }
        
        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
                gap: 25px;
            }
            
            .button-group {
                grid-template-columns: 1fr;
            }
            
            .button-group.triple {
                grid-template-columns: 1fr;
            }
            
            .title {
                font-size: 2em;
            }
            
            .subtitle {
                font-size: 1.1em;
            }
            
            .camera-container {
                min-height: 300px;
                padding: 15px;
            }
            
            .camera-stream {
                max-height: 300px;
            }
            
            .status, .camera-settings, #capturedImageContainer {
                padding: 15px;
            }
            
            .status-item {
                flex-direction: column;
                align-items: flex-start;
                gap: 5px;
            }
            
            .status-value {
                align-self: flex-end;
            }
        }
        
        @media (max-width: 480px) {
            body {
                padding: 10px;
            }
            
            .container {
                padding: 15px;
            }
            
            .title {
                font-size: 1.8em;
            }
            
            .button {
                padding: 12px 20px;
                font-size: 14px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">🎯 Hệ thống Điểm danh Thông minh</h1>
        <p class="subtitle">Face Recognition Attendance System - ESP32-CAM</p>
        
        <div class="status">
            <h3>📊 Trạng thái Hệ thống</h3>
            <div class="status-item">
                <span class="status-label">Trạng thái:</span>
                <span class="status-value" id="status" style="background: rgba(76, 175, 80, 0.3); color: #4CAF50;">Sẵn sàng</span>
            </div>
            <div class="status-item">
                <span class="status-label">Server:</span>
                <span class="status-value" id="server" style="background: rgba(255, 152, 0, 0.3); color: #FF9800;">Chưa kết nối</span>
            </div>
            <div class="status-item">
                <span class="status-label">WiFi:</span>
                <span class="status-value" id="wifi" style="background: rgba(76, 175, 80, 0.3); color: #4CAF50;">Đã kết nối</span>
            </div>
            <div class="status-item">
                <span class="status-label">Camera:</span>
                <span class="status-value" id="camera-status" style="background: rgba(33, 150, 243, 0.3); color: #2196F3;">Đang khởi tạo...</span>
            </div>
        </div>
        
        <div class="dashboard">
            <div class="left-panel">
                <div class="camera-container">
                    <div class="camera-placeholder" id="cameraPlaceholder">
                        📹 Nhấn "Kết nối Server" để bắt đầu
                    </div>
                    <img id="cameraStream" class="camera-stream" alt="Camera Stream">
                </div>
                
                <div class="button-group">
                    <button class="button" onclick="connectServer()">🔗 Kết nối Hệ thống</button>
                    <button class="button" onclick="disconnectServer()">❌ Ngắt kết nối</button>
                </div>
                
                <div class="button-group">
                    <button class="button" onclick="startCheckin()">✅ Điểm danh</button>
                    <button class="button" onclick="startRegister()">👤 Đăng ký mới</button>
                </div>
                
                <div class="button-group single">
                    <button class="button" onclick="getUsers()">👥 Danh sách người dùng</button>
                </div>
            </div>
            
            <div class="right-panel">
                <div id="result"></div>
                
                
                <div class="camera-settings">
                    <h3>⚙️ Cài đặt Camera</h3>
                    <div class="setting-group">
                        <label>Độ sáng: <span id="brightnessValue">0</span></label>
                        <input type="range" id="brightness" min="-2" max="2" value="0" onchange="updateCameraSetting('brightness', this.value)">
                    </div>
                    <div class="setting-group">
                        <label>Độ tương phản: <span id="contrastValue">0</span></label>
                        <input type="range" id="contrast" min="-2" max="2" value="0" onchange="updateCameraSetting('contrast', this.value)">
                    </div>
                    <div class="setting-group">
                        <label>Độ bão hòa: <span id="saturationValue">0</span></label>
                        <input type="range" id="saturation" min="-2" max="2" value="0" onchange="updateCameraSetting('saturation', this.value)">
                    </div>
                    <div class="setting-group">
                        <label>Độ sắc nét: <span id="sharpnessValue">0</span></label>
                        <input type="range" id="sharpness" min="-2" max="2" value="0" onchange="updateCameraSetting('sharpness', this.value)">
                    </div>
                </div>
                
                <div id="capturedImageContainer" style="display: none;">
                    <h4>Ảnh vừa chụp:</h4>
                    <img id="capturedImage" class="captured-image" alt="Captured Image">
                </div>
            </div>
        </div>
    </div>
    
    <!-- Modal cho Đăng ký -->
    <div id="registerModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>👤 Đăng ký người dùng mới</h2>
                <span class="close" onclick="closeRegisterModal()">&times;</span>
            </div>
            <div id="registerCameraContainer">
                <img id="registerCameraStream" class="camera-stream" alt="Register Camera Stream">
                <div class="capture-controls">
                    <button class="capture-btn" onclick="captureForRegister()">📸 Chụp ảnh</button>
                    <button class="capture-btn" onclick="retakePhoto()">🔄 Chụp lại</button>
                </div>
            </div>
            <div id="registerForm" style="display: none;">
                <div class="form-group">
                    <label for="registerName">Họ và tên:</label>
                    <input type="text" id="registerName" placeholder="Nhập họ và tên">
                </div>
                <div class="form-group">
                    <label for="registerStudentCode">Mã sinh viên:</label>
                    <input type="text" id="registerStudentCode" placeholder="Nhập mã sinh viên">
                </div>
                <div class="capture-controls">
                    <button class="capture-btn" onclick="submitRegister()">✅ Đăng ký</button>
                    <button class="capture-btn" onclick="retakePhoto()">🔄 Chụp lại</button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Modal cho Điểm danh -->
    <div id="checkinModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>✅ Điểm danh</h2>
                <span class="close" onclick="closeCheckinModal()">&times;</span>
            </div>
            <div id="checkinCameraContainer">
                <img id="checkinCameraStream" class="camera-stream" alt="Checkin Camera Stream">
                <div class="capture-controls">
                    <button class="capture-btn" onclick="captureForCheckin()">📸 Chụp ảnh</button>
                    <button class="capture-btn" onclick="retakePhoto()">🔄 Chụp lại</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
      // Global variables
      let streamInterval;
      let isStreaming = false;
      let isUpdating = false;
      let capturedImageData = null;
      let currentMode = null; // 'register' or 'checkin'
      
      // ===================
      // Main Dashboard Functions
      // ===================
      
      function connectServer() {
        const resultDiv = document.getElementById('result');
        resultDiv.className = 'loading';
        resultDiv.innerHTML = '<p><span class="loading"></span> Đang kiểm tra kết nối server...</p>';
        
        // Add timeout for connection
        const timeoutPromise = new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Timeout - Server không phản hồi sau 10 giây')), 10000)
        );
        
        const fetchPromise = fetch('/test-connection', {method: 'GET'});
        
        Promise.race([fetchPromise, timeoutPromise])
          .then(response => {
            if (!response.ok) {
              throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
          })
          .then(data => {
            if (data.connected) {
              resultDiv.className = 'success';
              resultDiv.innerHTML = 
                '<p>✅ <strong>Kết nối thành công!</strong><br>' +
                '<small>Server: ' + data.server_url + '</small><br>' +
                '<span class="loading"></span> Camera: Đang khởi động...</p>';
              
              document.getElementById('server').textContent = 'Connected';
              document.getElementById('server').style.color = '#4ECDC4';
              
              // Start camera stream with delay for better UX
              setTimeout(() => {
                startCameraStream();
              }, 1500);
            } else {
              throw new Error(`Server không phản hồi (Mã lỗi: ${data.response_code})`);
            }
          })
          .catch(error => {
            console.error('Connection error:', error);
            resultDiv.className = 'error';
            resultDiv.innerHTML = 
              '<p>❌ <strong>Kết nối thất bại!</strong><br>' +
              '<small>' + error.message + '</small><br>' +
              '<button class="button" onclick="connectServer()" style="margin-top: 10px; width: auto; padding: 8px 16px; font-size: 14px;">🔄 Thử lại</button></p>';
            
            document.getElementById('server').textContent = 'Error';
            document.getElementById('server').style.color = '#FF6B6B';
          });
      }
      
      function disconnectServer() {
        stopCameraStream();
        const resultDiv = document.getElementById('result');
        resultDiv.className = '';
        resultDiv.innerHTML = '<p>🔌 <strong>Đã ngắt kết nối server</strong></p>';
        document.getElementById('server').textContent = 'Disconnected';
        document.getElementById('server').style.color = '#FF6B6B';
      }
      
      function startCameraStream() {
        const cameraStream = document.getElementById('cameraStream');
        const placeholder = document.getElementById('cameraPlaceholder');
        
        if (!cameraStream || !placeholder) {
          console.error('Camera elements not found!');
          return;
        }
        
        cameraStream.style.display = 'block';
        placeholder.style.display = 'none';
        
        const streamUrl = 'http://' + window.location.hostname + ':81/stream';
        const snapshotUrl = 'http://' + window.location.hostname + ':81/snapshot';
        
        // Set crossOrigin to allow canvas operations
        cameraStream.crossOrigin = 'anonymous';
        
        // Try stream first
        cameraStream.src = streamUrl;
        
        cameraStream.onload = function() {
          console.log('Stream loaded successfully');
          document.getElementById('status').textContent = 'Streaming';
          document.getElementById('status').style.color = '#4ECDC4';
          isStreaming = true;
        };
        
        cameraStream.onerror = function() {
          console.log('Stream failed, using snapshot fallback');
          
          // Use snapshot polling as fallback
          function updateSnapshot() {
            if (isStreaming && !isUpdating) {
              isUpdating = true;
              const img = new Image();
              img.crossOrigin = 'anonymous'; // Allow cross-origin access
              img.onload = function() {
                cameraStream.src = img.src;
                isUpdating = false;
              };
              img.onerror = function() {
                console.log('Snapshot request failed, retrying...');
                isUpdating = false;
              };
              img.src = snapshotUrl + '?t=' + new Date().getTime();
            }
          }
          
          updateSnapshot();
          streamInterval = setInterval(updateSnapshot, 800);
          
          document.getElementById('status').textContent = 'Streaming (snapshot)';
          document.getElementById('status').style.color = '#4ECDC4';
          isStreaming = true;
        };
      }
      
      function stopCameraStream() {
        const cameraStream = document.getElementById('cameraStream');
        const placeholder = document.getElementById('cameraPlaceholder');
        
        if (streamInterval) {
          clearInterval(streamInterval);
          streamInterval = null;
        }
        
        if (cameraStream && placeholder) {
          cameraStream.style.display = 'none';
          placeholder.style.display = 'block';
          cameraStream.src = '';
        }
        
        document.getElementById('status').textContent = 'Stopped';
        document.getElementById('status').style.color = '#FF6B6B';
        isStreaming = false;
      }
      
      // ===================
      // Modal Functions
      // ===================
      
      function startRegister() {
        if (!isStreaming) {
          document.getElementById('result').innerHTML = '<p>❌ <strong>Vui lòng kết nối server trước!</strong></p>';
          return;
        }
        
        currentMode = 'register';
        document.getElementById('registerModal').style.display = 'block';
        startModalCameraStream('registerCameraStream');
      }
      
      function startCheckin() {
        if (!isStreaming) {
          document.getElementById('result').innerHTML = '<p>❌ <strong>Vui lòng kết nối server trước!</strong></p>';
          return;
        }
        
        currentMode = 'checkin';
        document.getElementById('checkinModal').style.display = 'block';
        startModalCameraStream('checkinCameraStream');
      }
      
      function startModalCameraStream(streamId) {
        const modalStream = document.getElementById(streamId);
        const streamUrl = 'http://' + window.location.hostname + ':81/stream';
        const snapshotUrl = 'http://' + window.location.hostname + ':81/snapshot';
        
        modalStream.style.display = 'block';
        modalStream.crossOrigin = 'anonymous'; // Allow cross-origin access
        modalStream.src = streamUrl;
        
        modalStream.onerror = function() {
          // Use snapshot fallback for modal
          function updateModalSnapshot() {
            if (modalStream.style.display !== 'none') {
              const img = new Image();
              img.crossOrigin = 'anonymous'; // Allow cross-origin access
              img.onload = function() {
                modalStream.src = img.src;
              };
              img.src = snapshotUrl + '?t=' + new Date().getTime();
            }
          }
          
          updateModalSnapshot();
          setInterval(updateModalSnapshot, 800);
        };
      }
      
      function closeRegisterModal() {
        document.getElementById('registerModal').style.display = 'none';
        document.getElementById('registerForm').style.display = 'none';
        document.getElementById('registerCameraContainer').style.display = 'block';
        capturedImageData = null;
        currentMode = null;
      }
      
      function closeCheckinModal() {
        document.getElementById('checkinModal').style.display = 'none';
        capturedImageData = null;
        currentMode = null;
      }
      
      // ===================
      // Capture Functions
      // ===================
      
      function captureForRegister() {
        const modalStream = document.getElementById('registerCameraStream');
        captureImage(modalStream, function(imageData) {
          capturedImageData = imageData;
          document.getElementById('registerCameraContainer').style.display = 'none';
          document.getElementById('registerForm').style.display = 'block';
        });
      }
      
      function captureForCheckin() {
        const modalStream = document.getElementById('checkinCameraStream');
        captureImage(modalStream, function(imageData) {
          capturedImageData = imageData;
          // Immediately process checkin
          processCheckin(imageData);
        });
      }
      
      function captureImage(streamElement, callback) {
        if (!streamElement || !streamElement.src) {
          alert('Camera stream không sẵn sàng!');
          return;
        }
        
        try {
          // Create canvas to capture current frame
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          
          // Set higher resolution for better face detection
          canvas.width = 640;  // Fixed width for consistency
          canvas.height = 480; // Fixed height for consistency
          
          // Draw image to canvas with better quality
          ctx.drawImage(streamElement, 0, 0, canvas.width, canvas.height);
          
          // Check image quality by analyzing brightness
          const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
          const data = imageData.data;
          let totalBrightness = 0;
          
          // Sample every 10th pixel for performance
          for (let i = 0; i < data.length; i += 40) {
            const r = data[i];
            const g = data[i + 1];
            const b = data[i + 2];
            totalBrightness += (r + g + b) / 3;
          }
          
          const avgBrightness = totalBrightness / (data.length / 40);
          console.log('Image brightness:', avgBrightness);
          
          // Warn if image is too dark or too bright
          if (avgBrightness < 50) {
            alert('⚠️ Ảnh quá tối! Vui lòng chụp lại với ánh sáng tốt hơn.');
            return;
          } else if (avgBrightness > 200) {
            alert('⚠️ Ảnh quá sáng! Vui lòng chụp lại với ánh sáng vừa phải.');
            return;
          }
          
          // Convert to base64 with high quality
          const base64Data = canvas.toDataURL('image/jpeg', 0.9);
          console.log('Image captured successfully, size:', base64Data.length);
          callback(base64Data);
        } catch (error) {
          console.error('Canvas capture error:', error);
          alert('Lỗi khi chụp ảnh: ' + error.message + '\\n\\nVui lòng thử lại hoặc refresh trang.');
        }
      }
      
      function retakePhoto() {
        if (currentMode === 'register') {
          document.getElementById('registerForm').style.display = 'none';
          document.getElementById('registerCameraContainer').style.display = 'block';
        }
        capturedImageData = null;
      }
      
      // ===================
      // Submit Functions
      // ===================
      
      function submitRegister() {
        const name = document.getElementById('registerName').value.trim();
        const studentCode = document.getElementById('registerStudentCode').value.trim();
        
        if (!name || !studentCode) {
          alert('Vui lòng nhập đầy đủ thông tin!');
          return;
        }
        
        if (!capturedImageData) {
          alert('Vui lòng chụp ảnh trước!');
          return;
        }
        
        const resultDiv = document.getElementById('result');
        resultDiv.className = 'loading';
        resultDiv.innerHTML = '<p><span class="loading"></span> Đang đăng ký...</p>';
        
        // Send to ESP32 register endpoint (which will forward to Python server)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 35000); // 35 second timeout
        
        fetch('/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: name,
            student_code: studentCode,
            image: capturedImageData
          }),
          signal: controller.signal
        })
        .then(response => {
          clearTimeout(timeoutId);
          console.log('Response status:', response.status);
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }
          return response.json();
        })
        .then(data => {
          console.log('Register response:', data);
          const resultDiv = document.getElementById('result');
          if (data.success) {
            resultDiv.className = 'success';
            resultDiv.innerHTML = 
              '<p>✅ <strong>Đăng ký thành công!</strong><br>' +
              '<small>Tên: ' + data.user.name + '<br>' +
              'Mã SV: ' + data.user.student_code + '<br>' +
              'ID: ' + data.user.user_id + '</small></p>';
            
            // Show captured image
            showCapturedImage(capturedImageData);
            closeRegisterModal();
          } else {
            resultDiv.className = 'error';
            resultDiv.innerHTML = 
              '<p>❌ <strong>Đăng ký thất bại:</strong><br><small>' + data.message + '</small></p>';
          }
        })
        .catch(error => {
          console.error('Register error:', error);
          let errorMessage = 'Lỗi không xác định';
          
          if (error.message.includes('Failed to fetch')) {
            errorMessage = 'Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng và thử lại.';
          } else if (error.message.includes('timeout')) {
            errorMessage = 'Request timeout. Server đang xử lý quá lâu, vui lòng thử lại.';
          } else if (error.message.includes('HTTP 500')) {
            errorMessage = 'Lỗi server. Vui lòng thử lại sau.';
          } else if (error.message.includes('HTTP 400')) {
            errorMessage = 'Dữ liệu không hợp lệ. Vui lòng kiểm tra thông tin và thử lại.';
          } else {
            errorMessage = error.message;
          }
          
          const resultDiv = document.getElementById('result');
          resultDiv.className = 'error';
          resultDiv.innerHTML = 
            '<p>❌ <strong>Lỗi đăng ký:</strong><br>' +
            '<small>' + errorMessage + '</small><br>' +
            '<button class="button" onclick="startRegister()" style="margin-top: 10px; width: auto; padding: 8px 16px; font-size: 14px;">🔄 Thử lại</button></p>';
        });
      }
      
      function processCheckin(imageData) {
        const resultDiv = document.getElementById('result');
        resultDiv.className = 'loading';
        resultDiv.innerHTML = '<p><span class="loading"></span> Đang xử lý điểm danh...</p>';
        
        // Send to ESP32 checkin endpoint (which will forward to Python server)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 35000); // 35 second timeout
        
        fetch('/checkin', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            image: imageData
          }),
          signal: controller.signal
        })
        .then(response => {
          clearTimeout(timeoutId);
          console.log('Response status:', response.status);
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }
          return response.json();
        })
        .then(data => {
          console.log('Checkin response:', data);
          const resultDiv = document.getElementById('result');
          if (data.success) {
            resultDiv.className = 'success';
            resultDiv.innerHTML = 
              '<p>✅ <strong>Điểm danh thành công!</strong><br>' +
              '<small>Tên: ' + data.user.name + '<br>' +
              'Mã sinh viên: ' + data.user.student_code + '<br>' +
              'Độ tin cậy: ' + (data.confidence * 100).toFixed(1) + '%<br>' +
              'Thời gian: ' + new Date().toLocaleString() + '</small></p>';
            
            // Show captured image
            showCapturedImage(imageData);
            closeCheckinModal();
          } else {
            resultDiv.className = 'error';
            resultDiv.innerHTML = 
              '<p>❌ <strong>Điểm danh thất bại!</strong><br><small>' + data.message + '</small></p>';
          }
        })
        .catch(error => {
          console.error('Checkin error:', error);
          let errorMessage = 'Lỗi không xác định';
          
          if (error.message.includes('Failed to fetch')) {
            errorMessage = 'Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng và thử lại.';
          } else if (error.message.includes('timeout')) {
            errorMessage = 'Request timeout. Server đang xử lý quá lâu, vui lòng thử lại.';
          } else if (error.message.includes('HTTP 500')) {
            errorMessage = 'Lỗi server. Vui lòng thử lại sau.';
          } else if (error.message.includes('HTTP 400')) {
            errorMessage = 'Dữ liệu không hợp lệ. Vui lòng chụp ảnh rõ nét hơn.';
          } else {
            errorMessage = error.message;
          }
          
          const resultDiv = document.getElementById('result');
          resultDiv.className = 'error';
          resultDiv.innerHTML = 
            '<p>❌ <strong>Lỗi điểm danh:</strong><br>' +
            '<small>' + errorMessage + '</small><br>' +
            '<button class="button" onclick="startCheckin()" style="margin-top: 10px; width: auto; padding: 8px 16px; font-size: 14px;">🔄 Thử lại</button></p>';
        });
      }
      
      // ===================
      // Utility Functions
      // ===================
      
      function showCapturedImage(imageData) {
        const container = document.getElementById('capturedImageContainer');
        const img = document.getElementById('capturedImage');
        
        img.src = imageData;
        container.style.display = 'block';
        
        // Auto hide after 10 seconds
        setTimeout(() => {
          container.style.display = 'none';
        }, 10000);
      }
      
      function updateCameraSetting(setting, value) {
        // Update the display value
        document.getElementById(setting + 'Value').textContent = value;
        
        // Send setting to ESP32
        fetch('/camera-setting', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            setting: setting,
            value: parseInt(value)
          })
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            console.log(`Camera ${setting} updated to ${value}`);
            showNotification(`Cài đặt ${setting} đã được cập nhật thành công!`, 'success');
          } else {
            console.error('Failed to update camera setting:', data.error);
            showNotification(`Lỗi cập nhật ${setting}: ${data.error}`, 'error');
          }
        })
        .catch(error => {
          console.error('Error updating camera setting:', error);
          showNotification(`Lỗi kết nối khi cập nhật ${setting}`, 'error');
        });
      }
      
      function showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
          <div class="notification-content">
            <span class="notification-icon">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
          </div>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
          if (notification.parentElement) {
            notification.remove();
          }
        }, 5000);
        
        // Add animation
        setTimeout(() => {
          notification.classList.add('show');
        }, 100);
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
        document.getElementById('result').innerHTML = '<p><span class="loading"></span> Đang test camera...</p>';
        const snapshotUrl = 'http://' + window.location.hostname + ':81/snapshot';
        
        fetch(snapshotUrl, {method: 'GET'})
          .then(response => {
            if (response.ok) {
              document.getElementById('result').innerHTML = 
                '<p>✅ <strong>Camera hoạt động!</strong><br>' +
                'Status: ' + response.status + '<br>' +
                'Content-Type: ' + response.headers.get('content-type') + '</p>';
            } else {
              document.getElementById('result').innerHTML = 
                '<p>❌ <strong>Camera lỗi!</strong><br>' +
                'Status: ' + response.status + '</p>';
            }
          })
          .catch(error => {
            document.getElementById('result').innerHTML = 
              '<p>❌ <strong>Camera không kết nối được!</strong><br>' +
              'Lỗi: ' + error + '</p>';
          });
      }
      
      function getUsers() {
        const resultDiv = document.getElementById('result');
        resultDiv.className = 'loading';
        resultDiv.innerHTML = '<p><span class="loading"></span> Đang tải danh sách người dùng...</p>';
        
        fetch('/users', {method: 'GET'})
          .then(response => {
            if (!response.ok) {
              throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
          })
          .then(data => {
            console.log('Users response:', data);
            resultDiv.className = 'success';
            
            if (data && data.length > 0) {
              let usersHtml = '<p>👥 <strong>Danh sách người dùng:</strong><br>';
              data.forEach(user => {
                usersHtml += '<small>• ' + user.name + ' (' + user.student_code + ')<br></small>';
              });
              usersHtml += '<br><small>Tổng cộng: ' + data.length + ' người dùng</small></p>';
              resultDiv.innerHTML = usersHtml;
            } else {
              resultDiv.innerHTML = '<p>👥 <strong>Danh sách người dùng:</strong><br><small>Chưa có người dùng nào được đăng ký</small></p>';
            }
          })
          .catch(error => {
            console.error('Users error:', error);
            resultDiv.className = 'error';
            resultDiv.innerHTML = 
              '<p>❌ <strong>Lỗi tải danh sách:</strong><br><small>' + error.message + '</small></p>';
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
      
      // Close modals when clicking outside
      window.onclick = function(event) {
        const registerModal = document.getElementById('registerModal');
        const checkinModal = document.getElementById('checkinModal');
        
        if (event.target === registerModal) {
          closeRegisterModal();
        }
        if (event.target === checkinModal) {
          closeCheckinModal();
        }
      }
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

  // Add CORS headers to allow cross-origin access
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Methods", "GET, POST, OPTIONS, HEAD");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Headers", "Content-Type");
  httpd_resp_set_hdr(req, "Access-Control-Max-Age", "3600");
  httpd_resp_set_hdr(req, "Cross-Origin-Embedder-Policy", "unsafe-none");
  httpd_resp_set_hdr(req, "Cross-Origin-Opener-Policy", "unsafe-none");
  httpd_resp_set_hdr(req, "Cross-Origin-Resource-Policy", "cross-origin");

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
  
  // Add CORS headers to allow cross-origin access
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Methods", "GET, POST, OPTIONS, HEAD");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Headers", "Content-Type");
  httpd_resp_set_hdr(req, "Access-Control-Max-Age", "3600");
  httpd_resp_set_hdr(req, "Cross-Origin-Embedder-Policy", "unsafe-none");
  httpd_resp_set_hdr(req, "Cross-Origin-Opener-Policy", "unsafe-none");
  httpd_resp_set_hdr(req, "Cross-Origin-Resource-Policy", "cross-origin");
  
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

  HTTPClient http;
  http.begin(serverUrl + String("/api/v1/checkin"));
  http.setTimeout(30000); // 30 second timeout
  http.setConnectTimeout(10000); // 10 second connection timeout
  
  // Create proper multipart form data
  String boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW";
  String formData = "--" + boundary + "\r\n";
  formData += "Content-Disposition: form-data; name=\"file\"; filename=\"checkin.jpg\"\r\n";
  formData += "Content-Type: image/jpeg\r\n\r\n";
  
  // Convert to bytes for multipart
  String binaryData = "";
  for (int i = 0; i < fb->len; i++) {
    binaryData += (char)fb->buf[i];
  }
  
  formData += binaryData;
  formData += "\r\n--" + boundary + "--\r\n";
  
  http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
  int httpResponseCode = http.POST(formData);
  
  esp_camera_fb_return(fb);
  
  String response = "";
  if (httpResponseCode > 0) {
    response = http.getString();
  } else {
    response = "{\"success\":false,\"error\":\"Connection failed: " + String(httpResponseCode) + "\"}";
  }
  http.end();

  DynamicJsonDocument responseDoc(1024);
  deserializeJson(responseDoc, response);

  if (responseDoc["success"]) {
    String userName = responseDoc["user"]["name"];
    float confidence = responseDoc["user"]["confidence"];
    
    Serial.println("Check-in Success! Name: " + userName + " Confidence: " + String(confidence));
    
    httpd_resp_send(req, response.c_str(), response.length());
  } else {
    Serial.println("Check-in Failed! Face not recognized");
    
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

  HTTPClient http;
  http.begin(serverUrl + String("/api/v1/register"));
  http.setTimeout(30000); // 30 second timeout
  http.setConnectTimeout(10000); // 10 second connection timeout
  
  // Create proper multipart form data
  String boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW";
  String formData = "--" + boundary + "\r\n";
  formData += "Content-Disposition: form-data; name=\"file\"; filename=\"register.jpg\"\r\n";
  formData += "Content-Type: image/jpeg\r\n\r\n";
  
  // Convert to bytes for multipart
  String binaryData = "";
  for (int i = 0; i < fb->len; i++) {
    binaryData += (char)fb->buf[i];
  }
  
  formData += binaryData;
  formData += "\r\n--" + boundary + "\r\n";
  formData += "Content-Disposition: form-data; name=\"name\"\r\n\r\n";
  formData += name;
  formData += "\r\n--" + boundary + "\r\n";
  formData += "Content-Disposition: form-data; name=\"student_code\"\r\n\r\n";
  formData += studentCode;
  formData += "\r\n--" + boundary + "--\r\n";
  
  http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
  int httpResponseCode = http.POST(formData);
  
  esp_camera_fb_return(fb);
  
  String response = "";
  if (httpResponseCode > 0) {
    response = http.getString();
  } else {
    response = "{\"success\":false,\"error\":\"Connection failed: " + String(httpResponseCode) + "\"}";
  }
  http.end();

  if (httpResponseCode > 0) {
    DynamicJsonDocument responseDoc(1024);
    deserializeJson(responseDoc, response);
    
    Serial.println("Registration completed! Name: " + name + " Student Code: " + studentCode);
    
    httpd_resp_send(req, response.c_str(), response.length());
  } else {
    Serial.println("Registration failed!");
    
    httpd_resp_send_500(req);
  }

  return ESP_OK;
}

static esp_err_t test_connection_handler(httpd_req_t *req) {
  HTTPClient http;
  http.begin(serverUrl + String("/api/v1/health"));
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
  http.begin(serverUrl + String("/api/v1/users"));
  http.setTimeout(10000); // 10 second timeout
  http.setConnectTimeout(5000); // 5 second connection timeout
  
  int httpResponseCode = http.GET();
  
  String response = "";
  if (httpResponseCode > 0) {
    response = http.getString();
  } else {
    response = "[]"; // Return empty array on error
  }
  http.end();
  
  httpd_resp_set_type(req, "application/json");
  return httpd_resp_send(req, response.c_str(), response.length());
}


static esp_err_t status_handler(httpd_req_t *req) {
  DynamicJsonDocument responseDoc(512);
  responseDoc["wifi_connected"] = (WiFi.status() == WL_CONNECTED);
  responseDoc["wifi_ip"] = WiFi.localIP().toString();
  responseDoc["server_url"] = serverUrl;
  responseDoc["uptime_ms"] = millis();
  
  String response;
  serializeJson(responseDoc, response);
  
  httpd_resp_set_type(req, "application/json");
  return httpd_resp_send(req, response.c_str(), response.length());
}

static esp_err_t camera_setting_handler(httpd_req_t *req) {
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
  
  String setting = doc["setting"];
  int value = doc["value"];
  
  sensor_t * s = esp_camera_sensor_get();
  if (s != NULL) {
    bool success = false;
    
    if (setting == "brightness") {
      s->set_brightness(s, value);
      success = true;
    } else if (setting == "contrast") {
      s->set_contrast(s, value);
      success = true;
    } else if (setting == "saturation") {
      s->set_saturation(s, value);
      success = true;
    } else if (setting == "sharpness") {
      s->set_sharpness(s, value);
      success = true;
    }
    
    DynamicJsonDocument responseDoc(512);
    responseDoc["success"] = success;
    responseDoc["setting"] = setting;
    responseDoc["value"] = value;
    responseDoc["message"] = success ? "Setting updated successfully" : "Invalid setting";
    
    String response;
    serializeJson(responseDoc, response);
    
    httpd_resp_set_type(req, "application/json");
    return httpd_resp_send(req, response.c_str(), response.length());
  }
  
  DynamicJsonDocument errorDoc(256);
  errorDoc["success"] = false;
  errorDoc["error"] = "Camera sensor not available";
  
  String errorResponse;
  serializeJson(errorDoc, errorResponse);
  
  httpd_resp_set_type(req, "application/json");
  return httpd_resp_send(req, errorResponse.c_str(), errorResponse.length());
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


  httpd_uri_t status_uri = {
    .uri       = "/status",
    .method    = HTTP_GET,
    .handler   = status_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t camera_setting_uri = {
    .uri       = "/camera-setting",
    .method    = HTTP_POST,
    .handler   = camera_setting_handler,
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
    httpd_register_uri_handler(camera_httpd, &status_uri);
    httpd_register_uri_handler(camera_httpd, &camera_setting_uri);
    Serial.println("✅ Main server started successfully on port 80");
  } else {
    Serial.printf("❌ Failed to start main server on port 80. Error: 0x%x\n", main_err);
  }
}

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
  
  Serial.begin(115200);
  Serial.setDebugOutput(false);
  

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
    config.frame_size = FRAMESIZE_SVGA;  // 800x600 - chất lượng cao hơn
    config.jpeg_quality = 6;  // Chất lượng rất cao (1-63, số càng nhỏ càng tốt)
    config.fb_count = 3;  // Tăng buffer để tránh lag
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;  // Tối ưu performance
  } else {
    config.frame_size = FRAMESIZE_VGA;  // 640x480 - tăng từ QVGA
    config.jpeg_quality = 8;  // Chất lượng cao hơn
    config.fb_count = 2;  // Tăng buffer
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  }

  Serial.println("Initializing camera...");
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("❌ Camera init failed with error 0x%x\n", err);
    return;
  } else {
    Serial.println("✅ Camera initialized successfully");
    
    // Get camera sensor info and optimize settings
    sensor_t * s = esp_camera_sensor_get();
    if (s != NULL) {
      Serial.printf("Camera sensor initialized successfully\n");
      Serial.printf("Camera resolution: %d\n", s->status.framesize);
      Serial.printf("Camera quality: %d\n", s->status.quality);
      
      // Optimize camera settings for better quality
      s->set_brightness(s, 0);     // Brightness: -2 to 2
      s->set_contrast(s, 0);       // Contrast: -2 to 2  
      s->set_saturation(s, 0);     // Saturation: -2 to 2
      s->set_sharpness(s, 0);      // Sharpness: -2 to 2
      s->set_denoise(s, 0);        // Denoise: 0 to 1
      s->set_gainceiling(s, (gainceiling_t)0);  // Gain ceiling: 2x to 128x
      s->set_colorbar(s, 0);       // Color bar: 0 to 1
      s->set_whitebal(s, 1);       // White balance: 0 to 1
      s->set_gain_ctrl(s, 1);      // Gain control: 0 to 1
      s->set_exposure_ctrl(s, 1);  // Exposure control: 0 to 1
      s->set_hmirror(s, 0);        // Horizontal mirror: 0 to 1
      s->set_vflip(s, 0);          // Vertical flip: 0 to 1
      s->set_aec2(s, 0);           // AEC2: 0 to 1
      s->set_awb_gain(s, 1);       // AWB gain: 0 to 1
      s->set_agc_gain(s, 0);       // AGC gain: 0 to 30
      s->set_aec_value(s, 300);    // AEC value: 0 to 1200
      
      Serial.println("✅ Camera settings optimized for high quality");
    }
  }

  // WiFi connection
  WiFi.begin(ssid, password);
  
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi connected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  startCameraServer();
  
  Serial.println("System Ready!");
  Serial.println("Web interface: http://" + WiFi.localIP().toString());
  Serial.println("Use web interface to test API");
}

void loop() {
  // All interactions through web interface
  delay(100);
}