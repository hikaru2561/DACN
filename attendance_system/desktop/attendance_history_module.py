"""
Module Quản lý Lịch sử Điểm danh
Chức năng: Xem, tìm kiếm, thống kê và xuất báo cáo điểm danh
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import csv
from api_client import APIClient
from config import UI_CONFIG

# ============================================================================
# COLOR SCHEME
# ============================================================================

COLORS = UI_CONFIG["colors"]

# ============================================================================
# ATTENDANCE HISTORY WINDOW
# ============================================================================

class AttendanceHistoryWindow:
    """Cửa sổ quản lý lịch sử điểm danh"""
    
    def __init__(self, parent):
        self.parent = parent
        self.api = APIClient()
        self.attendance_data = []
        
        # Cache
        self.students_cache = {}
        self.classes_cache = {}
        self.sessions_cache = {}
        
        # Window
        self.window = tk.Toplevel(parent)
        self.window.title("Lịch sử Điểm danh")
        self.window.geometry("1600x900")
        self.window.configure(bg=COLORS["light"])
        self.window.transient(parent)
        
        self.load_cache_data()
        self.create_ui()
        self.load_attendance_history()
    
    def load_cache_data(self):
        """Load dữ liệu cache"""
        try:
            # Load students
            students = self.api.get_students()
            self.students_cache = {s['student_id']: s for s in students}
            
            # Load classes
            classes = self.api.get_classes()
            self.classes_cache = {c['class_id']: c for c in classes}
            
            # Load sessions
            sessions = self.api.get_sessions()
            self.sessions_cache = {s['session_id']: s for s in sessions}
        
        except Exception as e:
            print(f"❌ Error loading cache: {e}")
    
    def create_ui(self):
        """Tạo giao diện"""
        # ============================================================
        # HEADER
        # ============================================================
        header = tk.Frame(self.window, bg=COLORS["info"], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📋 LỊCH SỬ ĐIỂM DANH",
            font=("Segoe UI", 20, "bold"),
            bg=COLORS["info"],
            fg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=30, pady=20)
        
        # ============================================================
        # FILTER PANEL
        # ============================================================
        filter_frame = tk.Frame(self.window, bg=COLORS["white"])
        filter_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Row 1: Tìm kiếm theo sinh viên, lớp
        row1 = tk.Frame(filter_frame, bg=COLORS["white"])
        row1.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row1,
            text="🔍 Tìm kiếm:",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            row1,
            text="MSSV/Tên SV:",
            font=("Segoe UI", 10),
            bg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=(20, 5))
        
        self.entry_student_search = tk.Entry(
            row1,
            font=("Segoe UI", 10),
            relief=tk.SOLID,
            borderwidth=1,
            width=20
        )
        self.entry_student_search.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            row1,
            text="Lớp:",
            font=("Segoe UI", 10),
            bg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=(20, 5))
        
        self.combo_class = ttk.Combobox(
            row1,
            font=("Segoe UI", 10),
            state="readonly",
            width=25
        )
        self.combo_class.pack(side=tk.LEFT, padx=5)
        
        # Populate classes
        class_values = ["Tất cả lớp"] + [
            f"{c['class_id']} - {c['class_name']}" 
            for c in self.classes_cache.values()
        ]
        self.combo_class['values'] = class_values
        self.combo_class.current(0)
        
        # Row 2: Tìm kiếm theo thời gian
        row2 = tk.Frame(filter_frame, bg=COLORS["white"])
        row2.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row2,
            text="📅 Thời gian:",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            row2,
            text="Từ ngày:",
            font=("Segoe UI", 10),
            bg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=(20, 5))
        
        self.entry_from_date = tk.Entry(
            row2,
            font=("Segoe UI", 10),
            relief=tk.SOLID,
            borderwidth=1,
            width=12
        )
        self.entry_from_date.pack(side=tk.LEFT, padx=5)
        self.entry_from_date.insert(0, (datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y"))
        
        tk.Label(
            row2,
            text="Đến ngày:",
            font=("Segoe UI", 10),
            bg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=(20, 5))
        
        self.entry_to_date = tk.Entry(
            row2,
            font=("Segoe UI", 10),
            relief=tk.SOLID,
            borderwidth=1,
            width=12
        )
        self.entry_to_date.pack(side=tk.LEFT, padx=5)
        self.entry_to_date.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        tk.Label(
            row2,
            text="Trạng thái:",
            font=("Segoe UI", 10),
            bg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=(20, 5))
        
        self.combo_status = ttk.Combobox(
            row2,
            font=("Segoe UI", 10),
            state="readonly",
            width=15
        )
        self.combo_status.pack(side=tk.LEFT, padx=5)
        self.combo_status['values'] = [
            "Tất cả",
            "Có mặt",
            "Vắng",
            "Đi muộn",
            "Về sớm",
            "Có phép"
        ]
        self.combo_status.current(0)
        
        # Buttons
        tk.Button(
            row2,
            text="🔍 Tìm kiếm",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["btn_save"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.search_attendance,
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            row2,
            text="🔄 Làm mới",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["btn_new"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.load_attendance_history,
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            row2,
            text="📊 Xuất CSV",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["warning"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.export_to_csv,
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # ============================================================
        # STATISTICS PANEL
        # ============================================================
        stats_frame = tk.Frame(self.window, bg=COLORS["white"])
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Stats cards
        cards_frame = tk.Frame(stats_frame, bg=COLORS["white"])
        cards_frame.pack(pady=10)
        
        self.stat_total = self.create_stat_card(
            cards_frame, "Tổng bản ghi", "0", COLORS["info"]
        )
        self.stat_total.pack(side=tk.LEFT, padx=10)
        
        self.stat_present = self.create_stat_card(
            cards_frame, "Có mặt", "0", COLORS["success"]
        )
        self.stat_present.pack(side=tk.LEFT, padx=10)
        
        self.stat_absent = self.create_stat_card(
            cards_frame, "Vắng", "0", COLORS["danger"]
        )
        self.stat_absent.pack(side=tk.LEFT, padx=10)
        
        self.stat_late = self.create_stat_card(
            cards_frame, "Đi muộn", "0", COLORS["warning"]
        )
        self.stat_late.pack(side=tk.LEFT, padx=10)
        
        # ============================================================
        # TABLE
        # ============================================================
        table_frame = tk.Frame(self.window, bg=COLORS["white"])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = (
            "STT", "ID Điểm danh", "MSSV", "Tên SV", "Lớp", 
            "Môn học", "Buổi học", "Giờ vào", "Giờ ra", 
            "Trạng thái", "Ngày", "Ghi chú"
        )
        
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
        headers_config = {
            "STT": (50, tk.CENTER),
            "ID Điểm danh": (100, tk.CENTER),
            "MSSV": (120, tk.CENTER),
            "Tên SV": (180, tk.W),
            "Lớp": (120, tk.CENTER),
            "Môn học": (150, tk.W),
            "Buổi học": (150, tk.W),
            "Giờ vào": (100, tk.CENTER),
            "Giờ ra": (100, tk.CENTER),
            "Trạng thái": (120, tk.CENTER),
            "Ngày": (100, tk.CENTER),
            "Ghi chú": (200, tk.W),
        }
        
        for col, (width, anchor) in headers_config.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=anchor)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Tags for colors
        self.tree.tag_configure('evenrow', background='#F8F9FA')
        self.tree.tag_configure('oddrow', background='#FFFFFF')
        self.tree.tag_configure('present', foreground=COLORS["success"])
        self.tree.tag_configure('absent', foreground=COLORS["danger"])
        self.tree.tag_configure('late', foreground=COLORS["warning"])
        
        # Context menu
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        # ============================================================
        # BOTTOM BUTTONS
        # ============================================================
        bottom_frame = tk.Frame(self.window, bg=COLORS["light"])
        bottom_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(
            bottom_frame,
            text="✏️ Sửa bản ghi",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_edit"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.edit_attendance,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            bottom_frame,
            text="🗑️ Xóa bản ghi",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_delete"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.delete_attendance,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            bottom_frame,
            text="✕ Đóng",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_cancel"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.window.destroy,
            padx=20,
            pady=10
        ).pack(side=tk.RIGHT, padx=5)
    
    def create_stat_card(self, parent, title, value, color):
        """Tạo card thống kê"""
        card = tk.Frame(
            parent,
            bg=color,
            relief=tk.RAISED,
            borderwidth=2
        )
        
        tk.Label(
            card,
            text=title,
            font=("Segoe UI", 10),
            bg=color,
            fg=COLORS["white"]
        ).pack(pady=(10, 5), padx=20)
        
        value_label = tk.Label(
            card,
            text=value,
            font=("Segoe UI", 24, "bold"),
            bg=color,
            fg=COLORS["white"]
        )
        value_label.pack(pady=(5, 10), padx=20)
        
        # Store label reference to update later
        card.value_label = value_label
        
        return card
    
    def load_attendance_history(self):
        """Load toàn bộ lịch sử điểm danh"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Get attendance data
            self.attendance_data = self.api.get_attendance()
            
            self.populate_tree(self.attendance_data)
            self.update_statistics(self.attendance_data)
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải lịch sử:\n{str(e)}")
    
    def populate_tree(self, data):
        """Điền dữ liệu vào tree"""
        for idx, record in enumerate(data, 1):
            # Get related data
            student = self.students_cache.get(record.get('student_id'), {})
            session = self.sessions_cache.get(record.get('session_id'), {})
            
            class_data = {}
            if session:
                class_data = self.classes_cache.get(session.get('class_id'), {})
            
            # Format times
            check_in = record.get('check_in_time', '')
            if check_in:
                try:
                    check_in = datetime.fromisoformat(check_in.replace('Z', '+00:00')).strftime('%H:%M:%S')
                except:
                    pass
            
            check_out = record.get('check_out_time', '')
            if check_out:
                try:
                    check_out = datetime.fromisoformat(check_out.replace('Z', '+00:00')).strftime('%H:%M:%S')
                except:
                    pass
            
            # Format date
            created_at = record.get('created_at', '')
            if created_at:
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime('%d/%m/%Y')
                except:
                    pass
            
            # Status icon
            status = record.get('status', 'Vắng')
            status_display = {
                'Có mặt': '✅ Có mặt',
                'Vắng': '❌ Vắng',
                'Đi muộn': '⏰ Đi muộn',
                'Về sớm': '🏃 Về sớm',
                'Có phép': '📝 Có phép'
            }.get(status, status)
            
            # Tags
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            tags = [tag]
            
            if status == 'Có mặt':
                tags.append('present')
            elif status == 'Vắng':
                tags.append('absent')
            elif status == 'Đi muộn':
                tags.append('late')
            
            # Insert row
            self.tree.insert("", tk.END, values=(
                idx,
                record.get('attendance_id', ''),
                record.get('student_id', ''),
                student.get('full_name', ''),
                class_data.get('class_name', ''),
                class_data.get('subject_id', ''),
                f"Buổi {record.get('session_id', '')}",
                check_in or 'N/A',
                check_out or 'N/A',
                status_display,
                created_at,
                record.get('notes', '')
            ), tags=tuple(tags))
    
    def update_statistics(self, data):
        """Cập nhật thống kê"""
        total = len(data)
        present = sum(1 for r in data if r.get('status') == 'Có mặt')
        absent = sum(1 for r in data if r.get('status') == 'Vắng')
        late = sum(1 for r in data if r.get('status') == 'Đi muộn')
        
        self.stat_total.value_label.config(text=str(total))
        self.stat_present.value_label.config(text=str(present))
        self.stat_absent.value_label.config(text=str(absent))
        self.stat_late.value_label.config(text=str(late))
    
    def search_attendance(self):
        """Tìm kiếm điểm danh theo bộ lọc"""
        student_search = self.entry_student_search.get().strip().lower()
        class_selected = self.combo_class.get()
        status_selected = self.combo_status.get()
        
        # Parse dates
        try:
            from_date_str = self.entry_from_date.get().strip()
            to_date_str = self.entry_to_date.get().strip()
            
            from_date = datetime.strptime(from_date_str, "%d/%m/%Y")
            to_date = datetime.strptime(to_date_str, "%d/%m/%Y") + timedelta(days=1)
        except:
            messagebox.showwarning("Lỗi", "Định dạng ngày không hợp lệ! Dùng: DD/MM/YYYY")
            return
        
        # Filter data
        filtered = []
        
        for record in self.attendance_data:
            # Filter by student
            if student_search:
                student = self.students_cache.get(record.get('student_id'), {})
                if (student_search not in record.get('student_id', '').lower() and
                    student_search not in student.get('full_name', '').lower()):
                    continue
            
            # Filter by class
            if class_selected != "Tất cả lớp":
                session = self.sessions_cache.get(record.get('session_id'), {})
                class_id = str(session.get('class_id', ''))
                if not class_selected.startswith(class_id):
                    continue
            
            # Filter by status
            if status_selected != "Tất cả":
                if record.get('status') != status_selected:
                    continue
            
            # Filter by date
            created_at = record.get('created_at', '')
            if created_at:
                try:
                    record_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if not (from_date <= record_date <= to_date):
                        continue
                except:
                    continue
            
            filtered.append(record)
        
        # Clear and populate
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.populate_tree(filtered)
        self.update_statistics(filtered)
        
        messagebox.showinfo("Kết quả", f"Tìm thấy {len(filtered)} bản ghi")
    
    def export_to_csv(self):
        """Xuất dữ liệu ra file CSV"""
        if not self.tree.get_children():
            messagebox.showwarning("Không có dữ liệu", "Không có dữ liệu để xuất!")
            return
        
        # Ask for file location
        filename = filedialog.asksaveasfilename(
            title="Lưu file CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"attendance_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # Write header
                headers = [self.tree.heading(col)['text'] for col in self.tree['columns']]
                writer.writerow(headers)
                
                # Write data
                for item in self.tree.get_children():
                    values = self.tree.item(item)['values']
                    writer.writerow(values)
            
            messagebox.showinfo(
                "Thành công",
                f"Đã xuất {len(self.tree.get_children())} bản ghi ra file:\n{filename}"
            )
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất file:\n{str(e)}")
    
    def show_context_menu(self, event):
        """Hiển thị context menu khi click chuột phải"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            menu = tk.Menu(self.window, tearoff=0)
            menu.add_command(label="✏️ Sửa", command=self.edit_attendance)
            menu.add_command(label="🗑️ Xóa", command=self.delete_attendance)
            menu.add_separator()
            menu.add_command(label="📋 Copy MSSV", command=self.copy_student_id)
            
            menu.post(event.x_root, event.y_root)
    
    def copy_student_id(self):
        """Copy MSSV vào clipboard"""
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0])['values']
        student_id = values[2]  # MSSV column
        
        self.window.clipboard_clear()
        self.window.clipboard_append(student_id)
        messagebox.showinfo("Đã copy", f"MSSV: {student_id}")
    
    def edit_attendance(self):
        """Sửa bản ghi điểm danh"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn bản ghi cần sửa!")
            return
        
        values = self.tree.item(selected[0])['values']
        attendance_id = values[1]
        
        # Open edit dialog
        EditAttendanceDialog(self.window, attendance_id, self.api, self.load_attendance_history)
    
    def delete_attendance(self):
        """Xóa bản ghi điểm danh"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn bản ghi cần xóa!")
            return
        
        values = self.tree.item(selected[0])['values']
        attendance_id = values[1]
        student_name = values[3]
        
        confirm = messagebox.askyesno(
            "Xác nhận xóa",
            f"Xóa bản ghi điểm danh:\n\n"
            f"ID: {attendance_id}\n"
            f"Sinh viên: {student_name}\n\n"
            f"⚠️ Không thể hoàn tác!"
        )
        
        if not confirm:
            return
        
        try:
            # Call API to delete
            success = self.api.delete_attendance(attendance_id)
            
            if success:
                messagebox.showinfo("Thành công", "Đã xóa bản ghi!")
                self.load_attendance_history()
            else:
                messagebox.showerror("Lỗi", "Không thể xóa bản ghi.")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xóa:\n{str(e)}")


# ============================================================================
# EDIT ATTENDANCE DIALOG
# ============================================================================

class EditAttendanceDialog:
    """Dialog sửa thông tin điểm danh"""
    
    def __init__(self, parent, attendance_id, api, callback):
        self.parent = parent
        self.attendance_id = attendance_id
        self.api = api
        self.callback = callback
        
        # Window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Sửa bản ghi điểm danh")
        self.dialog.geometry("500x600")
        self.dialog.configure(bg=COLORS["light"])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.load_attendance_data()
        self.create_ui()
    
    def load_attendance_data(self):
        """Load dữ liệu điểm danh"""
        try:
            self.attendance_data = self.api.get_attendance_by_id(self.attendance_id)
        except:
            messagebox.showerror("Lỗi", "Không thể tải dữ liệu!")
            self.dialog.destroy()
    
    def create_ui(self):
        """Tạo giao diện"""
        # Header
        header = tk.Frame(self.dialog, bg=COLORS["warning"], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="✏️ Sửa bản ghi điểm danh",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["warning"],
            fg=COLORS["white"]
        ).pack(pady=15)
        
        # Form
        form = tk.Frame(self.dialog, bg=COLORS["white"])
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Attendance ID (readonly)
        tk.Label(
            form,
            text="ID Điểm danh:",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"]
        ).pack(fill=tk.X, pady=(10, 5))
        
        entry_id = tk.Entry(form, font=("Segoe UI", 11), state='readonly')
        entry_id.pack(fill=tk.X, ipady=8)
        entry_id.insert(0, str(self.attendance_id))
        
        # Status
        tk.Label(
            form,
            text="Trạng thái: *",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"]
        ).pack(fill=tk.X, pady=(15, 5))
        
        self.combo_status = ttk.Combobox(
            form,
            font=("Segoe UI", 11),
            state="readonly"
        )
        self.combo_status.pack(fill=tk.X, ipady=8)
        self.combo_status['values'] = ["Có mặt", "Vắng", "Đi muộn", "Về sớm", "Có phép"]
        
        # Set current status
        current_status = self.attendance_data.get('status', 'Vắng')
        if current_status in self.combo_status['values']:
            self.combo_status.set(current_status)
        
        # Notes
        tk.Label(
            form,
            text="Ghi chú:",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"]
        ).pack(fill=tk.X, pady=(15, 5))
        
        self.text_notes = tk.Text(
            form,
            font=("Segoe UI", 11),
            height=5,
            wrap=tk.WORD
        )
        self.text_notes.pack(fill=tk.X)
        
        # Insert current notes
        if self.attendance_data.get('notes'):
            self.text_notes.insert('1.0', self.attendance_data['notes'])
        
        # Buttons
        btn_frame = tk.Frame(form, bg=COLORS["white"])
        btn_frame.pack(fill=tk.X, pady=30)
        
        tk.Button(
            btn_frame,
            text="💾 Lưu",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_save"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.save_changes,
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=10, expand=True)
        
        tk.Button(
            btn_frame,
            text="✕ Hủy",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_cancel"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.dialog.destroy,
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=10, expand=True)
    
    def save_changes(self):
        """Lưu thay đổi"""
        status = self.combo_status.get()
        notes = self.text_notes.get('1.0', tk.END).strip()
        
        if not status:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn trạng thái!")
            return
        
        data = {
            "status": status,
            "notes": notes
        }
        
        try:
            result = self.api.update_attendance(self.attendance_id, data)
            
            if result:
                messagebox.showinfo("Thành công", "Đã cập nhật bản ghi!")
                self.dialog.destroy()
                if self.callback:
                    self.callback()
            else:
                messagebox.showerror("Lỗi", "Không thể cập nhật.")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lưu:\n{str(e)}")


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    app = AttendanceHistoryWindow(root)
    root.mainloop()
