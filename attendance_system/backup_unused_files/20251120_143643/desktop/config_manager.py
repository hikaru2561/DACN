"""
Config Manager - Utility để quản lý cấu hình hệ thống
Chạy script này để cập nhật các thiết lập
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config import (
    CAMERA_CONFIG,
    API_CONFIG,
    FACE_RECOGNITION_CONFIG,
    ATTENDANCE_CONFIG,
    CAPTURE_CONFIG,
    set_camera_url,
    get_camera_url
)
import json
import os

class ConfigManagerWindow:
    """Cửa sổ quản lý cấu hình"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⚙️ Quản lý Cấu hình Hệ thống")
        self.root.geometry("800x700")
        self.root.configure(bg="#F5F5F5")
        
        self.create_ui()
        self.load_config()
    
    def create_ui(self):
        """Tạo giao diện"""
        # Header
        header = tk.Frame(self.root, bg="#2196F3", height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="⚙️ CẤU HÌNH HỆ THỐNG",
            font=("Segoe UI", 18, "bold"),
            bg="#2196F3",
            fg="white"
        ).pack(pady=20)
        
        # Main container
        main = tk.Frame(self.root, bg="white")
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Scrollbar
        canvas = tk.Canvas(main, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # ===== CAMERA CONFIG =====
        self.create_section(scrollable_frame, "📷 Cấu hình Camera")
        
        self.entry_camera_url = self.create_input(
            scrollable_frame,
            "Stream URL *",
            CAMERA_CONFIG["stream_url"]
        )
        
        self.entry_camera_fps = self.create_input(
            scrollable_frame,
            "FPS",
            str(CAMERA_CONFIG["fps"])
        )
        
        self.entry_max_retries = self.create_input(
            scrollable_frame,
            "Max Retries",
            str(CAMERA_CONFIG["max_retries"])
        )
        
        # ===== API CONFIG =====
        self.create_section(scrollable_frame, "🌐 Cấu hình API")
        
        self.entry_api_url = self.create_input(
            scrollable_frame,
            "API Base URL",
            API_CONFIG["base_url"]
        )
        
        self.entry_api_timeout = self.create_input(
            scrollable_frame,
            "API Timeout (seconds)",
            str(API_CONFIG["timeout"])
        )
        
        # ===== FACE RECOGNITION CONFIG =====
        self.create_section(scrollable_frame, "👤 Cấu hình Nhận diện")
        
        self.entry_similarity = self.create_input(
            scrollable_frame,
            "Ngưỡng độ tương đồng (0.0 - 1.0)",
            str(FACE_RECOGNITION_CONFIG["similarity_threshold"])
        )
        
        self.entry_confidence = self.create_input(
            scrollable_frame,
            "Ngưỡng confidence (0.0 - 1.0)",
            str(FACE_RECOGNITION_CONFIG["confidence_threshold"])
        )
        
        self.entry_det_thresh = self.create_input(
            scrollable_frame,
            "Detection threshold",
            str(FACE_RECOGNITION_CONFIG["det_thresh"])
        )
        
        # ===== ATTENDANCE CONFIG =====
        self.create_section(scrollable_frame, "📋 Cấu hình Điểm danh")
        
        self.entry_late_minutes = self.create_input(
            scrollable_frame,
            "Phút đi muộn",
            str(ATTENDANCE_CONFIG["late_threshold_minutes"])
        )
        
        self.entry_duplicate_minutes = self.create_input(
            scrollable_frame,
            "Phút chặn điểm danh trùng",
            str(ATTENDANCE_CONFIG["prevent_duplicate_minutes"])
        )
        
        # ===== CAPTURE CONFIG =====
        self.create_section(scrollable_frame, "📸 Cấu hình Chụp ảnh")
        
        self.entry_target_photos = self.create_input(
            scrollable_frame,
            "Số ảnh cần chụp",
            str(CAPTURE_CONFIG["target_photos"])
        )
        
        self.entry_min_quality = self.create_input(
            scrollable_frame,
            "Chất lượng tối thiểu (0.0 - 1.0)",
            str(CAPTURE_CONFIG["min_quality_score"])
        )
        
        self.entry_capture_delay = self.create_input(
            scrollable_frame,
            "Delay giữa các lần chụp (ms)",
            str(CAPTURE_CONFIG["capture_delay_ms"])
        )
        
        # Buttons
        btn_frame = tk.Frame(self.root, bg="#F5F5F5")
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Button(
            btn_frame,
            text="💾 Lưu cấu hình",
            font=("Segoe UI", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.save_config,
            padx=30,
            pady=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🔄 Tải lại",
            font=("Segoe UI", 12, "bold"),
            bg="#2196F3",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.load_config,
            padx=30,
            pady=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="✕ Đóng",
            font=("Segoe UI", 12, "bold"),
            bg="#F44336",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.root.destroy,
            padx=30,
            pady=15
        ).pack(side=tk.RIGHT, padx=5)
    
    def create_section(self, parent, title):
        """Tạo section header"""
        frame = tk.Frame(parent, bg="white")
        frame.pack(fill=tk.X, pady=(20, 10))
        
        tk.Label(
            frame,
            text=title,
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#2196F3"
        ).pack(anchor="w")
        
        tk.Frame(frame, bg="#2196F3", height=2).pack(fill=tk.X, pady=5)
    
    def create_input(self, parent, label, default_value):
        """Tạo input field"""
        frame = tk.Frame(parent, bg="white")
        frame.pack(fill=tk.X, pady=8)
        
        tk.Label(
            frame,
            text=label,
            font=("Segoe UI", 10),
            bg="white",
            anchor="w"
        ).pack(anchor="w")
        
        entry = tk.Entry(
            frame,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            borderwidth=1
        )
        entry.pack(fill=tk.X, ipady=6, pady=5)
        entry.insert(0, default_value)
        
        return entry
    
    def load_config(self):
        """Tải cấu hình hiện tại"""
        self.entry_camera_url.delete(0, tk.END)
        self.entry_camera_url.insert(0, CAMERA_CONFIG["stream_url"])
        
        self.entry_camera_fps.delete(0, tk.END)
        self.entry_camera_fps.insert(0, str(CAMERA_CONFIG["fps"]))
        
        self.entry_max_retries.delete(0, tk.END)
        self.entry_max_retries.insert(0, str(CAMERA_CONFIG["max_retries"]))
        
        self.entry_api_url.delete(0, tk.END)
        self.entry_api_url.insert(0, API_CONFIG["base_url"])
        
        self.entry_api_timeout.delete(0, tk.END)
        self.entry_api_timeout.insert(0, str(API_CONFIG["timeout"]))
        
        # ... load other fields
    
    def save_config(self):
        """Lưu cấu hình"""
        try:
            # Validate and update camera URL
            new_camera_url = self.entry_camera_url.get().strip()
            if not new_camera_url.startswith("http"):
                raise ValueError("URL camera phải bắt đầu với http:// hoặc https://")
            
            # Update config file
            config_file = os.path.join(
                os.path.dirname(__file__),
                "config.py"
            )
            
            # Read current config
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update camera URL
            import re
            content = re.sub(
                r'"stream_url":\s*"[^"]*"',
                f'"stream_url": "{new_camera_url}"',
                content
            )
            
            # Update API URL
            new_api_url = self.entry_api_url.get().strip()
            content = re.sub(
                r'"base_url":\s*"[^"]*"',
                f'"base_url": "{new_api_url}"',
                content
            )
            
            # Update similarity threshold
            new_similarity = float(self.entry_similarity.get().strip())
            content = re.sub(
                r'"similarity_threshold":\s*[\d.]+',
                f'"similarity_threshold": {new_similarity}',
                content
            )
            
            # Update late threshold
            new_late = int(self.entry_late_minutes.get().strip())
            content = re.sub(
                r'"late_threshold_minutes":\s*\d+',
                f'"late_threshold_minutes": {new_late}',
                content
            )
            
            # Update target photos
            new_photos = int(self.entry_target_photos.get().strip())
            content = re.sub(
                r'"target_photos":\s*\d+',
                f'"target_photos": {new_photos}',
                content
            )
            
            # Write back
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            messagebox.showinfo(
                "Thành công",
                "✅ Đã lưu cấu hình!\n\n"
                "⚠️ Khởi động lại ứng dụng để áp dụng thay đổi."
            )
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu cấu hình:\n{str(e)}")
    
    def run(self):
        """Chạy ứng dụng"""
        self.root.mainloop()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    app = ConfigManagerWindow()
    app.run()
