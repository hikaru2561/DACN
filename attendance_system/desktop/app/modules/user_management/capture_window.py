import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import os
import time
import threading
import numpy as np
from pathlib import Path
from app.core.config import CAMERA_CONFIG, PATHS
from app.core.colors import COLORS
from app.core.face_recognizer import FaceRecognizer

class CaptureWindow:
    def __init__(self, parent, user_code, user_name, stream_reader=None, dashboard=None):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Chụp ảnh mẫu - {user_name}")
        self.window.geometry("1200x900")
        self.window.configure(bg=COLORS["bg_dark"])
        
        self.user_code = user_code
        self.save_dir = PATHS["raw_dir"] / user_code
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        self.is_capturing = True
        self.photos_taken = 0
        self.target_photos = 20
        self.current_frame = None
        self.last_capture_time = 0
        
        # Sử dụng stream từ Dashboard
        self.stream_reader = stream_reader
        self.dashboard = dashboard
        
        # PAUSE dashboard stream
        if self.dashboard:
            print("⏸️ CaptureWindow: Pausing dashboard...")
            self.dashboard.pause_stream()
        
        # Load FaceRecognizer để kiểm tra trùng lặp
        try:
            self.recognizer = FaceRecognizer()
            print("✅ Loaded FaceRecognizer for duplicate check")
        except Exception as e:
            print(f"⚠️ Could not load FaceRecognizer: {e}")
            self.recognizer = None
            
        self.create_ui()
        
        self.cap = None  # Không cần VideoCapture nữa
        self.thread = threading.Thread(target=self.video_loop, daemon=True)
        self.thread.start()
        
        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def create_ui(self):
        # Main Container
        main_frame = tk.Frame(self.window, bg=COLORS["bg_dark"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Video Canvas (Optimized)
        self.video_canvas = tk.Canvas(main_frame, bg="black", highlightthickness=0, width=1024, height=768)
        self.video_canvas.pack(padx=10, pady=10)
        
        # Create image item once
        self.canvas_image_id = self.video_canvas.create_image(512, 384, anchor=tk.CENTER)
        
        # Info Overlay (Quality Scores)
        self.lbl_quality = tk.Label(self.window, text="Quality: N/A", font=("Segoe UI", 12, "bold"), 
                                    bg="black", fg="white")
        self.lbl_quality.place(x=30, y=30)

        # Control Panel
        control_panel = tk.Frame(self.window, bg=COLORS["bg_light"], height=120)
        control_panel.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Status & Progress
        status_frame = tk.Frame(control_panel, bg=COLORS["bg_light"])
        status_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.lbl_status = tk.Label(status_frame, text="Đang chờ khuôn mặt...", font=("Segoe UI", 12), bg=COLORS["bg_light"])
        self.lbl_status.pack(side=tk.LEFT)
        
        self.progress = ttk.Progressbar(status_frame, length=400, mode='determinate')
        self.progress.pack(side=tk.RIGHT, padx=10)
        
        # Buttons & Options
        btn_frame = tk.Frame(control_panel, bg=COLORS["bg_light"])
        btn_frame.pack(pady=10)
        
        self.var_auto = tk.BooleanVar(value=True)
        tk.Checkbutton(btn_frame, text="Tự động chụp (Auto)", variable=self.var_auto, 
                       bg=COLORS["bg_light"], font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=20)
        
        tk.Button(btn_frame, text="📸 CHỤP THỦ CÔNG (Space)", bg=COLORS["primary"], fg="white", font=("Segoe UI", 10, "bold"),
                  command=self.manual_capture).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="Đóng", command=self.close).pack(side=tk.LEFT, padx=10)
        
        self.window.bind('<space>', lambda e: self.manual_capture())

    def video_loop(self):
        """Sử dụng stream từ Dashboard với Face Detection"""
        print(f"🎥 CaptureWindow: stream_reader = {self.stream_reader}")
        
        while self.is_capturing:
            try:
                if self.stream_reader is None:
                    print("❌ No stream_reader!")
                    time.sleep(0.1)
                    continue
                
                frame = self.stream_reader.get_frame()
                
                if frame is None:
                    time.sleep(0.01)
                    continue
                    
                self.current_frame = frame
                
                # KHÔNG dùng brightness adjustment - giữ nguyên chất lượng Dashboard
                # Sử dụng frame gốc
                
                # --- QUALITY CHECK ---
                blur_score = 0
                face_detected = False
                
                # 1. Blur Check (Laplacian)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
                
                # 2. Simple Face Detection using Haar Cascade (fast)
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                status_color = (0, 255, 0) if blur_score > 100 else (0, 0, 255)
                
                # Draw overlay (đơn giản - không hiển thị blur)
                display_frame = frame.copy()
                
                # Draw face rectangles
                if len(faces) > 0:
                    face_detected = True
                    for (x, y, w, h) in faces:
                        cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Chỉ hiển thị Photos counter
                cv2.putText(display_frame, f"Photos: {self.photos_taken}/{self.target_photos}", (20, 40),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                # --- AUTO CAPTURE (Bỏ blur check) ---
                if self.var_auto.get() and self.photos_taken < self.target_photos:
                    # Chỉ cần có face là chụp
                    if face_detected:
                        current_time = time.time()
                        if current_time - self.last_capture_time > 0.5:
                            self.save_photo(frame)
                            self.last_capture_time = current_time
                
                # Convert and display
                frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(image=img)
                
                # Update Canvas
                self.video_canvas.itemconfig(self.canvas_image_id, image=photo)
                self.video_canvas.image = photo
                
            except Exception as e:
                print(f"❌ CaptureWindow video_loop error: {e}")
                import traceback
                traceback.print_exc()
            
            time.sleep(0.01)

    def manual_capture(self):
        if self.current_frame is not None:
            self.save_photo(self.current_frame)

    def save_photo(self, frame):
        if self.photos_taken >= self.target_photos:
            return
        
        # === KIỂM TRA TRÙNG LẶP (Chỉ check ảnh đầu tiên) ===
        if self.recognizer is not None and self.photos_taken == 0:
            try:
                results = self.recognizer.process_frame(frame)
                
                if len(results) > 0:
                    for res in results:
                        if res["name"] != "Unknown":
                            existing_id = str(res.get("id", ""))
                            existing_name = res["name"]
                            similarity = res["score"]
                            
                            # Nếu face thuộc về user KHÁC
                            if existing_id != str(self.user_code):
                                messagebox.showerror(
                                    "Khuôn mặt đã tồn tại!",
                                    f"⚠️ Khuôn mặt này đã được đăng ký!\n\n"
                                    f"👤 Người dùng: {existing_name}\n"
                                    f"🆔 ID: {existing_id}\n"
                                    f"📊 Độ tương đồng: {similarity*100:.1f}%\n\n"
                                    f"Vui lòng sử dụng khuôn mặt khác hoặc xóa user cũ!"
                                )
                                self.close()
                                return
                            else:
                                print(f"✅ Face belongs to user {self.user_code} - Continue")
            except Exception as e:
                print(f"⚠️ Duplicate check error: {e}")

        timestamp = int(time.time() * 1000)
        filename = f"{self.user_code}_{timestamp}.jpg"
        save_path = self.save_dir / filename
        
        cv2.imwrite(str(save_path), frame)
        
        self.photos_taken += 1
        self.progress['value'] = (self.photos_taken / self.target_photos) * 100
        self.lbl_status.config(text=f"Đã chụp: {self.photos_taken}/{self.target_photos}")
        
        # Auto train when complete
        if self.photos_taken >= self.target_photos:
            self.auto_train()

    def auto_train(self):
        """Tự động train sau khi chụp xong"""
        self.lbl_status.config(text="🧠 Đang trích xuất đặc trưng (Append)...")
        self.progress['mode'] = 'indeterminate'
        self.progress.start()
        
        def train_thread():
            try:
                from app.core.trainer import ModelTrainer
                trainer = ModelTrainer()
                # Use train_user for incremental update
                success, msg = trainer.train_user(self.user_code)
                
                # Update UI in main thread
                self.window.after(0, lambda: self.on_train_complete(success, msg))
            except Exception as e:
                self.window.after(0, lambda: self.on_train_complete(False, str(e)))
        
        threading.Thread(target=train_thread, daemon=True).start()
    
    def on_train_complete(self, success, msg):
        """Callback khi train xong"""
        self.progress.stop()
        
        if success:
            # Reload recognizer in dashboard to update known faces immediately
            # (Dashboard không còn tham chiếu trực tiếp, sẽ tự reload khi cần)
                
            messagebox.showinfo("Thành công",  
                f"✅ Đã chụp và cập nhật model!\n\n{msg}\n\nHệ thống có thể nhận diện ngay!")
        else:
            messagebox.showerror("Lỗi", f"Chụp ảnh thành công nhưng train thất bại:\n{msg}")
        
        self.close()

    def close(self):
        self.is_capturing = False
        
        # RESUME dashboard
        if self.dashboard:
            print("▶️ CaptureWindow: Resuming dashboard...")
            self.dashboard.resume_stream()
        
        self.window.destroy()
