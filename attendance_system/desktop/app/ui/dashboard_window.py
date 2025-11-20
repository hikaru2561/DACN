import tkinter as tk
from tkinter import messagebox
from app.core.colors import COLORS


# Import feature modules
try:
    from app.modules.student.student_window import StudentModuleNew
    STUDENT_MODULE_AVAILABLE = True
except ImportError as e:
    STUDENT_MODULE_AVAILABLE = False
    print(f"⚠️ Student module not available: {e}")

try:
    from app.modules.attendance.recognition import AttendanceModule
    ATTENDANCE_MODULE_AVAILABLE = True
except ImportError as e:
    ATTENDANCE_MODULE_AVAILABLE = False
    print(f"⚠️ Attendance module not available: {e}")

try:
    from app.modules.subject.subject_window import SubjectManagementWindow
    SUBJECT_MODULE_AVAILABLE = True
except ImportError as e:
    SUBJECT_MODULE_AVAILABLE = False
    print(f"⚠️ Subject module not available: {e}")

try:
    from app.modules.class_.class_window import ClassManagementWindow
    CLASS_MODULE_AVAILABLE = True
except ImportError as e:
    CLASS_MODULE_AVAILABLE = False
    print(f"⚠️ Class module not available: {e}")

try:
    from app.modules.session.session_window import SessionManagementWindow
    SESSION_MODULE_AVAILABLE = True
except ImportError as e:
    SESSION_MODULE_AVAILABLE = False
    print(f"⚠️ Session module not available: {e}")

try:
    from app.modules.teacher.teacher_window import TeacherManagementWindow
    TEACHER_MODULE_AVAILABLE = True
except ImportError as e:
    TEACHER_MODULE_AVAILABLE = False
    print(f"⚠️ Teacher module not available: {e}")

try:
    from app.modules.attendance.history import AttendanceHistoryWindow
    HISTORY_MODULE_AVAILABLE = True
except ImportError as e:
    HISTORY_MODULE_AVAILABLE = False
    print(f"⚠️ Attendance history module not available: {e}")


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
            from app.main import start_app
            start_app()
    
    def open_students(self):
        """Mở module quản lý sinh viên"""
        if STUDENT_MODULE_AVAILABLE:
            StudentModuleNew(self.root, self.api)
        else:
            messagebox.showerror("Lỗi", "Module Quản lý Sinh viên chưa được cài đặt!")
    
    def open_teachers(self):
        """Mở module quản lý giảng viên"""
        if TEACHER_MODULE_AVAILABLE:
            TeacherManagementWindow(self.root, self.api)
        else:
            messagebox.showerror("Lỗi", "Module Quản lý Giảng viên chưa được cài đặt!")
    
    def open_subjects(self):
        """Mở module quản lý môn học"""
        if SUBJECT_MODULE_AVAILABLE:
            SubjectManagementWindow(self.root, self.api)
        else:
            messagebox.showerror("Lỗi", "Module Quản lý Môn học chưa được cài đặt!")
    
    def open_classes(self):
        """Mở module quản lý lớp học"""
        if CLASS_MODULE_AVAILABLE:
            ClassManagementWindow(self.root, self.api)
        else:
            messagebox.showerror("Lỗi", "Module Quản lý Lớp học chưa được cài đặt!")
    
    def open_sessions(self):
        """Mở module quản lý buổi học"""
        if SESSION_MODULE_AVAILABLE:
            SessionManagementWindow(self.root, self.api)
        else:
            messagebox.showinfo("Coming Soon", "Module Quản lý Buổi học đang phát triển...")
    
    def open_attendance(self):
        """Mở module chọn buổi học để điểm danh"""
        try:
            from app.modules.attendance.session_selection import SessionSelectionWindow
            SessionSelectionWindow(self.root)
        except ImportError as e:
            print(f"❌ Error importing attendance module: {e}")
            messagebox.showerror("Lỗi", "Không thể mở module điểm danh!")
    
    def open_cameras(self):
        """Mở module quản lý camera"""
        try:
            from app.modules.camera.camera_window import CameraManagementWindow
            CameraManagementWindow(self.root, self.api)
        except ImportError as e:
            print(f"❌ Error importing camera module: {e}")
            messagebox.showerror("Lỗi", "Không thể mở module quản lý camera!")
    
    def open_attendance_history(self):
        """Mở module lịch sử điểm danh"""
        if not HISTORY_MODULE_AVAILABLE:
            messagebox.showwarning("Chưa có", "Module Lịch sử điểm danh chưa được cài đặt!")
            return
        
        try:
            AttendanceHistoryWindow(self.root, self.api)
        except Exception as e:
            print(f"❌ Error opening attendance history: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Lỗi", f"Không thể mở module lịch sử:\n{str(e)}")
    
    def open_reports(self):
        """Mở module báo cáo"""
        try:
            from app.modules.report.report_window import ReportWindow
            ReportWindow(self.root, self.api)
        except ImportError as e:
            print(f"❌ Error importing report module: {e}")
            messagebox.showerror("Lỗi", "Không thể mở module báo cáo!")
