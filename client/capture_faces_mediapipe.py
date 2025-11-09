"""
ESP32-CAM Face Capture Tool - MediaPipe Edition
Synchronized with ESP32 XGA_FLUSH_v7.1 firmware
Uses Google MediaPipe for accurate face detection
Detect faces → Check Quality → Auto-Capture 20 best shots → Preprocess → Save
"""

import cv2
import mediapipe as mp
import numpy as np
import requests
import sys
import time
import os
from threading import Thread
from datetime import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION - Synchronized with ESP32 v7.1
# ==========================================
ESP32_CAM_IP = "192.168.243.176" # IP đã cập nhật
STREAM_URL = f"http://{ESP32_CAM_IP}/stream"

# Dataset configuration
DATASET_ROOT = Path(r"d:\HUTECH\DACN\dataset")
DATASET_PROCESSED = DATASET_ROOT / "processed"

# MediaPipe Face Detection configuration
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Detection settings
MIN_DETECTION_CONFIDENCE = 0.6  # Confidence threshold (0-1)
MODEL_SELECTION = 1  # 0 = short range (<2m), 1 = full range (>2m)

# Preprocessing configuration
# 💡 v5: Giữ nguyên BBox gốc (KHÔNG margin)
FACE_OUTPUT_SIZE = (112, 112)
FACE_MARGIN_SAVE = 0.0  # Margin 0% - Giữ nguyên 100% BBox gốc
MIN_QUALITY_SCORE = 65  # Minimum quality score

# Capture settings
CAPTURE_COOLDOWN = 0.5  # Seconds between auto captures
MAX_CAPTURES_PER_SESSION = 20


class FaceQualityChecker:
    # ... (Không thay đổi class này) ...
    """Check face image quality for dataset - IMPROVED VERSION"""
    
    @staticmethod
    def check_brightness(face_img):
        """Check if face is well-lit (0-100 score)"""
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray)
        
        # Optimal brightness: 100-150 (điểm tối đa)
        if avg_brightness < 80:
            score = (avg_brightness / 80) * 70
        elif avg_brightness > 180:
            score = max(50, 100 - (avg_brightness - 180))
        else:
            score = 100
        return score, avg_brightness
    
    @staticmethod
    def check_sharpness(face_img):
        """Check if face is sharp/focused (0-100 score)"""
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        if laplacian_var < 100:
            score = (laplacian_var / 100) * 50
        elif laplacian_var > 500:
            score = 100
        else:
            score = 50 + ((laplacian_var - 100) / 400) * 50
        return min(100, score), laplacian_var
    
    @staticmethod
    def check_size(face_w, face_h):
        """Check if face size is appropriate (0-100 score)"""
        size = min(face_w, face_h)
        if size < 100:
            score = (size / 100) * 60
        elif size > 400:
            score = max(70, 100 - (size - 400) / 20)
        else:
            score = 100
        return min(100, max(0, score))
    
    @staticmethod
    def check_contrast(face_img):
        """Check contrast quality (0-100 score) - NEW"""
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        std_dev = np.std(gray)
        if std_dev < 30:
            score = (std_dev / 30) * 60
        elif std_dev > 90:
            score = max(70, 100 - (std_dev - 90) / 2)
        else:
            score = 100
        return score, std_dev
    
    @staticmethod
    def calculate_overall_quality(face_img, face_w, face_h):
        """Calculate overall quality score (0-100) - IMPROVED"""
        brightness_score, brightness_val = FaceQualityChecker.check_brightness(face_img)
        sharpness_score, sharpness_val = FaceQualityChecker.check_sharpness(face_img)
        size_score = FaceQualityChecker.check_size(face_w, face_h)
        contrast_score, contrast_val = FaceQualityChecker.check_contrast(face_img)
        
        overall = (
            brightness_score * 0.25 +
            sharpness_score * 0.40 +
            size_score * 0.20 +
            contrast_score * 0.15
        )
        
        return {
            'overall': overall,
            'brightness': brightness_score,
            'brightness_val': brightness_val,
            'sharpness': sharpness_score,
            'sharpness_val': sharpness_val,
            'size': size_score,
            'contrast': contrast_score,
            'contrast_val': contrast_val
        }


class ESP32FaceCapturer:
    # ... (Không thay đổi class này) ...
    def __init__(self, stream_url):
        self.stream_url = stream_url
        self.frame = None
        self.stopped = False
        self.connected = False
        self.capture_count = 0
        self.last_capture_time = 0
        
    def start(self):
        Thread(target=self.update, daemon=True).start()
        return self
        
    def update(self):
        try:
            print(f"🔄 Connecting to {self.stream_url}...")
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'ESP32-Face-Capture-MediaPipe-v1',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            })
            response = session.get(self.stream_url, stream=True, timeout=15)
            if response.status_code != 200:
                print(f"❌ HTTP Error: {response.status_code}")
                self.stopped = True
                return
            print("✅ Connected successfully!")
            self.connected = True
            bytes_data = bytes()
            frame_count = 0
            last_fps_time = time.time()
            for chunk in response.iter_content(chunk_size=10240):
                if self.stopped:
                    break
                bytes_data += chunk
                if len(bytes_data) > 50000:
                    last_start = bytes_data.rfind(b'\xff\xd8')
                    if last_start > 0:
                        bytes_data = bytes_data[last_start:]
                a = bytes_data.find(b'\xff\xd8')
                b = bytes_data.find(b'\xff\xd9')
                if a != -1 and b != -1:
                    jpg = bytes_data[a:b+2]
                    bytes_data = bytes_data[b+2:]
                    try:
                        frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                        if frame is not None:
                            self.frame = frame
                            frame_count += 1
                            current_time = time.time()
                            if current_time - last_fps_time >= 5.0:
                                fps = frame_count / (current_time - last_fps_time)
                                print(f"📊 Stream FPS: {fps:.1f} | Frames: {frame_count}")
                                frame_count = 0
                                last_fps_time = current_time
                    except:
                        continue
        except Exception as e:
            print(f"\n❌ Stream error: {e}")
        finally:
            self.stopped = True
            self.connected = False
            
    def read(self):
        return self.frame
        
    def stop(self):
        self.stopped = True


# ==========================================
# HÀM CẮT MẶT (v5.2 - BBox Gốc THU NHỎ thành VUÔNG)
# ==========================================
def get_aligned_square_crop(frame, detection, margin_percent=0.0):
    """
    Cắt ảnh VUÔNG dựa trên BBox gốc từ MediaPipe.
    
    v5.2: BBox Gốc → THU NHỎ thành VUÔNG
    - Lấy BBox gốc từ MediaPipe
    - Tìm cạnh NGẮN NHẤT (width hoặc height)
    - Thu nhỏ cạnh dài hơn để tạo KHUNG VUÔNG
    - Giữ nguyên tâm BBox gốc
    - KHÔNG thêm margin (hoặc thêm tùy chọn)
    
    Returns:
        (face_crop, bbox): Ảnh vuông đã crop và bounding box (x, y, w, h)
    """
    try:
        h, w = frame.shape[:2]
        
        # LẤY BOUNDING BOX GỐC TỪ MEDIAPIPE
        bbox = detection.location_data.relative_bounding_box
        
        # Chuyển đổi từ tọa độ tương đối (0-1) sang pixel
        x = int(bbox.xmin * w)
        y = int(bbox.ymin * h)
        box_w = int(bbox.width * w)
        box_h = int(bbox.height * h)
        
        # TÌM TÂM CỦA BBOX GỐC
        cx = x + box_w / 2
        cy = y + box_h / 2
        
        # TÌM CẠNH NGẮN NHẤT (để thu nhỏ thành vuông)
        square_size = min(box_w, box_h)
        
        # THÊM MARGIN NẾU CẦN (mặc định 0%)
        if margin_percent > 0:
            margin = int(square_size * margin_percent)
            square_size = square_size + 2 * margin
        
        # TÍNH TỌA ĐỘ KHUNG VUÔNG (tâm tại cx, cy)
        x1 = int(cx - square_size / 2)
        y1 = int(cy - square_size / 2)
        x2 = int(cx + square_size / 2)
        y2 = int(cy + square_size / 2)
        
        # ĐẢM BẢO KHÔNG VƯỢT BIÊN
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)
        
        # CẮT ẢNH
        face_crop = frame[y1:y2, x1:x2]
        
        return face_crop, (x1, y1, x2 - x1, y2 - y1)
        
    except Exception as e:
        print(f"⚠️  Lỗi khi cắt mặt: {e}")
        return frame, (0, 0, frame.shape[1], frame.shape[0])


# ==========================================
# 💡 HÀM TIỀN XỬ LÝ v5.2 (CLAHE - Adaptive)
# ==========================================
def preprocess_face(face_img):
    """
    Tiền xử lý v5.2 với CLAHE: Đơn giản hóa (ảnh đã VUÔNG từ crop)
    
    Steps:
    1. Resize 112x112 (không méo vì ảnh đã vuông)
    2. Grayscale
    3. CLAHE (Contrast Limited Adaptive Histogram Equalization)
       - Cân bằng histogram theo vùng cục bộ (8x8 tiles)
       - Giữ chi tiết tốt hơn so với HistEq toàn cục
    """
    if face_img.size == 0:
        return None
    
    try:
        # STEP 1: Resize 112x112
        face_resized = cv2.resize(
            face_img, 
            FACE_OUTPUT_SIZE, 
            interpolation=cv2.INTER_LANCZOS4
        )
        
        # STEP 2: Convert to GRAYSCALE
        face_gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
        
        # STEP 3: CLAHE (Adaptive Histogram Equalization)
        # clipLimit: Ngưỡng giới hạn tương phản (2.0 = vừa phải)
        # tileGridSize: Kích thước mỗi vùng cục bộ (8x8 pixels)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        face_gray_enhanced = clahe.apply(face_gray)
        
        return face_gray_enhanced
        
    except Exception as e:
        print(f"⚠️  Lỗi preprocess: {e}")
        return None


def save_face_capture(face_img, person_name, quality_info):
    """Save face to dataset - ONLY FINAL GRAYSCALE VERSION"""
    person_gray = DATASET_PROCESSED / person_name
    person_gray.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    quality_str = f"q{int(quality_info['overall'])}"
    filename = f"{person_name}_{timestamp}_{quality_str}.jpg"
    
    # 💡 Sử dụng hàm preprocess_face mới
    face_gray = preprocess_face(face_img)
    gray_path = None
    
    if face_gray is not None:
        gray_path = person_gray / filename
        cv2.imwrite(str(gray_path), face_gray, [cv2.IMWRITE_JPEG_QUALITY, 100])
    
    # File .txt đã bị xóa
    
    return gray_path


def draw_ui(frame, detections, face_detector, selected_face_idx, person_name, capture_count, auto_capture, show_help):
    """Draw UI overlay on frame with MediaPipe detections"""
    h, w = frame.shape[:2]
    
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 80), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    
    cv2.putText(frame, "ESP32-CAM Face Capture (MediaPipe)", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(frame, f"Person: {person_name} | Captured: {capture_count}/{MAX_CAPTURES_PER_SESSION}", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Draw faces
    if detections:
        for idx, detection in enumerate(detections):
            
            # SỬ DỤNG HÀM MỚI (CHỈ 1 LẦN)
            face_crop, (fx, fy, fw, fh) = get_aligned_square_crop(frame, detection, FACE_MARGIN_SAVE)
            
            if face_crop.size == 0:
                continue
            
            # Calculate quality
            quality = FaceQualityChecker.calculate_overall_quality(face_crop, fw, fh)
            confidence = detection.score[0]
            
            # Color based on quality
            if quality['overall'] >= MIN_QUALITY_SCORE:
                color = (0, 255, 0)  # Green
                status = "GOOD"
            elif quality['overall'] >= 40:
                color = (0, 255, 255)  # Yellow
                status = "OK"
            else:
                color = (0, 0, 255)  # Red
                status = "POOR"
            
            thickness = 3 if idx == selected_face_idx else 2
            
            # Draw bounding box
            cv2.rectangle(frame, (fx, fy), (fx + fw, fy + fh), color, thickness)
            
            # Draw quality info
            info_y = fy - 10 if fy > 60 else fy + fh + 20
            cv2.putText(frame, f"Face {idx+1}: {status} Q={quality['overall']:.0f} C={confidence:.2f}", 
                        (fx, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Draw quality bars
            bar_width = fw
            bar_height = 5
            bar_y = fy - 35 if fy > 85 else fy + fh + 35
            
            # Brightness bar (Yellow)
            bright_w = int((quality['brightness'] / 100) * bar_width)
            cv2.rectangle(frame, (fx, bar_y), (fx + bar_width, bar_y + bar_height), (50, 50, 50), -1)
            cv2.rectangle(frame, (fx, bar_y), (fx + bright_w, bar_y + bar_height), (0, 255, 255), -1)
            
            # Sharpness bar (Magenta)
            sharp_y = bar_y + bar_height + 2
            sharp_w = int((quality['sharpness'] / 100) * bar_width)
            cv2.rectangle(frame, (fx, sharp_y), (fx + bar_width, sharp_y + bar_height), (50, 50, 50), -1)
            cv2.rectangle(frame, (fx, sharp_y), (fx + sharp_w, sharp_y + bar_height), (255, 0, 255), -1)
            
            # Contrast bar (Cyan)
            contrast_y = sharp_y + bar_height + 2
            contrast_w = int((quality['contrast'] / 100) * bar_width)
            cv2.rectangle(frame, (fx, contrast_y), (fx + bar_width, contrast_y + bar_height), (50, 50, 50), -1)
            cv2.rectangle(frame, (fx, contrast_y), (fx + contrast_w, contrast_y + bar_height), (255, 255, 0), -1)
    
    # ... (Phần còn lại của draw_ui không đổi) ...
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, h-60), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    if auto_capture:
        cv2.putText(frame, f"🔴 AUTO CAPTURE ON (Saving best face >= Q{MIN_QUALITY_SCORE})", (10, h-35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 100, 255), 2)
    else:
        cv2.putText(frame, "⚪ Manual Mode (Press 'A' to auto-capture)", (10, h-35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
    cv2.putText(frame, "SPACE=Capture | A=Auto | H=Help | Q=Quit", (10, h-10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
    if show_help:
        help_overlay = frame.copy()
        help_w, help_h = 550, 380
        help_x = (w - help_w) // 2
        help_y = (h - help_h) // 2
        cv2.rectangle(help_overlay, (help_x, help_y), 
                      (help_x + help_w, help_y + help_h), (0, 0, 0), -1)
        cv2.addWeighted(help_overlay, 0.9, frame, 0.1, 0, frame)
        cv2.rectangle(frame, (help_x, help_y), 
                      (help_x + help_w, help_y + help_h), (0, 255, 255), 2)
        help_texts = [
            ("MEDIAPIPE FACE DETECTION (v5.2: Square MIN)", (255, 255, 0), True),
            ("", (255, 255, 255), False),
            ("SPACE - Capture selected face", (255, 255, 255), False),
            ("a - Toggle auto-capture mode", (255, 255, 255), False),
            ("n - Change person name", (255, 255, 255), False),
            ("UP/DOWN - Select face (if multiple)", (255, 255, 255), False),
            ("r - Reset capture count", (255, 255, 255), False),
            ("h - Toggle this help", (255, 255, 255), False),
            ("q/ESC - Quit", (255, 255, 255), False),
            ("", (255, 255, 255), False),
            ("Quality Indicators:", (0, 255, 255), False),
            ("GREEN = Good (>=60) | YELLOW = OK | RED = Poor", (255, 255, 255), False),
            ("", (255, 255, 255), False),
            ("Crop Method (v5.2):", (0, 255, 255), False),
            (f"BBox Goc -> Square MIN (Thu nho)", (255, 255, 255), False),
        ]
        y_offset = help_y + 30
        for text, color, bold in help_texts:
            if text:
                font_scale = 0.6 if bold else 0.5
                thickness = 2 if bold else 1
                cv2.putText(frame, text, (help_x + 20, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
            y_offset += 25
    return frame


def main():
    """Main application"""
    print("=" * 75)
    print("  ESP32-CAM FACE CAPTURE TOOL - MEDIAPIPE EDITION")
    print("  ⚡ v5.2: BBox Gốc → Thu nhỏ thành VUÔNG (0% Margin) ⚡")
    print("  🔧 CLAHE: Adaptive Histogram Equalization")
    print("=" * 75)
    print(f"📡 Stream URL: {STREAM_URL}")
    print(f"💾 Dataset: {DATASET_ROOT}")
    print(f"📊 Min Quality: {MIN_QUALITY_SCORE}/100")
    print(f"📦 Output Size: {FACE_OUTPUT_SIZE[0]}×{FACE_OUTPUT_SIZE[1]} (ML ready)")
    print(f"🔍 Detector: MediaPipe (Confidence >= {MIN_DETECTION_CONFIDENCE})")
    print(f"📸 Crop Method: BBox Gốc → Square MIN (Thu nhỏ)")
    print(f"💾 Save: GRAYSCALE + CLAHE (clipLimit=2.0, tile=8x8)")
    print(f"📸 MỤC TIÊU: Tự động chụp {MAX_CAPTURES_PER_SESSION} ảnh chất lượng cao.")
    print("=" * 75)
    
    DATASET_PROCESSED.mkdir(parents=True, exist_ok=True)
    
    person_name = input("\n👤 Enter person name for dataset: ").strip()
    if not person_name:
        person_name = "unknown"
    print(f"✅ Capturing for: {person_name}")
    
    capturer = ESP32FaceCapturer(STREAM_URL)
    capturer.start()
    
    print("\n⏳ Waiting for connection...")
    timeout = 20
    start_time = time.time()
    
    while not capturer.connected and not capturer.stopped:
        time.sleep(0.1)
        if time.time() - start_time > timeout:
            print(f"\n❌ Timeout after {timeout} seconds")
            return
    
    if capturer.stopped:
        print("\n❌ Failed to connect to ESP32-CAM")
        return
    
    print("\n📺 Starting MediaPipe face detection...")
    print(f"📋 CHẾ ĐỘ TỰ ĐỘNG CHỤP {MAX_CAPTURES_PER_SESSION} ẢNH ĐANG BẬT.")
    print("   (Nhấn 'a' để tạm dừng, 'h' để xem trợ giúp)\n")
    
    face_detector = mp_face_detection.FaceDetection(
        model_selection=MODEL_SELECTION,
        min_detection_confidence=MIN_DETECTION_CONFIDENCE
    )
    
    capture_count = 0
    selected_face_idx = 0
    auto_capture = True
    show_help = False
    
    try:
        while not capturer.stopped:
            frame = capturer.read()
            
            if frame is None:
                time.sleep(0.001)
                continue
            
            display_frame = frame.copy()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            results = face_detector.process(frame_rgb)
            detections = results.detections if results.detections else []
            
            if auto_capture and len(detections) > 0:
                current_time = time.time()
                if current_time - capturer.last_capture_time >= CAPTURE_COOLDOWN:
                    best_idx = -1
                    best_quality = 0
                    
                    for idx, detection in enumerate(detections):
                        # SỬ DỤNG HÀM MỚI
                        face_crop, (fx, fy, fw, fh) = get_aligned_square_crop(frame, detection, FACE_MARGIN_SAVE)
                        if face_crop.size == 0:
                            continue
                        
                        quality = FaceQualityChecker.calculate_overall_quality(face_crop, fw, fh)
                        if quality['overall'] >= best_quality and quality['overall'] >= MIN_QUALITY_SCORE:
                            best_quality = quality['overall']
                            best_idx = idx
                    
                    if best_idx >= 0:
                        detection = detections[best_idx]
                        # SỬ DỤNG HÀM MỚI
                        face_crop, _ = get_aligned_square_crop(frame, detection, FACE_MARGIN_SAVE)
                        quality = FaceQualityChecker.calculate_overall_quality(
                            face_crop, face_crop.shape[1], face_crop.shape[0]
                        )
                        
                        gray_path = save_face_capture(face_crop, person_name, quality)
                        capture_count += 1
                        capturer.last_capture_time = current_time
                        
                        gray_name = gray_path.name if gray_path else "N/A"
                        print(f"✅ Auto-captured #{capture_count}/{MAX_CAPTURES_PER_SESSION}: Q={quality['overall']:.0f} → {gray_name}")
                        
                        if capture_count >= MAX_CAPTURES_PER_SESSION:
                            print(f"\n🎉🎉🎉 HOÀN THÀNH! Đã chụp đủ {MAX_CAPTURES_PER_SESSION} ảnh.")
                            break
            
            display_frame = draw_ui(
                display_frame, detections, face_detector, selected_face_idx, 
                person_name, capture_count, auto_capture, show_help
            )
            
            cv2.imshow('ESP32-CAM Face Capture', display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:  # Quit
                break
                
            elif key == ord('h'):  # Toggle help
                show_help = not show_help
                
            elif key == ord('a'):  # Toggle auto-capture
                auto_capture = not auto_capture
                mode = "ON" if auto_capture else "OFF"
                print(f"\n🔄 Auto-capture: {mode}")
                
            elif key == ord(' ') and len(detections) > 0:  # Manual capture
                if selected_face_idx < len(detections):
                    detection = detections[selected_face_idx]
                    # SỬ DỤNG HÀM MỚI
                    face_crop, _ = get_aligned_square_crop(frame, detection, FACE_MARGIN_SAVE)
                    
                    if face_crop.size == 0:
                        print("⚠️  Face extraction failed")
                        continue
                    
                    quality = FaceQualityChecker.calculate_overall_quality(
                        face_crop, face_crop.shape[1], face_crop.shape[0]
                    )
                    
                    if quality['overall'] >= MIN_QUALITY_SCORE:
                        gray_path = save_face_capture(face_crop, person_name, quality)
                        capture_count += 1
                        capturer.last_capture_time = time.time()
                        gray_name = gray_path.name if gray_path else "N/A"
                        print(f"✅ Manual-captured #{capture_count}/{MAX_CAPTURES_PER_SESSION}: Q={quality['overall']:.0f} → {gray_name}")
                        
                        if capture_count >= MAX_CAPTURES_PER_SESSION:
                            print(f"\n🎉🎉🎉 HOÀN THÀNH! Đã chụp đủ {MAX_CAPTURES_PER_SESSION} ảnh.")
                            break
                    else:
                        print(f"⚠️  Quality too low: {quality['overall']:.0f} < {MIN_QUALITY_SCORE}")
                        
            elif key == ord('n'):  # Change person name
                cv2.destroyWindow('ESP32-CAM Face Capture')
                new_name = input("\n👤 Enter new person name: ").strip()
                if new_name:
                    person_name = new_name
                    capture_count = 0
                    print(f"✅ Changed to: {person_name}")
                    
            elif key == ord('r'):  # Reset count
                capture_count = 0
                print("\n🔄 Capture count reset")
                
            elif key == 82 and len(detections) > 0:  # Up arrow
                selected_face_idx = (selected_face_idx - 1) % len(detections)
                
            elif key == 84 and len(detections) > 0:  # Down arrow
                selected_face_idx = (selected_face_idx + 1) % len(detections)
    
    finally:
        # Cleanup
        face_detector.close()
        capturer.stop()
        cv2.destroyAllWindows()
        
        print("\n" + "=" * 75)
        print(f"✅ Session completed!")
        print(f"📊 Total captures: {capture_count}")
        print(f"💾 Saved to: {DATASET_ROOT}")
        print(f"📁 Grayscale (112x112): {DATASET_PROCESSED / person_name}")
        print("=" * 75)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user (Ctrl+C)")
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        cv2.destroyAllWindows()
        sys.exit(1)