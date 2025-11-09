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
    "primary": "#2196F3",
    "success": "#4CAF50",
    "danger": "#F44336",
    "warning": "#FF9800",
    "info": "#00BCD4",
    "dark": "#212121",
    "light": "#FAFAFA",
    "white": "#FFFFFF",
    "text": "#212121",
    "border": "#E0E0E0",
}


# ============================================================================
# CONFIGURATION
# ============================================================================

class AttendanceConfig:
    """Cấu hình điểm danh"""
    ESP32_CAM_IP = "192.168.243.176"
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
        self.rec_model = None  # Recognition only (extract embedding)
        self.embeddings_db = {}  # {student_id: [embeddings]}
        
        if INSIGHTFACE_AVAILABLE:
            try:
                print("🔄 Loading InsightFace models...")
                
                # Full pipeline (cho real-time recognition)
                self.app = FaceAnalysis(providers=['CPUExecutionProvider'])
                self.app.prepare(ctx_id=-1, det_size=(640, 640))
                
                # Recognition model only (cho training từ ảnh đã crop)
                from insightface.model_zoo import get_model
                self.rec_model = get_model('buffalo_l', providers=['CPUExecutionProvider'])
                self.rec_model.prepare(ctx_id=-1)
                
                print("✅ Models loaded!")
            except Exception as e:
                print(f"❌ Model load error: {e}")
                import traceback
                traceback.print_exc()
                self.app = None
                self.rec_model = None
        
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
    
    def build_embeddings(self, progress_callback=None):
        """Xây dựng embeddings database từ dataset/processed/
        
        Ảnh trong dataset ĐÃ LÀ FACE CROP + CLAHE rồi!
        → Không cần detect, chỉ cần extract embedding trực tiếp
        """
        if not INSIGHTFACE_AVAILABLE or self.rec_model is None:
            print("❌ InsightFace recognition model not available")
            return {"success": False, "error": "Recognition model not available"}
        
        self.embeddings_db = {}
        processed_dir = AttendanceConfig.DATASET_PROCESSED
        
        if not processed_dir.exists():
            print(f"⚠️ Dataset directory not found: {processed_dir}")
            return {"success": False, "error": f"Dataset not found: {processed_dir}"}
        
        # Đếm số student folders
        student_folders = [d for d in processed_dir.iterdir() if d.is_dir()]
        total_students = len(student_folders)
        
        if total_students == 0:
            return {"success": False, "error": "Không tìm thấy folder sinh viên nào!"}
        
        total_images = 0
        failed_images = 0
        
        # Duyệt qua từng student folder
        for idx, student_dir in enumerate(student_folders, 1):
            student_id = student_dir.name
            embeddings = []
            
            print(f"\n🔍 Processing folder: {student_dir}")
            
            # Update progress
            if progress_callback:
                progress_callback(idx, total_students, f"Đang xử lý: {student_id}")
            
            # Đọc tất cả ảnh .jpg
            image_files = list(student_dir.glob("*.jpg"))
            
            print(f"📁 Found {len(image_files)} images for {student_id}")
            
            for img_path in image_files:
                print(f"  📷 Processing: {img_path.name}")
                try:
                    # 🔥 ĐỌC ẢNH GỐC - InsightFace sẽ tự xử lý!
                    img = cv2.imread(str(img_path))
                    if img is None:
                        print(f"    ❌ cv2.imread failed")
                        failed_images += 1
                        continue
                    
                    print(f"    🖼️ Image size: {img.shape}")
                    
                    # 🔥 ĐƯA THẲNG VÀO InsightFace - TỰ ĐỘNG detect, align, resize, extract
                    # get_feat() mong đợi list of BGR images (bất kỳ kích thước)
                    embeddings_batch = self.rec_model.get_feat([img])
                    embedding = embeddings_batch[0]
                    
                    embeddings.append(embedding)
                    total_images += 1
                    print(f"    ✅ Embedding extracted (shape: {embedding.shape}, norm: {np.linalg.norm(embedding):.2f})")
                    
                except Exception as e:
                    print(f"    ❌ Error: {e}")
                    import traceback
                    traceback.print_exc()
                    failed_images += 1
            
            if len(embeddings) > 0:
                self.embeddings_db[student_id] = embeddings
                print(f"  ✅ {student_id}: {len(embeddings)} faces saved to embeddings_db")
            else:
                print(f"  ⚠️ {student_id}: No valid faces found")
        
        # Lưu vào file
        print(f"\n💾 Saving embeddings_db with {len(self.embeddings_db)} students...")
        print(f"   Students: {list(self.embeddings_db.keys())}")
        try:
            with open(AttendanceConfig.EMBEDDINGS_FILE, 'wb') as f:
                pickle.dump(self.embeddings_db, f)
            print(f"✅ Saved embeddings to {AttendanceConfig.EMBEDDINGS_FILE}")
            
            # Verify save
            with open(AttendanceConfig.EMBEDDINGS_FILE, 'rb') as f:
                verify = pickle.load(f)
            print(f"🔍 Verify: Loaded {len(verify)} students after save")
        except Exception as e:
            print(f"❌ Save embeddings error: {e}")
            return {"success": False, "error": str(e)}
        
        return {
            "success": True,
            "total_students": len(self.embeddings_db),
            "total_images": total_images,
            "failed_images": failed_images
        }
    
    def recognize_face(self, frame):
        """
        Nhận dạng khuôn mặt trong frame
        Returns: (student_id, similarity_score) or (None, 0)
        """
        if not INSIGHTFACE_AVAILABLE or self.app is None:
            return None, 0
        
        try:
            faces = self.app.get(frame)
            if len(faces) == 0:
                return None, 0
            
            # Lấy embedding của face đầu tiên
            query_embedding = faces[0].embedding
            
            # So sánh với database
            best_match = None
            best_similarity = 0
            
            for student_id, embeddings in self.embeddings_db.items():
                for emb in embeddings:
                    # Cosine similarity
                    similarity = self.cosine_similarity(query_embedding, emb)
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = student_id
            
            # Kiểm tra threshold
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
        """
        Args:
            parent: Cửa sổ cha
            api_client: APIClient instance
            session_id: ID của buổi học (nếu có)
        """
        self.parent = parent
        self.api = api_client
        self.session_id = session_id
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("Điểm danh sinh viên")
        self.window.geometry("1100x750")
        self.window.configure(bg=COLORS["dark"])
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Data
        self.stream = None
        self.recognition_engine = FaceRecognitionEngine()
        self.attendance_records = {}  # {student_id: timestamp}
        self.last_recognition_time = {}  # {student_id: timestamp} - cooldown
        self.students_in_class = []  # Danh sách sinh viên trong lớp
        self.is_running = False
        
        # Cache tên sinh viên để không phải gọi API liên tục
        self.student_names = {}  # {student_id: full_name}
        self.load_student_names()
        
        # Create UI
        self.create_widgets()
        
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
            print(f"📋 Loaded {len(self.student_names)} student names")
        except Exception as e:
            print(f"⚠️ Cannot load student names: {e}")
            self.student_names = {}
    
    def get_student_name(self, student_id):
        """Lấy tên sinh viên từ ID
        
        Args:
            student_id: ID sinh viên (string hoặc int)
        
        Returns:
            Tên sinh viên hoặc ID nếu không tìm thấy
        """
        student_id = str(student_id)
        return self.student_names.get(student_id, student_id)
    
    def create_widgets(self):
        """Tạo giao diện"""
        # Header
        header = tk.Frame(self.window, bg=COLORS["success"], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="✅ ĐIỂM DANH SINH VIÊN",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["success"],
            fg=COLORS["white"]
        )
        title.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Stats label
        self.stats_label = tk.Label(
            header,
            text="Có mặt: 0/0",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["success"],
            fg=COLORS["white"]
        )
        self.stats_label.pack(side=tk.RIGHT, padx=20)
        
        # Main content
        main_frame = tk.Frame(self.window, bg=COLORS["light"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left: Video stream
        left_frame = tk.Frame(main_frame, bg=COLORS["dark"])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        video_header = tk.Label(
            left_frame,
            text="📹 Camera",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["dark"],
            fg=COLORS["white"]
        )
        video_header.pack(pady=10)
        
        self.video_label = tk.Label(left_frame, bg=COLORS["dark"])
        self.video_label.pack(expand=True, padx=10, pady=10)
        
        # Right: Attendance list
        right_frame = tk.Frame(main_frame, bg=COLORS["white"], width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_frame.pack_propagate(False)
        
        list_header = tk.Label(
            right_frame,
            text="📋 Danh sách điểm danh",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"]
        )
        list_header.pack(pady=10)
        
        # Treeview
        tree_frame = tk.Frame(right_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("STT", "MSSV", "Họ tên", "Trạng thái")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        self.tree.heading("STT", text="STT")
        self.tree.heading("MSSV", text="MSSV")
        self.tree.heading("Họ tên", text="Họ tên")
        self.tree.heading("Trạng thái", text="Trạng thái")
        
        self.tree.column("STT", width=40, anchor=tk.CENTER)
        self.tree.column("MSSV", width=100, anchor=tk.CENTER)
        self.tree.column("Họ tên", width=150)
        self.tree.column("Trạng thái", width=80, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Alternating row colors
        self.tree.tag_configure('present', background='#C8E6C9')
        self.tree.tag_configure('absent', background='#FFCCBC')
        self.tree.tag_configure('late', background='#FFF9C4')
        
        # Control panel
        control = tk.Frame(self.window, bg=COLORS["light"], height=80)
        control.pack(fill=tk.X, padx=20, pady=(0, 20))
        control.pack_propagate(False)
        
        self.status_label = tk.Label(
            control,
            text="⏸️ Sẵn sàng điểm danh",
            font=("Segoe UI", 11),
            bg=COLORS["light"],
            fg=COLORS["text"]
        )
        self.status_label.pack(pady=10)
        
        # Buttons
        btn_frame = tk.Frame(control, bg=COLORS["light"])
        btn_frame.pack()
        
        self.btn_start = tk.Button(
            btn_frame,
            text="▶️ Bắt đầu điểm danh",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["success"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.start_attendance,
            padx=20,
            pady=10
        )
        self.btn_start.pack(side=tk.LEFT, padx=5)
        
        self.btn_stop = tk.Button(
            btn_frame,
            text="⏸️ Dừng",
            font=("Segoe UI", 10),
            bg=COLORS["warning"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.stop_attendance,
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        btn_save = tk.Button(
            btn_frame,
            text="💾 Lưu điểm danh",
            font=("Segoe UI", 10),
            bg=COLORS["primary"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.save_attendance,
            padx=20,
            pady=10
        )
        btn_save.pack(side=tk.LEFT, padx=5)
        
        btn_rebuild = tk.Button(
            btn_frame,
            text="🔄 Rebuild DB",
            font=("Segoe UI", 10),
            bg=COLORS["info"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.rebuild_embeddings,
            padx=15,
            pady=10
        )
        btn_rebuild.pack(side=tk.LEFT, padx=5)
        
        btn_close = tk.Button(
            btn_frame,
            text="✕ Đóng",
            font=("Segoe UI", 10),
            bg=COLORS["danger"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.on_closing,
            padx=20,
            pady=10
        )
        btn_close.pack(side=tk.LEFT, padx=5)
    
    def load_session_students(self):
        """Load danh sách sinh viên trong lớp (từ session)"""
        # TODO: Gọi API để lấy danh sách sinh viên
        # Tạm thời dùng dữ liệu mẫu
        self.students_in_class = [
            {"student_id": "2280602549", "full_name": "Nguyễn Kim Quang", "status": "absent"}
        ]
        self.update_attendance_list()
    
    def update_attendance_list(self):
        """Cập nhật bảng điểm danh"""
        self.tree.delete(*self.tree.get_children())
        
        present_count = 0
        for idx, student in enumerate(self.students_in_class, 1):
            student_id = student['student_id']
            status = "absent"
            
            if student_id in self.attendance_records:
                status = "present"
                present_count += 1
            
            status_text = "✅" if status == "present" else "❌"
            
            self.tree.insert("", tk.END, values=(
                idx,
                student_id,
                student['full_name'],
                status_text
            ), tags=(status,))
        
        # Update stats
        total = len(self.students_in_class)
        self.stats_label.config(text=f"Có mặt: {present_count}/{total}")
    
    def start_attendance(self):
        """Bắt đầu điểm danh"""
        if self.is_running:
            return
        
        # Khởi động stream
        self.stream = ESP32StreamReader(AttendanceConfig.STREAM_URL)
        self.stream.start()
        
        self.is_running = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.status_label.config(text="🔴 Đang điểm danh...", fg=COLORS["success"])
        
        # Đợi kết nối
        self.window.after(100, self.check_connection)
    
    def check_connection(self):
        """Kiểm tra kết nối stream"""
        if self.stream.connected:
            self.update_video()
        elif self.stream.stopped:
            self.status_label.config(text="❌ Không thể kết nối camera!", fg=COLORS["danger"])
            messagebox.showerror("Lỗi", "Không thể kết nối ESP32-CAM!")
            self.stop_attendance()
        else:
            self.window.after(100, self.check_connection)
    
    def update_video(self):
        """Cập nhật video stream + recognition"""
        if not self.is_running or self.stream is None or self.stream.stopped:
            return
        
        frame = self.stream.read()
        if frame is None:
            self.window.after(30, self.update_video)
            return
        
        display = frame.copy()
        
        # Face recognition
        faces = self.recognition_engine.get_faces_in_frame(frame)
        
        for face in faces:
            # Get bounding box
            bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = bbox
            
            # Recognize
            student_id, similarity = self.recognition_engine.recognize_face(frame)
            
            # Kiểm tra cooldown
            current_time = time.time()
            if student_id:
                last_time = self.last_recognition_time.get(student_id, 0)
                
                # Nếu đã qua cooldown, mark attendance
                if current_time - last_time >= AttendanceConfig.RECOGNITION_COOLDOWN:
                    if student_id not in self.attendance_records:
                        self.mark_attendance(student_id)
                    self.last_recognition_time[student_id] = current_time
                
                # Draw box (green)
                cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw label - Hiển thị TÊN thay vì ID
                student_name = self.get_student_name(student_id)
                label = f"{student_name} ({similarity:.2f})"
                cv2.putText(display, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            else:
                # Unknown (red box)
                cv2.rectangle(display, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(display, "Unknown", (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Convert to PhotoImage
        frame_rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        
        # Resize
        max_width = 650
        max_height = 600
        frame_pil.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(frame_pil)
        self.video_label.config(image=photo)
        self.video_label.image = photo
        
        # Next frame
        self.window.after(30, self.update_video)
    
    def mark_attendance(self, student_id):
        """Đánh dấu điểm danh"""
        self.attendance_records[student_id] = datetime.now()
        self.update_attendance_list()
        
        # Flash status - Hiển thị TÊN
        student_name = self.get_student_name(student_id)
        self.status_label.config(
            text=f"✅ Đã điểm danh: {student_name}",
            fg=COLORS["success"]
        )
        print(f"✅ Marked: {student_name} ({student_id})")
    
    def stop_attendance(self):
        """Dừng điểm danh"""
        self.is_running = False
        if self.stream:
            self.stream.stop()
        
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.status_label.config(text="⏸️ Đã dừng", fg=COLORS["text"])
    
    def save_attendance(self):
        """Lưu điểm danh vào database"""
        if len(self.attendance_records) == 0:
            messagebox.showwarning("Cảnh báo", "Chưa có dữ liệu điểm danh!")
            return
        
        # TODO: Gọi API để lưu điểm danh
        # For now, just show summary
        present_count = len(self.attendance_records)
        total = len(self.students_in_class)
        
        messagebox.showinfo(
            "Lưu điểm danh",
            f"Đã điểm danh: {present_count}/{total} sinh viên\n\n"
            f"Có mặt: {present_count}\n"
            f"Vắng: {total - present_count}\n\n"
            "Chức năng lưu vào database sẽ được bổ sung sau."
        )
    
    def rebuild_embeddings(self):
        """Rebuild embeddings database với progress dialog"""
        confirm = messagebox.askyesno(
            "Xác nhận",
            "Rebuild embeddings database?\n\n"
            "Quá trình này sẽ:\n"
            "- Đọc lại tất cả ảnh từ dataset/processed/\n"
            "- Tạo lại embeddings cho tất cả sinh viên\n"
            "- Mất vài phút tùy số lượng ảnh\n\n"
            "Tiếp tục?"
        )
        
        if not confirm:
            return
        
        # Tạo progress window
        progress_window = tk.Toplevel(self.window)
        progress_window.title("Build Embeddings")
        progress_window.geometry("500x200")
        progress_window.configure(bg=COLORS["light"])
        progress_window.transient(self.window)
        progress_window.grab_set()
        
        # Header
        header_label = tk.Label(
            progress_window,
            text="🔄 Đang build embeddings database...",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["light"],
            fg=COLORS["text"]
        )
        header_label.pack(pady=20)
        
        # Progress label
        progress_label = tk.Label(
            progress_window,
            text="Đang khởi tạo...",
            font=("Segoe UI", 10),
            bg=COLORS["light"],
            fg=COLORS["text"]
        )
        progress_label.pack(pady=10)
        
        # Stats label
        stats_label = tk.Label(
            progress_window,
            text="",
            font=("Segoe UI", 9),
            bg=COLORS["light"],
            fg=COLORS["text"]
        )
        stats_label.pack(pady=5)
        
        progress_window.update()
        
        # Progress callback
        def update_progress(current, total, message):
            progress_label.config(text=f"{message} ({current}/{total})")
            stats_label.config(text=f"Tiến độ: {int(current/total*100)}%")
            progress_window.update()
        
        # Build embeddings
        result = self.recognition_engine.build_embeddings(progress_callback=update_progress)
        
        progress_window.destroy()
        
        if result["success"]:
            self.status_label.config(text="✅ Rebuild thành công!", fg=COLORS["success"])
            messagebox.showinfo(
                "Thành công",
                f"Đã rebuild embeddings database!\n\n"
                f"✅ Sinh viên: {result['total_students']}\n"
                f"✅ Ảnh thành công: {result['total_images']}\n"
                f"⚠️ Ảnh thất bại: {result['failed_images']}\n\n"
                f"💾 Lưu tại: {AttendanceConfig.EMBEDDINGS_FILE}"
            )
        else:
            self.status_label.config(text="❌ Rebuild thất bại!", fg=COLORS["danger"])
            messagebox.showerror(
                "Lỗi",
                f"Build embeddings thất bại!\n\n"
                f"Lỗi: {result.get('error', 'Unknown error')}"
            )
    
    def on_closing(self):
        """Đóng cửa sổ"""
        if self.is_running:
            self.stop_attendance()
        self.window.destroy()


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    from api_client import APIClient
    api = APIClient("http://localhost:8000/api")
    
    AttendanceModule(root, api)
    root.mainloop()
