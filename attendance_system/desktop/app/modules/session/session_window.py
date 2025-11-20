"""
Module Quản lý Buổi học (Sessions)
Chức năng: CRUD đầy đủ + Quản lý lịch học
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, time
from app.core.api_client import APIClient
import calendar

# ============================================================================
# COLOR SCHEME
# ============================================================================

COLORS = {
    "form_header": "#2C3E50", # Dark Blue for Sessions
    "table_header": "#3498DB",
    "btn_save": "#2980B9",
    "btn_edit": "#F39C12",
    "btn_delete": "#C0392B",
    "btn_new": "#27AE60",
    "white": "#FFFFFF",
    "light": "#F8F9FA",
    "border": "#BDC3C7",
    "text": "#2C3E50",
    "success": "#27AE60",
    "danger": "#E74C3C",
    "btn_cancel": "#95A5A6",
    "primary": "#3498DB",
}

# ============================================================================
# SESSION MANAGEMENT WINDOW
# ============================================================================

class SessionManagementWindow:
    """Cửa sổ quản lý buổi học"""
    
    def __init__(self, parent, api_client):
        self.parent = parent
        self.api = api_client
        self.current_session = None
        
        # Cache data
        self.classes_cache = []
        
        # Tạo window
        self.window = tk.Toplevel(parent)
        self.window.title("Quản lý Buổi học")
        self.window.geometry("1600x900")
        self.window.configure(bg=COLORS["light"])
        
        # Remove transient to allow minimize/maximize
        # self.window.transient(parent)
        
        self.load_cache_data()
        self.create_ui()
        self.load_sessions()
    
    def load_cache_data(self):
        """Load dữ liệu lớp học"""
        try:
            self.classes_cache = self.api.get_classes(is_active=True)
        except Exception as e:
            print(f"❌ Error loading cache data: {e}")
    
    def create_ui(self):
        """Tạo giao diện"""
        # ============================================================
        # LEFT PANEL: FORM
        # ============================================================
        left_panel = tk.Frame(self.window, bg=COLORS["white"], width=500)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        left_panel.pack_propagate(False)
        
        # Header
        header_frame = tk.Frame(left_panel, bg=COLORS["form_header"], height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="Thông tin buổi học",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["form_header"],
            fg=COLORS["white"]
        ).pack(pady=12)
        
        # Form Container with scrollbar
        canvas = tk.Canvas(left_panel, bg=COLORS["white"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS["white"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=480) # Set width to fit
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        form_container = tk.Frame(scrollable_frame, bg=COLORS["white"])
        form_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # === LỚP HỌC ===
        tk.Label(form_container, text="Lớp học *:", font=("Segoe UI", 10), bg=COLORS["white"], anchor="w").pack(fill=tk.X, pady=(5, 2))
        self.combo_class = ttk.Combobox(form_container, font=("Segoe UI", 10), state="readonly")
        self.combo_class.pack(fill=tk.X, ipady=4)
        self.combo_class['values'] = [f"{c['class_id']} - {c['class_name']}" for c in self.classes_cache]
        
        # === NGÀY HỌC ===
        tk.Label(form_container, text="Ngày học *:", font=("Segoe UI", 10), bg=COLORS["white"], anchor="w").pack(fill=tk.X, pady=(10, 2))
        date_frame = tk.Frame(form_container, bg=COLORS["white"])
        date_frame.pack(fill=tk.X)
        
        self.combo_day = ttk.Combobox(date_frame, font=("Segoe UI", 10), state="readonly", width=5)
        self.combo_day['values'] = [str(i) for i in range(1, 32)]
        self.combo_day.pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(date_frame, text="/", bg=COLORS["white"]).pack(side=tk.LEFT)
        
        self.combo_month = ttk.Combobox(date_frame, font=("Segoe UI", 10), state="readonly", width=5)
        self.combo_month['values'] = [str(i) for i in range(1, 13)]
        self.combo_month.pack(side=tk.LEFT, padx=5)
        tk.Label(date_frame, text="/", bg=COLORS["white"]).pack(side=tk.LEFT)
        
        self.combo_year = ttk.Combobox(date_frame, font=("Segoe UI", 10), state="readonly", width=8)
        current_year = datetime.now().year
        self.combo_year['values'] = [str(y) for y in range(current_year - 1, current_year + 3)]
        self.combo_year.pack(side=tk.LEFT, padx=5)
        
        today = datetime.now()
        self.combo_day.set(str(today.day))
        self.combo_month.set(str(today.month))
        self.combo_year.set(str(today.year))
        
        # === GIỜ BẮT ĐẦU ===
        tk.Label(form_container, text="Giờ bắt đầu *:", font=("Segoe UI", 10), bg=COLORS["white"], anchor="w").pack(fill=tk.X, pady=(10, 2))
        start_frame = tk.Frame(form_container, bg=COLORS["white"])
        start_frame.pack(fill=tk.X)
        
        self.combo_start_hour = ttk.Combobox(start_frame, font=("Segoe UI", 10), state="readonly", width=5)
        self.combo_start_hour['values'] = [f"{i:02d}" for i in range(24)]
        self.combo_start_hour.pack(side=tk.LEFT, padx=(0, 5))
        self.combo_start_hour.set("07")
        tk.Label(start_frame, text=":", bg=COLORS["white"]).pack(side=tk.LEFT)
        
        self.combo_start_minute = ttk.Combobox(start_frame, font=("Segoe UI", 10), state="readonly", width=5)
        self.combo_start_minute['values'] = [f"{i:02d}" for i in range(0, 60, 5)]
        self.combo_start_minute.pack(side=tk.LEFT, padx=5)
        self.combo_start_minute.set("00")
        
        # === GIỜ KẾT THÚC ===
        tk.Label(form_container, text="Giờ kết thúc *:", font=("Segoe UI", 10), bg=COLORS["white"], anchor="w").pack(fill=tk.X, pady=(10, 2))
        end_frame = tk.Frame(form_container, bg=COLORS["white"])
        end_frame.pack(fill=tk.X)
        
        self.combo_end_hour = ttk.Combobox(end_frame, font=("Segoe UI", 10), state="readonly", width=5)
        self.combo_end_hour['values'] = [f"{i:02d}" for i in range(24)]
        self.combo_end_hour.pack(side=tk.LEFT, padx=(0, 5))
        self.combo_end_hour.set("09")
        tk.Label(end_frame, text=":", bg=COLORS["white"]).pack(side=tk.LEFT)
        
        self.combo_end_minute = ttk.Combobox(end_frame, font=("Segoe UI", 10), state="readonly", width=5)
        self.combo_end_minute['values'] = [f"{i:02d}" for i in range(0, 60, 5)]
        self.combo_end_minute.pack(side=tk.LEFT, padx=5)
        self.combo_end_minute.set("00")
        
        # === PHÒNG HỌC ===
        tk.Label(form_container, text="Phòng học:", font=("Segoe UI", 10), bg=COLORS["white"], anchor="w").pack(fill=tk.X, pady=(10, 2))
        self.entry_room = tk.Entry(form_container, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1)
        self.entry_room.pack(fill=tk.X, ipady=4)
        
        # === TRẠNG THÁI ===
        tk.Label(form_container, text="Trạng thái:", font=("Segoe UI", 10), bg=COLORS["white"], anchor="w").pack(fill=tk.X, pady=(10, 2))
        self.combo_status = ttk.Combobox(form_container, font=("Segoe UI", 10), state="readonly")
        self.combo_status['values'] = ["Scheduled", "In Progress", "Completed", "Cancelled"]
        self.combo_status.pack(fill=tk.X, ipady=4)
        self.combo_status.set("Scheduled")
        
        # === GHI CHÚ ===
        tk.Label(form_container, text="Ghi chú:", font=("Segoe UI", 10), bg=COLORS["white"], anchor="w").pack(fill=tk.X, pady=(10, 2))
        self.text_notes = tk.Text(form_container, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1, height=4)
        self.text_notes.pack(fill=tk.X)
        
        # === BUTTONS ===
        btn_frame = tk.Frame(form_container, bg=COLORS["white"])
        btn_frame.pack(fill=tk.X, pady=20)
        
        def create_btn(parent, text, color, cmd):
            return tk.Button(parent, text=text, font=("Segoe UI", 10, "bold"), bg=color, fg=COLORS["white"], 
                             relief=tk.FLAT, cursor="hand2", command=cmd, width=10, pady=5)

        center_btns = tk.Frame(btn_frame, bg=COLORS["white"])
        center_btns.pack(expand=True)
        
        create_btn(center_btns, "Lưu", COLORS["btn_save"], self.save_session).pack(side=tk.LEFT, padx=3)
        create_btn(center_btns, "Sửa", COLORS["btn_edit"], self.edit_session).pack(side=tk.LEFT, padx=3)
        create_btn(center_btns, "Xóa", COLORS["btn_delete"], self.delete_session).pack(side=tk.LEFT, padx=3)
        create_btn(center_btns, "Mới", COLORS["btn_new"], self.clear_form).pack(side=tk.LEFT, padx=3)

        # ============================================================
        # RIGHT PANEL: DANH SÁCH BUỔI HỌC
        # ============================================================
        right_panel = tk.Frame(self.window, bg=COLORS["white"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        search_header = tk.Frame(right_panel, bg=COLORS["table_header"], height=50)
        search_header.pack(fill=tk.X)
        search_header.pack_propagate(False)
        tk.Label(search_header, text="Danh sách buổi học", font=("Segoe UI", 14, "bold"), bg=COLORS["table_header"], fg=COLORS["white"]).pack(side=tk.LEFT, padx=15, pady=12)
        
        # Filter
        filter_frame = tk.Frame(right_panel, bg=COLORS["white"])
        filter_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(filter_frame, text="Lọc theo lớp:", font=("Segoe UI", 10, "bold"), bg=COLORS["white"]).pack(side=tk.LEFT, padx=(0, 10))
        self.combo_filter_class = ttk.Combobox(filter_frame, font=("Segoe UI", 10), state="readonly", width=30)
        self.combo_filter_class['values'] = ["Tất cả"] + [f"{c['class_id']} - {c['class_name']}" for c in self.classes_cache]
        self.combo_filter_class.pack(side=tk.LEFT, padx=5)
        self.combo_filter_class.set("Tất cả")
        
        tk.Button(filter_frame, text="Lọc", bg=COLORS["btn_save"], fg="white", relief=tk.FLAT, command=self.filter_sessions).pack(side=tk.LEFT, padx=5)
        tk.Button(filter_frame, text="Tất cả", bg=COLORS["btn_new"], fg="white", relief=tk.FLAT, command=self.load_sessions).pack(side=tk.LEFT, padx=5)
        
        # Table
        table_container = tk.Frame(right_panel, bg=COLORS["white"])
        table_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        tree_scroll_y = ttk.Scrollbar(table_container, orient=tk.VERTICAL)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ("STT", "ID", "Lớp học", "Ngày", "Giờ bắt đầu", "Giờ kết thúc", "Phòng", "Trạng thái")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set, height=20)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        for col in columns:
            self.tree.heading(col, text=col)
            
        self.tree.column("STT", width=40, anchor=tk.CENTER)
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Lớp học", width=200)
        self.tree.column("Ngày", width=100, anchor=tk.CENTER)
        self.tree.column("Giờ bắt đầu", width=80, anchor=tk.CENTER)
        self.tree.column("Giờ kết thúc", width=80, anchor=tk.CENTER)
        self.tree.column("Phòng", width=80, anchor=tk.CENTER)
        self.tree.column("Trạng thái", width=100, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<ButtonRelease-1>', self.on_tree_select)
        self.tree.tag_configure('evenrow', background='#F8F9FA')
        self.tree.tag_configure('oddrow', background='#FFFFFF')
        self.tree.tag_configure('completed', foreground='#27AE60')
        self.tree.tag_configure('cancelled', foreground='#E74C3C')

    def load_sessions(self):
        """Load danh sách buổi học"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            sessions = self.api.get_sessions()
            for idx, session in enumerate(sessions, 1):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                tags = [tag]
                
                class_name = str(session.get('class_id', ''))
                for c in self.classes_cache:
                    if c['class_id'] == session.get('class_id'):
                        class_name = c['class_name']
                        break
                
                session_date = session.get('session_date', '')
                if session_date:
                    try:
                        session_date = datetime.fromisoformat(session_date.replace('Z', '+00:00')).strftime('%d/%m/%Y')
                    except: pass
                
                status = session.get('status', 'Scheduled')
                if status == 'Completed': tags.append('completed')
                elif status == 'Cancelled': tags.append('cancelled')
                
                status_display = {
                    'Scheduled': 'Đã lên lịch',
                    'In Progress': 'Đang học',
                    'Completed': 'Hoàn thành',
                    'Cancelled': 'Đã hủy'
                }.get(status, status)
                
                self.tree.insert("", tk.END, values=(
                    idx,
                    session.get('session_id', ''),
                    class_name,
                    session_date,
                    session.get('start_time', ''),
                    session.get('end_time', ''),
                    session.get('room', ''),
                    status_display
                ), tags=tuple(tags))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách buổi học:\n{str(e)}")

    def filter_sessions(self):
        """Lọc buổi học theo lớp"""
        filter_value = self.combo_filter_class.get()
        if filter_value == "Tất cả":
            self.load_sessions()
            return
        
        class_id = int(filter_value.split(' - ')[0])
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            sessions = self.api.get_sessions(class_id=class_id)
            for idx, session in enumerate(sessions, 1):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                tags = [tag]
                
                class_name = str(session.get('class_id', ''))
                for c in self.classes_cache:
                    if c['class_id'] == session.get('class_id'):
                        class_name = c['class_name']
                        break
                
                session_date = session.get('session_date', '')
                if session_date:
                    try:
                        session_date = datetime.fromisoformat(session_date.replace('Z', '+00:00')).strftime('%d/%m/%Y')
                    except: pass
                
                status = session.get('status', 'Scheduled')
                if status == 'Completed': tags.append('completed')
                elif status == 'Cancelled': tags.append('cancelled')
                
                status_display = {
                    'Scheduled': 'Đã lên lịch',
                    'In Progress': 'Đang học',
                    'Completed': 'Hoàn thành',
                    'Cancelled': 'Đã hủy'
                }.get(status, status)
                
                self.tree.insert("", tk.END, values=(
                    idx,
                    session.get('session_id', ''),
                    class_name,
                    session_date,
                    session.get('start_time', ''),
                    session.get('end_time', ''),
                    session.get('room', ''),
                    status_display
                ), tags=tuple(tags))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lọc:\n{str(e)}")

    def on_tree_select(self, event):
        """Xử lý khi chọn buổi học từ table"""
        selected = self.tree.selection()
        if not selected: return
        
        item = self.tree.item(selected[0])
        values = item['values']
        if len(values) < 2: return
        
        session_id = int(values[1])
        try:
            session = self.api.get_session(session_id)
            if session:
                self.current_session = session
                self.populate_form(session)
        except Exception as e:
            print(f"❌ Error loading session: {e}")

    def populate_form(self, session):
        """Điền thông tin buổi học vào form"""
        self.clear_form_fields_only()
        try:
            class_id = session.get('class_id')
            for val in self.combo_class['values']:
                if val.startswith(str(class_id)):
                    self.combo_class.set(val)
                    break
            
            session_date = session.get('session_date')
            if session_date:
                try:
                    dt = datetime.fromisoformat(session_date.replace('Z', '+00:00'))
                    self.combo_day.set(str(dt.day))
                    self.combo_month.set(str(dt.month))
                    self.combo_year.set(str(dt.year))
                except: pass
            
            start_time = session.get('start_time')
            if start_time:
                parts = start_time.split(':')
                if len(parts) >= 2:
                    self.combo_start_hour.set(parts[0])
                    self.combo_start_minute.set(parts[1])
            
            end_time = session.get('end_time')
            if end_time:
                parts = end_time.split(':')
                if len(parts) >= 2:
                    self.combo_end_hour.set(parts[0])
                    self.combo_end_minute.set(parts[1])
            
            self.entry_room.insert(0, str(session.get('room', '')))
            self.combo_status.set(session.get('status', 'Scheduled'))
            
            notes = session.get('notes', '')
            if notes:
                self.text_notes.insert('1.0', notes)
        except Exception as e:
            print(f"❌ Error in populate_form: {e}")

    def clear_form_fields_only(self):
        """Xóa form"""
        self.combo_class.set('')
        today = datetime.now()
        self.combo_day.set(str(today.day))
        self.combo_month.set(str(today.month))
        self.combo_year.set(str(today.year))
        self.combo_start_hour.set("07")
        self.combo_start_minute.set("00")
        self.combo_end_hour.set("09")
        self.combo_end_minute.set("00")
        self.entry_room.delete(0, tk.END)
        self.combo_status.set("Scheduled")
        self.text_notes.delete('1.0', tk.END)

    def clear_form(self):
        """Làm mới form"""
        self.clear_form_fields_only()
        self.current_session = None
        self.tree.selection_remove(*self.tree.selection())

    def validate_form(self):
        """Validate form"""
        if not self.combo_class.get():
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn lớp học!")
            return False
        try:
            day = int(self.combo_day.get())
            month = int(self.combo_month.get())
            year = int(self.combo_year.get())
            date(year, month, day)
        except:
            messagebox.showwarning("Lỗi", "Ngày không hợp lệ!")
            return False
        try:
            start_hour = int(self.combo_start_hour.get())
            start_minute = int(self.combo_start_minute.get())
            end_hour = int(self.combo_end_hour.get())
            end_minute = int(self.combo_end_minute.get())
            start_time_obj = time(start_hour, start_minute)
            end_time_obj = time(end_hour, end_minute)
            if end_time_obj <= start_time_obj:
                messagebox.showwarning("Lỗi", "Giờ kết thúc phải sau giờ bắt đầu!")
                return False
        except:
            messagebox.showwarning("Lỗi", "Thời gian không hợp lệ!")
            return False
        return True

    def save_session(self):
        """Lưu buổi học mới"""
        if not self.validate_form(): return
        
        class_id = int(self.combo_class.get().split(' - ')[0])
        session_date = f"{self.combo_year.get()}-{self.combo_month.get().zfill(2)}-{self.combo_day.get().zfill(2)}"
        start_time = f"{self.combo_start_hour.get()}:{self.combo_start_minute.get()}:00"
        end_time = f"{self.combo_end_hour.get()}:{self.combo_end_minute.get()}:00"
        
        data = {
            "class_id": class_id,
            "session_date": session_date,
            "start_time": start_time,
            "end_time": end_time,
            "room": self.entry_room.get().strip(),
            "status": self.combo_status.get(),
            "notes": self.text_notes.get('1.0', tk.END).strip()
        }
        
        try:
            if self.api.create_session(data):
                messagebox.showinfo("Thành công", "Đã thêm buổi học!")
                self.clear_form()
                self.load_sessions()
            else:
                messagebox.showerror("Lỗi", "Không thể thêm buổi học.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lưu:\n{str(e)}")

    def edit_session(self):
        """Cập nhật buổi học"""
        if not self.current_session:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn buổi học để sửa!")
            return
        if not self.validate_form(): return
        
        class_id = int(self.combo_class.get().split(' - ')[0])
        session_date = f"{self.combo_year.get()}-{self.combo_month.get().zfill(2)}-{self.combo_day.get().zfill(2)}"
        start_time = f"{self.combo_start_hour.get()}:{self.combo_start_minute.get()}:00"
        end_time = f"{self.combo_end_hour.get()}:{self.combo_end_minute.get()}:00"
        
        data = {
            "class_id": class_id,
            "session_date": session_date,
            "start_time": start_time,
            "end_time": end_time,
            "room": self.entry_room.get().strip(),
            "status": self.combo_status.get(),
            "notes": self.text_notes.get('1.0', tk.END).strip()
        }
        
        try:
            if self.api.update_session(self.current_session['session_id'], data):
                messagebox.showinfo("Thành công", "Cập nhật thành công!")
                self.clear_form()
                self.load_sessions()
            else:
                messagebox.showerror("Lỗi", "Cập nhật thất bại.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi cập nhật:\n{str(e)}")

    def delete_session(self):
        """Xóa buổi học"""
        if not self.current_session:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn buổi học để xóa!")
            return
            
        sid = self.current_session['session_id']
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa buổi học {sid}?"):
            try:
                if self.api.delete_session(sid):
                    messagebox.showinfo("Thành công", "Đã xóa buổi học!")
                    self.clear_form()
                    self.load_sessions()
                else:
                    messagebox.showerror("Lỗi", "Xóa thất bại.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa:\n{str(e)}")
