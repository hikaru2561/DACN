"""
HỆ THỐNG QUẢN LÝ ĐIỂM DANH
Desktop Application - Main Entry Point
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from api_client import APIClient
from student_module_new import StudentModuleNew
from attendance_module import AttendanceModule

# Import các module mới
try:
    from subject_module import SubjectManagementWindow
    SUBJECT_MODULE_AVAILABLE = True
except ImportError:
    SUBJECT_MODULE_AVAILABLE = False
    print("⚠️ Subject module not available")

try:
    from class_module import ClassManagementWindow
    CLASS_MODULE_AVAILABLE = True
except ImportError:
    CLASS_MODULE_AVAILABLE = False
    print("⚠️ Class module not available")

try:
    from session_module import SessionManagementWindow
    SESSION_MODULE_AVAILABLE = True
except ImportError:
    SESSION_MODULE_AVAILABLE = False
    print("⚠️ Session module not available")

try:
    from teacher_module import TeacherManagementWindow
    TEACHER_MODULE_AVAILABLE = True
except ImportError:
    TEACHER_MODULE_AVAILABLE = False
    print("⚠️ Teacher module not available")

try:
    from attendance_history_module import AttendanceHistoryWindow
    HISTORY_MODULE_AVAILABLE = True
except ImportError:
    HISTORY_MODULE_AVAILABLE = False
    print("⚠️ Attendance history module not available")


# ============================================================================
# COLOR SCHEME
# ============================================================================

COLORS = {
    "primary": "#2196F3",      # Blue
    "primary_dark": "#1976D2", # Dark Blue
    "success": "#4CAF50",      # Green
    "success_dark": "#388E3C", # Dark Green
    "danger": "#F44336",       # Red
    "danger_dark": "#D32F2F",  # Dark Red
    "warning": "#FF9800",      # Orange
    "warning_dark": "#F57C00", # Dark Orange
    "info": "#00BCD4",         # Cyan
    "info_dark": "#0097A7",    # Dark Cyan
    "purple": "#9C27B0",       # Purple
    "purple_dark": "#7B1FA2",  # Dark Purple
    "teal": "#009688",         # Teal
    "teal_dark": "#00796B",    # Dark Teal
    "deep_orange": "#FF5722",  # Deep Orange
    "deep_orange_dark": "#E64A19", # Dark Deep Orange
    "blue_grey": "#607D8B",    # Blue Grey
    "blue_grey_dark": "#455A64", # Dark Blue Grey
    "dark": "#212121",         # Dark Gray
    "light": "#FAFAFA",        # Light Gray
    "white": "#FFFFFF",
    "text": "#212121",
    "text_secondary": "#757575",
    "border": "#E0E0E0",
}


# ============================================================================
# LOGIN WINDOW
# ============================================================================

class LoginWindow:
    """Màn hình đăng nhập"""
    
    def __init__(self, root, api_client, on_login_success):
        self.root = root
        self.api = api_client
        self.on_login_success = on_login_success
        
        # Configure root
        self.root.title("Đăng nhập - Hệ thống điểm danh")
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
        header = tk.Frame(self.root, bg=COLORS["primary"], height=120)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Icon in header
        icon_label = tk.Label(
            header,
            text="🎓",
            font=("Segoe UI", 48),
            bg=COLORS["primary"],
            fg=COLORS["white"]
        )
        icon_label.pack(pady=(20, 5))
        
        title_label = tk.Label(
            header, 
            text="HỆ THỐNG QUẢN LÝ ĐIỂM DANH",
            font=("Segoe UI", 16, "bold"),
            fg=COLORS["white"],
            bg=COLORS["primary"]
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header,
            text="Face Recognition Attendance System",
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
            text="© 2025 HUTECH - Hệ thống điểm danh tự động",
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


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class MainApplication:
    """Ứng dụng chính - Dashboard"""
    
    def __init__(self, root, api_client, username):
        self.root = root
        self.api = api_client
        self.username = username
        
        # Configure root
        self.root.title("Hệ thống quản lý điểm danh - Dashboard")
        self.root.geometry("1000x700")
        
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
        """Tạo giao diện chính"""
        # Top bar
        top_bar = tk.Frame(self.root, bg=COLORS["primary"], height=70)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)
        
        # Title with icon
        title_frame = tk.Frame(top_bar, bg=COLORS["primary"])
        title_frame.pack(side=tk.LEFT, padx=25)
        
        title = tk.Label(
            title_frame,
            text="🎓 HỆ THỐNG QUẢN LÝ ĐIỂM DANH",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["primary"],
            fg=COLORS["white"]
        )
        title.pack()
        
        subtitle = tk.Label(
            title_frame,
            text="Nhận diện khuôn mặt - Face Recognition",
            font=("Segoe UI", 9),
            bg=COLORS["primary"],
            fg=COLORS["white"]
        )
        subtitle.pack()
        
        # Right side buttons
        right_frame = tk.Frame(top_bar, bg=COLORS["primary"])
        right_frame.pack(side=tk.RIGHT, padx=20)
        
        # User info
        user_frame = tk.Frame(right_frame, bg=COLORS["primary_dark"], relief=tk.FLAT)
        user_frame.pack(side=tk.LEFT, padx=10, pady=15, ipadx=15, ipady=8)
        
        user_label = tk.Label(
            user_frame,
            text=f"👤 {self.username}",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["primary_dark"],
            fg=COLORS["white"]
        )
        user_label.pack()
        
        # Logout button
        logout_btn = tk.Button(
            right_frame,
            text="🚪 Đăng xuất",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["danger"],
            fg=COLORS["white"],
            activebackground=COLORS["danger_dark"],
            activeforeground=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.logout,
            padx=20,
            pady=10
        )
        logout_btn.pack(side=tk.LEFT)
        
        # Main content
        content_frame = tk.Frame(self.root, bg=COLORS["light"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Dashboard title
        title_container = tk.Frame(content_frame, bg=COLORS["light"])
        title_container.pack(pady=(0, 25))
        
        dashboard_title = tk.Label(
            title_container,
            text="📊 DASHBOARD",
            font=("Segoe UI", 16, "bold"),
            bg=COLORS["light"],
            fg=COLORS["text"]
        )
        dashboard_title.pack()
        
        dashboard_subtitle = tk.Label(
            title_container,
            text="Chọn chức năng bên dưới để bắt đầu",
            font=("Segoe UI", 10),
            bg=COLORS["light"],
            fg=COLORS["text_secondary"]
        )
        dashboard_subtitle.pack()
        
        # Button container (để dùng grid layout)
        button_container = tk.Frame(content_frame, bg=COLORS["light"])
        button_container.pack(fill=tk.BOTH, expand=True)
        
        # Module buttons (4x2 grid) với icons Unicode
        modules = [
            {
                "name": "Quản lý Sinh viên",
                "icon": "👨‍🎓",
                "color": COLORS["primary"],
                "hover": COLORS["primary_dark"],
                "cmd": self.open_students
            },
            {
                "name": "Quản lý Giảng viên",
                "icon": "👨‍🏫",
                "color": COLORS["success"],
                "hover": COLORS["success_dark"],
                "cmd": self.open_teachers
            },
            {
                "name": "Quản lý Môn học",
                "icon": "📚",
                "color": COLORS["warning"],
                "hover": COLORS["warning_dark"],
                "cmd": self.open_subjects
            },
            {
                "name": "Quản lý Lớp học",
                "icon": "🏫",
                "color": COLORS["info"],
                "hover": COLORS["info_dark"],
                "cmd": self.open_classes
            },
            {
                "name": "Quản lý Buổi học",
                "icon": "📅",
                "color": COLORS["purple"],
                "hover": COLORS["purple_dark"],
                "cmd": self.open_sessions
            },
            {
                "name": "Điểm danh Lớp học",
                "icon": "✅",
                "color": COLORS["success"],
                "hover": COLORS["success_dark"],
                "cmd": self.open_attendance
            },
            {
                "name": "Lịch sử Điểm danh",
                "icon": "📋",
                "color": COLORS["teal"],
                "hover": COLORS["teal_dark"],
                "cmd": self.open_attendance_history
            },
            {
                "name": "Quản lý Camera",
                "icon": "📷",
                "color": COLORS["deep_orange"],
                "hover": COLORS["deep_orange_dark"],
                "cmd": self.open_cameras
            },
            {
                "name": "Báo cáo Thống kê",
                "icon": "📊",
                "color": COLORS["blue_grey"],
                "hover": COLORS["blue_grey_dark"],
                "cmd": self.open_reports
            },
        ]
        
        # Create grid with improved styling
        self.module_buttons = []
        for i, module in enumerate(modules):
            row = i // 4
            col = i % 4
            
            # Container for each button with border effect
            btn_frame = tk.Frame(
                button_container,
                bg=COLORS["white"],
                relief=tk.RAISED,
                bd=1,
                highlightthickness=1,
                highlightbackground=COLORS["border"]
            )
            btn_frame.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
            
            # Icon label
            icon_label = tk.Label(
                btn_frame,
                text=module["icon"],
                font=("Segoe UI", 36),
                bg=COLORS["white"],
                fg=module["color"]
            )
            icon_label.pack(pady=(20, 5))
            
            # Title label
            title_label = tk.Label(
                btn_frame,
                text=module["name"],
                font=("Segoe UI", 12, "bold"),
                bg=COLORS["white"],
                fg=COLORS["text"],
                wraplength=180
            )
            title_label.pack(pady=(0, 5))
            
            # Action button
            action_btn = tk.Button(
                btn_frame,
                text="Mở",
                font=("Segoe UI", 9, "bold"),
                bg=module["color"],
                fg=COLORS["white"],
                activebackground=module["hover"],
                activeforeground=COLORS["white"],
                relief=tk.FLAT,
                cursor="hand2",
                command=module["cmd"],
                width=12,
                pady=6
            )
            action_btn.pack(pady=(5, 20))
            
            # Store reference for hover effects
            self.module_buttons.append({
                "frame": btn_frame,
                "icon": icon_label,
                "title": title_label,
                "button": action_btn,
                "color": module["color"],
                "hover": module["hover"]
            })
            
            # Bind hover events
            self._bind_hover(btn_frame, icon_label, title_label, action_btn, module["color"], module["hover"])
        
        # Configure grid weights for responsive layout
        for i in range(4):
            button_container.columnconfigure(i, weight=1, minsize=220)
        for i in range(2):
            button_container.rowconfigure(i, weight=1, minsize=200)
    
    def _bind_hover(self, frame, icon, title, button, color, hover_color):
        """Bind hover effects to module cards"""
        def on_enter(e):
            frame.config(bg=color, highlightbackground=color, highlightthickness=2)
            icon.config(bg=color, fg=COLORS["white"])
            title.config(bg=color, fg=COLORS["white"])
            button.config(bg=COLORS["white"], fg=color)
        
        def on_leave(e):
            frame.config(bg=COLORS["white"], highlightbackground=COLORS["border"], highlightthickness=1)
            icon.config(bg=COLORS["white"], fg=color)
            title.config(bg=COLORS["white"], fg=COLORS["text"])
            button.config(bg=color, fg=COLORS["white"])
        
        # Bind to all widgets in the card
        for widget in [frame, icon, title]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
    
    def logout(self):
        """Đăng xuất"""
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất?"):
            self.root.destroy()
            start_app()
    
    def open_students(self):
        """Mở module quản lý sinh viên"""
        StudentModuleNew(self.root, self.api)
    
    def open_teachers(self):
        """Mở module quản lý giảng viên"""
        if TEACHER_MODULE_AVAILABLE:
            TeacherManagementWindow(self.root)
        else:
            messagebox.showerror("Lỗi", "Module Quản lý Giảng viên chưa được cài đặt!")
    
    def open_subjects(self):
        """Mở module quản lý môn học"""
        if SUBJECT_MODULE_AVAILABLE:
            SubjectManagementWindow(self.root)
        else:
            messagebox.showerror("Lỗi", "Module Quản lý Môn học chưa được cài đặt!")
    
    def open_classes(self):
        """Mở module quản lý lớp học"""
        if CLASS_MODULE_AVAILABLE:
            ClassManagementWindow(self.root)
        else:
            messagebox.showerror("Lỗi", "Module Quản lý Lớp học chưa được cài đặt!")
    
    def open_sessions(self):
        """Mở module quản lý buổi học"""
        if SESSION_MODULE_AVAILABLE:
            SessionManagementWindow(self.root)
        else:
            messagebox.showinfo("Coming Soon", "Module Quản lý Buổi học đang phát triển...")
    
    def open_attendance(self):
        """Mở module chọn buổi học để điểm danh"""
        try:
            from attendance_session_module import SessionSelectionWindow
            SessionSelectionWindow(self.root)
        except ImportError as e:
            print(f"❌ Error importing attendance module: {e}")
            messagebox.showerror("Lỗi", "Không thể mở module điểm danh!")
    
    def open_cameras(self):
        """Mở module quản lý camera"""
        messagebox.showinfo("Coming Soon", "Module Quản lý Camera đang phát triển...")
    
    def open_attendance_history(self):
        """Mở module lịch sử điểm danh"""
        if not HISTORY_MODULE_AVAILABLE:
            messagebox.showwarning("Chưa có", "Module Lịch sử điểm danh chưa được cài đặt!")
            return
        
        try:
            AttendanceHistoryWindow(self.root)
        except Exception as e:
            print(f"❌ Error opening attendance history: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Lỗi", f"Không thể mở module lịch sử:\n{str(e)}")
    
    def open_reports(self):
        """Mở module báo cáo"""
        messagebox.showinfo("Coming Soon", "Module Báo cáo đang phát triển...")


# ============================================================================
# APPLICATION STARTER
# ============================================================================

def start_app():
    """Khởi động ứng dụng"""
    # Initialize API client
    api = APIClient()
    
    # Create root window
    root = tk.Tk()
    
    # Login callback
    def on_login_success(username):
        # Create new root for main app
        main_root = tk.Tk()
        app = MainApplication(main_root, api, username)
        main_root.mainloop()
    
    # Show login window
    LoginWindow(root, api, on_login_success)
    root.mainloop()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    try:
        start_app()
    except KeyboardInterrupt:
        print("\n👋 Tạm biệt!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
