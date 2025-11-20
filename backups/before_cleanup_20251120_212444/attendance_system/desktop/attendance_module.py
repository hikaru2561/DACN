"""
Attendance Module - Điểm danh sinh viên bằng nhận dạng khuôn mặt
Tích hợp InsightFace + Cosine Similarity
"""
import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
from datetime import datetime, date
from pathlib import Path
from threading import Thread
import time
import pickle
import requests

try:
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False
    print("⚠️ InsightFace not installed. Face recognition disabled.")


# ============================================================================
# COLOR SCHEME
# ============================================================================

COLORS = {
    "header": "#2C3E50", # Dark Blue
    "bg": "#F8F9FA",
    "white": "#FFFFFF",
    "text": "#2C3E50",
    "btn_start": "#27AE60", # Green
    "btn_stop": "#E74C3C",  # Red
    "btn_save": "#3498DB",  # Blue
    "btn_close": "#95A5A6", # Gray
    "success": "#27AE60",
    "warning": "#F39C12",
    "danger": "#E74C3C",
    "border": "#BDC3C7"
}


# ============================================================================
# CONFIGURATION
# ============================================================================

class AttendanceConfig:
    """Cấu hình điểm danh"""
    ESP32_CAM_IP = "192.168.1.169"
    STREAM_URL = f"http://{ESP32_CAM_IP}/stream"
    
    # Dataset paths
    DATASET_ROOT = Path(r"d:\HUTECH\DACN\dataset")
    DATASET_PROCESSED = DATASET_ROOT / "processed"
    EMBEDDINGS_FILE = DATASET_ROOT / "face_embeddings.pkl"
    
    # Recognition settings
    SIMILARITY_THRESHOLD = 0.50  # Cosine similarity threshold
    RECOGNITION_COOLDOWN = 3.0  # Giây giữa các lần điểm danh (tránh trùng)
    
    # Display settings
    ATTENDANCE_STATUS = {
        "present": "Có mặt",
        "absent": "Vắng",
        "late": "Đi muộn"
    }


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
                'User-Agent': 'DesktopApp-Attendance',
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
# FACE RECOGNITION ENGINE
# ============================================================================

class FaceRecognitionEngine:
    """Engine nhận dạng khuôn mặt"""
    
    def __init__(self):
        """Khởi tạo InsightFace model"""
        self.app = None  # Full pipeline (detection + recognition)
        self.embeddings_db = {}  # {student_id: [embeddings]}
        
        if INSIGHTFACE_AVAILABLE:
            try:
                print("🔄 Loading InsightFace models...")
                
                # Full pipeline (cho cả training và recognition)
                # app.get() tự động detect + align + extract embedding
                self.app = FaceAnalysis(providers=['CPUExecutionProvider'])
                self.app.prepare(ctx_id=-1, det_size=(640, 640))
                
                print("✅ Models loaded!")
            except Exception as e:
                print(f"❌ Model load error: {e}")
                import traceback
                traceback.print_exc()
                self.app = None
        
        # Load embeddings từ file
        self.load_embeddings()
    
    def load_embeddings(self):
        """Load embeddings từ file pickle"""
        try:
            if AttendanceConfig.EMBEDDINGS_FILE.exists():
                with open(AttendanceConfig.EMBEDDINGS_FILE, 'rb') as f:
                    self.embeddings_db = pickle.load(f)
                print(f"✅ Loaded {len(self.embeddings_db)} students from embeddings DB")
            else:
                print("⚠️ No embeddings file found. Building from dataset...")
                self.build_embeddings()
        except Exception as e:
            print(f"❌ Load embeddings error: {e}")
            self.embeddings_db = {}
    
    def add_student_embeddings(self, student_id, progress_callback=None):
        """Thêm embeddings cho MỘT sinh viên mới (không rebuild toàn bộ)"""
        if not INSIGHTFACE_AVAILABLE or self.app is None:
            return {"success": False, "message": "InsightFace không khả dụng"}
        
        student_dir = AttendanceConfig.DATASET_PROCESSED / student_id
        
        if not student_dir.exists():
            return {"success": False, "message": f"Không tìm thấy folder: {student_dir}"}
        
        # Đọc ảnh của sinh viên này
        image_files = list(student_dir.glob("*.jpg"))
        
        if len(image_files) == 0:
            return {"success": False, "message": "Không có ảnh nào trong folder!"}
        
        print(f"\n🔍 Extracting embeddings cho sinh viên: {student_id}")
        
        embeddings = []
        failed = 0
        
        for idx, img_path in enumerate(image_files, 1):
            if progress_callback:
                progress_callback(idx, len(image_files), f"Đang xử lý ảnh {idx}/{len(image_files)}")
            
            try:
                img = cv2.imread(str(img_path))
                if img is None:
                    failed += 1
                    continue
                
                faces = self.app.get(img)
                
                if len(faces) == 0:
                    failed += 1
                    continue
                
                embedding = faces[0].embedding
                embeddings.append(embedding)
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                failed += 1
        
        if len(embeddings) == 0:
            return {"success": False, "message": "Không extract được embedding nào!"}
        
        self.embeddings_db[student_id] = embeddings
        
        try:
            with open(AttendanceConfig.EMBEDDINGS_FILE, 'wb') as f:
                pickle.dump(self.embeddings_db, f)
            
            return {
                "success": True,
                "message": f"Đã trích xuất {len(embeddings)} embeddings",
                "images_processed": len(embeddings),
                "images_failed": failed
            }
            
        except Exception as e:
            return {"success": False, "message": f"Lỗi lưu file: {str(e)}"}
    
    def build_embeddings(self, progress_callback=None):
        """Xây dựng embeddings database từ dataset/processed/"""
        if not INSIGHTFACE_AVAILABLE or self.app is None:
            return {"success": False, "error": "InsightFace app not available"}
        
        self.embeddings_db = {}
        processed_dir = AttendanceConfig.DATASET_PROCESSED
        
        if not processed_dir.exists():
            return {"success": False, "error": f"Dataset not found: {processed_dir}"}
        
        student_folders = [d for d in processed_dir.iterdir() if d.is_dir()]
        total_students = len(student_folders)
        
        if total_students == 0:
            return {"success": False, "error": "Không tìm thấy folder sinh viên nào!"}
        
        total_images = 0
        failed_images = 0
        
        for idx, student_dir in enumerate(student_folders, 1):
            student_id = student_dir.name
            embeddings = []
            
            if progress_callback:
                progress_callback(idx, total_students, f"Đang xử lý: {student_id}")
            
            image_files = list(student_dir.glob("*.jpg"))
            
            for img_path in image_files:
                try:
                    img = cv2.imread(str(img_path))
                    if img is None:
                        failed_images += 1
                        continue
                    
                    faces = self.app.get(img)
                    
                    if len(faces) == 0:
                        failed_images += 1
                        continue
                    
                    face = faces[0]
                    embedding = face.embedding
                    embeddings.append(embedding)
                    total_images += 1
                    
                except Exception as e:
                    failed_images += 1
            
            if len(embeddings) > 0:
                self.embeddings_db[student_id] = embeddings
        
        try:
            with open(AttendanceConfig.EMBEDDINGS_FILE, 'wb') as f:
                pickle.dump(self.embeddings_db, f)
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        return {
            "success": True,
            "total_students": len(self.embeddings_db),
            "total_images": total_images,
            "failed_images": failed_images
        }
    
    def recognize_face(self, face_embedding):
        """Nhận dạng khuôn mặt từ embedding"""
        if not INSIGHTFACE_AVAILABLE or self.app is None:
            return None, 0
        
        try:
            best_match = None
            best_similarity = 0
            
            for student_id, embeddings in self.embeddings_db.items():
                for emb in embeddings:
                    similarity = self.cosine_similarity(face_embedding, emb)
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = student_id
            
            if best_similarity >= AttendanceConfig.SIMILARITY_THRESHOLD:
                return best_match, best_similarity
            else:
                return None, best_similarity
        
        except Exception as e:
            print(f"❌ Recognition error: {e}")
            return None, 0
    
    @staticmethod
    def cosine_similarity(a, b):
        """Tính cosine similarity giữa 2 vectors"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def get_faces_in_frame(self, frame):
        """Phát hiện tất cả khuôn mặt trong frame"""
        if not INSIGHTFACE_AVAILABLE or self.app is None:
            return []
        
        try:
            faces = self.app.get(frame)
            return faces
        except Exception as e:
            print(f"❌ Face detection error: {e}")
            return []


# ============================================================================
# ATTENDANCE MODULE WINDOW
# ============================================================================

class AttendanceModule:
    """Module điểm danh sinh viên"""
    
    def __init__(self, parent, api_client, session_id=None):
        self.parent = parent
        self.api = api_client
        self.session_id = session_id
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("Điểm danh sinh viên")
        self.window.geometry("1400x800")
        self.window.configure(bg=COLORS["bg"])
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Data
        self.stream = None
        self.recognition_engine = FaceRecognitionEngine()
        self.attendance_records = {}  # {student_id: timestamp}
        self.last_recognition_time = {}  # {student_id: timestamp} - cooldown
        self.students_in_class = []  # Danh sách sinh viên trong lớp
        self.is_running = False
        
        # Cache tên sinh viên
        self.student_names = {}  # {student_id: full_name}
        self.load_student_names()
        
        # Create UI
        self.create_ui()
        
        # Load students nếu có session_id
        if self.session_id:
            self.load_session_students()
    
    def load_student_names(self):
        """Load danh sách tên sinh viên từ API"""
        try:
            students = self.api.get_students()
            self.student_names = {
                str(s.get('student_id')): s.get('full_name', 'Unknown')
                for s in students
            }
        except Exception as e:
            print(f"⚠️ Cannot load student names: {e}")
            self.student_names = {}
    
    def get_student_name(self, student_id):
        """Lấy tên sinh viên từ ID"""
        student_id = str(student_id)
        return self.student_names.get(student_id, student_id)
    
    def create_ui(self):
        """Tạo giao diện"""
        # Header
        header = tk.Frame(self.window, bg=COLORS["header"], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="✅ ĐIỂM DANH SINH VIÊN",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["header"],
            fg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=20)
        
        # Stats label
        self.stats_label = tk.Label(
            header,
            text="Có mặt: 0/0",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["header"],
            fg=COLORS["white"]
        )
        self.stats_label.pack(side=tk.RIGHT, padx=20)
        
        # Main content
        main_container = tk.Frame(self.window, bg=COLORS["bg"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left: Video stream
        left_frame = tk.Frame(main_container, bg=COLORS["white"], relief=tk.RIDGE, borderwidth=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        video_header = tk.Label(
            left_frame,
            text="📹 Camera Stream",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"]
        )
        video_header.pack(pady=10)
        
        self.video_label = tk.Label(left_frame, bg="#000000")
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Right: Attendance list
        right_frame = tk.Frame(main_container, bg=COLORS["white"], width=400, relief=tk.RIDGE, borderwidth=1)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_frame.pack_propagate(False)
        
        list_header = tk.Label(
            right_frame,
            text="📋 Danh sách điểm danh",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"]
        )
        list_header.pack(pady=10)
        
        # Treeview
        tree_frame = tk.Frame(right_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("STT", "MSSV", "Họ tên", "Trạng thái")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.tree.heading("STT", text="STT")
        self.tree.heading("MSSV", text="MSSV")
        self.tree.heading("Họ tên", text="Họ tên")
        self.tree.heading("Trạng thái", text="Trạng thái")
        
        self.tree.column("STT", width=40, anchor=tk.CENTER)
        self.tree.column("MSSV", width=80, anchor=tk.CENTER)
        self.tree.column("Họ tên", width=150)
        self.tree.column("Trạng thái", width=80, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tags
        self.tree.tag_configure('present', foreground=COLORS["success"])
        self.tree.tag_configure('absent', foreground=COLORS["danger"])
        
        # Control panel
        control_panel = tk.Frame(self.window, bg=COLORS["white"], height=80, relief=tk.RIDGE, borderwidth=1)
        control_panel.pack(fill=tk.X, padx=20, pady=(0, 20))
        control_panel.pack_propagate(False)
        
        # Status
        self.status_label = tk.Label(
            control_panel,
            text="Sẵn sàng",
            font=("Segoe UI", 10),
            bg=COLORS["white"],
            fg=COLORS["text"]
        )
        self.status_label.pack(side=tk.TOP, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(control_panel, bg=COLORS["white"])
        btn_frame.pack(pady=5)
        
        self.btn_start = tk.Button(
            btn_frame,
            text="▶️ Bắt đầu",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["btn_start"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            command=self.start_attendance,
            width=15
        )
        self.btn_start.pack(side=tk.LEFT, padx=5)
        
        self.btn_stop = tk.Button(
            btn_frame,
            text="⏸️ Dừng",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["btn_stop"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            command=self.stop_attendance,
            width=15,
            state=tk.DISABLED
        )
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="💾 Lưu kết quả",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["btn_save"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            command=self.save_attendance,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="✕ Đóng",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["btn_close"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            command=self.on_closing,
            width=10
        ).pack(side=tk.LEFT, padx=5)
    
    def load_session_students(self):
        """Load danh sách sinh viên trong lớp"""
        # TODO: Implement API call to get students in session
        pass
    
    def start_attendance(self):
        """Bắt đầu điểm danh"""
        if self.is_running:
            return
        
        self.stream = ESP32StreamReader(AttendanceConfig.STREAM_URL)
        self.stream.start()
        
        self.is_running = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.status_label.config(text="Đang điểm danh...", fg=COLORS["success"])
        
        self.window.after(100, self.check_connection)
    
    def check_connection(self):
        """Kiểm tra kết nối"""
        if self.stream.connected:
            self.update_video()
        elif self.stream.stopped:
            self.status_label.config(text="Không thể kết nối camera!", fg=COLORS["danger"])
            messagebox.showerror("Lỗi", "Không thể kết nối ESP32-CAM!")
            self.stop_attendance()
        else:
            self.window.after(100, self.check_connection)
    
    def update_video(self):
        """Cập nhật video và nhận diện"""
        if not self.is_running or self.stream is None or self.stream.stopped:
            return
        
        frame = self.stream.read()
        if frame is None:
            self.window.after(30, self.update_video)
            return
        
        display = frame.copy()
        
        # Face Recognition
        faces = self.recognition_engine.get_faces_in_frame(frame)
        
        for face in faces:
            bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = bbox
            
            student_id, similarity = self.recognition_engine.recognize_face(face.embedding)
            
            if student_id:
                # Cooldown check
                current_time = time.time()
                last_time = self.last_recognition_time.get(student_id, 0)
                
                if current_time - last_time >= AttendanceConfig.RECOGNITION_COOLDOWN:
                    if student_id not in self.attendance_records:
                        self.mark_attendance(student_id)
                    self.last_recognition_time[student_id] = current_time
                
                # Draw
                student_name = self.get_student_name(student_id)
                cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(display, f"{student_name} ({similarity:.2f})", (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            else:
                cv2.rectangle(display, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(display, "Unknown", (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Display
        cv2image = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        
        # Resize to fit
        display_width = self.video_label.winfo_width()
        display_height = self.video_label.winfo_height()
        
        if display_width > 10 and display_height > 10:
            img = img.resize((display_width, display_height), Image.LANCZOS)
            
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)
        
        self.window.after(30, self.update_video)
    
    def mark_attendance(self, student_id):
        """Ghi nhận điểm danh"""
        self.attendance_records[student_id] = datetime.now()
        
        # Update UI
        # Tìm item trong treeview
        found = False
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            if str(values[1]) == str(student_id):
                self.tree.item(item, values=(values[0], values[1], values[2], "Có mặt"), tags=('present',))
                found = True
                break
        
        if not found:
            # Add new row if not in list
            count = len(self.tree.get_children()) + 1
            name = self.get_student_name(student_id)
            self.tree.insert("", tk.END, values=(count, student_id, name, "Có mặt"), tags=('present',))
            
        # Update stats
        total = len(self.tree.get_children())
        present = len(self.attendance_records)
        self.stats_label.config(text=f"Có mặt: {present}/{total}")
    
    def stop_attendance(self):
        """Dừng điểm danh"""
        self.is_running = False
        if self.stream:
            self.stream.stop()
        
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.status_label.config(text="Đã dừng", fg=COLORS["text"])
        self.video_label.configure(image='')
    
    def save_attendance(self):
        """Lưu kết quả điểm danh"""
        if not self.attendance_records:
            messagebox.showwarning("Thông báo", "Chưa có dữ liệu điểm danh!")
            return
            
        if messagebox.askyesno("Xác nhận", "Lưu kết quả điểm danh vào hệ thống?"):
            # TODO: Call API to save attendance
            messagebox.showinfo("Thành công", "Đã lưu kết quả điểm danh!")
    
    def on_closing(self):
        """Đóng cửa sổ"""
        self.stop_attendance()
        self.window.destroy()
    
    def rebuild_embeddings(self):
        """Rebuild embeddings DB"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn rebuild toàn bộ embeddings?\nQuá trình này có thể mất nhiều thời gian."):
            # Show progress dialog
            progress_win = tk.Toplevel(self.window)
            progress_win.title("Processing...")
            progress_win.geometry("300x150")
            
            lbl = tk.Label(progress_win, text="Đang xử lý...", pady=20)
            lbl.pack()
            
            bar = ttk.Progressbar(progress_win, length=200, mode='determinate')
            bar.pack(pady=10)
            
            def run():
                def callback(curr, total, msg):
                    bar['value'] = (curr / total) * 100
                    lbl.config(text=msg)
                    progress_win.update()
                
                result = self.recognition_engine.build_embeddings(callback)
                progress_win.destroy()
                
                if result['success']:
                    messagebox.showinfo("Thành công", f"Đã rebuild xong!\nTotal students: {result['total_students']}")
                else:
                    messagebox.showerror("Lỗi", f"Lỗi: {result.get('error')}")
            
            Thread(target=run, daemon=True).start()
