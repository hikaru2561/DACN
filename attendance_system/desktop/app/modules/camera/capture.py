"""
Camera Capture Module - Chụp ảnh khuôn mặt sinh viên
Tích hợp ESP32-CAM + MediaPipe Face Detection + Anti-Duplicate Validation
"""
import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
import requests
from PIL import Image, ImageTk
from datetime import datetime
from pathlib import Path
from threading import Thread
import time
import pickle
from app.core.config import (
    CAMERA_CONFIG,
    CAPTURE_CONFIG,
    UI_CONFIG,
    FACE_RECOGNITION_CONFIG,
    get_camera_url,
    get_dataset_path,
    get_embeddings_path
)

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("⚠️ MediaPipe not installed. Using basic face detection.")

try:
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False
    print("⚠️ InsightFace not installed. Duplicate check disabled.")


# ============================================================================
# COLOR SCHEME (From Config)
# ============================================================================

COLORS = UI_CONFIG["colors"]


# ============================================================================
# CONFIGURATION (From Config)
# ============================================================================

class CaptureConfig:
    """Cấu hình chụp ảnh"""
    STREAM_URL = get_camera_url()
    
    # Dataset paths
    DATASET_ROOT = Path(get_dataset_path())
    DATASET_RAW = DATASET_ROOT
    
    # Capture settings
    TARGET_PHOTOS = CAPTURE_CONFIG["target_photos"]
    FACE_OUTPUT_SIZE = (224, 224)  # None = không resize, giữ nguyên size crop
    MIN_QUALITY_SCORE = CAPTURE_CONFIG["min_quality_score"] * 100  # Convert to percentage
    CAPTURE_COOLDOWN = CAPTURE_CONFIG["capture_delay_ms"] / 1000  # Convert to seconds
    
    # MediaPipe settings
    MIN_DETECTION_CONFIDENCE = 0.6
    MODEL_SELECTION = 1  # 0=short range, 1=full range
    
    # Anti-duplicate settings
    ENABLE_DUPLICATE_CHECK = False  # 🔥 TẠM THỜI TỮT - Có thể bật sau khi test
    DUPLICATE_THRESHOLD = FACE_RECOGNITION_CONFIG["similarity_threshold"]
    EMBEDDINGS_FILE = Path(get_embeddings_path())


# ============================================================================
# DUPLICATE CHECKER - Kiểm tra trùng lặp với sinh viên khác
# ============================================================================

class DuplicateChecker:
    """Kiểm tra ảnh chụp có trùng với sinh viên khác trong DB không"""
    
    def __init__(self):
        self.embeddings_db = {}
        self.face_app = None
        self.enabled = INSIGHTFACE_AVAILABLE and CaptureConfig.ENABLE_DUPLICATE_CHECK
        
        if self.enabled:
            print("🔄 Initializing duplicate checker...")
            self.load_embeddings()
            self.init_face_model()
        else:
            print("⚠️ Duplicate check DISABLED (set ENABLE_DUPLICATE_CHECK=True to enable)")
    
    def load_embeddings(self):
        """Load embeddings hiện có từ file"""
        if not CaptureConfig.EMBEDDINGS_FILE.exists():
            print("⚠️ No embeddings file found. Duplicate check disabled.")
            self.enabled = False
            return
        
        try:
            with open(CaptureConfig.EMBEDDINGS_FILE, 'rb') as f:
                self.embeddings_db = pickle.load(f)
            print(f"✅ Loaded {len(self.embeddings_db)} students for duplicate check")
        except Exception as e:
            print(f"❌ Error loading embeddings: {e}")
            self.enabled = False
    
    def init_face_model(self):
        """Khởi tạo InsightFace model"""
        try:
            print("🔄 Loading InsightFace for duplicate check...")
            self.face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
            self.face_app.prepare(ctx_id=0, det_size=(640, 640))
            print("✅ InsightFace loaded")
        except Exception as e:
            print(f"❌ Error loading InsightFace: {e}")
            self.enabled = False
    
    def check_duplicate(self, frame, target_student_id):
        """Kiểm tra xem khuôn mặt trong frame có trùng với sinh viên khác không
        
        Args:
            frame: Frame ảnh từ camera
            target_student_id: ID sinh viên đang chụp
            
        Returns:
            tuple: (is_duplicate, matched_student_id, similarity_score)
        """
        # Nếu tắt duplicate check → luôn trả về False (không trùng)
        if not self.enabled or not self.face_app:
            return False, None, 0.0
        
        try:
            # Detect và extract embedding
            faces = self.face_app.get(frame)
            
            if not faces:
                return False, None, 0.0
            
            # Lấy khuôn mặt đầu tiên
            face_embedding = faces[0].embedding
            
            # So sánh với tất cả sinh viên trong DB (trừ chính nó)
            for student_id, embeddings_list in self.embeddings_db.items():
                # Bỏ qua chính sinh viên đang chụp
                if student_id == target_student_id:
                    continue
                
                # So sánh với tất cả embeddings của sinh viên này
                for stored_embedding in embeddings_list:
                    similarity = self.cosine_similarity(face_embedding, stored_embedding)
                    
                    # Nếu similarity cao → trùng với sinh viên khác
                    if similarity >= CaptureConfig.DUPLICATE_THRESHOLD:
                        return True, student_id, similarity
            
            return False, None, 0.0
        
        except Exception as e:
            print(f"❌ Duplicate check error: {e}")
            return False, None, 0.0
    
    @staticmethod
    def cosine_similarity(emb1, emb2):
        """Tính cosine similarity"""
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    
    def close(self):
        """Cleanup resources"""
        if self.face_app:
            del self.face_app
        self.face_app = None


# ============================================================================
# ESP32 STREAM READER
# ============================================================================

class ESP32StreamReader:
    """Đọc video stream từ ESP32-CAM"""
    
    def __init__(self, stream_url):
        self.stream_url = stream_url
        self.frame = None
        self.stopped = False
        self.connected = False
        
    def start(self):
        """Bắt đầu thread đọc stream"""
        Thread(target=self._update, daemon=True).start()
        return self
    
    def _update(self):
        """Thread đọc stream liên tục"""
        try:
            print(f"🔄 Connecting to {self.stream_url}...")
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'DesktopApp-CameraCapture',
                'Connection': 'keep-alive'
            })
            
            response = session.get(self.stream_url, stream=True, timeout=15)
            if response.status_code != 200:
                print(f"❌ HTTP Error: {response.status_code}")
                self.stopped = True
                return
            
            print("✅ Connected!")
            self.connected = True
            
            bytes_data = bytes()
            for chunk in response.iter_content(chunk_size=10240):
                if self.stopped:
                    break
                
                bytes_data += chunk
                
                # Giữ buffer không quá lớn
                if len(bytes_data) > 50000:
                    last_start = bytes_data.rfind(b'\xff\xd8')
                    if last_start > 0:
                        bytes_data = bytes_data[last_start:]
                
                # Tìm JPEG markers
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
                    except:
                        continue
        
        except Exception as e:
            print(f"❌ Stream error: {e}")
        finally:
            self.stopped = True
            self.connected = False
    
    def read(self):
        """Đọc frame hiện tại"""
        return self.frame
    
    def stop(self):
        """Dừng stream"""
        self.stopped = True


# ============================================================================
# FACE QUALITY CHECKER
# ============================================================================

class FaceQualityChecker:
    """Đánh giá chất lượng ảnh khuôn mặt"""
    
    @staticmethod
    def check_brightness(face_img):
        """Kiểm tra độ sáng (0-100)"""
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray)
        
        if avg_brightness < 80:
            score = (avg_brightness / 80) * 70
        elif avg_brightness > 180:
            score = max(50, 100 - (avg_brightness - 180))
        else:
            score = 100
        return score, avg_brightness
    
    @staticmethod
    def check_sharpness(face_img):
        """Kiểm tra độ nét (0-100)"""
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
    def check_contrast(face_img):
        """Kiểm tra độ tương phản (0-100)"""
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
    def calculate_overall_quality(face_img):
        """Tính điểm tổng thể (0-100)"""
        h, w = face_img.shape[:2]
        
        brightness_score, _ = FaceQualityChecker.check_brightness(face_img)
        sharpness_score, _ = FaceQualityChecker.check_sharpness(face_img)
        contrast_score, _ = FaceQualityChecker.check_contrast(face_img)
        
        # Size score
        size = min(h, w)
        if size < 100:
            size_score = (size / 100) * 60
        elif size > 400:
            size_score = max(70, 100 - (size - 400) / 20)
        else:
            size_score = 100
        
        overall = (
            brightness_score * 0.25 +
            sharpness_score * 0.40 +
            size_score * 0.20 +
            contrast_score * 0.15
        )
        
        return {
            'overall': overall,
            'brightness': brightness_score,
            'sharpness': sharpness_score,
            'contrast': contrast_score,
            'size': size_score
        }


# ============================================================================
# FACE PROCESSOR
# ============================================================================

class FaceProcessor:
    """Xử lý khuôn mặt: detect, crop, preprocess"""
    
    def __init__(self):
        """Khởi tạo MediaPipe (nếu có)"""
        self.detector = None
        if MEDIAPIPE_AVAILABLE:
            mp_face_detection = mp.solutions.face_detection
            self.detector = mp_face_detection.FaceDetection(
                model_selection=CaptureConfig.MODEL_SELECTION,
                min_detection_confidence=CaptureConfig.MIN_DETECTION_CONFIDENCE
            )
    
    def detect_faces(self, frame):
        """Phát hiện khuôn mặt trong frame"""
        if not MEDIAPIPE_AVAILABLE or self.detector is None:
            return []
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.detector.process(frame_rgb)
        return results.detections if results.detections else []
    
    @staticmethod
    def crop_face(frame, detection):
        """Cắt khuôn mặt vuông từ detection"""
        try:
            h, w = frame.shape[:2]
            bbox = detection.location_data.relative_bounding_box
            
            # Convert to pixels
            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            box_w = int(bbox.width * w)
            box_h = int(bbox.height * h)
            
            # Tìm tâm
            cx = x + box_w / 2
            cy = y + box_h / 2
            
            # Tạo khung vuông (cạnh = min(w, h))
            square_size = min(box_w, box_h)
            
            # Tọa độ khung vuông
            x1 = int(cx - square_size / 2)
            y1 = int(cy - square_size / 2)
            x2 = int(cx + square_size / 2)
            y2 = int(cy + square_size / 2)
            
            # Clamp to frame bounds
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(w, x2)
            y2 = min(h, y2)
            
            # Crop
            face_crop = frame[y1:y2, x1:x2]
            
            return face_crop, (x1, y1, x2 - x1, y2 - y1)
        
        except Exception as e:
            print(f"⚠️ Crop error: {e}")
            return None, None
    
    @staticmethod
    def preprocess_face(face_img):
        """Tiền xử lý khuôn mặt: Resize 224x224 → Grayscale → CLAHE
        
        Args:
            face_img: Ảnh khuôn mặt đã crop (BGR, size bất kỳ)
        
        Returns:
            Ảnh GRAYSCALE 224x224 đã enhance (1 channel)
        """
        if face_img is None or face_img.size == 0:
            return None
        
        try:
            # Bước 1: Resize về 224x224
            if CaptureConfig.FACE_OUTPUT_SIZE is not None:
                face_resized = cv2.resize(
                    face_img,
                    CaptureConfig.FACE_OUTPUT_SIZE,  # (224, 224)
                    interpolation=cv2.INTER_LANCZOS4
                )
            else:
                face_resized = face_img
            
            # Bước 2: Convert sang Grayscale
            face_gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
            
            # Bước 3: CLAHE enhancement (trên ảnh xám)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            face_gray_enhanced = clahe.apply(face_gray)
            
            return face_gray_enhanced
        
        except Exception as e:
            print(f"⚠️ Preprocess error: {e}")
            return None
    
    def close(self):
        """Đóng detector"""
        if self.detector:
            self.detector.close()


# ============================================================================
# CAMERA CAPTURE WINDOW
# ============================================================================

class CameraCaptureWindow:
    """Cửa sổ chụp ảnh khuôn mặt"""
    
    def __init__(self, parent, student_id, student_name, on_complete=None):
        """
        Args:
            parent: Cửa sổ cha
            student_id: MSSV
            student_name: Tên sinh viên
            on_complete: Callback khi hoàn thành chụp (nhận student_id)
        """
        self.parent = parent
        self.student_id = student_id
        self.student_name = student_name
        self.on_complete = on_complete
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Chụp ảnh - {student_id}")
        self.window.geometry("900x700")
        self.window.configure(bg=COLORS["dark"])
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Data
        self.capture_count = 0
        self.last_capture_time = 0
        self.auto_capture = True
        
        # Components
        self.stream = None
        self.processor = FaceProcessor()
        self.duplicate_checker = DuplicateChecker()  # 🔥 Thêm duplicate checker
        self.photo_label = None
        
        # Tracking
        self.duplicate_warnings = 0  # Số lần cảnh báo trùng lặp
        
        # Create UI
        self.create_widgets()
        
        # Start capture
        self.start_capture()
    
    def create_widgets(self):
        """Tạo giao diện"""
        # Header
        header = tk.Frame(self.window, bg=COLORS["info"], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text=f"📷 CHỤP ẢNH KHUÔN MẶT - {self.student_name}",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["info"],
            fg=COLORS["white"]
        )
        title.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Progress label
        self.progress_label = tk.Label(
            header,
            text=f"0/{CaptureConfig.TARGET_PHOTOS}",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["info"],
            fg=COLORS["white"]
        )
        self.progress_label.pack(side=tk.RIGHT, padx=20)
        
        # Video frame
        video_frame = tk.Frame(self.window, bg=COLORS["dark"])
        video_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.video_label = tk.Label(video_frame, bg=COLORS["dark"])
        self.video_label.pack(expand=True)
        
        # Control panel
        control = tk.Frame(self.window, bg=COLORS["light"], height=100)
        control.pack(fill=tk.X, padx=20, pady=(0, 20))
        control.pack_propagate(False)
        
        # Status label
        self.status_label = tk.Label(
            control,
            text="⏳ Đang kết nối camera...",
            font=("Segoe UI", 11),
            bg=COLORS["light"],
            fg=COLORS["text"]
        )
        self.status_label.pack(pady=10)
        
        # Buttons
        btn_frame = tk.Frame(control, bg=COLORS["light"])
        btn_frame.pack(pady=10)
        
        self.auto_btn = tk.Button(
            btn_frame,
            text="⏸️ Tạm dừng tự động",
            font=("Segoe UI", 10),
            bg=COLORS["warning"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.toggle_auto,
            padx=15,
            pady=8
        )
        self.auto_btn.pack(side=tk.LEFT, padx=5)
        
        btn_close = tk.Button(
            btn_frame,
            text="✕ Đóng",
            font=("Segoe UI", 10),
            bg=COLORS["danger"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.on_closing,
            padx=15,
            pady=8
        )
        btn_close.pack(side=tk.LEFT, padx=5)
    
    def start_capture(self):
        """Bắt đầu chụp ảnh"""
        # Tạo thư mục
        save_dir = CaptureConfig.DATASET_RAW / self.student_id
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Khởi động stream
        self.stream = ESP32StreamReader(CaptureConfig.STREAM_URL)
        self.stream.start()
        
        # Đợi kết nối
        self.window.after(100, self.check_connection)
    
    def check_connection(self):
        """Kiểm tra kết nối stream"""
        if self.stream.connected:
            self.status_label.config(
                text="✅ Kết nối thành công! Đang chụp tự động...",
                fg=COLORS["success"]
            )
            self.update_video()
        elif self.stream.stopped:
            self.status_label.config(
                text="❌ Không thể kết nối ESP32-CAM!",
                fg=COLORS["danger"]
            )
            messagebox.showerror("Lỗi", "Không thể kết nối tới ESP32-CAM!\nKiểm tra:\n- IP: 192.168.243.176\n- Camera đang bật\n- Cùng mạng WiFi")
        else:
            self.window.after(100, self.check_connection)
    
    def update_video(self):
        """Cập nhật video stream"""
        if self.stream.stopped or self.capture_count >= CaptureConfig.TARGET_PHOTOS:
            if self.capture_count >= CaptureConfig.TARGET_PHOTOS:
                self.status_label.config(
                    text=f"🎉 Hoàn thành! Đã chụp {self.capture_count} ảnh",
                    fg=COLORS["success"]
                )
                messagebox.showinfo(
                    "Thành công", 
                    f"Đã chụp đủ {CaptureConfig.TARGET_PHOTOS} ảnh!\n\n"
                    f"Lưu tại: dataset/raw/{self.student_id}/\n\n"
                    "Đang trích xuất embeddings..."
                )
                
                # 🔥 GỌI CALLBACK để extract embeddings ngay sau khi chụp xong
                if self.on_complete:
                    self.on_complete(self.student_id)
                
            return
        
        frame = self.stream.read()
        if frame is None:
            self.window.after(30, self.update_video)
            return
        
        display = frame.copy()
        
        # Detect faces
        detections = self.processor.detect_faces(frame)
        
        # Auto capture
        if self.auto_capture and len(detections) > 0:
            current_time = time.time()
            if current_time - self.last_capture_time >= CaptureConfig.CAPTURE_COOLDOWN:
                # Tìm face tốt nhất
                best_face = None
                best_quality = 0
                
                for detection in detections:
                    face_crop, bbox = self.processor.crop_face(frame, detection)
                    if face_crop is None or face_crop.size == 0:
                        continue
                    
                    quality = FaceQualityChecker.calculate_overall_quality(face_crop)
                    if quality['overall'] >= best_quality and quality['overall'] >= CaptureConfig.MIN_QUALITY_SCORE:
                        best_quality = quality['overall']
                        best_face = (face_crop, quality)
                
                # Lưu ảnh tốt nhất
                if best_face:
                    should_save = True  # Mặc định là lưu
                    
                    # 🔥 KIỂM TRA TRÙNG LẶP (nếu được bật)
                    if CaptureConfig.ENABLE_DUPLICATE_CHECK:
                        is_duplicate, matched_id, similarity = self.duplicate_checker.check_duplicate(
                            frame, self.student_id
                        )
                        
                        if is_duplicate:
                            should_save = False  # Không lưu nếu trùng
                            
                            # Cảnh báo trùng lặp
                            self.duplicate_warnings += 1
                            print(f"⚠️ DUPLICATE DETECTED! Face matches {matched_id} (similarity: {similarity:.3f})")
                            
                            # Hiển thị cảnh báo trên UI
                            self.status_label.config(
                                text=f"⚠️ CẢNH BÁO: Khuôn mặt trùng với sinh viên {matched_id}!",
                                fg=COLORS["danger"]
                            )
                            
                            # Nếu cảnh báo quá 3 lần → dừng chụp
                            if self.duplicate_warnings >= 3:
                                self.auto_capture = False
                                messagebox.showwarning(
                                    "Phát hiện trùng lặp",
                                    f"⚠️ Khuôn mặt đang chụp trùng với sinh viên khác trong hệ thống!\n\n"
                                    f"Sinh viên trùng: {matched_id}\n"
                                    f"Độ tương đồng: {similarity:.2%}\n\n"
                                    f"Vui lòng kiểm tra lại:\n"
                                    f"1. Đúng người đang chụp không?\n"
                                    f"2. Sinh viên {matched_id} đã có trong hệ thống chưa?\n\n"
                                    f"Nhấn 'Tiếp tục' để chụp lại hoặc 'Đóng' để hủy."
                                )
                                self.toggle_auto()  # Chuyển sang chế độ tạm dừng
                    
                    # Lưu ảnh (nếu không trùng hoặc không bật check)
                    if should_save:
                        self.save_photo(best_face[0], best_face[1], frame=frame)
                        self.last_capture_time = current_time
                        self.duplicate_warnings = 0  # Reset cảnh báo
        
        # Draw faces
        for detection in detections:
            face_crop, bbox = self.processor.crop_face(frame, detection)
            if bbox is None:
                continue
            
            x, y, w, h = bbox
            
            if face_crop is not None and face_crop.size > 0:
                quality = FaceQualityChecker.calculate_overall_quality(face_crop)
                
                # Color based on quality
                if quality['overall'] >= CaptureConfig.MIN_QUALITY_SCORE:
                    color = (0, 255, 0)
                    status = "GOOD"
                elif quality['overall'] >= 40:
                    color = (0, 255, 255)
                    status = "OK"
                else:
                    color = (0, 0, 255)
                    status = "POOR"
                
                # Draw box
                cv2.rectangle(display, (x, y), (x + w, y + h), color, 2)
                
                # Draw quality
                cv2.putText(display, f"{status} Q={quality['overall']:.0f}",
                           (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Convert to PhotoImage
        frame_rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        
        # Resize to fit window
        max_width = 850
        max_height = 500
        frame_pil.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(frame_pil)
        self.video_label.config(image=photo)
        self.video_label.image = photo
        
        # Update progress
        self.progress_label.config(text=f"{self.capture_count}/{CaptureConfig.TARGET_PHOTOS}")
        
        # Next frame
        self.window.after(30, self.update_video)
    
    def save_photo(self, face_img, quality_info, frame=None):
        """Lưu ảnh TOÀN DIỆN từ camera (frame gốc)
        
        Args:
            face_img: Ảnh khuôn mặt đã crop (chỉ dùng để check quality)
            quality_info: Thông tin chất lượng
            frame: Frame gốc từ camera (LƯU CÁI NÀY!)
        """
        try:
            # 🔥 LƯU FRAME GỐC TOÀN DIỆN - KHÔNG CROP, KHÔNG RESIZE!
            # Frame nguyên bản từ ESP32-CAM
            
            # Tạo filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            quality_str = f"q{int(quality_info['overall'])}"
            filename = f"{self.student_id}_{timestamp}_{quality_str}.jpg"
            
            # Lưu FRAME GỐC (toàn bộ ảnh từ camera, không crop)
            save_dir = CaptureConfig.DATASET_RAW / self.student_id
            save_path = save_dir / filename
            
            if frame is not None:
                # Lưu frame gốc
                cv2.imwrite(str(save_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
                self.capture_count += 1
                print(f"✅ Saved {self.capture_count}/{CaptureConfig.TARGET_PHOTOS}: {filename} (Size: {frame.shape}) - FULL FRAME")
            else:
                print(f"⚠️ Frame is None, skipping save")
            
        except Exception as e:
            print(f"❌ Save error: {e}")
            import traceback
            traceback.print_exc()
    
    def toggle_auto(self):
        """Bật/tắt chụp tự động"""
        self.auto_capture = not self.auto_capture
        
        if self.auto_capture:
            self.auto_btn.config(text="⏸️ Tạm dừng tự động", bg=COLORS["warning"])
            self.status_label.config(text="🔴 Đang chụp tự động...")
        else:
            self.auto_btn.config(text="▶️ Tiếp tục chụp", bg=COLORS["success"])
            self.status_label.config(text="⏸️ Đã tạm dừng. Nhấn 'Tiếp tục' để chụp.")
    
    def on_closing(self):
        """Đóng cửa sổ"""
        if self.stream:
            self.stream.stop()
        if self.processor:
            self.processor.close()
        self.window.destroy()


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    CameraCaptureWindow(root, "2280602549", "Nguyễn Kim Quang")
    root.mainloop()
