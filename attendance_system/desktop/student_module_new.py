"""
Module Quản lý Sinh viên - REDESIGNED
Giao diện: Form bên trái + Table/Search bên phải (theo UI mẫu)
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from api_client import APIClient
import re

# Import camera module nếu có
try:
    from camera_capture_module import CameraCaptureWindow
    CAMERA_AVAILABLE = True
except ImportError:
    CAMERA_AVAILABLE = False
    print("⚠️ Camera module not available")


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
    "btn_capture": "#5DADE2",
    "btn_training": "#48C9B0",
    "white": "#FFFFFF",
    "light": "#F8F9FA",
    "border": "#BDC3C7",
    "text": "#2C3E50",
    "success": "#27AE60",
    "danger": "#E74C3C",
}


# ============================================================================
# STUDENT MODULE (NEW DESIGN)
# ============================================================================

class StudentModuleNew:
    """Module quản lý sinh viên - Giao diện mẫu"""
    
    def __init__(self, parent, api_client):
        self.parent = parent
        self.api = api_client
        self.current_student = None  # Sinh viên đang được chọn
        
        # Create main window
        self.window = tk.Toplevel(parent)
        self.window.title("Quản lý thông tin sinh viên")
        self.window.geometry("1400x750")
        self.window.configure(bg=COLORS["light"])
        
        self.create_widgets()
        self.load_students()
    
    def create_widgets(self):
        """Tạo giao diện"""
        # ============================================================
        # LEFT PANEL: THÔNG TIN SINH VIÊN (FORM)
        # ============================================================
        
        left_panel = tk.Frame(self.window, bg=COLORS["white"], width=600)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        left_panel.pack_propagate(False)
        
        # Header: THÔNG TIN SINH VIÊN
        header_frame = tk.Frame(left_panel, bg=COLORS["form_header"], height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="Thông tin sinh viên",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["form_header"],
            fg=COLORS["white"]
        ).pack(pady=12)
        
        # Form container
        form_container = tk.Frame(left_panel, bg=COLORS["white"])
        form_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # === Row 1: ID Sinh viên ===
        row1 = tk.Frame(form_container, bg=COLORS["white"])
        row1.pack(fill=tk.X, pady=8)
        
        tk.Label(
            row1,
            text="ID Sinh viên:",
            font=("Segoe UI", 10),
            bg=COLORS["white"],
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.entry_id = tk.Entry(
            row1,
            font=("Segoe UI", 10),
            relief=tk.SOLID,
            borderwidth=1,
            width=10
        )
        self.entry_id.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(
            row1,
            text="Tên Sinh viên:",
            font=("Segoe UI", 10),
            bg=COLORS["white"],
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.entry_name = tk.Entry(
            row1,
            font=("Segoe UI", 10),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_name.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # === Row 2: Lớp học + CMND ===
        row2 = tk.Frame(form_container, bg=COLORS["white"])
        row2.pack(fill=tk.X, pady=8)
        
        tk.Label(
            row2,
            text="Lớp học:",
            font=("Segoe UI", 10),
            bg=COLORS["white"],
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.entry_class = tk.Entry(
            row2,
            font=("Segoe UI", 10),
            relief=tk.SOLID,
            borderwidth=1,
            width=15
        )
        self.entry_class.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(
            row2,
            text="CMND:",
            font=("Segoe UI", 10),
            bg=COLORS["white"],
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.entry_cmnd = tk.Entry(
            row2,
            font=("Segoe UI", 10),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_cmnd.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # === Row 3: Giới tính + Ngày sinh ===
        row3 = tk.Frame(form_container, bg=COLORS["white"])
        row3.pack(fill=tk.X, pady=8)
        
        tk.Label(
            row3,
            text="Giới tính:",
            font=("Segoe UI", 10),
            bg=COLORS["white"],
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        gender_frame = tk.Frame(row3, bg=COLORS["white"])
        gender_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        self.var_gender = tk.StringVar(value="Nam")
        tk.Radiobutton(
            gender_frame,
            text="Nam",
            variable=self.var_gender,
            value="Nam",
            font=("Segoe UI", 9),
            bg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(
            gender_frame,
            text="Nữ",
            variable=self.var_gender,
            value="Nữ",
            font=("Segoe UI", 9),
            bg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            row3,
            text="Ngày sinh:",
            font=("Segoe UI", 10),
            bg=COLORS["white"],
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.entry_dob = tk.Entry(
            row3,
            font=("Segoe UI", 10),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_dob.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # === Row 4: Email + SĐT ===
        row4 = tk.Frame(form_container, bg=COLORS["white"])
        row4.pack(fill=tk.X, pady=8)
        
        tk.Label(
            row4,
            text="Email:",
            font=("Segoe UI", 10),
            bg=COLORS["white"],
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.entry_email = tk.Entry(
            row4,
            font=("Segoe UI", 10),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_email.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))
        
        tk.Label(
            row4,
            text="SĐT:",
            font=("Segoe UI", 10),
            bg=COLORS["white"],
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.entry_phone = tk.Entry(
            row4,
            font=("Segoe UI", 10),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_phone.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # === Row 5: Địa chỉ ===
        row5 = tk.Frame(form_container, bg=COLORS["white"])
        row5.pack(fill=tk.X, pady=8)
        
        tk.Label(
            row5,
            text="Địa chỉ:",
            font=("Segoe UI", 10),
            bg=COLORS["white"],
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.entry_address = tk.Entry(
            row5,
            font=("Segoe UI", 10),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_address.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # === BUTTONS ROW 1: Lưu, Sửa, Xóa, Làm mới ===
        btn_row1 = tk.Frame(form_container, bg=COLORS["white"])
        btn_row1.pack(fill=tk.X, pady=20)
        
        # Center buttons
        btn_center = tk.Frame(btn_row1, bg=COLORS["white"])
        btn_center.pack(expand=True)
        
        self.btn_save = tk.Button(
            btn_center,
            text="Lưu",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_save"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.save_student,
            width=10,
            height=1,
            borderwidth=0,
            activebackground="#3498DB",
            activeforeground=COLORS["white"]
        )
        self.btn_save.pack(side=tk.LEFT, padx=8)
        
        self.btn_edit = tk.Button(
            btn_center,
            text="Sửa",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_edit"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.edit_student,
            width=10,
            height=1,
            borderwidth=0,
            activebackground="#E67E22",
            activeforeground=COLORS["white"]
        )
        self.btn_edit.pack(side=tk.LEFT, padx=8)
        
        self.btn_delete = tk.Button(
            btn_center,
            text="Xóa",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_delete"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.delete_student,
            width=10,
            height=1,
            borderwidth=0,
            activebackground="#C0392B",
            activeforeground=COLORS["white"]
        )
        self.btn_delete.pack(side=tk.LEFT, padx=8)
        
        self.btn_new = tk.Button(
            btn_center,
            text="Làm mới",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_new"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.clear_form,
            width=10,
            height=1,
            borderwidth=0,
            activebackground="#27AE60",
            activeforeground=COLORS["white"]
        )
        self.btn_new.pack(side=tk.LEFT, padx=8)
        
        # === BUTTONS ROW 2: Lấy ảnh, Training Data ===
        btn_row2 = tk.Frame(form_container, bg=COLORS["white"])
        btn_row2.pack(fill=tk.X, pady=10)
        
        # Center buttons
        btn_center2 = tk.Frame(btn_row2, bg=COLORS["white"])
        btn_center2.pack(expand=True)
        
        self.btn_capture = tk.Button(
            btn_center2,
            text="📷 Lấy ảnh sinh viên",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["btn_capture"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.capture_photos,
            width=22,
            height=2,
            borderwidth=0,
            activebackground="#3498DB",
            activeforeground=COLORS["white"]
        )
        self.btn_capture.pack(side=tk.LEFT, padx=10)
        
        self.btn_training = tk.Button(
            btn_center2,
            text="🔄 Training Data",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["btn_training"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.training_data,
            width=22,
            height=2,
            borderwidth=0,
            activebackground="#16A085",
            activeforeground=COLORS["white"]
        )
        self.btn_training.pack(side=tk.LEFT, padx=10)
        
        # ============================================================
        # RIGHT PANEL: HỆ THỐNG TÌM KIẾM + TABLE
        # ============================================================
        
        right_panel = tk.Frame(self.window, bg=COLORS["white"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header: HỆ THỐNG TÌM KIẾM
        search_header = tk.Frame(right_panel, bg=COLORS["table_header"], height=50)
        search_header.pack(fill=tk.X)
        search_header.pack_propagate(False)
        
        tk.Label(
            search_header,
            text="Hệ thống tìm kiếm",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["table_header"],
            fg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=15, pady=12)
        
        # Search controls
        search_controls = tk.Frame(right_panel, bg=COLORS["white"])
        search_controls.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(
            search_controls,
            text="Tìm kiếm theo:",
            font=("Segoe UI", 10),
            bg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_type = ttk.Combobox(
            search_controls,
            values=["ID Sinh viên", "Tên sinh viên"],
            state="readonly",
            font=("Segoe UI", 9),
            width=15
        )
        self.search_type.set("ID Sinh viên")
        self.search_type.pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_entry = tk.Entry(
            search_controls,
            font=("Segoe UI", 10),
            relief=tk.SOLID,
            borderwidth=1,
            width=30
        )
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_students())
        
        tk.Button(
            search_controls,
            text="Tìm kiếm",
            font=("Segoe UI", 10),
            bg=COLORS["btn_save"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.search_students,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            search_controls,
            text="Xem tất cả",
            font=("Segoe UI", 10),
            bg=COLORS["btn_new"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.load_students,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # Table container
        table_container = tk.Frame(right_panel, bg=COLORS["white"])
        table_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Treeview with scrollbar
        tree_scroll_y = ttk.Scrollbar(table_container, orient=tk.VERTICAL)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Define columns
        columns = ("STT", "ID","Họ tên", "Chuyên ngành", "Chương trình học", "Năm học", "Học kì",  "Lớp biên chế")
        
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
        self.tree.heading("ID", text="ID")
        self.tree.heading("Họ tên", text="Họ tên")
        self.tree.heading("Chuyên ngành", text="Chuyên ngành")
        self.tree.heading("Chương trình học", text="Chương trình học")
        self.tree.heading("Năm học", text="Năm học")
        self.tree.heading("Học kì", text="Học kì")
        self.tree.heading("Lớp biên chế", text="Lớp biên chế")
        
        # Column widths
        self.tree.column("STT", width=40, anchor=tk.CENTER)
        self.tree.column("ID", width=100, anchor=tk.CENTER)
        self.tree.column("Họ tên", width=150)
        self.tree.column("Chuyên ngành", width=100, anchor=tk.CENTER)
        self.tree.column("Chương trình học", width=120)
        self.tree.column("Năm học", width=80, anchor=tk.CENTER)
        self.tree.column("Học kì", width=80, anchor=tk.CENTER)
        self.tree.column("Lớp biên chế", width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind click event
        self.tree.bind('<ButtonRelease-1>', self.on_tree_select)
        
        # Alternating row colors
        self.tree.tag_configure('evenrow', background='#F8F9FA')
        self.tree.tag_configure('oddrow', background='#FFFFFF')
    
    def load_students(self):
        """Load tất cả sinh viên"""
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            students = self.api.get_students()
            
            for idx, student in enumerate(students, 1):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                
                self.tree.insert("", tk.END, values=(
                    idx,                                                    # STT
                    student.get('student_id', ''),                          # ID
                    student.get('full_name', ''),                           # Họ tên (FULL NAME)
                    "IT",                                                   # Chuyên ngành (placeholder)
                    "Chính quy",                                            # Chương trình học
                    "2020-21",                                              # Năm học
                    "Học kì I",                                             # Học kì
                    student.get('class_id', 'D12CNPM1')                     # Lớp biên chế
                ), tags=(tag,))
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách sinh viên:\n{str(e)}")
    
    def search_students(self):
        """Tìm kiếm sinh viên"""
        search_text = self.search_entry.get().strip()
        
        if not search_text:
            self.load_students()
            return
        
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            students = self.api.get_students()
            search_type = self.search_type.get()
            
            filtered = []
            for student in students:
                if search_type == "ID Sinh viên":
                    if search_text.lower() in student.get('student_id', '').lower():
                        filtered.append(student)
                else:  # Tên sinh viên
                    if search_text.lower() in student.get('full_name', '').lower():
                        filtered.append(student)
            
            for idx, student in enumerate(filtered, 1):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                
                self.tree.insert("", tk.END, values=(
                    idx,                                                    # STT
                    student.get('student_id', ''),                          # ID
                    student.get('full_name', ''),                           # Họ tên (FULL NAME)
                    "IT",                                                   # Chuyên ngành
                    "Chính quy",                                            # Chương trình học
                    "2020-21",                                              # Năm học
                    "Học kì I",                                             # Học kì
                    student.get('class_id', 'D12CNPM1')                     # Lớp biên chế
                ), tags=(tag,))
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tìm kiếm:\n{str(e)}")
    
    def on_tree_select(self, event):
        """Khi click vào sinh viên trong bảng → Load thông tin vào form"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        values = item['values']
        
        if len(values) < 2:
            return
        
        # Get student_id from table (column index 1)
        student_id = str(values[1])
        
        print(f"🔍 Selected student ID: {student_id}")  # Debug
        
        try:
            # Fetch full student data from API
            students = self.api.get_students()
            student = next((s for s in students if str(s.get('student_id', '')) == student_id), None)
            
            if student:
                print(f"✅ Found student: {student.get('full_name')}")  # Debug
                # IMPORTANT: Set current_student BEFORE populating form
                self.current_student = student
                self.populate_form(student)
                print(f"✅ current_student set to: {self.current_student.get('student_id')}")  # Debug
            else:
                print(f"❌ Student not found: {student_id}")  # Debug
                self.current_student = None
        
        except Exception as e:
            print(f"❌ Error loading student: {e}")  # Debug
            import traceback
            traceback.print_exc()
            self.current_student = None
    
    def populate_form(self, student):
        """Điền thông tin sinh viên vào form"""
        # Clear form first (but DON'T clear current_student)
        self.clear_form_fields_only()
        
        try:
            # ID Sinh viên
            if student.get('student_id'):
                self.entry_id.delete(0, tk.END)
                self.entry_id.insert(0, str(student['student_id']))
            
            # Tên sinh viên
            if student.get('full_name'):
                self.entry_name.delete(0, tk.END)
                self.entry_name.insert(0, str(student['full_name']))
            
            # Lớp học
            if student.get('class_id'):
                self.entry_class.delete(0, tk.END)
                self.entry_class.insert(0, str(student['class_id']))
            
            # Email
            if student.get('email'):
                self.entry_email.delete(0, tk.END)
                self.entry_email.insert(0, str(student['email']))
            
            # Phone
            if student.get('phone'):
                self.entry_phone.delete(0, tk.END)
                self.entry_phone.insert(0, str(student['phone']))
            
            # Gender
            gender = student.get('gender', 'Nam')
            self.var_gender.set(gender if gender else 'Nam')
            
            # Date of birth
            dob = student.get('date_of_birth')
            if dob:
                self.entry_dob.delete(0, tk.END)
                self.entry_dob.insert(0, str(dob))
            
            # Address (placeholder - not in database)
            # self.entry_address.delete(0, tk.END)
            # self.entry_address.insert(0, '')
            
            # CMND (placeholder - not in database)
            # self.entry_cmnd.delete(0, tk.END)
            # self.entry_cmnd.insert(0, '')
            
            print(f"✅ Form populated for: {student.get('full_name')}")
            
        except Exception as e:
            print(f"❌ Error in populate_form: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def clear_form_fields_only(self):
        """Xóa các field trong form (KHÔNG xóa current_student)"""
        try:
            self.entry_id.delete(0, tk.END)
            self.entry_name.delete(0, tk.END)
            self.entry_class.delete(0, tk.END)
            self.entry_cmnd.delete(0, tk.END)
            self.entry_dob.delete(0, tk.END)
            self.entry_email.delete(0, tk.END)
            self.entry_phone.delete(0, tk.END)
            self.entry_address.delete(0, tk.END)
            self.var_gender.set("Nam")
        except Exception as e:
            print(f"⚠️ Error clearing form fields: {e}")
    
    def clear_form(self):
        """Xóa toàn bộ form và reset current_student"""
        try:
            self.clear_form_fields_only()
            self.current_student = None
            print("✅ Form cleared and current_student reset")
        except Exception as e:
            print(f"⚠️ Error in clear_form: {e}")
    
    def save_student(self):
        """Lưu/Thêm mới sinh viên"""
        # Validate
        student_id = self.entry_id.get().strip()
        full_name = self.entry_name.get().strip()
        
        if not student_id or not full_name:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập ID và Tên sinh viên!")
            return
        
        # Prepare data
        data = {
            "student_id": student_id,
            "full_name": full_name,
            "gender": self.var_gender.get(),
            "date_of_birth": self.entry_dob.get().strip() or None,
            "email": self.entry_email.get().strip() or None,
            "phone": self.entry_phone.get().strip() or None,
            "class_id": self.entry_class.get().strip() or None,
        }
        
        try:
            if self.current_student:
                # Update existing
                self.api.update_student(student_id, data)
                messagebox.showinfo("Thành công", "Cập nhật sinh viên thành công!")
            else:
                # Create new
                self.api.create_student(data)
                messagebox.showinfo("Thành công", "Thêm sinh viên thành công!")
            
            self.load_students()
            self.clear_form()
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu sinh viên:\n{str(e)}")
    
    def edit_student(self):
        """Sửa sinh viên (tương tự save)"""
        if not self.current_student:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sinh viên cần sửa!")
            return
        
        self.save_student()
    
    def delete_student(self):
        """Xóa sinh viên"""
        if not self.current_student:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sinh viên cần xóa!")
            return
        
        student_id = self.current_student['student_id']
        confirm = messagebox.askyesno(
            "Xác nhận",
            f"Bạn có chắc muốn xóa sinh viên {student_id}?"
        )
        
        if confirm:
            try:
                self.api.delete_student(student_id)
                messagebox.showinfo("Thành công", "Xóa sinh viên thành công!")
                self.load_students()
                self.clear_form()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa sinh viên:\n{str(e)}")
    
    def capture_photos(self):
        """Chụp ảnh khuôn mặt cho sinh viên"""
        if not self.current_student:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sinh viên cần chụp ảnh!")
            return
        
        if not CAMERA_AVAILABLE:
            messagebox.showerror(
                "Lỗi",
                "Camera module chưa được cài đặt!\n\n"
                "File cần thiết: camera_capture_module.py"
            )
            return
        
        student_id = self.current_student['student_id']
        full_name = self.current_student['full_name']
        
        print(f"📷 Opening camera for: {student_id} - {full_name}")
        
        try:
            CameraCaptureWindow(self.window, student_id, full_name)
        except Exception as e:
            print(f"❌ Camera error: {e}")
            messagebox.showerror("Lỗi", f"Không thể mở camera:\n{str(e)}")
    
    def training_data(self):
        """Training data (rebuild embeddings)"""
        confirm = messagebox.askyesno(
            "Xác nhận",
            "Bạn có muốn training lại dữ liệu khuôn mặt?\n\n"
            "Quá trình này sẽ:\n"
            "- Đọc lại tất cả ảnh từ dataset\n"
            "- Tạo lại embeddings\n"
            "- Mất vài phút\n\n"
            "Tiếp tục?"
        )
        
        if not confirm:
            return
        
        try:
            # Import và khởi tạo FaceRecognitionEngine
            from attendance_module import FaceRecognitionEngine
            
            # Tạo progress dialog
            progress_window = tk.Toplevel(self.window)
            progress_window.title("Training Progress")
            progress_window.geometry("400x150")
            progress_window.resizable(False, False)
            progress_window.transient(self.window)
            
            # Center window
            progress_window.update_idletasks()
            x = (progress_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (progress_window.winfo_screenheight() // 2) - (150 // 2)
            progress_window.geometry(f"+{x}+{y}")
            
            # Progress label
            lbl_status = tk.Label(
                progress_window,
                text="Đang khởi tạo...",
                font=("Segoe UI", 11),
                pady=20
            )
            lbl_status.pack()
            
            # Progress bar (indeterminate)
            from tkinter import ttk
            progress_bar = ttk.Progressbar(
                progress_window,
                mode='indeterminate',
                length=350
            )
            progress_bar.pack(pady=10)
            progress_bar.start(10)
            
            def run_training():
                """Chạy training trong thread riêng"""
                try:
                    engine = FaceRecognitionEngine()
                    
                    def update_progress(current, total, message):
                        lbl_status.config(text=f"{message} ({current}/{total})")
                        progress_window.update()
                    
                    result = engine.build_embeddings(progress_callback=update_progress)
                    
                    progress_window.after(0, lambda: on_training_complete(result))
                    
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    progress_window.after(0, lambda: on_training_error(str(e)))
            
            def on_training_complete(result):
                """Callback khi training xong"""
                progress_bar.stop()
                progress_window.destroy()
                
                if result.get("success"):
                    messagebox.showinfo(
                        "Thành công",
                        f"Training hoàn tất!\n\n"
                        f"✅ Số sinh viên: {result['total_students']}\n"
                        f"✅ Số ảnh: {result['total_images']}\n"
                        f"⚠️ Ảnh lỗi: {result['failed_images']}"
                    )
                else:
                    messagebox.showerror(
                        "Lỗi",
                        f"Training thất bại!\n\n{result.get('error', 'Unknown error')}"
                    )
            
            def on_training_error(error_msg):
                """Callback khi có lỗi"""
                progress_bar.stop()
                progress_window.destroy()
                messagebox.showerror("Lỗi", f"Training error:\n{error_msg}")
            
            # Chạy training trong thread riêng để không block UI
            import threading
            training_thread = threading.Thread(target=run_training, daemon=True)
            training_thread.start()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Lỗi",
                f"Không thể khởi động training:\n{str(e)}"
            )


# ============================================================================
# BACKWARD COMPATIBILITY
# ============================================================================

# Alias để không phá code cũ
StudentModule = StudentModuleNew
