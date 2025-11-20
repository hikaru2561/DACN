"""
Module Quản lý Lớp học (Classes)
Chức năng: CRUD đầy đủ + Quản lý sinh viên trong lớp
"""
import tkinter as tk
from tkinter import ttk, messagebox
from app.core.api_client import APIClient
import re

# ============================================================================
# COLOR SCHEME
# ============================================================================

COLORS = {
    "form_header": "#9B59B6", # Purple for Classes
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
    "btn_students": "#8E44AD",
}

# ============================================================================
# CLASS MANAGEMENT WINDOW
# ============================================================================

class ClassManagementWindow:
    """Cửa sổ quản lý lớp học"""
    
    def __init__(self, parent, api_client):
        self.parent = parent
        self.api = api_client
        self.current_class = None
        
        # Cache data
        self.subjects_cache = []
        self.teachers_cache = []
        
        # Tạo window
        self.window = tk.Toplevel(parent)
        self.window.title("Quản lý Lớp học")
        self.window.geometry("1600x900")
        self.window.configure(bg=COLORS["light"])
        
        # Remove transient to allow minimize/maximize
        # self.window.transient(parent)
        
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
            text="Thông tin lớp học",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["form_header"],
            fg=COLORS["white"]
        ).pack(pady=12)
        
        # Form Container
        form_container = tk.Frame(left_panel, bg=COLORS["white"])
        form_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # --- Helper function to create labeled entry ---
        def create_entry(parent, label_text, default_val=""):
            frame = tk.Frame(parent, bg=COLORS["white"])
            frame.pack(fill=tk.X, pady=5)
            
            lbl = tk.Label(frame, text=label_text, font=("Segoe UI", 10), bg=COLORS["white"], width=12, anchor="w")
            lbl.pack(side=tk.LEFT)
            
            entry = tk.Entry(frame, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            if default_val:
                entry.insert(0, default_val)
            return entry
            
        # === Fields ===
        self.entry_class_name = create_entry(form_container, "Tên lớp *:")
        
        # Môn học (Combobox)
        frame_sub = tk.Frame(form_container, bg=COLORS["white"])
        frame_sub.pack(fill=tk.X, pady=5)
        tk.Label(frame_sub, text="Môn học *:", font=("Segoe UI", 10), bg=COLORS["white"], width=12, anchor="w").pack(side=tk.LEFT)
        self.combo_subject = ttk.Combobox(frame_sub, font=("Segoe UI", 10), state="readonly")
        self.combo_subject.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.combo_subject['values'] = [f"{s['subject_id']} - {s['subject_name']}" for s in self.subjects_cache if s.get('is_active', True)]
        
        # Giảng viên (Combobox)
        frame_tea = tk.Frame(form_container, bg=COLORS["white"])
        frame_tea.pack(fill=tk.X, pady=5)
        tk.Label(frame_tea, text="Giảng viên *:", font=("Segoe UI", 10), bg=COLORS["white"], width=12, anchor="w").pack(side=tk.LEFT)
        self.combo_teacher = ttk.Combobox(frame_tea, font=("Segoe UI", 10), state="readonly")
        self.combo_teacher.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.combo_teacher['values'] = [f"{t['teacher_id']} - {t['full_name']}" for t in self.teachers_cache if t.get('is_active', True)]
        
        self.entry_semester = create_entry(form_container, "Học kỳ *:")
        self.entry_academic_year = create_entry(form_container, "Năm học *:")
        self.entry_room = create_entry(form_container, "Phòng học:")
        self.entry_max_students = create_entry(form_container, "Sĩ số tối đa:", "50")
        
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
        
        create_btn(center_btns, "Lưu", COLORS["btn_save"], self.save_class).pack(side=tk.LEFT, padx=3)
        create_btn(center_btns, "Sửa", COLORS["btn_edit"], self.edit_class).pack(side=tk.LEFT, padx=3)
        create_btn(center_btns, "Xóa", COLORS["btn_delete"], self.delete_class).pack(side=tk.LEFT, padx=3)
        create_btn(center_btns, "Mới", COLORS["btn_new"], self.clear_form).pack(side=tk.LEFT, padx=3)
        create_btn(center_btns, "Sinh viên", COLORS["btn_students"], self.manage_students).pack(side=tk.LEFT, padx=3)

        # ============================================================
        # RIGHT PANEL: DANH SÁCH LỚP HỌC
        # ============================================================
        right_panel = tk.Frame(self.window, bg=COLORS["white"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        search_header = tk.Frame(right_panel, bg=COLORS["table_header"], height=50)
        search_header.pack(fill=tk.X)
        search_header.pack_propagate(False)
        tk.Label(search_header, text="Danh sách lớp học", font=("Segoe UI", 14, "bold"), bg=COLORS["table_header"], fg=COLORS["white"]).pack(side=tk.LEFT, padx=15, pady=12)
        
        # Search
        search_controls = tk.Frame(right_panel, bg=COLORS["white"])
        search_controls.pack(fill=tk.X, padx=15, pady=15)
        
        self.entry_search = tk.Entry(search_controls, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1, width=30)
        self.entry_search.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_search.bind('<Return>', lambda e: self.search_classes())
        
        tk.Button(search_controls, text="Tìm kiếm", bg=COLORS["btn_save"], fg="white", relief=tk.FLAT, command=self.search_classes).pack(side=tk.LEFT, padx=5)
        tk.Button(search_controls, text="Tất cả", bg=COLORS["btn_new"], fg="white", relief=tk.FLAT, command=self.load_classes).pack(side=tk.LEFT, padx=5)
        
        # Table
        table_container = tk.Frame(right_panel, bg=COLORS["white"])
        table_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        tree_scroll_y = ttk.Scrollbar(table_container, orient=tk.VERTICAL)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ("STT", "ID", "Tên lớp", "Môn học", "Giảng viên", "Học kỳ", "Năm học", "Phòng", "Trạng thái")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set, height=20)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        for col in columns:
            self.tree.heading(col, text=col)
            
        self.tree.column("STT", width=40, anchor=tk.CENTER)
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Tên lớp", width=150)
        self.tree.column("Môn học", width=150)
        self.tree.column("Giảng viên", width=150)
        self.tree.column("Học kỳ", width=80, anchor=tk.CENTER)
        self.tree.column("Năm học", width=80, anchor=tk.CENTER)
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
                
                # Resolve names
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
                
                status = "Hoạt động" if cls.get('is_active', True) else "Ngừng"
                
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
                       if search_term in str(c.get('class_name', '')).lower()
                       or search_term in str(c.get('semester', '')).lower()
                       or search_term in str(c.get('room', '')).lower()]
            
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
                
                status = "Hoạt động" if cls.get('is_active', True) else "Ngừng"
                
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
        if not selected: return
        
        item = self.tree.item(selected[0])
        values = item['values']
        if len(values) < 2: return
        
        class_id = int(values[1])
        try:
            cls = self.api.get_class(class_id)
            if cls:
                self.current_class = cls
                self.populate_form(cls)
        except Exception as e:
            print(f"❌ Error loading class: {e}")

    def populate_form(self, cls):
        """Điền thông tin lớp vào form"""
        self.clear_form_fields_only()
        try:
            self.entry_class_name.insert(0, str(cls.get('class_name', '')))
            
            subject_id = cls.get('subject_id')
            for val in self.combo_subject['values']:
                if val.startswith(subject_id):
                    self.combo_subject.set(val)
                    break
            
            teacher_id = cls.get('teacher_id')
            for val in self.combo_teacher['values']:
                if val.startswith(teacher_id):
                    self.combo_teacher.set(val)
                    break
            
            self.entry_semester.insert(0, str(cls.get('semester', '')))
            self.entry_academic_year.insert(0, str(cls.get('academic_year', '')))
            self.entry_room.insert(0, str(cls.get('room', '')))
            self.entry_max_students.delete(0, tk.END)
            self.entry_max_students.insert(0, str(cls.get('max_students', '50')))
            self.var_active.set(cls.get('is_active', True))
        except Exception as e:
            print(f"❌ Error in populate_form: {e}")

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
            if max_students <= 0: raise ValueError()
        except:
            messagebox.showwarning("Lỗi", "Số sinh viên tối đa phải là số nguyên dương!")
            return False
        return True

    def save_class(self):
        """Lưu lớp học mới"""
        if not self.validate_form(): return
        
        subject_id = self.combo_subject.get().split(' - ')[0]
        teacher_id = self.combo_teacher.get().split(' - ')[0]
        
        data = {
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
            if self.api.create_class(data):
                messagebox.showinfo("Thành công", "Đã thêm lớp học!")
                self.clear_form()
                self.load_classes()
            else:
                messagebox.showerror("Lỗi", "Không thể thêm lớp học.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lưu:\n{str(e)}")

    def edit_class(self):
        """Cập nhật lớp học"""
        if not self.current_class:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lớp học để sửa!")
            return
        if not self.validate_form(): return
        
        subject_id = self.combo_subject.get().split(' - ')[0]
        teacher_id = self.combo_teacher.get().split(' - ')[0]
        
        data = {
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
            if self.api.update_class(self.current_class['class_id'], data):
                messagebox.showinfo("Thành công", "Cập nhật thành công!")
                self.clear_form()
                self.load_classes()
            else:
                messagebox.showerror("Lỗi", "Cập nhật thất bại.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi cập nhật:\n{str(e)}")

    def delete_class(self):
        """Xóa lớp học"""
        if not self.current_class:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lớp học để xóa!")
            return
            
        cid = self.current_class['class_id']
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa lớp {cid}?"):
            try:
                if self.api.delete_class(cid):
                    messagebox.showinfo("Thành công", "Đã xóa lớp học!")
                    self.clear_form()
                    self.load_classes()
                else:
                    messagebox.showerror("Lỗi", "Xóa thất bại.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa:\n{str(e)}")

    def manage_students(self):
        """Quản lý sinh viên trong lớp"""
        if not self.current_class:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lớp học trước!")
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
        
        # Remove transient
        # self.window.transient(parent)
        
        self.create_ui()
        self.load_enrolled_students()
    
    def create_ui(self):
        """Tạo giao diện"""
        # Header
        header = tk.Frame(self.window, bg=COLORS["form_header"], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text=f"👥 Sinh viên - {self.class_data['class_name']}",
            font=("Segoe UI", 16, "bold"),
            bg=COLORS["form_header"],
            fg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=20, pady=10)
        
        # Main container
        main = tk.Frame(self.window, bg=COLORS["light"])
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left: Add Student
        left = tk.Frame(main, bg=COLORS["white"], width=400)
        left.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left.pack_propagate(False)
        
        tk.Label(left, text="Thêm sinh viên vào lớp", font=("Segoe UI", 12, "bold"), bg=COLORS["white"]).pack(pady=10)
        
        # Search student to add
        search_frame = tk.Frame(left, bg=COLORS["white"])
        search_frame.pack(fill=tk.X, padx=10)
        tk.Label(search_frame, text="Tìm sinh viên:", bg=COLORS["white"]).pack(anchor="w")
        self.entry_search_student = tk.Entry(search_frame, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1)
        self.entry_search_student.pack(fill=tk.X, pady=5)
        tk.Button(search_frame, text="Tìm", bg=COLORS["btn_save"], fg="white", command=self.search_students_to_add).pack(fill=tk.X, pady=5)
        
        # List of students to add
        list_frame = tk.Frame(left, bg=COLORS["white"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.listbox_students = tk.Listbox(list_frame, font=("Segoe UI", 10), selectmode=tk.MULTIPLE)
        self.listbox_students.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scroll = tk.Scrollbar(list_frame, command=self.listbox_students.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_students.config(yscrollcommand=scroll.set)
        
        tk.Button(left, text=">> Thêm vào lớp >>", bg=COLORS["btn_new"], fg="white", font=("Segoe UI", 10, "bold"), command=self.add_students_to_class, height=2).pack(fill=tk.X, padx=10, pady=10)
        
        # Right: Enrolled Students
        right = tk.Frame(main, bg=COLORS["white"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(right, text="Danh sách sinh viên trong lớp", font=("Segoe UI", 12, "bold"), bg=COLORS["white"]).pack(pady=10)
        
        # Table
        table_frame = tk.Frame(right, bg=COLORS["white"])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        cols = ("MSSV", "Họ tên", "Ngày sinh", "Giới tính")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(right, text="Xóa khỏi lớp", bg=COLORS["btn_delete"], fg="white", command=self.remove_student_from_class).pack(fill=tk.X, padx=10, pady=10)

    def load_enrolled_students(self):
        """Load sinh viên đã đăng ký"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        # TODO: Implement API call to get enrolled students
        pass

    def search_students_to_add(self):
        """Tìm sinh viên để thêm"""
        # TODO: Implement API call to search students
        pass

    def add_students_to_class(self):
        """Thêm sinh viên vào lớp"""
        # TODO: Implement API call to enroll students
        pass

    def remove_student_from_class(self):
        """Xóa sinh viên khỏi lớp"""
        # TODO: Implement API call to remove student
        pass
