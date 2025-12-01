"""
Module Điểm danh Trực tiếp
Hiển thị camera + Thông tin sinh viên chi tiết khi điểm danh thành công
"""
import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
from datetime import datetime
from pathlib import Path
from threading import Thread
import time
import pickle
import requests
from app.core.api_client import APIClient
from app.core.config import (
    CAMERA_CONFIG, 
    FACE_RECOGNITION_CONFIG, 
    ATTENDANCE_CONFIG,
    UI_CONFIG,
    get_camera_url,
    get_embeddings_path
)

try:
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False
    print("⚠️ InsightFace not installed")

# ============================================================================
# COLOR SCHEME (From Config)
# ============================================================================

COLORS = UI_CONFIG["colors"]

# ============================================================================
# CONFIGURATION (From Config)
# ============================================================================

class AttendanceConfig:
    """Cấu hình điểm danh"""
    STREAM_URL = get_camera_url()
    
    # Dataset paths
    EMBEDDINGS_FILE = Path(get_embeddings_path())
    
    # Recognition settings
    SIMILARITY_THRESHOLD = FACE_RECOGNITION_CONFIG["similarity_threshold"]
    RECOGNITION_COOLDOWN = ATTENDANCE_CONFIG["prevent_duplicate_minutes"] * 60  # Convert to seconds


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
        Thread(target=self._update, daemon=True).start()
        return self
    
    def _update(self):
        try:
            session = requests.Session()
            response = session.get(self.stream_url, stream=True, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ HTTP Error: {response.status_code}")
                self.stopped = True
                return
            
            self.connected = True
            print("✅ Connected to ESP32-CAM")
            
            bytes_data = b''
            for chunk in response.iter_content(chunk_size=1024):
                if self.stopped:
                    break
                
                bytes_data += chunk
                a = bytes_data.find(b'\xff\xd8')
                b = bytes_data.find(b'\xff\xd9')
                
                if a != -1 and b != -1:
                    jpg = bytes_data[a:b+2]
                    bytes_data = bytes_data[b+2:]
                    
                    frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    if frame is not None:
                        self.frame = frame
        
        except Exception as e:
            print(f"❌ Stream error: {e}")
            self.stopped = True
            self.connected = False
    
    def read(self):
        return self.frame
    
    def stop(self):
        self.stopped = True


# ============================================================================
# FACE RECOGNITION ENGINE
# ============================================================================

class FaceRecognitionEngine:
    """Engine nhận diện khuôn mặt"""
    
    def __init__(self):
        if not INSIGHTFACE_AVAILABLE:
            raise ImportError("InsightFace not installed")
        
        print("🔄 Loading InsightFace model...")
        self.app = FaceAnalysis(providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        
        self.embeddings_db = {}
        self.load_embeddings()
        print(f"✅ Loaded {len(self.embeddings_db)} students")
    
    def load_embeddings(self):
        """Load embeddings từ file .pkl"""
        if not AttendanceConfig.EMBEDDINGS_FILE.exists():
            print("⚠️ No embeddings file found")
            return
        
        try:
            with open(AttendanceConfig.EMBEDDINGS_FILE, 'rb') as f:
                self.embeddings_db = pickle.load(f)
        except Exception as e:
            print(f"❌ Error loading embeddings: {e}")
    
    def recognize_face(self, face_embedding):
        """Nhận diện khuôn mặt từ embedding"""
        if not self.embeddings_db:
            return None, 0.0
        
        best_match = None
        best_similarity = 0.0
        
        for student_id, embeddings_list in self.embeddings_db.items():
            for stored_embedding in embeddings_list:
                similarity = self.cosine_similarity(face_embedding, stored_embedding)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = student_id
        
        if best_similarity >= AttendanceConfig.SIMILARITY_THRESHOLD:
            return best_match, best_similarity
        
        return None, best_similarity
    
    @staticmethod
    def cosine_similarity(emb1, emb2):
        """Tính cosine similarity"""
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))


# ============================================================================
# ATTENDANCE LIVE WINDOW
# ============================================================================

class AttendanceLiveWindow:
    """Cửa sổ điểm danh trực tiếp"""
    
    def __init__(self, parent, session_data):
        self.parent = parent
        self.session_data = session_data
        self.api = APIClient()
        
        # Recognition
        self.recognition_engine = None
        self.stream_reader = None
        self.is_running = False
        
        # Tracking
        self.last_recognition = {}  # {student_id: timestamp}
        self.attended_students = set()  # Set of student_ids
        
        # UI
        self.current_photo_label = None
        
        # Tạo window
        self.window = tk.Toplevel(parent)
        self.window.title("Hệ thống Điểm danh Khuôn mặt")
        self.window.geometry("1600x900")
        self.window.configure(bg=COLORS["light"])
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.create_ui()
        self.load_session_info()
        
        # Start recognition
        Thread(target=self.init_recognition, daemon=True).start()
    
    def create_ui(self):
        """Tạo giao diện"""
        # ============================================================
        # HEADER
        # ============================================================
        header = tk.Frame(self.window, bg=COLORS["red"], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="Hệ thống điểm danh khuôn mặt",
            font=("Segoe UI", 20, "bold"),
            bg=COLORS["red"],
            fg=COLORS["white"]
        ).pack(pady=20)
        
        # ============================================================
        # MAIN CONTAINER
        # ============================================================
        main_container = tk.Frame(self.window, bg=COLORS["light"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # ============================================================
        # LEFT PANEL: VIDEO STREAM
        # ============================================================
        left_panel = tk.Frame(main_container, bg=COLORS["white"], width=850)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Video header
        video_header = tk.Frame(left_panel, bg=COLORS["info"], height=50)
        video_header.pack(fill=tk.X)
        video_header.pack_propagate(False)
        
        tk.Label(
            video_header,
            text="Màn hình nhận diện",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["info"],
            fg=COLORS["white"]
        ).pack(pady=10)
        
        # Video frame
        self.video_frame = tk.Label(
            left_panel,
            bg=COLORS["dark"],
            text="Đang kết nối camera...",
            font=("Segoe UI", 16),
            fg=COLORS["white"]
        )
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Controls
        control_frame = tk.Frame(left_panel, bg=COLORS["white"])
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.status_label = tk.Label(
            control_frame,
            text="● Đang khởi động...",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["white"],
            fg=COLORS["warning"]
        )
        self.status_label.pack(pady=10)
        
        btn_frame = tk.Frame(control_frame, bg=COLORS["white"])
        btn_frame.pack(expand=True)
        
        tk.Button(
            btn_frame,
            text="⏸ Tạm dừng" if self.is_running else "▶ Bắt đầu",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["warning"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.toggle_recognition,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="✕ Kết thúc",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["danger"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.on_closing,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        # ============================================================
        # RIGHT PANEL: STUDENT INFO
        # ============================================================
        right_panel = tk.Frame(main_container, bg=COLORS["white"], width=700)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Info header
        info_header = tk.Frame(right_panel, bg=COLORS["success"], height=50)
        info_header.pack(fill=tk.X)
        info_header.pack_propagate(False)
        
        tk.Label(
            info_header,
            text="Điểm danh thành công",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["success"],
            fg=COLORS["white"]
        ).pack(pady=10)
        
        # ===== PHOTO =====
        photo_frame = tk.Frame(right_panel, bg=COLORS["white"])
        photo_frame.pack(pady=20)
        
        self.current_photo_label = tk.Label(
            photo_frame,
            bg=COLORS["light"],
            width=200,
            height=200,
            text="Chưa có ảnh",
            font=("Segoe UI", 12),
            relief=tk.SOLID,
            borderwidth=2
        )
        self.current_photo_label.pack()
        
        # ===== STUDENT INFO =====
        info_container = tk.Frame(right_panel, bg=COLORS["white"])
        info_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # ID Sinh viên
        self.create_info_row(info_container, "ID Sinh Viên:", "id_label")
        
        # Tên sinh viên
        self.create_info_row(info_container, "Tên Sinh Viên:", "name_label")
        
        # Thời gian
        self.create_info_row(info_container, "Thời gian:", "time_label")
        
        # ===== SESSION INFO =====
        tk.Label(
            info_container,
            text="Thông tin buổi học",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w"
        ).pack(fill=tk.X, pady=(30, 10))
        
        separator = tk.Frame(info_container, bg=COLORS["primary"], height=2)
        separator.pack(fill=tk.X, pady=5)
        
        self.create_info_row(info_container, "Lớp tin chi:", "class_label")
        self.create_info_row(info_container, "Tên môn học/ID Buổi học:", "subject_label")
        self.create_info_row(info_container, "Thời gian:", "session_time_label")
        
        # Clear button
        tk.Button(
            right_panel,
            text="🔄 Xóa thông tin",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["info"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.clear_student_info,
            padx=30,
            pady=12
        ).pack(pady=20)
    
    def create_info_row(self, parent, label_text, var_name):
        """Tạo một hàng thông tin"""
        row = tk.Frame(parent, bg=COLORS["white"])
        row.pack(fill=tk.X, pady=8)
        
        tk.Label(
            row,
            text=label_text,
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w",
            width=20
        ).pack(side=tk.LEFT)
        
        value_label = tk.Label(
            row,
            text="-",
            font=("Segoe UI", 11),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w"
        )
        value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        setattr(self, var_name, value_label)
    
    def load_session_info(self):
        """Load thông tin buổi học"""
        try:
            # Get class info
            class_info = self.api.get_class(self.session_data.get('class_id'))
            class_name = class_info.get('class_name', 'N/A') if class_info else 'N/A'
            
            # Get subject info
            subject_name = 'N/A'
            if class_info and class_info.get('subject_id'):
                subject = self.api.get_subject(class_info['subject_id'])
                if subject:
                    subject_name = subject.get('subject_name', 'N/A')
            
            # Update UI
            self.class_label.config(text=class_name)
            self.subject_label.config(
                text=f"{subject_name} / {self.session_data.get('session_id', 'N/A')}"
            )
            
            session_date = self.session_data.get('session_date', '')
            start_time = self.session_data.get('start_time', '')
            end_time = self.session_data.get('end_time', '')
            self.session_time_label.config(text=f"{session_date} {start_time} - {end_time}")
        
        except Exception as e:
            print(f"❌ Error loading session info: {e}")
    
    def init_recognition(self):
        """Khởi tạo recognition engine"""
        try:
            self.status_label.config(text="● Đang tải model...", fg=COLORS["warning"])
            self.recognition_engine = FaceRecognitionEngine()
            
            self.status_label.config(text="● Đang kết nối camera...", fg=COLORS["warning"])
            self.stream_reader = ESP32StreamReader(AttendanceConfig.STREAM_URL)
            self.stream_reader.start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.stream_reader.connected and time.time() - start_time < timeout:
                time.sleep(0.5)
            
            if self.stream_reader.connected:
                self.is_running = True
                self.status_label.config(text="● Đã sẵn sàng - Đang nhận diện...", fg=COLORS["success"])
                self.update_video()
            else:
                self.status_label.config(text="● Lỗi: Không kết nối được camera", fg=COLORS["danger"])
                messagebox.showerror("Lỗi", "Không thể kết nối camera ESP32!")
        
        except Exception as e:
            self.status_label.config(text=f"● Lỗi: {str(e)}", fg=COLORS["danger"])
            messagebox.showerror("Lỗi", f"Không thể khởi động nhận diện:\n{str(e)}")
    
    def update_video(self):
        """Cập nhật video frame"""
        if not self.is_running:
            return
        
        frame = self.stream_reader.read()
        
        if frame is not None:
            # Process frame
            display_frame = frame.copy()
            
            # Detect faces
            try:
                faces = self.recognition_engine.app.get(frame)
                
                for face in faces:
                    # Get bounding box
                    bbox = face.bbox.astype(int)
                    x1, y1, x2, y2 = bbox
                    
                    # Recognize
                    student_id, similarity = self.recognition_engine.recognize_face(face.embedding)
                    
                    if student_id:
                        # Check cooldown
                        current_time = time.time()
                        last_time = self.last_recognition.get(student_id, 0)
                        
                        if current_time - last_time > AttendanceConfig.RECOGNITION_COOLDOWN:
                            self.last_recognition[student_id] = current_time
                            
                            # Mark attendance
                            if student_id not in self.attended_students:
                                self.mark_attendance(student_id, similarity, frame[y1:y2, x1:x2])
                                self.attended_students.add(student_id)
                        
                        # Draw rectangle (green)
                        cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                        
                        # Draw text
                        text = f"ID:{student_id}"
                        cv2.putText(display_frame, text, (x1, y1-10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        
                        conf_text = f"{similarity:.2f}"
                        cv2.putText(display_frame, conf_text, (x1, y2+30),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    else:
                        # Unknown face (red)
                        cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                        cv2.putText(display_frame, "Unknown", (x1, y1-10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            
            except Exception as e:
                print(f"❌ Recognition error: {e}")
            
            # Convert to PhotoImage
            display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(display_frame)
            
            # Resize to fit
            img.thumbnail((800, 600), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.video_frame.config(image=photo, text="")
            self.video_frame.image = photo
        
        # Schedule next update
        if self.is_running:
            self.window.after(30, self.update_video)
    
    def mark_attendance(self, student_id, similarity, face_image):
        """Đánh dấu điểm danh thành công"""
        try:
            # Get student info
            student = self.api.get_student(student_id)
            
            if not student:
                print(f"❌ Student {student_id} not found")
                return
            
            # Update UI
            self.id_label.config(text=student_id)
            self.name_label.config(text=student.get('full_name', 'N/A'))
            self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
            
            # Update photo
            try:
                face_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(face_rgb)
                img = img.resize((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                self.current_photo_label.config(image=photo, text="")
                self.current_photo_label.image = photo
            except Exception as e:
                print(f"❌ Error displaying photo: {e}")
            
            # Save to database
            attendance_data = {
                "session_id": self.session_data['session_id'],
                "student_id": student_id,
                "check_in_time": datetime.now().isoformat(),
                "status": "Có mặt",
                "confidence_score": float(similarity)
            }
            
            try:
                self.api.create_attendance(attendance_data)
                print(f"✅ Attendance marked: {student_id} - {student.get('full_name')}")
                
                # Play success sound (optional)
                # winsound.Beep(1000, 200)
            
            except Exception as e:
                print(f"❌ Error saving attendance: {e}")
        
        except Exception as e:
            print(f"❌ Error marking attendance: {e}")
    
    def clear_student_info(self):
        """Xóa thông tin sinh viên hiện tại"""
        self.id_label.config(text="-")
        self.name_label.config(text="-")
        self.time_label.config(text="-")
        
        self.current_photo_label.config(image="", text="Chưa có ảnh")
        self.current_photo_label.image = None
    
    def toggle_recognition(self):
        """Bật/tắt nhận diện"""
        self.is_running = not self.is_running
        
        if self.is_running:
            self.status_label.config(text="● Đang nhận diện...", fg=COLORS["success"])
            self.update_video()
        else:
            self.status_label.config(text="● Đã tạm dừng", fg=COLORS["warning"])
    
    def on_closing(self):
        """Đóng cửa sổ"""
        confirm = messagebox.askyesno(
            "Xác nhận",
            f"Kết thúc điểm danh?\n\n"
            f"Đã điểm danh: {len(self.attended_students)} sinh viên"
        )
        
        if not confirm:
            return
        
        # Update session status
        try:
            self.api.update_session(
                self.session_data['session_id'],
                {'status': 'Completed'}
            )
        except:
            pass
        
        # Stop recognition
        self.is_running = False
        if self.stream_reader:
            self.stream_reader.stop()
        
        self.window.destroy()


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    # Test session data
    test_session = {
        'session_id': 1,
        'class_id': 1,
        'session_date': '2025-11-14',
        'start_time': '07:00:00',
        'end_time': '09:00:00'
    }
    
    app = AttendanceLiveWindow(root, test_session)
    root.mainloop()
