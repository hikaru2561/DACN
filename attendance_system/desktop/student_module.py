"""
Module Quản lý Sinh viên
Chức năng: CRUD sinh viên, chụp ảnh khuôn mặt, quản lý dataset
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from api_client import APIClient
from camera_capture_module import CameraCaptureWindow
import re


# ============================================================================
# COLOR SCHEME (copy từ main.py)
# ============================================================================

COLORS = {
    "primary": "#2196F3",
    "primary_dark": "#1976D2",
    "success": "#4CAF50",
    "success_dark": "#388E3C",
    "danger": "#F44336",
    "danger_dark": "#D32F2F",
    "warning": "#FF9800",
    "info": "#00BCD4",
    "dark": "#212121",
    "light": "#FAFAFA",
    "white": "#FFFFFF",
    "text": "#212121",
    "text_secondary": "#757575",
    "border": "#E0E0E0",
}


# ============================================================================
# STUDENT MODULE WINDOW
# ============================================================================

class StudentModule:
    """Module quản lý sinh viên"""
    
    def __init__(self, parent, api_client):
        """
        Khởi tạo module
        Args:
            parent: Cửa sổ cha (Main Dashboard)
            api_client: APIClient instance
        """
        self.parent = parent
        self.api = api_client
        
        # Tạo cửa sổ mới
        self.window = tk.Toplevel(parent)
        self.window.title("Quản lý Sinh viên")
        self.window.geometry("1200x700")
        self.window.configure(bg=COLORS["light"])
        
        # Center window
        self.center_window()
        
        # Data
        self.students = []
        self.selected_student = None
        
        # Create UI
        self.create_widgets()
        
        # Load initial data
        self.load_students()
    
    def center_window(self):
        """Center window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Tạo giao diện module"""
        # ========================================================================
        # HEADER
        # ========================================================================
        header = tk.Frame(self.window, bg=COLORS["primary"], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Title
        title = tk.Label(
            header,
            text="👨‍🎓 QUẢN LÝ SINH VIÊN",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["primary"],
            fg=COLORS["white"]
        )
        title.pack(side=tk.LEFT, padx=25, pady=20)
        
        # Close button
        close_btn = tk.Button(
            header,
            text="✕ Đóng",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["danger"],
            fg=COLORS["white"],
            activebackground=COLORS["danger_dark"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.window.destroy,
            padx=20,
            pady=10
        )
        close_btn.pack(side=tk.RIGHT, padx=20)
        
        # ========================================================================
        # TOOLBAR
        # ========================================================================
        toolbar = tk.Frame(self.window, bg=COLORS["white"], height=80)
        toolbar.pack(fill=tk.X, padx=20, pady=(20, 10))
        toolbar.pack_propagate(False)
        
        # Left side - Search
        left_frame = tk.Frame(toolbar, bg=COLORS["white"])
        left_frame.pack(side=tk.LEFT, fill=tk.Y, pady=10)
        
        search_container = tk.Frame(
            left_frame,
            bg=COLORS["white"],
            highlightthickness=2,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["primary"]
        )
        search_container.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(
            search_container,
            text="🔍",
            font=("Segoe UI", 14),
            bg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=(10, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_students())
        
        search_entry = tk.Entry(
            search_container,
            textvariable=self.search_var,
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            bg=COLORS["white"],
            fg=COLORS["text"],
            width=35
        )
        search_entry.pack(side=tk.LEFT, padx=(0, 10), pady=8)
        
        # Right side - Action buttons
        right_frame = tk.Frame(toolbar, bg=COLORS["white"])
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Refresh button
        btn_refresh = tk.Button(
            right_frame,
            text="🔄",
            font=("Segoe UI", 12),
            bg=COLORS["white"],
            fg=COLORS["text"],
            activebackground=COLORS["light"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.load_students,
            width=3,
            height=1,
            bd=1,
            highlightthickness=1,
            highlightbackground=COLORS["border"]
        )
        btn_refresh.pack(side=tk.RIGHT, padx=3)
        btn_refresh.pack(side=tk.RIGHT, padx=3)
        
        # Camera button
        btn_camera = tk.Button(
            right_frame,
            text="� Chụp ảnh",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["info"],
            fg=COLORS["white"],
            activebackground="#0097A7",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.capture_photos,
            padx=18,
            pady=10
        )
        btn_camera.pack(side=tk.RIGHT, padx=3)
        
        # Edit button
        btn_edit = tk.Button(
            right_frame,
            text="✏️ Sửa",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["warning"],
            fg=COLORS["white"],
            activebackground="#F57C00",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.edit_student,
            padx=20,
            pady=10
        )
        btn_edit.pack(side=tk.RIGHT, padx=3)
        
        # Delete button
        btn_delete = tk.Button(
            right_frame,
            text="�️ Xóa",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["danger"],
            fg=COLORS["white"],
            activebackground=COLORS["danger_dark"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.delete_student,
            padx=20,
            pady=10
        )
        btn_delete.pack(side=tk.RIGHT, padx=3)
        
        # Add button (highlight)
        btn_add = tk.Button(
            right_frame,
            text="➕ Thêm mới",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["success"],
            fg=COLORS["white"],
            activebackground=COLORS["success_dark"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.add_student,
            padx=18,
            pady=10
        )
        btn_add.pack(side=tk.RIGHT, padx=3)
        
        # ========================================================================
        # TABLE (Treeview)
        # ========================================================================
        table_frame = tk.Frame(self.window, bg=COLORS["white"])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        
        # Treeview
        columns = ("STT", "MSSV", "Họ tên", "Giới tính", "Ngày sinh", "Email", "SĐT", "Ảnh")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="tree headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode="browse",
            height=20
        )
        
        # Configure scrollbars
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Column headers
        self.tree.heading("#0", text="")
        self.tree.heading("STT", text="STT")
        self.tree.heading("MSSV", text="MÃ SINH VIÊN")
        self.tree.heading("Họ tên", text="HỌ VÀ TÊN")
        self.tree.heading("Giới tính", text="GIỚI TÍNH")
        self.tree.heading("Ngày sinh", text="NGÀY SINH")
        self.tree.heading("Email", text="EMAIL")
        self.tree.heading("SĐT", text="SỐ ĐIỆN THOẠI")
        self.tree.heading("Ảnh", text="SỐ ẢNH")
        
        # Column widths
        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("STT", width=50, anchor=tk.CENTER)
        self.tree.column("MSSV", width=120, anchor=tk.CENTER)
        self.tree.column("Họ tên", width=220)
        self.tree.column("Giới tính", width=100, anchor=tk.CENTER)
        self.tree.column("Ngày sinh", width=120, anchor=tk.CENTER)
        self.tree.column("Email", width=250)
        self.tree.column("SĐT", width=130, anchor=tk.CENTER)
        self.tree.column("Ảnh", width=80, anchor=tk.CENTER)
        
        # Pack
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click
        self.tree.bind("<Double-1>", lambda e: self.edit_student())
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Treeview style
        style.configure("Treeview", 
                       background=COLORS["white"],
                       foreground=COLORS["text"],
                       rowheight=35,
                       fieldbackground=COLORS["white"],
                       font=("Segoe UI", 10),
                       borderwidth=0)
        
        style.configure("Treeview.Heading",
                       background=COLORS["primary"],
                       foreground=COLORS["white"],
                       font=("Segoe UI", 10, "bold"),
                       borderwidth=1,
                       relief="flat")
        
        style.map('Treeview.Heading',
                 background=[('active', COLORS["primary_dark"])])
        
        # Alternate row colors
        self.tree.tag_configure('oddrow', background=COLORS["white"])
        self.tree.tag_configure('evenrow', background=COLORS["light"])
        
        # ========================================================================
        # STATUS BAR
        # ========================================================================
        self.status_bar = tk.Label(
            self.window,
            text="Sẵn sàng",
            font=("Segoe UI", 9),
            bg=COLORS["light"],
            fg=COLORS["text_secondary"],
            anchor=tk.W,
            padx=20,
            pady=5
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_students(self):
        """Load danh sách sinh viên từ API"""
        try:
            self.status_bar.config(text="⏳ Đang tải danh sách sinh viên...")
            self.window.update()
            
            # Clear table
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get data from API
            students = self.api.get_students()
            
            if students is None:
                messagebox.showerror("Lỗi", "Không thể kết nối API!")
                self.status_bar.config(text="❌ Lỗi kết nối API")
                return
            
            self.students = students
            
            # Populate table with alternating colors
            for idx, student in enumerate(students):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                self.tree.insert("", tk.END, values=(
                    idx + 1,  # STT
                    student.get('student_id', ''),
                    student.get('full_name', ''),
                    student.get('gender', ''),
                    student.get('date_of_birth', '')[:10] if student.get('date_of_birth') else '',
                    student.get('email', ''),
                    student.get('phone', ''),
                    f"📷 {student.get('face_count', 0)}"
                ), tags=(tag,))
            
            self.status_bar.config(text=f"✅ Đã tải {len(students)} sinh viên")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tải dữ liệu: {str(e)}")
            self.status_bar.config(text="❌ Lỗi")
    
    def search_students(self):
        """Tìm kiếm sinh viên"""
        keyword = self.search_var.get().lower().strip()
        
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filter and display
        count = 0
        for idx, student in enumerate(self.students):
            student_id = student.get('student_id', '').lower()
            full_name = student.get('full_name', '').lower()
            
            if keyword in student_id or keyword in full_name:
                tag = 'evenrow' if count % 2 == 0 else 'oddrow'
                self.tree.insert("", tk.END, values=(
                    count + 1,  # STT
                    student.get('student_id', ''),
                    student.get('full_name', ''),
                    student.get('gender', ''),
                    student.get('date_of_birth', '')[:10] if student.get('date_of_birth') else '',
                    student.get('email', ''),
                    student.get('phone', ''),
                    f"📷 {student.get('face_count', 0)}"
                ), tags=(tag,))
                count += 1
        
        self.status_bar.config(text=f"🔍 Tìm thấy {count} sinh viên")
    
    def add_student(self):
        """Mở form thêm sinh viên"""
        StudentFormDialog(self.window, self.api, mode="add", callback=self.load_students)
    
    def edit_student(self):
        """Mở form sửa sinh viên"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sinh viên cần sửa!")
            return
        
        # Get student data
        item = self.tree.item(selected[0])
        student_id = item['values'][1]  # Column index 1 (MSSV, vì STT là 0)
        
        # Find student in list
        student_data = next((s for s in self.students if s['student_id'] == student_id), None)
        
        if student_data:
            StudentFormDialog(self.window, self.api, mode="edit", student_data=student_data, callback=self.load_students)
    
    def delete_student(self):
        """Xóa sinh viên"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sinh viên cần xóa!")
            return
        
        item = self.tree.item(selected[0])
        student_id = item['values'][1]  # Column index 1
        full_name = item['values'][2]   # Column index 2
        
        # Confirm
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa sinh viên:\n{student_id} - {full_name}?"):
            return
        
        # Delete via API
        self.status_bar.config(text="⏳ Đang xóa...")
        self.window.update()
        
        success = self.api.delete_student(student_id)
        
        if success:
            messagebox.showinfo("Thành công", "Đã xóa sinh viên!")
            self.load_students()
        else:
            messagebox.showerror("Lỗi", "Không thể xóa sinh viên!")
            self.status_bar.config(text="❌ Lỗi xóa")
    
    def capture_photos(self):
        """Mở module chụp ảnh khuôn mặt"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sinh viên cần chụp ảnh!")
            return
        
        item = self.tree.item(selected[0])
        student_id = item['values'][1]  # Column index 1
        full_name = item['values'][2]   # Column index 2
        
        # Mở cửa sổ chụp ảnh
        try:
            CameraCaptureWindow(self.window, student_id, full_name)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở camera:\n{str(e)}")



# ============================================================================
# STUDENT FORM DIALOG (Add/Edit)
# ============================================================================

class StudentFormDialog:
    """Dialog form thêm/sửa sinh viên"""
    
    def __init__(self, parent, api_client, mode="add", student_data=None, callback=None):
        """
        Args:
            parent: Cửa sổ cha
            api_client: APIClient instance
            mode: "add" hoặc "edit"
            student_data: Dữ liệu sinh viên (nếu mode="edit")
            callback: Function gọi sau khi save thành công
        """
        self.parent = parent
        self.api = api_client
        self.mode = mode
        self.student_data = student_data
        self.callback = callback
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Thêm sinh viên" if mode == "add" else "Sửa thông tin sinh viên")
        self.dialog.geometry("500x600")
        self.dialog.configure(bg=COLORS["white"])
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.center_dialog()
        
        # Create UI
        self.create_form()
    
    def center_dialog(self):
        """Center dialog"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_form(self):
        """Tạo form"""
        # Header
        header = tk.Frame(self.dialog, bg=COLORS["primary"], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="➕ THÊM SINH VIÊN MỚI" if self.mode == "add" else "✏️ SỬA THÔNG TIN SINH VIÊN",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["primary"],
            fg=COLORS["white"]
        )
        title.pack(pady=18)
        
        # Form fields
        form_frame = tk.Frame(self.dialog, bg=COLORS["white"])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # MSSV
        self.create_field(form_frame, "MSSV:", "student_id", row=0, required=True, readonly=(self.mode=="edit"))
        
        # Họ tên
        self.create_field(form_frame, "Họ tên:", "full_name", row=1, required=True)
        
        # Giới tính
        tk.Label(
            form_frame,
            text="Giới tính:",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"]
        ).grid(row=2, column=0, sticky=tk.W, pady=(15, 5))
        
        self.gender_var = tk.StringVar(value=self.student_data.get('gender', 'Nam') if self.student_data else 'Nam')
        gender_frame = tk.Frame(form_frame, bg=COLORS["white"])
        gender_frame.grid(row=2, column=1, sticky=tk.W, pady=(15, 5))
        
        tk.Radiobutton(gender_frame, text="Nam", variable=self.gender_var, value="Nam", 
                      bg=COLORS["white"], font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 15))
        tk.Radiobutton(gender_frame, text="Nữ", variable=self.gender_var, value="Nữ",
                      bg=COLORS["white"], font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 15))
        tk.Radiobutton(gender_frame, text="Khác", variable=self.gender_var, value="Khác",
                      bg=COLORS["white"], font=("Segoe UI", 10)).pack(side=tk.LEFT)
        
        # Ngày sinh
        self.create_field(form_frame, "Ngày sinh:", "date_of_birth", row=3, placeholder="YYYY-MM-DD")
        
        # Email
        self.create_field(form_frame, "Email:", "email", row=4, placeholder="student@example.com")
        
        # Số điện thoại
        self.create_field(form_frame, "Số điện thoại:", "phone", row=5, placeholder="0912345678")
        
        # Buttons
        btn_frame = tk.Frame(self.dialog, bg=COLORS["white"])
        btn_frame.pack(fill=tk.X, padx=40, pady=(0, 30))
        
        btn_save = tk.Button(
            btn_frame,
            text="💾 Lưu",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["success"],
            fg=COLORS["white"],
            activebackground=COLORS["success_dark"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.save,
            padx=30,
            pady=10
        )
        btn_save.pack(side=tk.LEFT, padx=5)
        
        btn_cancel = tk.Button(
            btn_frame,
            text="✕ Hủy",
            font=("Segoe UI", 11),
            bg=COLORS["border"],
            fg=COLORS["text"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.dialog.destroy,
            padx=30,
            pady=10
        )
        btn_cancel.pack(side=tk.LEFT, padx=5)
    
    def create_field(self, parent, label_text, field_name, row, required=False, readonly=False, placeholder=""):
        """Tạo field trong form"""
        # Label
        label = tk.Label(
            parent,
            text=label_text + (" *" if required else ""),
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"]
        )
        label.grid(row=row, column=0, sticky=tk.W, pady=(15, 5))
        
        # Entry
        entry_var = tk.StringVar()
        
        if self.student_data and field_name in self.student_data:
            value = self.student_data[field_name]
            if field_name == "date_of_birth" and value:
                value = value[:10]  # YYYY-MM-DD
            entry_var.set(value or "")
        
        entry = tk.Entry(
            parent,
            textvariable=entry_var,
            font=("Segoe UI", 10),
            bg=COLORS["light"] if readonly else COLORS["white"],
            fg=COLORS["text"],
            relief=tk.SOLID,
            bd=1,
            state="readonly" if readonly else "normal"
        )
        entry.grid(row=row, column=1, sticky=tk.EW, pady=(15, 5))
        
        # Store reference
        setattr(self, f"{field_name}_var", entry_var)
        
        # Configure grid weight
        parent.grid_columnconfigure(1, weight=1)
    
    def validate(self):
        """Validate form"""
        # MSSV
        student_id = self.student_id_var.get().strip()
        if not student_id:
            messagebox.showerror("Lỗi", "Vui lòng nhập MSSV!")
            return False
        
        if not re.match(r'^[A-Z0-9]+$', student_id):
            messagebox.showerror("Lỗi", "MSSV chỉ được chứa chữ in hoa và số!")
            return False
        
        # Họ tên
        full_name = self.full_name_var.get().strip()
        if not full_name:
            messagebox.showerror("Lỗi", "Vui lòng nhập họ tên!")
            return False
        
        # Email (optional but validate format if provided)
        email = self.email_var.get().strip()
        if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            messagebox.showerror("Lỗi", "Email không hợp lệ!")
            return False
        
        # Date of birth (optional but validate format if provided)
        dob = self.date_of_birth_var.get().strip()
        if dob and not re.match(r'^\d{4}-\d{2}-\d{2}$', dob):
            messagebox.showerror("Lỗi", "Ngày sinh phải theo định dạng YYYY-MM-DD!")
            return False
        
        return True
    
    def save(self):
        """Lưu dữ liệu"""
        if not self.validate():
            return
        
        # Prepare data
        data = {
            "student_id": self.student_id_var.get().strip(),
            "full_name": self.full_name_var.get().strip(),
            "gender": self.gender_var.get(),
            "date_of_birth": self.date_of_birth_var.get().strip() or None,
            "email": self.email_var.get().strip() or None,
            "phone": self.phone_var.get().strip() or None
        }
        
        # Call API
        try:
            if self.mode == "add":
                result = self.api.create_student(data)
            else:
                result = self.api.update_student(data["student_id"], data)
            
            if result:
                messagebox.showinfo("Thành công", "Đã lưu thông tin sinh viên!")
                self.dialog.destroy()
                
                # Callback
                if self.callback:
                    self.callback()
            else:
                messagebox.showerror("Lỗi", "Không thể lưu dữ liệu!")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lưu: {str(e)}")


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    # Test module
    root = tk.Tk()
    root.withdraw()
    
    from api_client import APIClient
    api = APIClient()
    
    StudentModule(root, api)
    root.mainloop()
