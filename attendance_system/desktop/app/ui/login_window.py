import tkinter as tk
from tkinter import messagebox
from app.core.colors import COLORS

class LoginWindow:
    """Màn hình đăng nhập"""
    
    def __init__(self, root, api_client, on_login_success):
        self.root = root
        self.api = api_client
        self.on_login_success = on_login_success
        
        # Configure root
        self.root.title("Đăng nhập - Hệ thống kiểm soát ra vào")
        self.root.geometry("500x550")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["white"])
        
        # Center window
        self.center_window()
        
        # Create UI
        self.create_widgets()
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Tạo giao diện đăng nhập"""
        # Header bar
        header = tk.Frame(self.root, bg=COLORS["primary"], height=150)  # Tăng từ 120 → 150
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Icon in header
        icon_label = tk.Label(
            header,
            text="🔐",
            font=("Segoe UI", 48),
            bg=COLORS["primary"],
            fg=COLORS["white"]
        )
        icon_label.pack(pady=(20, 5))
        
        title_label = tk.Label(
            header, 
            text="HỆ THỐNG KIỂM SOÁT RA VÀO",
            font=("Segoe UI", 14, "bold"),  # Giảm từ 16 → 14
            fg=COLORS["white"],
            bg=COLORS["primary"]
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header,
            text="Face Recognition Access Control System",
            font=("Segoe UI", 9),
            fg=COLORS["white"],
            bg=COLORS["primary"]
        )
        subtitle_label.pack(pady=(0, 10))
        
        # Main form
        main_frame = tk.Frame(self.root, bg=COLORS["white"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=40)
        
        # Login title
        login_title = tk.Label(
            main_frame,
            text="ĐĂNG NHẬP HỆ THỐNG",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"]
        )
        login_title.pack(pady=(0, 30))
        
        # Username
        tk.Label(
            main_frame,
            text="Tên đăng nhập",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"]
        ).pack(anchor=tk.W, pady=(0, 8))
        
        username_frame = tk.Frame(main_frame, bg=COLORS["white"], highlightthickness=1, highlightbackground=COLORS["border"])
        username_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            username_frame,
            text="👤",
            font=("Segoe UI", 14),
            bg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=(10, 5))
        
        self.username_entry = tk.Entry(
            username_frame,
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            bg=COLORS["white"],
            fg=COLORS["text"]
        )
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), pady=10)
        self.username_entry.insert(0, "admin")
        
        # Password
        tk.Label(
            main_frame,
            text="Mật khẩu",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"]
        ).pack(anchor=tk.W, pady=(0, 8))
        
        password_frame = tk.Frame(main_frame, bg=COLORS["white"], highlightthickness=1, highlightbackground=COLORS["border"])
        password_frame.pack(fill=tk.X, pady=(0, 30))
        
        tk.Label(
            password_frame,
            text="🔒",
            font=("Segoe UI", 14),
            bg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=(10, 5))
        
        self.password_entry = tk.Entry(
            password_frame,
            font=("Segoe UI", 11),
            show="●",
            relief=tk.FLAT,
            bg=COLORS["white"],
            fg=COLORS["text"]
        )
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), pady=10)
        self.password_entry.insert(0, "admin123")
        
        # Login button
        self.login_btn = tk.Button(
            main_frame,
            text="🚀 ĐĂNG NHẬP",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["primary"],
            fg=COLORS["white"],
            activebackground=COLORS["primary_dark"],
            activeforeground=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.do_login,
            pady=12
        )
        self.login_btn.pack(fill=tk.X, pady=(0, 20))
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.do_login())
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="",
            font=("Segoe UI", 9),
            fg=COLORS["danger"],
            bg=COLORS["white"]
        )
        self.status_label.pack(pady=(10, 0))
        
        # Footer
        footer = tk.Frame(self.root, bg=COLORS["light"], height=40)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        
        footer_label = tk.Label(
            footer,
            text="© 2025 HUTECH - Hệ thống kiểm soát ra vào bằng nhận diện khuôn mặt",
            font=("Segoe UI", 8),
            bg=COLORS["light"],
            fg=COLORS["text_secondary"]
        )
        footer_label.pack(pady=10)
        
        # Check API connection on startup
        self.root.after(500, self.check_api)
    
    def check_api(self):
        """Kiểm tra kết nối API"""
        if self.api.health_check():
            self.status_label.config(
                text="✅ Kết nối API thành công",
                fg=COLORS["success"]
            )
        else:
            self.status_label.config(
                text="❌ Không thể kết nối API. Vui lòng kiểm tra Backend.",
                fg=COLORS["danger"]
            )
    
    def do_login(self):
        """Xử lý đăng nhập"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.status_label.config(
                text="⚠️ Vui lòng nhập đầy đủ thông tin",
                fg=COLORS["warning"]
            )
            return
        
        # TODO: Implement real authentication via API
        # For now, use hardcoded credentials
        if username == "admin" and password == "admin123":
            # Success
            self.root.destroy()
            self.on_login_success(username)
        else:
            self.status_label.config(
                text="❌ Tên đăng nhập hoặc mật khẩu không đúng",
                fg=COLORS["danger"]
            )
