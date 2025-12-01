"""
Module Chọn Buổi học để Điểm danh
Luồng: Dashboard → Chọn Buổi học → Điểm danh
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from app.core.api_client import APIClient
from app.core.config import UI_CONFIG

# ============================================================================
# COLOR SCHEME (From Config)
# ============================================================================

COLORS = UI_CONFIG["colors"]


# ============================================================================
# SESSION SELECTION WINDOW
# ============================================================================

class SessionSelectionWindow:
    """Cửa sổ chọn buổi học để điểm danh"""
    
    def __init__(self, parent):
        self.parent = parent
        self.api = APIClient()
        self.selected_session = None
        
        # Tạo window
        self.window = tk.Toplevel(parent)
        self.window.title("Chọn buổi học để điểm danh")
        self.window.geometry("1400x800")
        self.window.configure(bg=COLORS["light"])
        # self.window.transient(parent)  # Removed to enable minimize/maximize
        # self.window.grab_set()         # Removed to allow interaction with other windows if needed
        
        self.create_ui()
        self.load_today_sessions()
    
    def create_ui(self):
        """Tạo giao diện"""
        # ============================================================
        # HEADER
        # ============================================================
        header = tk.Frame(self.window, bg=COLORS["primary"], height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📋 CHỌN BUỔI HỌC ĐỂ ĐIỂM DANH",
            font=("Segoe UI", 24, "bold"),
            bg=COLORS["primary"],
            fg=COLORS["white"]
        ).pack(pady=30)
        
        # ============================================================
        # FILTER PANEL
        # ============================================================
        filter_frame = tk.Frame(self.window, bg=COLORS["white"])
        filter_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Date filter
        tk.Label(
            filter_frame,
            text="📅 Ngày học:",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=10)
        
        self.entry_date = tk.Entry(
            filter_frame,
            font=("Segoe UI", 11),
            width=15
        )
        self.entry_date.pack(side=tk.LEFT, padx=5)
        self.entry_date.insert(0, date.today().strftime("%Y-%m-%d"))
        
        tk.Button(
            filter_frame,
            text="🔍 Tìm kiếm",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["info"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.search_sessions,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            filter_frame,
            text="📅 Hôm nay",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["success"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.load_today_sessions,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            filter_frame,
            text="🔄 Tất cả",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["warning"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.load_all_sessions,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        # ============================================================
        # TABLE
        # ============================================================
        table_frame = tk.Frame(self.window, bg=COLORS["white"])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ("STT", "ID", "Lớp học", "Môn học", "Giảng viên", "Ngày", "Giờ bắt đầu", "Giờ kết thúc", "Phòng", "Trạng thái")
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            height=20
        )
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        # Headers
        for col in columns:
            self.tree.heading(col, text=col)
        
        # Widths
        self.tree.column("STT", width=50, anchor=tk.CENTER)
        self.tree.column("ID", width=60, anchor=tk.CENTER)
        self.tree.column("Lớp học", width=200)
        self.tree.column("Môn học", width=200)
        self.tree.column("Giảng viên", width=150)
        self.tree.column("Ngày", width=120, anchor=tk.CENTER)
        self.tree.column("Giờ bắt đầu", width=100, anchor=tk.CENTER)
        self.tree.column("Giờ kết thúc", width=100, anchor=tk.CENTER)
        self.tree.column("Phòng", width=80, anchor=tk.CENTER)
        self.tree.column("Trạng thái", width=120, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind events
        self.tree.bind('<Double-1>', lambda e: self.start_attendance())
        self.tree.bind('<ButtonRelease-1>', self.on_tree_select)
        
        # Tags
        self.tree.tag_configure('evenrow', background='#F8F9FA')
        self.tree.tag_configure('oddrow', background='#FFFFFF')
        self.tree.tag_configure('scheduled', foreground='#2196F3')
        self.tree.tag_configure('in_progress', foreground='#4CAF50', font=('Segoe UI', 10, 'bold'))
        self.tree.tag_configure('completed', foreground='#9E9E9E')
        self.tree.tag_configure('cancelled', foreground='#F44336')
        
        # ============================================================
        # FOOTER BUTTONS
        # ============================================================
        footer = tk.Frame(self.window, bg=COLORS["light"])
        footer.pack(fill=tk.X, padx=20, pady=20)
        
        btn_frame = tk.Frame(footer, bg=COLORS["light"])
        btn_frame.pack(expand=True)
        
        tk.Button(
            btn_frame,
            text="✅ Bắt đầu điểm danh",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["success"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.start_attendance,
            padx=40,
            pady=15
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame,
            text="✕ Đóng",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["btn_cancel"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.window.destroy,
            padx=40,
            pady=15
        ).pack(side=tk.LEFT, padx=10)
    
    def load_sessions(self, filters=None):
        """Load danh sách buổi học"""
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Get sessions
            sessions = self.api.get_sessions()
            
            # Apply filters
            if filters:
                if 'date' in filters:
                    filter_date = filters['date']
                    sessions = [s for s in sessions if s.get('session_date') == filter_date]
            
            # Sort by date and time
            sessions.sort(key=lambda s: (s.get('session_date', ''), s.get('start_time', '')))
            
            for idx, session in enumerate(sessions, 1):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                tags = [tag]
                
                # Get class info
                class_info = self.api.get_class(session.get('class_id'))
                class_name = class_info.get('class_name', 'N/A') if class_info else 'N/A'
                
                # Get subject name
                subject_name = 'N/A'
                if class_info and class_info.get('subject_id'):
                    subject = self.api.get_subject(class_info['subject_id'])
                    if subject:
                        subject_name = subject.get('subject_name', 'N/A')
                
                # Get teacher name
                teacher_name = 'N/A'
                if class_info and class_info.get('teacher_id'):
                    teacher = self.api.get_teacher(class_info['teacher_id'])
                    if teacher:
                        teacher_name = teacher.get('full_name', 'N/A')
                
                # Status
                status = session.get('status', 'Scheduled')
                status_text = {
                    'Scheduled': '📅 Đã lên lịch',
                    'In Progress': '▶️ Đang diễn ra',
                    'Completed': '✅ Hoàn thành',
                    'Cancelled': '❌ Đã hủy'
                }.get(status, status)
                
                # Add status tag
                if status == 'In Progress':
                    tags.append('in_progress')
                elif status == 'Completed':
                    tags.append('completed')
                elif status == 'Cancelled':
                    tags.append('cancelled')
                else:
                    tags.append('scheduled')
                
                self.tree.insert("", tk.END, values=(
                    idx,
                    session.get('session_id', ''),
                    class_name,
                    subject_name,
                    teacher_name,
                    session.get('session_date', ''),
                    session.get('start_time', ''),
                    session.get('end_time', ''),
                    session.get('room', ''),
                    status_text
                ), tags=tuple(tags))
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách buổi học:\n{str(e)}")
    
    def load_today_sessions(self):
        """Load buổi học hôm nay"""
        today = date.today().strftime("%Y-%m-%d")
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, today)
        self.load_sessions({'date': today})
    
    def load_all_sessions(self):
        """Load tất cả buổi học"""
        self.entry_date.delete(0, tk.END)
        self.load_sessions()
    
    def search_sessions(self):
        """Tìm kiếm buổi học theo ngày"""
        search_date = self.entry_date.get().strip()
        if search_date:
            try:
                # Validate date format
                datetime.strptime(search_date, "%Y-%m-%d")
                self.load_sessions({'date': search_date})
            except ValueError:
                messagebox.showwarning(
                    "Lỗi định dạng",
                    "Định dạng ngày không hợp lệ!\nVui lòng dùng: YYYY-MM-DD"
                )
        else:
            self.load_sessions()
    
    def on_tree_select(self, event):
        """Xử lý khi chọn buổi học"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        values = item['values']
        
        if len(values) < 2:
            return
        
        session_id = int(values[1])
        
        try:
            session = self.api.get_session(session_id)
            if session:
                self.selected_session = session
        except Exception as e:
            print(f"❌ Error loading session: {e}")
            self.selected_session = None
    
    def start_attendance(self):
        """Bắt đầu điểm danh cho buổi học đã chọn"""
        if not self.selected_session:
            messagebox.showwarning(
                "Chưa chọn buổi học",
                "Vui lòng chọn một buổi học để bắt đầu điểm danh!"
            )
            return
        
        session_id = self.selected_session['session_id']
        session_date = self.selected_session.get('session_date', '')
        
        # Check if session is in the future
        try:
            session_datetime = datetime.strptime(session_date, "%Y-%m-%d")
            if session_datetime.date() > date.today():
                messagebox.showwarning(
                    "Chưa đến giờ",
                    f"Buổi học này diễn ra vào {session_date}.\nChưa thể điểm danh!"
                )
                return
        except:
            pass
        
        # Check if session is cancelled
        if self.selected_session.get('status') == 'Cancelled':
            messagebox.showwarning(
                "Buổi học đã hủy",
                "Không thể điểm danh cho buổi học đã bị hủy!"
            )
            return
        
        # Update session status to "In Progress"
        try:
            self.api.update_session(session_id, {'status': 'In Progress'})
        except:
            pass
        
        # Close this window and open attendance window
        self.window.destroy()
        
        # Import and open attendance window
        from app.modules.attendance.live_attendance import AttendanceLiveWindow
        AttendanceLiveWindow(self.parent, self.selected_session)


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    app = SessionSelectionWindow(root)
    root.mainloop()
