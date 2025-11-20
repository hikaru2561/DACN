"""
Module Quản lý Giảng viên (Teachers)
Chức năng: CRUD đầy đủ cho giảng viên
"""
import tkinter as tk
from tkinter import ttk, messagebox
from api_client import APIClient
import re

# ============================================================================
# COLOR SCHEME
# ============================================================================

COLORS = {
    "form_header": "#FF6666",
    "table_header": "#4A90E2",
    "btn_save": "#5DADE2",
    "btn_edit": "#F39C12",
    "btn_delete": "#EC7063",
    "btn_new": "#52BE80",
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
# TEACHER MANAGEMENT WINDOW
# ============================================================================

class TeacherManagementWindow:
    """Cửa sổ quản lý giảng viên"""
    
    def __init__(self, parent, api_client):
        self.parent = parent
        self.api = api_client
        self.current_teacher = None
        
        # Tạo window
        self.window = tk.Toplevel(parent)
        self.window.title("Quản lý Giảng viên")
        self.window.geometry("1400x800")
        self.window.configure(bg=COLORS["light"])
        
        # Remove transient to allow minimize/maximize
        # self.window.transient(parent) 
        
        self.create_ui()
        self.load_teachers()
    
    def create_ui(self):
        """Tạo giao diện"""
        # ============================================================
        # LEFT PANEL: FORM NHẬP LIỆU
        # ============================================================
        left_panel = tk.Frame(self.window, bg=COLORS["white"], width=450)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        left_panel.pack_propagate(False)
        
        # Header
        header_frame = tk.Frame(left_panel, bg=COLORS["form_header"], height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="Thông tin giảng viên",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["form_header"],
            fg=COLORS["white"]
        ).pack(pady=12)
        
        # Form Container
        form_container = tk.Frame(left_panel, bg=COLORS["white"])
        form_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # --- Helper function to create labeled entry ---
        def create_entry(parent, label_text):
            frame = tk.Frame(parent, bg=COLORS["white"])
            frame.pack(fill=tk.X, pady=5)
            
            lbl = tk.Label(frame, text=label_text, font=("Segoe UI", 10), bg=COLORS["white"], width=12, anchor="w")
            lbl.pack(side=tk.LEFT)
            
            entry = tk.Entry(frame, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            return entry

        # === Fields ===
        self.entry_teacher_id = create_entry(form_container, "Mã GV *:")
        self.entry_full_name = create_entry(form_container, "Họ tên *:")
        self.entry_email = create_entry(form_container, "Email *:")
        self.entry_phone = create_entry(form_container, "Điện thoại:")
        self.entry_department = create_entry(form_container, "Khoa/Bộ môn:")
        
        # === Trạng thái ===
        status_frame = tk.Frame(form_container, bg=COLORS["white"])
        status_frame.pack(fill=tk.X, pady=10)
        tk.Label(status_frame, text="Trạng thái:", font=("Segoe UI", 10), bg=COLORS["white"], width=12, anchor="w").pack(side=tk.LEFT)
        
        self.var_active = tk.BooleanVar(value=True)
        tk.Checkbutton(
            status_frame,
            text="Đang hoạt động",
            variable=self.var_active,
            font=("Segoe UI", 10),
            bg=COLORS["white"]
        ).pack(side=tk.LEFT)
        
        # === BUTTONS ===
        btn_frame = tk.Frame(form_container, bg=COLORS["white"])
        btn_frame.pack(fill=tk.X, pady=20)
        
        def create_btn(parent, text, color, cmd):
            return tk.Button(parent, text=text, font=("Segoe UI", 10, "bold"), bg=color, fg=COLORS["white"], 
                             relief=tk.FLAT, cursor="hand2", command=cmd, width=10, pady=5)

        center_btns = tk.Frame(btn_frame, bg=COLORS["white"])
        center_btns.pack(expand=True)
        
        create_btn(center_btns, "Lưu", COLORS["btn_save"], self.save_teacher).pack(side=tk.LEFT, padx=5)
        create_btn(center_btns, "Sửa", COLORS["btn_edit"], self.edit_teacher).pack(side=tk.LEFT, padx=5)
        create_btn(center_btns, "Xóa", COLORS["btn_delete"], self.delete_teacher).pack(side=tk.LEFT, padx=5)
        create_btn(center_btns, "Làm mới", COLORS["btn_new"], self.clear_form).pack(side=tk.LEFT, padx=5)

        # ============================================================
        # RIGHT PANEL: DANH SÁCH GIẢNG VIÊN
        # ============================================================
        right_panel = tk.Frame(self.window, bg=COLORS["white"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        search_header = tk.Frame(right_panel, bg=COLORS["table_header"], height=50)
        search_header.pack(fill=tk.X)
        search_header.pack_propagate(False)
        tk.Label(search_header, text="Danh sách giảng viên", font=("Segoe UI", 14, "bold"), bg=COLORS["table_header"], fg=COLORS["white"]).pack(side=tk.LEFT, padx=15, pady=12)
        
        # Search
        search_controls = tk.Frame(right_panel, bg=COLORS["white"])
        search_controls.pack(fill=tk.X, padx=15, pady=15)
        
        self.entry_search = tk.Entry(search_controls, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1, width=30)
        self.entry_search.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_search.bind('<Return>', lambda e: self.search_teachers())
        
        tk.Button(search_controls, text="Tìm kiếm", bg=COLORS["btn_save"], fg="white", relief=tk.FLAT, command=self.search_teachers).pack(side=tk.LEFT, padx=5)
        tk.Button(search_controls, text="Tất cả", bg=COLORS["btn_new"], fg="white", relief=tk.FLAT, command=self.load_teachers).pack(side=tk.LEFT, padx=5)
        
        # Table
        table_container = tk.Frame(right_panel, bg=COLORS["white"])
        table_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        tree_scroll_y = ttk.Scrollbar(table_container, orient=tk.VERTICAL)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ("STT", "Mã GV", "Họ tên", "Email", "Điện thoại", "Khoa", "Trạng thái")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set, height=20)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        for col in columns:
            self.tree.heading(col, text=col)
            
        self.tree.column("STT", width=40, anchor=tk.CENTER)
        self.tree.column("Mã GV", width=80, anchor=tk.CENTER)
        self.tree.column("Họ tên", width=150)
        self.tree.column("Email", width=150)
        self.tree.column("Điện thoại", width=100)
        self.tree.column("Khoa", width=120)
        self.tree.column("Trạng thái", width=100, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<ButtonRelease-1>', self.on_tree_select)
        self.tree.tag_configure('evenrow', background='#F8F9FA')
        self.tree.tag_configure('oddrow', background='#FFFFFF')
        self.tree.tag_configure('inactive', foreground='#95A5A6')

    def load_teachers(self):
        """Load danh sách giảng viên"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            teachers = self.api.get_teachers()
            for idx, teacher in enumerate(teachers, 1):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                tags = [tag]
                if not teacher.get('is_active', True):
                    tags.append('inactive')
                
                status = "Hoạt động" if teacher.get('is_active', True) else "Nghỉ việc"
                
                self.tree.insert("", tk.END, values=(
                    idx,
                    teacher.get('teacher_id', ''),
                    teacher.get('full_name', ''),
                    teacher.get('email', ''),
                    teacher.get('phone', ''),
                    teacher.get('department', ''),
                    status
                ), tags=tuple(tags))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách giảng viên:\n{str(e)}")

    def search_teachers(self):
        """Tìm kiếm giảng viên"""
        search_term = self.entry_search.get().strip().lower()
        if not search_term:
            self.load_teachers()
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            teachers = self.api.get_teachers()
            filtered = [t for t in teachers 
                       if search_term in str(t.get('teacher_id', '')).lower() 
                       or search_term in str(t.get('full_name', '')).lower()
                       or search_term in str(t.get('email', '')).lower()
                       or search_term in str(t.get('department', '')).lower()]
            
            for idx, teacher in enumerate(filtered, 1):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                tags = [tag]
                if not teacher.get('is_active', True):
                    tags.append('inactive')
                
                status = "Hoạt động" if teacher.get('is_active', True) else "Nghỉ việc"
                
                self.tree.insert("", tk.END, values=(
                    idx,
                    teacher.get('teacher_id', ''),
                    teacher.get('full_name', ''),
                    teacher.get('email', ''),
                    teacher.get('phone', ''),
                    teacher.get('department', ''),
                    status
                ), tags=tuple(tags))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tìm kiếm:\n{str(e)}")

    def on_tree_select(self, event):
        """Xử lý khi chọn giảng viên từ table"""
        selected = self.tree.selection()
        if not selected: return
        
        item = self.tree.item(selected[0])
        values = item['values']
        if len(values) < 2: return
        
        teacher_id = str(values[1])
        try:
            teacher = self.api.get_teacher(teacher_id)
            if teacher:
                self.current_teacher = teacher
                self.populate_form(teacher)
        except Exception as e:
            print(f"❌ Error loading teacher: {e}")

    def populate_form(self, teacher):
        """Điền thông tin giảng viên vào form"""
        self.clear_form_fields_only()
        try:
            self.entry_teacher_id.insert(0, str(teacher.get('teacher_id', '')))
            self.entry_teacher_id.config(state='readonly')
            self.entry_full_name.insert(0, str(teacher.get('full_name', '')))
            self.entry_email.insert(0, str(teacher.get('email', '')))
            self.entry_phone.insert(0, str(teacher.get('phone', '')))
            self.entry_department.insert(0, str(teacher.get('department', '')))
            self.var_active.set(teacher.get('is_active', True))
        except Exception as e:
            print(f"❌ Error in populate_form: {e}")

    def clear_form_fields_only(self):
        """Xóa các field trong form"""
        self.entry_teacher_id.config(state='normal')
        self.entry_teacher_id.delete(0, tk.END)
        self.entry_full_name.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)
        self.entry_department.delete(0, tk.END)
        self.var_active.set(True)

    def clear_form(self):
        """Làm mới form"""
        self.clear_form_fields_only()
        self.current_teacher = None
        self.tree.selection_remove(*self.tree.selection())

    def validate_form(self):
        """Validate dữ liệu form"""
        teacher_id = self.entry_teacher_id.get().strip()
        full_name = self.entry_full_name.get().strip()
        email = self.entry_email.get().strip()
        
        if not teacher_id or not full_name or not email:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ Mã GV, Họ tên và Email!")
            return False
            
        if not re.match(r'^[A-Za-z0-9]+$', teacher_id):
            messagebox.showwarning("Mã không hợp lệ", "Mã giảng viên chỉ được chứa chữ cái và số!")
            return False
            
        return True

    def save_teacher(self):
        """Lưu giảng viên mới"""
        if not self.validate_form(): return
        
        data = {
            "teacher_id": self.entry_teacher_id.get().strip().upper(),
            "full_name": self.entry_full_name.get().strip(),
            "email": self.entry_email.get().strip(),
            "phone": self.entry_phone.get().strip(),
            "department": self.entry_department.get().strip(),
            "is_active": self.var_active.get()
        }
        
        try:
            if self.api.create_teacher(data):
                messagebox.showinfo("Thành công", "Đã thêm giảng viên!")
                self.clear_form()
                self.load_teachers()
            else:
                messagebox.showerror("Lỗi", "Không thể thêm giảng viên (có thể mã đã tồn tại).")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lưu:\n{str(e)}")

    def edit_teacher(self):
        """Cập nhật giảng viên"""
        if not self.current_teacher:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn giảng viên cần sửa!")
            return
        
        data = {
            "full_name": self.entry_full_name.get().strip(),
            "email": self.entry_email.get().strip(),
            "phone": self.entry_phone.get().strip(),
            "department": self.entry_department.get().strip(),
            "is_active": self.var_active.get()
        }
        
        try:
            if self.api.update_teacher(self.current_teacher['teacher_id'], data):
                messagebox.showinfo("Thành công", "Cập nhật thành công!")
                self.clear_form()
                self.load_teachers()
            else:
                messagebox.showerror("Lỗi", "Cập nhật thất bại.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi cập nhật:\n{str(e)}")

    def delete_teacher(self):
        """Xóa giảng viên"""
        if not self.current_teacher:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn giảng viên cần xóa!")
            return
            
        tid = self.current_teacher['teacher_id']
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa giảng viên {tid}?"):
            try:
                if self.api.delete_teacher(tid):
                    messagebox.showinfo("Thành công", "Đã xóa giảng viên!")
                    self.clear_form()
                    self.load_teachers()
                else:
                    messagebox.showerror("Lỗi", "Xóa thất bại.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa:\n{str(e)}")
