"""
Module Quản lý Giảng viên (Teachers)
Chức năng: CRUD đầy đủ cho giảng viên
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from api_client import APIClient
import re

# ============================================================================
# COLOR SCHEME
# ============================================================================

COLORS = {
    "primary": "#2C3E50",
    "secondary": "#34495E", 
    "success": "#27AE60",
    "danger": "#E74C3C",
    "warning": "#F39C12",
    "info": "#3498DB",
    "light": "#ECF0F1",
    "dark": "#2C3E50",
    "white": "#FFFFFF",
    "text": "#2C3E50",
    
    # Buttons
    "btn_save": "#3498DB",
    "btn_edit": "#F39C12", 
    "btn_delete": "#E74C3C",
    "btn_new": "#27AE60",
    "btn_cancel": "#95A5A6",
}

# ============================================================================
# TEACHER MANAGEMENT WINDOW
# ============================================================================

class TeacherManagementWindow:
    """Cửa sổ quản lý giảng viên"""
    
    def __init__(self, parent):
        self.parent = parent
        self.api = APIClient()
        self.current_teacher = None
        
        # Tạo window
        self.window = tk.Toplevel(parent)
        self.window.title("Quản lý Giảng viên")
        self.window.geometry("1400x800")
        self.window.configure(bg=COLORS["light"])
        self.window.transient(parent)
        
        self.create_ui()
        self.load_teachers()
    
    def create_ui(self):
        """Tạo giao diện"""
        # ============================================================
        # HEADER
        # ============================================================
        header = tk.Frame(self.window, bg=COLORS["primary"], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="👨‍🏫 QUẢN LÝ GIẢNG VIÊN",
            font=("Segoe UI", 20, "bold"),
            bg=COLORS["primary"],
            fg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=30, pady=20)
        
        # ============================================================
        # MAIN CONTAINER - 2 PANELS
        # ============================================================
        main_container = tk.Frame(self.window, bg=COLORS["light"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # ============================================================
        # LEFT PANEL: FORM NHẬP LIỆU
        # ============================================================
        left_panel = tk.Frame(main_container, bg=COLORS["white"], width=500)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Form Header
        form_header = tk.Frame(left_panel, bg="#E67E22", height=50)
        form_header.pack(fill=tk.X)
        form_header.pack_propagate(False)
        
        tk.Label(
            form_header,
            text="📝 Thông tin giảng viên",
            font=("Segoe UI", 14, "bold"),
            bg="#E67E22",
            fg=COLORS["white"]
        ).pack(pady=12)
        
        # Form Container với scrollbar
        form_container = tk.Frame(left_panel, bg=COLORS["white"])
        form_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # === MÃ GIẢNG VIÊN ===
        tk.Label(
            form_container,
            text="Mã giảng viên *",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w"
        ).pack(fill=tk.X, pady=(10, 5))
        
        self.entry_teacher_id = tk.Entry(
            form_container,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_teacher_id.pack(fill=tk.X, ipady=8)
        
        # === HỌ TÊN ===
        tk.Label(
            form_container,
            text="Họ và tên *",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w"
        ).pack(fill=tk.X, pady=(15, 5))
        
        self.entry_full_name = tk.Entry(
            form_container,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_full_name.pack(fill=tk.X, ipady=8)
        
        # === EMAIL ===
        tk.Label(
            form_container,
            text="Email *",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w"
        ).pack(fill=tk.X, pady=(15, 5))
        
        self.entry_email = tk.Entry(
            form_container,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_email.pack(fill=tk.X, ipady=8)
        
        # === ĐIỆN THOẠI ===
        tk.Label(
            form_container,
            text="Điện thoại",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w"
        ).pack(fill=tk.X, pady=(15, 5))
        
        self.entry_phone = tk.Entry(
            form_container,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_phone.pack(fill=tk.X, ipady=8)
        
        # === KHOA/BỘ MÔN ===
        tk.Label(
            form_container,
            text="Khoa/Bộ môn",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w"
        ).pack(fill=tk.X, pady=(15, 5))
        
        self.entry_department = tk.Entry(
            form_container,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_department.pack(fill=tk.X, ipady=8)
        
        # === TRẠNG THÁI ===
        tk.Label(
            form_container,
            text="Trạng thái",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w"
        ).pack(fill=tk.X, pady=(15, 5))
        
        self.var_active = tk.BooleanVar(value=True)
        tk.Checkbutton(
            form_container,
            text="Đang hoạt động",
            variable=self.var_active,
            font=("Segoe UI", 10),
            bg=COLORS["white"]
        ).pack(anchor="w")
        
        # === BUTTONS ===
        btn_frame = tk.Frame(form_container, bg=COLORS["white"])
        btn_frame.pack(fill=tk.X, pady=30)
        
        # Center buttons
        btn_center = tk.Frame(btn_frame, bg=COLORS["white"])
        btn_center.pack(expand=True)
        
        tk.Button(
            btn_center,
            text="💾 Lưu",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_save"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.save_teacher,
            width=12,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_center,
            text="✏️ Sửa",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_edit"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.edit_teacher,
            width=12,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_center,
            text="🗑️ Xóa",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_delete"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.delete_teacher,
            width=12,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_center,
            text="🔄 Làm mới",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_new"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.clear_form,
            width=12,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        # ============================================================
        # RIGHT PANEL: DANH SÁCH GIẢNG VIÊN
        # ============================================================
        right_panel = tk.Frame(main_container, bg=COLORS["white"])
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Search Bar
        search_frame = tk.Frame(right_panel, bg=COLORS["white"])
        search_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(
            search_frame,
            text="🔍 Tìm kiếm:",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.entry_search = tk.Entry(
            search_frame,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_search.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        
        tk.Button(
            search_frame,
            text="Tìm kiếm",
            font=("Segoe UI", 10),
            bg=COLORS["btn_save"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.search_teachers,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            search_frame,
            text="Xem tất cả",
            font=("Segoe UI", 10),
            bg=COLORS["btn_new"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.load_teachers,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # Table Container
        table_container = tk.Frame(right_panel, bg=COLORS["white"])
        table_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Treeview with scrollbars
        tree_scroll_y = ttk.Scrollbar(table_container, orient=tk.VERTICAL)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Define columns
        columns = ("STT", "Mã GV", "Họ tên", "Email", "Điện thoại", "Khoa", "Trạng thái")
        
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            height=20
        )
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Column headers
        self.tree.heading("STT", text="STT")
        self.tree.heading("Mã GV", text="Mã GV")
        self.tree.heading("Họ tên", text="Họ tên")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Điện thoại", text="Điện thoại")
        self.tree.heading("Khoa", text="Khoa")
        self.tree.heading("Trạng thái", text="Trạng thái")
        
        # Column widths
        self.tree.column("STT", width=50, anchor=tk.CENTER)
        self.tree.column("Mã GV", width=100, anchor=tk.CENTER)
        self.tree.column("Họ tên", width=200)
        self.tree.column("Email", width=200)
        self.tree.column("Điện thoại", width=120, anchor=tk.CENTER)
        self.tree.column("Khoa", width=180)
        self.tree.column("Trạng thái", width=120, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind click event
        self.tree.bind('<ButtonRelease-1>', self.on_tree_select)
        
        # Alternating row colors
        self.tree.tag_configure('evenrow', background='#F8F9FA')
        self.tree.tag_configure('oddrow', background='#FFFFFF')
        self.tree.tag_configure('inactive', foreground='#95A5A6')
    
    def load_teachers(self):
        """Load danh sách giảng viên"""
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            teachers = self.api.get_teachers()
            
            for idx, teacher in enumerate(teachers, 1):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                
                # Add inactive tag if not active
                tags = [tag]
                if not teacher.get('is_active', True):
                    tags.append('inactive')
                
                status = "✅ Hoạt động" if teacher.get('is_active', True) else "❌ Nghỉ việc"
                
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
        
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            teachers = self.api.get_teachers()
            filtered = [t for t in teachers 
                       if search_term in t.get('teacher_id', '').lower() 
                       or search_term in t.get('full_name', '').lower()
                       or search_term in t.get('email', '').lower()
                       or search_term in t.get('department', '').lower()]
            
            for idx, teacher in enumerate(filtered, 1):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                tags = [tag]
                if not teacher.get('is_active', True):
                    tags.append('inactive')
                
                status = "✅ Hoạt động" if teacher.get('is_active', True) else "❌ Nghỉ việc"
                
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
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        values = item['values']
        
        if len(values) < 2:
            return
        
        teacher_id = str(values[1])  # Mã GV
        
        try:
            # Fetch full teacher data from API
            teacher = self.api.get_teacher(teacher_id)
            
            if teacher:
                self.current_teacher = teacher
                self.populate_form(teacher)
            else:
                self.current_teacher = None
        
        except Exception as e:
            print(f"❌ Error loading teacher: {e}")
            self.current_teacher = None
    
    def populate_form(self, teacher):
        """Điền thông tin giảng viên vào form"""
        self.clear_form_fields_only()
        
        try:
            # Mã giảng viên
            if teacher.get('teacher_id'):
                self.entry_teacher_id.insert(0, str(teacher['teacher_id']))
                self.entry_teacher_id.config(state='readonly')  # Không cho sửa mã
            
            # Họ tên
            if teacher.get('full_name'):
                self.entry_full_name.insert(0, str(teacher['full_name']))
            
            # Email
            if teacher.get('email'):
                self.entry_email.insert(0, str(teacher['email']))
            
            # Phone
            if teacher.get('phone'):
                self.entry_phone.insert(0, str(teacher['phone']))
            
            # Department
            if teacher.get('department'):
                self.entry_department.insert(0, str(teacher['department']))
            
            # Trạng thái
            self.var_active.set(teacher.get('is_active', True))
        
        except Exception as e:
            print(f"❌ Error in populate_form: {e}")
            raise
    
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
        
        if not teacher_id:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập mã giảng viên!")
            self.entry_teacher_id.focus()
            return False
        
        # Validate mã giảng viên (chỉ chữ, số và không có khoảng trắng)
        if not re.match(r'^[A-Za-z0-9]+$', teacher_id):
            messagebox.showwarning(
                "Mã không hợp lệ",
                "Mã giảng viên chỉ được chứa chữ cái và số, không có khoảng trắng!"
            )
            self.entry_teacher_id.focus()
            return False
        
        if not full_name:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập họ tên!")
            self.entry_full_name.focus()
            return False
        
        if not email:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập email!")
            self.entry_email.focus()
            return False
        
        # Validate email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            messagebox.showwarning(
                "Email không hợp lệ",
                "Vui lòng nhập địa chỉ email đúng định dạng!"
            )
            self.entry_email.focus()
            return False
        
        # Validate phone (optional but if provided must be valid)
        phone = self.entry_phone.get().strip()
        if phone and not re.match(r'^[0-9]{10,11}$', phone):
            messagebox.showwarning(
                "Số điện thoại không hợp lệ",
                "Số điện thoại phải có 10-11 chữ số!"
            )
            self.entry_phone.focus()
            return False
        
        return True
    
    def save_teacher(self):
        """Lưu giảng viên mới"""
        if not self.validate_form():
            return
        
        teacher_data = {
            "teacher_id": self.entry_teacher_id.get().strip().upper(),
            "full_name": self.entry_full_name.get().strip(),
            "email": self.entry_email.get().strip(),
            "phone": self.entry_phone.get().strip(),
            "department": self.entry_department.get().strip(),
            "is_active": self.var_active.get()
        }
        
        try:
            result = self.api.create_teacher(teacher_data)
            
            if result:
                messagebox.showinfo(
                    "Thành công",
                    f"Đã thêm giảng viên:\n{teacher_data['teacher_id']} - {teacher_data['full_name']}"
                )
                self.clear_form()
                self.load_teachers()
            else:
                messagebox.showerror("Lỗi", "Không thể thêm giảng viên. Mã có thể đã tồn tại.")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lưu giảng viên:\n{str(e)}")
    
    def edit_teacher(self):
        """Cập nhật giảng viên"""
        if not self.current_teacher:
            messagebox.showwarning(
                "Chưa chọn giảng viên",
                "Vui lòng chọn giảng viên từ danh sách để chỉnh sửa!"
            )
            return
        
        if not self.validate_form():
            return
        
        teacher_id = self.current_teacher['teacher_id']
        
        teacher_data = {
            "full_name": self.entry_full_name.get().strip(),
            "email": self.entry_email.get().strip(),
            "phone": self.entry_phone.get().strip(),
            "department": self.entry_department.get().strip(),
            "is_active": self.var_active.get()
        }
        
        try:
            result = self.api.update_teacher(teacher_id, teacher_data)
            
            if result:
                messagebox.showinfo(
                    "Thành công",
                    f"Đã cập nhật giảng viên:\n{teacher_id} - {teacher_data['full_name']}"
                )
                self.clear_form()
                self.load_teachers()
            else:
                messagebox.showerror("Lỗi", "Không thể cập nhật giảng viên.")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi cập nhật:\n{str(e)}")
    
    def delete_teacher(self):
        """Xóa giảng viên"""
        if not self.current_teacher:
            messagebox.showwarning(
                "Chưa chọn giảng viên",
                "Vui lòng chọn giảng viên từ danh sách để xóa!"
            )
            return
        
        teacher_id = self.current_teacher['teacher_id']
        teacher_name = self.current_teacher['full_name']
        
        confirm = messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc muốn xóa giảng viên:\n\n"
            f"{teacher_id} - {teacher_name}\n\n"
            f"⚠️ Hành động này không thể hoàn tác!"
        )
        
        if not confirm:
            return
        
        try:
            success = self.api.delete_teacher(teacher_id)
            
            if success:
                messagebox.showinfo(
                    "Thành công",
                    f"Đã xóa giảng viên: {teacher_id}"
                )
                self.clear_form()
                self.load_teachers()
            else:
                messagebox.showerror("Lỗi", "Không thể xóa giảng viên.")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xóa:\n{str(e)}")


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide root window
    
    app = TeacherManagementWindow(root)
    root.mainloop()
