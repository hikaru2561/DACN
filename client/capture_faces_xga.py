"""
ESP32-CAM Face Capture Tool - XGA 1024×768
Synchronized with ESP32 XGA_FLUSH_v7.1 firmware
Detect faces, draw bounding boxes, capture and preprocess
Auto-save to dataset with quality checks
"""

import cv2
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
ESP32_CAM_IP = "192.168.1.12"
STREAM_URL = f"http://{ESP32_CAM_IP}/stream"

# ESP32 Camera Settings (for reference):
# - Resolution: XGA 1024×768
# - JPEG Quality: 14 (~25-30 KB/frame)
# - Frame Buffers: 2 (CAMERA_GRAB_LATEST)
# - Target FPS: ~100 FPS (1ms delay)
# - WiFi: Sleep disabled, max power

# Dataset configuration
DATASET_ROOT = Path(r"d:\HUTECH\DACN\dataset")
DATASET_RAW = DATASET_ROOT / "raw"
DATASET_PROCESSED = DATASET_ROOT / "processed"

# Face detection configuration
FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
MIN_FACE_SIZE = (80, 80)  # Minimum face size to detect
MAX_FACE_SIZE = (600, 600)  # Maximum face size

# Preprocessing configuration
FACE_OUTPUT_SIZE = (224, 224)  # Standard size for ML models
BRIGHTNESS_THRESHOLD = 30  # Minimum average brightness
BLUR_THRESHOLD = 100  # Minimum Laplacian variance (sharpness)
MIN_QUALITY_SCORE = 60  # Minimum quality score (0-100)

# Capture settings
CAPTURE_COOLDOWN = 0.5  # Seconds between auto captures
MAX_CAPTURES_PER_SESSION = 100

class FaceQualityChecker:
    """Check face image quality for dataset"""
    
    @staticmethod
    def check_brightness(face_img):
        """Check if face is well-lit (0-100 score)"""
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray)
        # Score: 0 at brightness=0, 100 at brightness=128+
        score = min(100, (avg_brightness / 128) * 100)
        return score, avg_brightness
    
    @staticmethod
    def check_sharpness(face_img):
        """Check if face is sharp/focused (0-100 score)"""
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        # Score: 0 at var=0, 100 at var=500+
        score = min(100, (laplacian_var / 500) * 100)
        return score, laplacian_var
    
    @staticmethod
    def check_size(face_w, face_h):
        """Check if face size is appropriate (0-100 score)"""
        # Ideal size: 150-400 pixels
        size = min(face_w, face_h)
        if size < 80:
            score = (size / 80) * 50  # Too small
        elif size > 400:
            score = max(50, 100 - (size - 400) / 10)  # Too large
        else:
            score = 100  # Perfect size
        return min(100, max(0, score))
    
    @staticmethod
    def calculate_overall_quality(face_img, face_w, face_h):
        """Calculate overall quality score (0-100)"""
        brightness_score, brightness_val = FaceQualityChecker.check_brightness(face_img)
        sharpness_score, sharpness_val = FaceQualityChecker.check_sharpness(face_img)
        size_score = FaceQualityChecker.check_size(face_w, face_h)
        
        # Weighted average
        overall = (brightness_score * 0.3 + sharpness_score * 0.5 + size_score * 0.2)
        
        return {
            'overall': overall,
            'brightness': brightness_score,
            'brightness_val': brightness_val,
            'sharpness': sharpness_score,
            'sharpness_val': sharpness_val,
            'size': size_score
        }


class ESP32FaceCapturer:
    def __init__(self, stream_url):
        self.stream_url = stream_url
        self.frame = None
        self.stopped = False
        self.connected = False
        self.capture_count = 0
        self.last_capture_time = 0
        
    def start(self):
        """Start stream reading thread"""
        Thread(target=self.update, daemon=True).start()
        return self
        
    def update(self):
        """Main stream reading loop"""
        try:
            print(f"🔄 Connecting to {self.stream_url}...")
            
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'ESP32-Face-Capture-v7.1',
                'Connection': 'keep-alive',  # Keep connection for better performance
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
            print(f"📡 ESP32-CAM XGA_FLUSH_v7.1")
            print(f"🎯 Expected: XGA 1024×768, JPEG Q14, ~100 FPS")
            self.connected = True
            
            bytes_data = bytes()
            frame_count = 0
            last_fps_time = time.time()
            
            # ⚡ OPTIMIZED for XGA JPEG Q14 (~25-30KB frames)
            for chunk in response.iter_content(chunk_size=10240):  # 10KB chunks for Q14
                if self.stopped:
                    break
                    
                bytes_data += chunk
                
                # ⚡ Buffer management: Keep only last 50KB (~2 frames max)
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
                        frame = cv2.imdecode(
                            np.frombuffer(jpg, dtype=np.uint8), 
                            cv2.IMREAD_COLOR
                        )
                        if frame is not None:
                            self.frame = frame
                            frame_count += 1
                            
                            # FPS reporting every 5 seconds
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
        """Get current frame"""
        return self.frame
        
    def stop(self):
        """Stop streaming"""
        self.stopped = True


def preprocess_face(face_img):
    """Preprocess face image for dataset"""
    # Resize to standard size
    face_resized = cv2.resize(face_img, FACE_OUTPUT_SIZE, interpolation=cv2.INTER_AREA)
    
    # Histogram equalization for better contrast
    img_yuv = cv2.cvtColor(face_resized, cv2.COLOR_BGR2YUV)
    img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
    face_equalized = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
    
    # Denoise slightly
    face_denoised = cv2.fastNlMeansDenoisingColored(face_equalized, None, 10, 10, 7, 21)
    
    # Sharpen
    kernel = np.array([[-1,-1,-1],
                       [-1, 9,-1],
                       [-1,-1,-1]])
    face_sharpened = cv2.filter2D(face_denoised, -1, kernel)
    
    return face_sharpened


def save_face_capture(face_img, person_name, quality_info):
    """Save face to dataset with metadata"""
    # Create person directory
    person_raw = DATASET_RAW / person_name
    person_processed = DATASET_PROCESSED / person_name
    person_raw.mkdir(parents=True, exist_ok=True)
    person_processed.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    quality_str = f"q{int(quality_info['overall'])}"
    
    filename = f"{person_name}_{timestamp}_{quality_str}.jpg"
    
    # Save raw image
    raw_path = person_raw / filename
    cv2.imwrite(str(raw_path), face_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    
    # Preprocess and save
    face_processed = preprocess_face(face_img)
    processed_path = person_processed / filename
    cv2.imwrite(str(processed_path), face_processed, [cv2.IMWRITE_JPEG_QUALITY, 95])
    
    # Save metadata
    metadata_path = person_raw / f"{filename}.txt"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write(f"Person: {person_name}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Quality Score: {quality_info['overall']:.1f}/100\n")
        f.write(f"Brightness: {quality_info['brightness']:.1f}/100 (val: {quality_info['brightness_val']:.1f})\n")
        f.write(f"Sharpness: {quality_info['sharpness']:.1f}/100 (var: {quality_info['sharpness_val']:.1f})\n")
        f.write(f"Size Score: {quality_info['size']:.1f}/100\n")
    
    return raw_path, processed_path


def draw_ui(frame, faces, selected_face_idx, person_name, capture_count, auto_capture, show_help):
    """Draw UI overlay on frame"""
    h, w = frame.shape[:2]
    
    # Semi-transparent overlay for header
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 80), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    
    # Header
    cv2.putText(frame, "ESP32-CAM Face Capture Tool", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.putText(frame, f"Person: {person_name} | Captured: {capture_count}", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Draw faces
    for idx, (x, y, fw, fh) in enumerate(faces):
        # Calculate quality
        face_roi = frame[y:y+fh, x:x+fw]
        quality = FaceQualityChecker.calculate_overall_quality(face_roi, fw, fh)
        
        # Color based on quality
        if quality['overall'] >= MIN_QUALITY_SCORE:
            color = (0, 255, 0)  # Green - good quality
            status = "GOOD"
        elif quality['overall'] >= 40:
            color = (0, 255, 255)  # Yellow - acceptable
            status = "OK"
        else:
            color = (0, 0, 255)  # Red - poor quality
            status = "POOR"
        
        # Thicker box if selected
        thickness = 3 if idx == selected_face_idx else 2
        
        # Draw bounding box
        cv2.rectangle(frame, (x, y), (x+fw, y+fh), color, thickness)
        
        # Draw quality info box
        info_y = y - 10 if y > 40 else y + fh + 20
        cv2.putText(frame, f"Face {idx+1}: {status} ({quality['overall']:.0f})", 
                    (x, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw quality bars
        bar_width = fw
        bar_height = 6
        bar_y = y - 20 if y > 50 else y + fh + 30
        
        # Brightness bar
        bright_w = int((quality['brightness'] / 100) * bar_width)
        cv2.rectangle(frame, (x, bar_y), (x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
        cv2.rectangle(frame, (x, bar_y), (x + bright_w, bar_y + bar_height), (0, 255, 255), -1)
        
        # Sharpness bar
        sharp_y = bar_y + bar_height + 2
        sharp_w = int((quality['sharpness'] / 100) * bar_width)
        cv2.rectangle(frame, (x, sharp_y), (x + bar_width, sharp_y + bar_height), (50, 50, 50), -1)
        cv2.rectangle(frame, (x, sharp_y), (x + sharp_w, sharp_y + bar_height), (255, 0, 255), -1)
    
    # Status bar at bottom
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, h-60), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    
    # Auto-capture indicator
    if auto_capture:
        cv2.putText(frame, "🔴 AUTO CAPTURE ON", (10, h-35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    else:
        cv2.putText(frame, "⚪ Manual Mode", (10, h-35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
    
    cv2.putText(frame, "Press 'h' for help", (10, h-10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
    
    # Help overlay
    if show_help:
        help_overlay = frame.copy()
        help_w, help_h = 500, 320
        help_x = (w - help_w) // 2
        help_y = (h - help_h) // 2
        
        cv2.rectangle(help_overlay, (help_x, help_y), 
                     (help_x + help_w, help_y + help_h), (0, 0, 0), -1)
        cv2.addWeighted(help_overlay, 0.9, frame, 0.1, 0, frame)
        
        cv2.rectangle(frame, (help_x, help_y), 
                     (help_x + help_w, help_y + help_h), (0, 255, 255), 2)
        
        help_texts = [
            ("KEYBOARD SHORTCUTS", (255, 255, 0), True),
            ("", (255, 255, 255), False),
            ("SPACE - Capture selected face", (255, 255, 255), False),
            ("a - Toggle auto-capture mode", (255, 255, 255), False),
            ("n - Change person name", (255, 255, 255), False),
            ("↑/↓ - Select face (if multiple)", (255, 255, 255), False),
            ("r - Reset capture count", (255, 255, 255), False),
            ("h - Toggle this help", (255, 255, 255), False),
            ("q/ESC - Quit", (255, 255, 255), False),
            ("", (255, 255, 255), False),
            ("Quality Indicators:", (0, 255, 255), False),
            ("GREEN = Good | YELLOW = OK | RED = Poor", (255, 255, 255), False),
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
    print("  ESP32-CAM FACE CAPTURE TOOL v7.1")
    print("  Synchronized with ESP32 XGA_FLUSH_v7.1 firmware")
    print("  Detect → Draw → Capture → Preprocess → Save to Dataset")
    print("=" * 75)
    print(f"📡 Stream URL: {STREAM_URL}")
    print(f"💾 Dataset: {DATASET_ROOT}")
    print(f"📊 Min Quality: {MIN_QUALITY_SCORE}/100")
    print(f"🎯 ESP32 Config: XGA 1024×768, JPEG Q14, ~100 FPS")
    print(f"📦 Output Size: {FACE_OUTPUT_SIZE[0]}×{FACE_OUTPUT_SIZE[1]} (ML ready)")
    print("=" * 75)
    
    # Create dataset directories
    DATASET_RAW.mkdir(parents=True, exist_ok=True)
    DATASET_PROCESSED.mkdir(parents=True, exist_ok=True)
    
    # Get person name
    person_name = input("\n👤 Enter person name for dataset: ").strip()
    if not person_name:
        person_name = "unknown"
    print(f"✅ Capturing for: {person_name}")
    
    # Initialize capturer
    capturer = ESP32FaceCapturer(STREAM_URL)
    capturer.start()
    
    # Wait for connection
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
    
    print("\n📺 Starting face detection...")
    print("📋 Press 'h' for keyboard shortcuts\n")
    
    # Main loop variables
    capture_count = 0
    selected_face_idx = 0
    auto_capture = False
    show_help = False
    
    while not capturer.stopped:
        frame = capturer.read()
        
        if frame is None:
            time.sleep(0.001)
            continue
        
        # Make a copy for processing
        display_frame = frame.copy()
        
        # Detect faces
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = FACE_CASCADE.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=MIN_FACE_SIZE,
            maxSize=MAX_FACE_SIZE
        )
        
        # Auto-capture logic
        if auto_capture and len(faces) > 0 and capture_count < MAX_CAPTURES_PER_SESSION:
            current_time = time.time()
            if current_time - capturer.last_capture_time >= CAPTURE_COOLDOWN:
                # Get best quality face
                best_idx = -1
                best_quality = 0
                
                for idx, (x, y, fw, fh) in enumerate(faces):
                    face_roi = frame[y:y+fh, x:x+fw]
                    quality = FaceQualityChecker.calculate_overall_quality(face_roi, fw, fh)
                    if quality['overall'] > best_quality and quality['overall'] >= MIN_QUALITY_SCORE:
                        best_quality = quality['overall']
                        best_idx = idx
                
                # Capture best face
                if best_idx >= 0:
                    x, y, fw, fh = faces[best_idx]
                    face_roi = frame[y:y+fh, x:x+fw]
                    quality = FaceQualityChecker.calculate_overall_quality(face_roi, fw, fh)
                    
                    raw_path, proc_path = save_face_capture(face_roi, person_name, quality)
                    capture_count += 1
                    capturer.last_capture_time = current_time
                    
                    print(f"✅ Auto-captured #{capture_count}: Q={quality['overall']:.0f} → {proc_path.name}")
        
        # Draw UI
        display_frame = draw_ui(
            display_frame, faces, selected_face_idx, 
            person_name, capture_count, auto_capture, show_help
        )
        
        # Display
        cv2.imshow('ESP32-CAM Face Capture', display_frame)
        
        # Handle keyboard
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') or key == 27:  # Quit
            break
            
        elif key == ord('h'):  # Toggle help
            show_help = not show_help
            
        elif key == ord('a'):  # Toggle auto-capture
            auto_capture = not auto_capture
            mode = "ON" if auto_capture else "OFF"
            print(f"\n🔄 Auto-capture: {mode}")
            
        elif key == ord(' ') and len(faces) > 0:  # Manual capture
            if selected_face_idx < len(faces):
                x, y, fw, fh = faces[selected_face_idx]
                face_roi = frame[y:y+fh, x:x+fw]
                quality = FaceQualityChecker.calculate_overall_quality(face_roi, fw, fh)
                
                if quality['overall'] >= MIN_QUALITY_SCORE:
                    raw_path, proc_path = save_face_capture(face_roi, person_name, quality)
                    capture_count += 1
                    capturer.last_capture_time = time.time()
                    print(f"✅ Captured #{capture_count}: Q={quality['overall']:.0f} → {proc_path.name}")
                else:
                    print(f"⚠️  Quality too low: {quality['overall']:.0f} < {MIN_QUALITY_SCORE}")
                    
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
            
        elif key == 82 and len(faces) > 0:  # Up arrow
            selected_face_idx = (selected_face_idx - 1) % len(faces)
            
        elif key == 84 and len(faces) > 0:  # Down arrow
            selected_face_idx = (selected_face_idx + 1) % len(faces)
    
    # Cleanup
    capturer.stop()
    cv2.destroyAllWindows()
    
    print("\n" + "=" * 70)
    print(f"✅ Session completed!")
    print(f"📊 Total captures: {capture_count}")
    print(f"💾 Saved to: {DATASET_ROOT / person_name}")
    print(f"📁 Raw images: {DATASET_RAW / person_name}")
    print(f"📁 Processed: {DATASET_PROCESSED / person_name}")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user (Ctrl+C)")
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        cv2.destroyAllWindows()
        sys.exit(1)
