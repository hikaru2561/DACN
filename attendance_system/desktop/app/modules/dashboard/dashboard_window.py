import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import threading
import time
import requests
import mediapipe as mp
import unicodedata
import os
from datetime import datetime
from app.core.colors import COLORS
from app.core.config import API_BASE_URL, CAMERA_CONFIG, PATHS
from app.core.api_client import APIClient
from app.modules.user_management.user_window import UserManagementWindow
from app.modules.history.history_window import HistoryWindow
from app.core.face_recognizer import FaceRecognizer

def remove_accents(text):
    """
    Chuyển tiếng Việt có dấu thành không dấu
    Ví dụ: Nguyễn Kim Quang -> Nguyen Kim Quang
    """
    if not text:
        return text
    
    # Normalize unicode (NFD = decomposed form)
    nfd = unicodedata.normalize('NFD', text)
    
    # Remove combining characters (dấu)
    output = ''
    for char in nfd:
        if unicodedata.category(char) != 'Mn':  # Mn = Mark, Nonspacing
            output += char
    
    # Đặc biệt xử lý Đ/đ
    output = output.replace('Đ', 'D').replace('đ', 'd')
    
    return output

class StreamReader:
    """Reads MJPEG stream in a separate thread to ensure low latency"""
    def __init__(self, url):
        self.url = url
        self.latest_frame = None
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)

    def update(self):
        print(f"📡 Connecting to stream: {self.url}")
        try:
            session = requests.Session()
            response = session.get(self.url, stream=True, timeout=5)
            
            bytes_data = bytes()
            for chunk in response.iter_content(chunk_size=4096):
                if not self.running:
                    break
                    
                bytes_data += chunk
                a = bytes_data.find(b'\xff\xd8')
                b = bytes_data.find(b'\xff\xd9')
                
                if a != -1 and b != -1:
                    jpg = bytes_data[a:b+2]
                    bytes_data = bytes_data[b+2:]
                    
                    try:
                        frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                        if frame is not None:
                            with self.lock:
                                self.latest_frame = frame
                    except Exception:
                        pass
                        
        except Exception as e:
            print(f"❌ Stream Error: {e}")
            self.running = False

    def get_frame(self):
        with self.lock:
            if self.latest_frame is not None:
                return self.latest_frame.copy()
            return None

class DashboardWindow:
    def __init__(self, root, user_name="Admin"):
        self.root = root
        self.root.title("HỆ THỐNG KIỂM SOÁT RA VÀO - FACE ACCESS CONTROL")
        self.root.geometry("1400x900")
        self.root.configure(bg=COLORS["bg_dark"])
        
        self.api = APIClient()
        self.user_name = user_name
        self.is_running = True
        
        # Initialize Face Recognizer (InsightFace)
        self.recognizer = FaceRecognizer()
        
        # Initialize MediaPipe Face Detection (Fast)
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(min_detection_confidence=0.6)
        
        # Initialize MediaPipe Face Mesh for Eye Tracking (Liveness Detection)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Liveness Detection State
        self.liveness_required = True  # Bật liveness check
        self.liveness_verified = False
        self.liveness_verified_time = 0  # Thời điểm verify thành công
        self.liveness_timeout = 10  # Timeout 10s sau khi verify
        self.blink_counter = 0
        self.blink_threshold = 0.21  # EAR threshold
        self.prev_ear = 0.3
        self.blinks_needed = 2  # Cần nháy 2 lần
        
        self.last_open_time = 0
        self.last_esp_update = 0
        self.recognition_paused_until = 0  # Pause recognition sau access
        self.last_recognition_name = ""  # Lưu kết quả nhận diện để hiển thị
        self.saved_recognition_results = []  # Lưu TẤT CẢ kết quả để vẽ trong pause
        
        # Stream Reader
        stream_url = CAMERA_CONFIG.get("stream_url")
        self.stream_reader = StreamReader(stream_url)
        
        # Layout
        self.create_layout()
        
        # Start Threads
        self.stream_reader.start()
        
        self.display_thread = threading.Thread(target=self.video_loop, daemon=True)
        self.display_thread.start()
        
        self.recognition_thread = threading.Thread(target=self.recognition_loop, daemon=True)
        self.recognition_thread.start()
        
        self.log_thread = threading.Thread(target=self.update_logs_loop, daemon=True)
        self.log_thread.start()

    def create_layout(self):
        # Header
        header = tk.Frame(self.root, bg=COLORS["primary"], height=60)
        header.pack(fill=tk.X)
        
        tk.Label(header, text="🔐 FACE ACCESS CONTROL", font=("Segoe UI", 18, "bold"), 
                 bg=COLORS["primary"], fg="white").pack(side=tk.LEFT, padx=20)
        
        tk.Button(header, text="Đăng xuất", bg=COLORS["danger"], fg="white", 
                  command=self.logout).pack(side=tk.RIGHT, padx=20)
        
        tk.Label(header, text=f"Xin chào, {self.user_name}", font=("Segoe UI", 12), 
                 bg=COLORS["primary"], fg="white").pack(side=tk.RIGHT, padx=20)

        # Main Content
        main_container = tk.Frame(self.root, bg=COLORS["bg_dark"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left: Camera Stream
        left_panel = tk.Frame(main_container, bg="black", width=1050)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.video_canvas = tk.Canvas(left_panel, bg="black", highlightthickness=0, width=1024, height=768)
        self.video_canvas.pack(padx=10, pady=10)
        self.canvas_image_id = self.video_canvas.create_image(512, 384, anchor=tk.CENTER)
        
        # Right: Controls & Logs
        right_panel = tk.Frame(main_container, bg=COLORS["bg_light"], width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)
        right_panel.pack_propagate(False)
        
        control_frame = tk.LabelFrame(right_panel, text="Điều khiển", bg=COLORS["bg_light"], font=("Segoe UI", 10, "bold"))
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(control_frame, text="🔓 MỞ CỬA (Manual)", bg=COLORS["success"], fg="white", font=("Segoe UI", 12, "bold"),
                  height=2, command=self.manual_open_door).pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(control_frame, text="👥 Quản lý Người dùng", bg=COLORS["info"], fg="white",
                  command=self.open_user_management).pack(fill=tk.X, padx=10, pady=5)

        tk.Button(control_frame, text="📜 Lịch sử Ra vào", bg=COLORS["warning"], fg="white",
                  command=self.open_history).pack(fill=tk.X, padx=10, pady=5)
        
        log_frame = tk.LabelFrame(right_panel, text="Lịch sử ra vào (Gần nhất)", bg=COLORS["bg_light"], font=("Segoe UI", 10, "bold"))
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        cols = ("time", "name", "status")
        self.tree_log = ttk.Treeview(log_frame, columns=cols, show="headings", height=15)
        self.tree_log.heading("time", text="Thời gian")
        self.tree_log.heading("name", text="Người dùng")
        self.tree_log.heading("status", text="Trạng thái")
        self.tree_log.column("time", width=80)
        self.tree_log.column("name", width=120)
        self.tree_log.column("status", width=80)
        self.tree_log.pack(fill=tk.BOTH, expand=True)
    
    def calculate_ear(self, eye_landmarks):
        """
        Calculate Eye Aspect Ratio (EAR)
        EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
        """
        # Vertical distances
        A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        # Horizontal distance
        C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        
        if C == 0:
            return 0.3
        ear = (A + B) / (2.0 * C)
        return ear
    
    def detect_blink(self, landmarks, frame_shape):
        """
        Detect eye blinks using Face Mesh landmarks
        Returns True if blink detected
        """
        h, w = frame_shape[:2]
        
        # Left eye landmarks indices (MediaPipe Face Mesh)
        LEFT_EYE = [33, 160, 158, 133, 153, 144]
        # Right eye landmarks indices
        RIGHT_EYE = [362, 385, 387, 263, 373, 380]
        
        try:
            # Extract left eye points
            left_eye = np.array([(landmarks[i].x * w, landmarks[i].y * h) for i in LEFT_EYE])
            # Extract right eye points
            right_eye = np.array([(landmarks[i].x * w, landmarks[i].y * h) for i in RIGHT_EYE])
            
            # Calculate EAR for both eyes
            left_ear = self.calculate_ear(left_eye)
            right_ear = self.calculate_ear(right_eye)
            ear = (left_ear + right_ear) / 2.0
            
            # Detect blink: EAR drops below threshold then rises above
            blink_detected = False
            if self.prev_ear > self.blink_threshold and ear < self.blink_threshold:
                # Eye closed
                pass
            elif self.prev_ear < self.blink_threshold and ear > self.blink_threshold:
                # Eye opened again -> blink detected
                blink_detected = True
                self.blink_counter += 1
                print(f"👁️ Blink detected! Count: {self.blink_counter}/{self.blinks_needed}")
                
                # Nếu đủ số lần nháy -> Set verified time
                if self.blink_counter >= self.blinks_needed and not self.liveness_verified:
                    self.liveness_verified = True
                    self.liveness_verified_time = time.time()
                    print(f"✅ Liveness verified! (Will timeout in {self.liveness_timeout}s if no recognition)")
            
            self.prev_ear = ear
            return blink_detected, ear
            
        except Exception as e:
            return False, 0.3

    def video_loop(self):
        """Display Loop with MediaPipe Detection + Liveness Check"""
        self.is_paused = False
        self.recognition_results = []
        
        while self.is_running:
            if self.is_paused:
                time.sleep(0.1)
                continue

            frame = self.stream_reader.get_frame()
            if frame is not None:
                self.current_frame = frame
                
                h, w, _ = frame.shape
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Kiểm tra xem có đang trong thời gian pause không
                current_time = time.time()
                is_in_pause = current_time < self.recognition_paused_until
                
                # 1. Liveness Detection (Face Mesh for blink detection)
                # KHÔNG hiển thị prompt nháy mắt khi đang pause (đang hiển thị result)
                if self.liveness_required and not self.liveness_verified and not is_in_pause:
                    mesh_results = self.face_mesh.process(frame_rgb)
                    
                    if mesh_results.multi_face_landmarks:
                        landmarks = mesh_results.multi_face_landmarks[0].landmark
                        blink_detected, ear = self.detect_blink(landmarks, frame.shape)
                        
                        # Kiểm tra đủ số lần nháy mắt
                        if self.blink_counter >= self.blinks_needed:
                            self.liveness_verified = True
                            print("✅ Liveness verified!")
                        
                        # Hiển thị prompt
                        prompt_text = f"NHAY MAT: {self.blink_counter}/{self.blinks_needed}"
                        cv2.putText(frame_rgb, prompt_text, (w//2 - 150, 50), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)
                        cv2.putText(frame_rgb, "De xac thuc ban la nguoi that", (w//2 - 200, 100),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                    
                    # Reset nếu không có face
                    else:
                        pass
                
                # 2. Face Detection (chỉ khi đã verify liveness hoặc không cần)
                show_recognition = not self.liveness_required or self.liveness_verified
                
                if show_recognition and not is_in_pause:
                    results = self.face_detection.process(frame_rgb)
                    
                    if results.detections:
                        for detection in results.detections:
                            bboxC = detection.location_data.relative_bounding_box
                            x = int(bboxC.xmin * w)
                            y = int(bboxC.ymin * h)
                            bw = int(bboxC.width * w)
                            bh = int(bboxC.height * h)
                            
                            cx, cy = x + bw//2, y + bh//2
                            
                            name = None
                            color = None
                            best_match_dist = float('inf')
                            
                            for res in self.recognition_results:
                                rx1, ry1, rx2, ry2 = [c * 2 for c in res["bbox"]]
                                rcx, rcy = (rx1 + rx2)//2, (ry1 + ry2)//2
                                dist = ((cx - rcx)**2 + (cy - rcy)**2)**0.5
                                
                                if dist < 100:
                                    if dist < best_match_dist:
                                        best_match_dist = dist
                                        name = res["name"]
                                        if name != "Unknown":
                                            color = (0, 255, 0)
                                        else:
                                            color = (255, 0, 0)
                            
                            # Vẽ bbox và tên
                            if name is not None and color is not None:
                                display_name = remove_accents(name)
                                cv2.rectangle(frame_rgb, (x, y), (x + bw, y + bh), color, 2)
                                cv2.putText(frame_rgb, display_name, (x, y - 10), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                
                # 3. Hiển thị BBOX BÁM THEO FACE trong pause time
                if is_in_pause and len(self.saved_recognition_results) > 0:
                    remaining = self.recognition_paused_until - current_time
                    
                    # DETECT FACE REAL-TIME để update bbox position
                    current_detections = self.face_detection.process(frame_rgb)
                    
                    if current_detections.detections:
                        # Match detection hiện tại với recognition results
                        for detection in current_detections.detections:
                            bboxC = detection.location_data.relative_bounding_box
                            x = int(bboxC.xmin * w)
                            y = int(bboxC.ymin * h)
                            bw = int(bboxC.width * w)
                            bh = int(bboxC.height * h)
                            
                            cx, cy = x + bw//2, y + bh//2
                            
                            # Tìm recognition result gần nhất
                            best_match_name = None
                            best_match_dist = float('inf')
                            best_match_score = 0.0  # Khởi tạo score
                            
                            for res in self.saved_recognition_results:
                                old_bbox = res.get("bbox", [])
                                if len(old_bbox) == 4:
                                    # Old bbox center (scale x2)
                                    ox1, oy1, ox2, oy2 = [int(c * 2) for c in old_bbox]
                                    ocx, ocy = (ox1 + ox2)//2, (oy1 + oy2)//2
                                    
                                    # Distance giữa vị trí cũ và mới
                                    dist = ((cx - ocx)**2 + (cy - ocy)**2)**0.5
                                    
                                    # Nếu gần nhau (<200px) → Same person
                                    if dist < 200 and dist < best_match_dist:
                                        best_match_dist = dist
                                        best_match_name = res.get("name", "Unknown")
                                        best_match_score = res.get("score", 0.0)  # Lấy score
                            
                            # Vẽ bbox ở VỊ TRÍ MỚI
                            if best_match_name:
                                if best_match_name != "Unknown":
                                    bbox_color = (0, 255, 0)
                                    # Hiển thị tên + score
                                    label = f"{remove_accents(best_match_name)} {int(best_match_score*100)}%"
                                else:
                                    bbox_color = (255, 0, 0)
                                    label = "UNKNOWN"
                                
                                # Vẽ bbox ở vị trí HIỆN TẠI (không phải vị trí cũ)
                                cv2.rectangle(frame_rgb, (x, y), (x + bw, y + bh), bbox_color, 3)
                                cv2.putText(frame_rgb, label, (x, y - 10), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, bbox_color, 2)
                    
                    # Hiển thị message chính
                    if hasattr(self, 'last_recognition_name'):
                        if self.last_recognition_name != "Unknown":
                            msg = f"ACCESS GRANTED: {remove_accents(self.last_recognition_name)}"
                            msg_color = (0, 255, 0)
                        else:
                            msg = "UNKNOWN - Access Denied"
                            msg_color = (255, 0, 0)
                        
                        cv2.putText(frame_rgb, msg, (w//2 - 300, h//2), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, msg_color, 3)
                        cv2.putText(frame_rgb, f"Reset in {int(remaining)+1}s...", (w//2 - 150, h//2 + 60),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

                # Display
                try:
                    img = Image.fromarray(frame_rgb)
                    photo = ImageTk.PhotoImage(image=img)
                    self.video_canvas.itemconfig(self.canvas_image_id, image=photo)
                    self.video_canvas.image = photo
                except Exception:
                    pass
            
            time.sleep(0.01)

    def recognition_loop(self):
        """InsightFace Recognition - Flow: Nháy mắt → Nhận diện → Reset"""
        while self.is_running:
            if hasattr(self, 'current_frame') and self.current_frame is not None and not self.is_paused:
                try:
                    current_time = time.time()
                    
                    # === CHECK 1: Recognition đang bị pause (ESP đang xử lý hoặc chờ Unknown) ===
                    if current_time < self.recognition_paused_until:
                        remaining = self.recognition_paused_until - current_time
                        time.sleep(0.3)
                        continue
                    
                    # === STEP 1: Yêu cầu nháy mắt ===
                    if self.liveness_required and not self.liveness_verified:
                        # Chưa verify liveness → Chờ người dùng nháy mắt
                        self.recognition_results = []
                        time.sleep(0.3)
                        continue
                    
                    # === STEP 2: Đã nháy mắt → Bắt đầu nhận diện ===
                    frame_to_process = self.current_frame.copy()
                    small_frame = cv2.resize(frame_to_process, (0, 0), fx=0.5, fy=0.5)
                    results = self.recognizer.process_frame(small_frame)
                    self.recognition_results = results

                    # === STEP 3: Xử lý kết quả ===
                    recognized = False
                    for res in results:
                        if res["name"] != "Unknown":
                            recognized = True
                            
                            # Debounce: Tránh trigger nhiều lần
                            if current_time - self.last_open_time > 10:
                                print(f"✅ RECOGNIZED: {res['name']} (Score: {res['score']:.2f})")
                                
                                # Lưu TẤT CẢ kết quả để hiển thị
                                self.last_recognition_name = res['name']
                                self.saved_recognition_results = results  # Lưu tất cả
                                
                                self.trigger_access(res, frame_to_process)
                                self.last_open_time = current_time
                                
                                # PAUSE 6s để đồng bộ với ESP (đóng khóa sau 5s + 1s buffer)
                                self.recognition_paused_until = current_time + 6
                                print(f"⏸️ Pausing 6s (ESP closing door + buffer)...")
                                
                                # RESET liveness → Người tiếp theo phải nháy mắt lại
                                self.liveness_verified = False
                                self.blink_counter = 0
                                self.liveness_verified_time = 0
                                print("🔄 RESET → Yêu cầu nháy mắt cho người tiếp theo\n")
                            break  # Chỉ xử lý 1 người
                    
                    # === STEP 4: Nếu không nhận diện được ai (Unknown) ===
                    if not recognized and self.liveness_verified:
                        print("❌ Unknown face detected")
                        
                        # Lưu kết quả "Unknown" + TẤT CẢ faces
                        self.last_recognition_name = "Unknown"
                        self.saved_recognition_results = results  # Lưu tất cả
                        
                        # PAUSE 3s rồi reset
                        self.recognition_paused_until = current_time + 3
                        print(f"⏸️ Pausing 3s then reset...")
                        
                        # RESET liveness → Yêu cầu nháy mắt lại
                        self.liveness_verified = False
                        self.blink_counter = 0
                        self.liveness_verified_time = 0
                        print("🔄 RESET → Vui lòng nháy mắt lại\n")
                        
                except Exception as e:
                    print(f"❌ Recognition error: {e}")
                    import traceback
                    traceback.print_exc()
            
            time.sleep(0.5)





    def send_to_esp(self, name):
        def _send():
            try:
                stream_url = CAMERA_CONFIG.get("stream_url", "")
                if "http" in stream_url:
                    ip = stream_url.split("//")[1].split("/")[0].split(":")[0]
                    url = f"http://{ip}:81/control?var=face&val={name}"
                    
                    requests.get(url, timeout=3.0)
                    print(f"📤 Sent to ESP: {name} ({url})")
            except Exception as e:
                print(f"❌ ESP Send Error: {e}")
        threading.Thread(target=_send, daemon=True).start()

    def trigger_access(self, res, frame):
        """Log access, save snapshot, and notify backend"""
        print(f"🚀 TRIGGER ACCESS CALLED for {res['name']}")
        
        # Debug Frame
        if frame is None:
            print("❌ FRAME IS NONE!")
            return
        print(f"🖼️ Frame Shape: {frame.shape}, Dtype: {frame.dtype}")
        
        try:
            user_name = res['name']
            
            # 1. Save Snapshot
            filepath = ""
            try:
                # Hardcode path
                history_dir = r"D:\HUTECH\DACN\dataset\history"
                if not os.path.exists(history_dir):
                    os.makedirs(history_dir, exist_ok=True)
                
                # Sanitize ID (chỉ giữ số và chữ)
                raw_id = str(res.get('id', 'unknown'))
                safe_id = "".join(c for c in raw_id if c.isalnum())
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"ACCESS_{timestamp}_{safe_id}.jpg"
                filepath = os.path.join(history_dir, filename)
                
                print(f"💾 Attempting to save to: {filepath}")
                
                # Save image
                success = cv2.imwrite(filepath, frame)
                if success:
                    print(f"📸 Snapshot SAVED SUCCESSFULLY!")
                else:
                    print(f"❌ cv2.imwrite FAILED! Trying fallback...")
                    # Fallback: Lưu vào thư mục hiện tại
                    fallback_path = f"fallback_{filename}"
                    cv2.imwrite(fallback_path, frame)
                    print(f"⚠️ Saved to fallback: {os.path.abspath(fallback_path)}")
                    filepath = os.path.abspath(fallback_path)
                        
            except Exception as e:
                print(f"❌ Snapshot Exception: {e}")
                import traceback
                traceback.print_exc()
                filepath = ""

            # 2. Send to ESP & Save Log (Threaded)
            def _api_call():
                try:
                    # Send name to ESP (for OLED display)
                    name_no_accent = remove_accents(user_name)
                    stream_url = CAMERA_CONFIG.get("stream_url", "")
                    if "http" in stream_url:
                        ip = stream_url.split("//")[1].split("/")[0].split(":")[0]
                        esp_url = f"http://{ip}:81/control?var=face&val={name_no_accent}"
                        requests.get(esp_url, timeout=3.0)
                        print(f"📤 Sent to ESP: {name_no_accent}")
                    
                    # Create Log in DB
                    log_data = {
                        "user_id": res.get("id"),
                        "status": "GRANTED",
                        "similarity_score": float(res.get("score", 0.0)),
                        "snapshot_path": filepath, 
                        "note": f"Identified as {user_name}"
                    }
                    self.api.post("/access-logs/", log_data)
                    print("✅ Log saved to DB")
                    
                except Exception as e:
                    print(f"⚠️ API/ESP Error (non-critical): {e}")
            
            threading.Thread(target=_api_call, daemon=True).start()
            
        except Exception as e:
            print(f"❌ trigger_access error: {e}")

    def manual_open_door(self):
        """Mở cửa thủ công bởi Admin"""
        try:
            # 1. Lấy current frame từ stream
            if not hasattr(self, 'current_frame') or self.current_frame is None:
                messagebox.showwarning("Cảnh báo", "Không có hình ảnh từ camera!")
                return
            
            frame = self.current_frame.copy()
            current_time = time.time()
            
            # 2. Lưu snapshot (giống trigger_access)
            filepath = ""
            try:
                # Hardcode path giống trigger_access
                history_dir = r"D:\HUTECH\DACN\dataset\history"
                if not os.path.exists(history_dir):
                    os.makedirs(history_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"MANUAL_{timestamp}_admin.jpg"
                filepath = os.path.join(history_dir, filename)
                
                cv2.imwrite(filepath, frame)
                print(f"📸 Manual snapshot saved: {filepath}")
            except Exception as e:
                print(f"⚠️ Could not save snapshot: {e}")
                filepath = ""
            
            # 3. Gửi lệnh đến ESP32 (background thread)
            def _send_esp_and_log():
                try:
                    # Gửi lệnh mở cửa đến ESP (port 81) - giống send_to_esp
                    stream_url = CAMERA_CONFIG.get("stream_url", "")
                    if stream_url and "http" in stream_url:
                        ip = stream_url.split("//")[1].split("/")[0].split(":")[0]  # Extract IP only
                        esp_url = f"http://{ip}:81/control?var=face&val=ADMIN"  # Giống send_to_esp
                        requests.get(esp_url, timeout=3.0)
                        print(f"📤 Sent to ESP: ADMIN ({esp_url})")
                    
                    # Lưu log vào database
                    log_data = {
                        "user_id": None,  # Không có user_id (admin mở)
                        "status": "MANUAL",  # Status đặc biệt
                        "similarity_score": 1.0,  # Confidence = 1.0 (thủ công)
                        "snapshot_path": filepath if filepath else None,  # Giống trigger_access
                        "note": "Manual open by Admin"  # Ghi chú
                    }
                    
                    self.api.post("/access-logs", log_data)
                    print("✅ Manual access log saved to DB")
                    
                except Exception as e:
                    print(f"⚠️ ESP/Log error (non-critical): {e}")
            
            threading.Thread(target=_send_esp_and_log, daemon=True).start()
            
            # 4. Thông báo thành công
            messagebox.showinfo(
                "Thành công", 
                f"✅ Đã mở cửa thủ công!\n\n"
                f"🕒 Thời gian: {time.strftime('%H:%M:%S', time.localtime(current_time))}\n"
                f"📸 Ảnh đã lưu: {filename}"
            )
            
        except Exception as e:
            print(f"❌ Manual open error: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Lỗi", f"Không thể mở cửa: {str(e)}")

    def pause_stream(self):
        """Pause dashboard video display, but keep stream_reader running for CaptureWindow"""
        self.is_paused = True
        print("⏸️ Dashboard paused (stream_reader still running)")

    def resume_stream(self):
        """Resume dashboard video display"""
        self.is_paused = False
        print("▶️ Dashboard resumed")

    def open_user_management(self):
        # Truyền cả stream_reader VÀ dashboard reference
        # để CaptureWindow có thể pause/resume stream
        user_window = UserManagementWindow(self.root, stream_reader=self.stream_reader, dashboard=self)
        user_window.window.protocol("WM_DELETE_WINDOW", lambda: user_window.window.destroy())

    def open_history(self):
        # Pause stream - History không cần camera
        self.pause_stream()
        history_window = HistoryWindow(self.root)
        history_window.window.protocol("WM_DELETE_WINDOW", lambda: self.on_subwindow_close(history_window.window))

    def on_subwindow_close(self, window):
        window.destroy()
        self.resume_stream()

    def update_logs_loop(self):
        while self.is_running:
            try:
                # Add trailing slash to avoid 307 Redirect
                logs = self.api.get("/access-logs/?limit=15")
                print(f"📊 Loaded {len(logs)} logs")  # Debug
                self.tree_log.delete(*self.tree_log.get_children())
                for log in logs:
                    time_str = log["timestamp"].split("T")[1][:8]
                    status = log.get("status", "UNKNOWN")
                    user_name = log.get("user_name", log.get("note", "Unknown"))
                    self.tree_log.insert("", tk.END, values=(time_str, user_name, status))
            except Exception as e:
                print(f"❌ Log update error: {e}")  # Debug
            time.sleep(5)

    def logout(self):
        self.is_running = False
        self.stream_reader.stop()
        self.root.destroy()

    def __del__(self):
        self.is_running = False
        if hasattr(self, 'stream_reader'):
            self.stream_reader.stop()
