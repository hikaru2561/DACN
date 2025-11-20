"""
Module Quản lý Lớp học (Classes)
Chức năng: CRUD đầy đủ + Quản lý sinh viên trong lớp
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
    "btn_students": "#9B59B6",
}

# ============================================================================
# CLASS MANAGEMENT WINDOW
# ============================================================================

class ClassManagementWindow:
    """Cửa sổ quản lý lớp học"""
    
    def __init__(self, parent):
        self.parent = parent
        self.api = APIClient()
        self.current_class = None
        
        # Cache data
        self.subjects_cache = []
        self.teachers_cache = []
        
        # Tạo window
        self.window = tk.Toplevel(parent)
        self.window.title("Quản lý Lớp học")
        self.window.geometry("1600x900")
        self.window.configure(bg=COLORS["light"])
        self.window.transient(parent)
        
        self.load_cache_data()
        self.create_ui()
        self.load_classes()
    
    def load_cache_data(self):
        """Load dữ liệu môn học và giảng viên"""
        try:
            self.subjects_cache = self.api.get_subjects()
            self.teachers_cache = self.api.get_teachers()
        except Exception as e:
            print(f"❌ Error loading cache data: {e}")
    
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
            text="🎓 QUẢN LÝ LỚP HỌC",
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
        # LEFT PANEL: FORM
        # ============================================================
        left_panel = tk.Frame(main_container, bg=COLORS["white"], width=550)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Form Header
        form_header = tk.Frame(left_panel, bg="#9B59B6", height=50)
        form_header.pack(fill=tk.X)
        form_header.pack_propagate(False)
        
        tk.Label(
            form_header,
            text="📝 Thông tin lớp học",
            font=("Segoe UI", 14, "bold"),
            bg="#9B59B6",
            fg=COLORS["white"]
        ).pack(pady=12)
        
        # Form Container
        form_container = tk.Frame(left_panel, bg=COLORS["white"])
        form_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # === TÊN LỚP HỌC ===
        tk.Label(
            form_container,
            text="Tên lớp học *",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w"
        ).pack(fill=tk.X, pady=(10, 5))
        
        self.entry_class_name = tk.Entry(
            form_container,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_class_name.pack(fill=tk.X, ipady=8)
        
        # === MÔN HỌC ===
        tk.Label(
            form_container,
            text="Môn học *",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w"
        ).pack(fill=tk.X, pady=(15, 5))
        
        self.combo_subject = ttk.Combobox(
            form_container,
            font=("Segoe UI", 11),
            state="readonly"
        )
        self.combo_subject.pack(fill=tk.X, ipady=8)
        
        # Populate subjects
        subject_values = [f"{s['subject_id']} - {s['subject_name']}" 
                         for s in self.subjects_cache if s.get('is_active', True)]
        self.combo_subject['values'] = subject_values
        
        # === GIẢNG VIÊN ===
        tk.Label(
            form_container,
            text="Giảng viên *",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w"
        ).pack(fill=tk.X, pady=(15, 5))
        
        self.combo_teacher = ttk.Combobox(
            form_container,
            font=("Segoe UI", 11),
            state="readonly"
        )
        self.combo_teacher.pack(fill=tk.X, ipady=8)
        
        # Populate teachers
        teacher_values = [f"{t['teacher_id']} - {t['full_name']}" 
                         for t in self.teachers_cache if t.get('is_active', True)]
        self.combo_teacher['values'] = teacher_values
        
        # === HỌC KỲ ===
        tk.Label(
            form_container,
            text="Học kỳ *",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w"
        ).pack(fill=tk.X, pady=(15, 5))
        
        self.entry_semester = tk.Entry(
            form_container,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_semester.pack(fill=tk.X, ipady=8)
        
        # === NĂM HỌC ===
        tk.Label(
            form_container,
            text="Năm học *",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w"
        ).pack(fill=tk.X, pady=(15, 5))
        
        self.entry_academic_year = tk.Entry(
            form_container,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_academic_year.pack(fill=tk.X, ipady=8)
        
        # === PHÒNG HỌC ===
        tk.Label(
            form_container,
            text="Phòng học",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w"
        ).pack(fill=tk.X, pady=(15, 5))
        
        self.entry_room = tk.Entry(
            form_container,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_room.pack(fill=tk.X, ipady=8)
        
        # === SỐ SINH VIÊN TỐI ĐA ===
        tk.Label(
            form_container,
            text="Số sinh viên tối đa",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w"
        ).pack(fill=tk.X, pady=(15, 5))
        
        self.entry_max_students = tk.Entry(
            form_container,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_max_students.pack(fill=tk.X, ipady=8)
        self.entry_max_students.insert(0, "50")
        
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
            command=self.save_class,
            width=10,
            height=2
        ).pack(side=tk.LEFT, padx=3)
        
        tk.Button(
            btn_center,
            text="✏️ Sửa",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_edit"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.edit_class,
            width=10,
            height=2
        ).pack(side=tk.LEFT, padx=3)
        
        tk.Button(
            btn_center,
            text="🗑️ Xóa",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_delete"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.delete_class,
            width=10,
            height=2
        ).pack(side=tk.LEFT, padx=3)
        
        tk.Button(
            btn_center,
            text="🔄 Mới",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_new"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.clear_form,
            width=10,
            height=2
        ).pack(side=tk.LEFT, padx=3)
        
        tk.Button(
            btn_center,
            text="👥 SV",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_students"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.manage_students,
            width=10,
            height=2
        ).pack(side=tk.LEFT, padx=3)
        
        # ============================================================
        # RIGHT PANEL: DANH SÁCH LỚP HỌC
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
            text="Tìm",
            font=("Segoe UI", 10),
            bg=COLORS["btn_save"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.search_classes,
            width=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            search_frame,
            text="Tất cả",
            font=("Segoe UI", 10),
            bg=COLORS["btn_new"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.load_classes,
            width=8
        ).pack(side=tk.LEFT, padx=5)
        
        # Table
        table_container = tk.Frame(right_panel, bg=COLORS["white"])
        table_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        tree_scroll_y = ttk.Scrollbar(table_container, orient=tk.VERTICAL)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ("STT", "ID", "Tên lớp", "Môn học", "Giảng viên", "Học kỳ", "Năm học", "Phòng", "Trạng thái")
        
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            height=25
        )
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Headers
        for col in columns:
            self.tree.heading(col, text=col)
        
        # Widths
        self.tree.column("STT", width=50, anchor=tk.CENTER)
        self.tree.column("ID", width=60, anchor=tk.CENTER)
        self.tree.column("Tên lớp", width=200)
        self.tree.column("Môn học", width=150)
        self.tree.column("Giảng viên", width=150)
        self.tree.column("Học kỳ", width=100, anchor=tk.CENTER)
        self.tree.column("Năm học", width=100, anchor=tk.CENTER)
        self.tree.column("Phòng", width=80, anchor=tk.CENTER)
        self.tree.column("Trạng thái", width=100, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.tree.bind('<ButtonRelease-1>', self.on_tree_select)
        
        self.tree.tag_configure('evenrow', background='#F8F9FA')
        self.tree.tag_configure('oddrow', background='#FFFFFF')
        self.tree.tag_configure('inactive', foreground='#95A5A6')
    
    def load_classes(self):
        """Load danh sách lớp học"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            classes = self.api.get_classes()
            
            for idx, cls in enumerate(classes, 1):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                tags = [tag]
                if not cls.get('is_active', True):
                    tags.append('inactive')
                
                # Get subject name
                subject_name = cls.get('subject_id', '')
                for s in self.subjects_cache:
                    if s['subject_id'] == cls.get('subject_id'):
                        subject_name = s['subject_name']
                        break
                
                # Get teacher name
                teacher_name = cls.get('teacher_id', '')
                for t in self.teachers_cache:
                    if t['teacher_id'] == cls.get('teacher_id'):
                        teacher_name = t['full_name']
                        break
                
                status = "✅ Hoạt động" if cls.get('is_active', True) else "❌ Ngừng"
                
                self.tree.insert("", tk.END, values=(
                    idx,
                    cls.get('class_id', ''),
                    cls.get('class_name', ''),
                    subject_name,
                    teacher_name,
                    cls.get('semester', ''),
                    cls.get('academic_year', ''),
                    cls.get('room', ''),
                    status
                ), tags=tuple(tags))
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách lớp học:\n{str(e)}")
    
    def search_classes(self):
        """Tìm kiếm lớp học"""
        search_term = self.entry_search.get().strip().lower()
        
        if not search_term:
            self.load_classes()
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            classes = self.api.get_classes()
            filtered = [c for c in classes 
                       if search_term in c.get('class_name', '').lower()
                       or search_term in c.get('semester', '').lower()
                       or search_term in c.get('room', '').lower()]
            
            for idx, cls in enumerate(filtered, 1):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                tags = [tag]
                if not cls.get('is_active', True):
                    tags.append('inactive')
                
                subject_name = cls.get('subject_id', '')
                for s in self.subjects_cache:
                    if s['subject_id'] == cls.get('subject_id'):
                        subject_name = s['subject_name']
                        break
                
                teacher_name = cls.get('teacher_id', '')
                for t in self.teachers_cache:
                    if t['teacher_id'] == cls.get('teacher_id'):
                        teacher_name = t['full_name']
                        break
                
                status = "✅ Hoạt động" if cls.get('is_active', True) else "❌ Ngừng"
                
                self.tree.insert("", tk.END, values=(
                    idx,
                    cls.get('class_id', ''),
                    cls.get('class_name', ''),
                    subject_name,
                    teacher_name,
                    cls.get('semester', ''),
                    cls.get('academic_year', ''),
                    cls.get('room', ''),
                    status
                ), tags=tuple(tags))
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tìm kiếm:\n{str(e)}")
    
    def on_tree_select(self, event):
        """Xử lý khi chọn lớp từ table"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        values = item['values']
        
        if len(values) < 2:
            return
        
        class_id = int(values[1])
        
        try:
            cls = self.api.get_class(class_id)
            
            if cls:
                self.current_class = cls
                self.populate_form(cls)
            else:
                self.current_class = None
        
        except Exception as e:
            print(f"❌ Error loading class: {e}")
            self.current_class = None
    
    def populate_form(self, cls):
        """Điền thông tin lớp vào form"""
        self.clear_form_fields_only()
        
        try:
            self.entry_class_name.insert(0, str(cls.get('class_name', '')))
            
            # Subject
            subject_id = cls.get('subject_id')
            for idx, val in enumerate(self.combo_subject['values']):
                if val.startswith(subject_id):
                    self.combo_subject.current(idx)
                    break
            
            # Teacher
            teacher_id = cls.get('teacher_id')
            for idx, val in enumerate(self.combo_teacher['values']):
                if val.startswith(teacher_id):
                    self.combo_teacher.current(idx)
                    break
            
            self.entry_semester.insert(0, str(cls.get('semester', '')))
            self.entry_academic_year.insert(0, str(cls.get('academic_year', '')))
            self.entry_room.insert(0, str(cls.get('room', '')))
            
            max_students = cls.get('max_students', 50)
            self.entry_max_students.delete(0, tk.END)
            self.entry_max_students.insert(0, str(max_students))
            
            self.var_active.set(cls.get('is_active', True))
        
        except Exception as e:
            print(f"❌ Error in populate_form: {e}")
            raise
    
    def clear_form_fields_only(self):
        """Xóa form"""
        self.entry_class_name.delete(0, tk.END)
        self.combo_subject.set('')
        self.combo_teacher.set('')
        self.entry_semester.delete(0, tk.END)
        self.entry_academic_year.delete(0, tk.END)
        self.entry_room.delete(0, tk.END)
        self.entry_max_students.delete(0, tk.END)
        self.entry_max_students.insert(0, "50")
        self.var_active.set(True)
    
    def clear_form(self):
        """Làm mới form"""
        self.clear_form_fields_only()
        self.current_class = None
        self.tree.selection_remove(*self.tree.selection())
    
    def validate_form(self):
        """Validate form"""
        if not self.entry_class_name.get().strip():
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên lớp học!")
            return False
        
        if not self.combo_subject.get():
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn môn học!")
            return False
        
        if not self.combo_teacher.get():
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn giảng viên!")
            return False
        
        if not self.entry_semester.get().strip():
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập học kỳ!")
            return False
        
        if not self.entry_academic_year.get().strip():
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập năm học!")
            return False
        
        try:
            max_students = int(self.entry_max_students.get().strip())
            if max_students <= 0:
                raise ValueError()
        except:
            messagebox.showwarning("Lỗi", "Số sinh viên tối đa phải là số nguyên dương!")
            return False
        
        return True
    
    def save_class(self):
        """Lưu lớp học mới"""
        if not self.validate_form():
            return
        
        subject_id = self.combo_subject.get().split(' - ')[0]
        teacher_id = self.combo_teacher.get().split(' - ')[0]
        
        class_data = {
            "class_name": self.entry_class_name.get().strip(),
            "subject_id": subject_id,
            "teacher_id": teacher_id,
            "semester": self.entry_semester.get().strip(),
            "academic_year": self.entry_academic_year.get().strip(),
            "room": self.entry_room.get().strip(),
            "max_students": int(self.entry_max_students.get().strip()),
            "is_active": self.var_active.get()
        }
        
        try:
            result = self.api.create_class(class_data)
            
            if result:
                messagebox.showinfo(
                    "Thành công",
                    f"Đã thêm lớp học:\n{class_data['class_name']}"
                )
                self.clear_form()
                self.load_classes()
            else:
                messagebox.showerror("Lỗi", "Không thể thêm lớp học.")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lưu:\n{str(e)}")
    
    def edit_class(self):
        """Cập nhật lớp học"""
        if not self.current_class:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn lớp học để sửa!")
            return
        
        if not self.validate_form():
            return
        
        class_id = self.current_class['class_id']
        subject_id = self.combo_subject.get().split(' - ')[0]
        teacher_id = self.combo_teacher.get().split(' - ')[0]
        
        class_data = {
            "class_name": self.entry_class_name.get().strip(),
            "subject_id": subject_id,
            "teacher_id": teacher_id,
            "semester": self.entry_semester.get().strip(),
            "academic_year": self.entry_academic_year.get().strip(),
            "room": self.entry_room.get().strip(),
            "max_students": int(self.entry_max_students.get().strip()),
            "is_active": self.var_active.get()
        }
        
        try:
            result = self.api.update_class(class_id, class_data)
            
            if result:
                messagebox.showinfo("Thành công", f"Đã cập nhật lớp: {class_data['class_name']}")
                self.clear_form()
                self.load_classes()
            else:
                messagebox.showerror("Lỗi", "Không thể cập nhật lớp học.")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi cập nhật:\n{str(e)}")
    
    def delete_class(self):
        """Xóa lớp học"""
        if not self.current_class:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn lớp học để xóa!")
            return
        
        class_id = self.current_class['class_id']
        class_name = self.current_class['class_name']
        
        confirm = messagebox.askyesno(
            "Xác nhận xóa",
            f"Xóa lớp học:\n\n{class_name}\n\n⚠️ Không thể hoàn tác!"
        )
        
        if not confirm:
            return
        
        try:
            success = self.api.delete_class(class_id)
            
            if success:
                messagebox.showinfo("Thành công", f"Đã xóa lớp: {class_name}")
                self.clear_form()
                self.load_classes()
            else:
                messagebox.showerror("Lỗi", "Không thể xóa lớp học.")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xóa:\n{str(e)}")
    
    def manage_students(self):
        """Quản lý sinh viên trong lớp"""
        if not self.current_class:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn lớp học trước!")
            return
        
        ClassStudentsWindow(self.window, self.current_class, self.api)


# ============================================================================
# CLASS STUDENTS WINDOW
# ============================================================================

class ClassStudentsWindow:
    """Cửa sổ quản lý sinh viên trong lớp"""
    
    def __init__(self, parent, class_data, api):
        self.parent = parent
        self.class_data = class_data
        self.api = api
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"Sinh viên - {class_data['class_name']}")
        self.window.geometry("1200x700")
        self.window.configure(bg=COLORS["light"])
        self.window.transient(parent)
        
        self.create_ui()
        self.load_enrolled_students()
    
    def create_ui(self):
        """Tạo giao diện"""
        # Header
        header = tk.Frame(self.window, bg=COLORS["info"], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text=f"👥 Sinh viên - {self.class_data['class_name']}",
            font=("Segoe UI", 16, "bold"),
            bg=COLORS["info"],
            fg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        # Main container
        main = tk.Frame(self.window, bg=COLORS["light"])
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left: Enrolled students
        left = tk.Frame(main, bg=COLORS["white"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(
            left,
            text="📋 Sinh viên đã đăng ký",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["white"]
        ).pack(pady=10)
        
        tree_frame = tk.Frame(left)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        cols = ("STT", "MSSV", "Họ tên", "Lớp")
        self.tree_enrolled = ttk.Treeview(
            tree_frame,
            columns=cols,
            show="headings",
            yscrollcommand=scroll.set
        )
        scroll.config(command=self.tree_enrolled.yview)
        
        for col in cols:
            self.tree_enrolled.heading(col, text=col)
        
        self.tree_enrolled.column("STT", width=50, anchor=tk.CENTER)
        self.tree_enrolled.column("MSSV", width=120, anchor=tk.CENTER)
        self.tree_enrolled.column("Họ tên", width=200)
        self.tree_enrolled.column("Lớp", width=100)
        
        self.tree_enrolled.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(
            left,
            text="🗑️ Xóa khỏi lớp",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_delete"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.unenroll_student,
            padx=20,
            pady=10
        ).pack(pady=10)
        
        # Right: Add students
        right = tk.Frame(main, bg=COLORS["white"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            right,
            text="➕ Thêm sinh viên",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["white"]
        ).pack(pady=10)
        
        search_frame = tk.Frame(right, bg=COLORS["white"])
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            search_frame,
            text="Tìm MSSV:",
            font=("Segoe UI", 10),
            bg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=5)
        
        self.entry_search = tk.Entry(
            search_frame,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        tk.Button(
            search_frame,
            text="Tìm",
            font=("Segoe UI", 10),
            bg=COLORS["btn_save"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.search_students,
            width=8
        ).pack(side=tk.LEFT, padx=5)
        
        tree_frame2 = tk.Frame(right)
        tree_frame2.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scroll2 = ttk.Scrollbar(tree_frame2, orient=tk.VERTICAL)
        scroll2.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree_available = ttk.Treeview(
            tree_frame2,
            columns=cols,
            show="headings",
            yscrollcommand=scroll2.set
        )
        scroll2.config(command=self.tree_available.yview)
        
        for col in cols:
            self.tree_available.heading(col, text=col)
        
        self.tree_available.column("STT", width=50, anchor=tk.CENTER)
        self.tree_available.column("MSSV", width=120, anchor=tk.CENTER)
        self.tree_available.column("Họ tên", width=200)
        self.tree_available.column("Lớp", width=100)
        
        self.tree_available.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(
            right,
            text="➕ Thêm vào lớp",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_new"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.enroll_student,
            padx=20,
            pady=10
        ).pack(pady=10)
    
    def load_enrolled_students(self):
        """Load sinh viên đã đăng ký"""
        for item in self.tree_enrolled.get_children():
            self.tree_enrolled.delete(item)
        
        try:
            students = self.api.get_class_students(self.class_data['class_id'])
            
            for idx, student in enumerate(students, 1):
                self.tree_enrolled.insert("", tk.END, values=(
                    idx,
                    student.get('student_id', ''),
                    student.get('full_name', ''),
                    student.get('class_name', '')
                ))
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải sinh viên:\n{str(e)}")
    
    def search_students(self):
        """Tìm sinh viên để thêm"""
        for item in self.tree_available.get_children():
            self.tree_available.delete(item)
        
        search_term = self.entry_search.get().strip()
        
        try:
            all_students = self.api.get_students()
            enrolled = self.api.get_class_students(self.class_data['class_id'])
            enrolled_ids = {s['student_id'] for s in enrolled}
            
            available = [s for s in all_students 
                        if s['student_id'] not in enrolled_ids
                        and (not search_term or search_term in s['student_id'])]
            
            for idx, student in enumerate(available, 1):
                self.tree_available.insert("", tk.END, values=(
                    idx,
                    student.get('student_id', ''),
                    student.get('full_name', ''),
                    student.get('class_name', '')
                ))
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tìm kiếm:\n{str(e)}")
    
    def enroll_student(self):
        """Thêm sinh viên vào lớp"""
        selected = self.tree_available.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn sinh viên!")
            return
        
        item = self.tree_available.item(selected[0])
        student_id = item['values'][1]
        student_name = item['values'][2]
        
        try:
            result = self.api.enroll_student(self.class_data['class_id'], student_id)
            
            if result:
                messagebox.showinfo("Thành công", f"Đã thêm {student_name} vào lớp!")
                self.load_enrolled_students()
                self.search_students()
            else:
                messagebox.showerror("Lỗi", "Không thể thêm sinh viên.")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi thêm:\n{str(e)}")
    
    def unenroll_student(self):
        """Xóa sinh viên khỏi lớp"""
        selected = self.tree_enrolled.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn sinh viên!")
            return
        
        item = self.tree_enrolled.item(selected[0])
        student_id = item['values'][1]
        student_name = item['values'][2]
        
        confirm = messagebox.askyesno(
            "Xác nhận",
            f"Xóa {student_name} khỏi lớp?"
        )
        
        if not confirm:
            return
        
        try:
            success = self.api.unenroll_student(self.class_data['class_id'], student_id)
            
            if success:
                messagebox.showinfo("Thành công", f"Đã xóa {student_name} khỏi lớp!")
                self.load_enrolled_students()
            else:
                messagebox.showerror("Lỗi", "Không thể xóa sinh viên.")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xóa:\n{str(e)}")


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    app = ClassManagementWindow(root)
    root.mainloop()
