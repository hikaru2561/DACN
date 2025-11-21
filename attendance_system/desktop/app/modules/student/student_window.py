"""
Module Quản lý Sinh viên - REDESIGNED
Giao diện: Form bên trái + Table/Search bên phải (theo UI mẫu)
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app.core.api_client import APIClient
import re
import os
from PIL import Image, ImageTk

# Import camera module nếu có
# Import camera module nếu có
try:
    from app.modules.camera.capture import CameraCaptureWindow
    CAMERA_AVAILABLE = True
except ImportError as e:
    CAMERA_AVAILABLE = False
    print(f"⚠️ Camera module not available: {e}")


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
    "btn_cancel": "#95A5A6",
    "primary": "#3498DB",
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
        self.classes = [] # Danh sách lớp học
        
        # Create main window
        self.window = tk.Toplevel(parent)
        self.window.title("Quản lý thông tin sinh viên")
        self.window.geometry("1400x780")
        self.window.configure(bg=COLORS["light"])
        
        self.load_classes() # Load danh sách lớp trước khi tạo UI
        self.create_widgets()
        self.load_students()
        
    def load_classes(self):
        """Load danh sách lớp học từ API"""
        try:
            # Lấy danh sách lớp đang active
            classes_data = self.api.get_classes(is_active=True)
            # Chỉ lấy tên lớp để hiển thị trong combobox
            self.classes = [c.get('class_name', '') for c in classes_data]
            print(f"📋 Loaded {len(self.classes)} classes")
        except Exception as e:
            print(f"⚠️ Error loading classes: {e}")
            self.classes = []

    def create_widgets(self):
        """Tạo giao diện"""
        # ============================================================
        # LEFT PANEL: THÔNG TIN SINH VIÊN (FORM)
        # ============================================================
        
        left_panel = tk.Frame(self.window, bg=COLORS["white"], width=500)
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
        
        # --- Helper function to create labeled entry ---
        def create_entry(parent, label_text, width=None):
            frame = tk.Frame(parent, bg=COLORS["white"])
            frame.pack(fill=tk.X, pady=5)
            
            lbl = tk.Label(frame, text=label_text, font=("Segoe UI", 10), bg=COLORS["white"], width=12, anchor="w")
            lbl.pack(side=tk.LEFT)
            
            entry = tk.Entry(frame, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1)
            if width:
                entry.config(width=width)
                entry.pack(side=tk.LEFT, padx=(0, 10))
            else:
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            return entry, frame

        # === Row 1: ID & Tên ===
        self.entry_id, _ = create_entry(form_container, "ID Sinh viên:")
        self.entry_name, _ = create_entry(form_container, "Họ tên:")
        
        # === Row 2: Lớp (Combobox) ===
        row_class = tk.Frame(form_container, bg=COLORS["white"])
        row_class.pack(fill=tk.X, pady=5)
        tk.Label(row_class, text="Lớp học:", font=("Segoe UI", 10), bg=COLORS["white"], width=12, anchor="w").pack(side=tk.LEFT)
        
        self.combo_class = ttk.Combobox(row_class, values=self.classes, font=("Segoe UI", 10), state="readonly")
        self.combo_class.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # === Row 3: CMND/CCCD ===
        self.entry_national_id, _ = create_entry(form_container, "CMND/CCCD:")
        
        # === Row 4: Giới tính & Ngày sinh ===
        row_gender_dob = tk.Frame(form_container, bg=COLORS["white"])
        row_gender_dob.pack(fill=tk.X, pady=5)
        
        tk.Label(row_gender_dob, text="Giới tính:", font=("Segoe UI", 10), bg=COLORS["white"], width=12, anchor="w").pack(side=tk.LEFT)
        
        gender_frame = tk.Frame(row_gender_dob, bg=COLORS["white"])
        gender_frame.pack(side=tk.LEFT)
        self.var_gender = tk.StringVar(value="Nam")
        tk.Radiobutton(gender_frame, text="Nam", variable=self.var_gender, value="Nam", bg=COLORS["white"]).pack(side=tk.LEFT)
        tk.Radiobutton(gender_frame, text="Nữ", variable=self.var_gender, value="Nữ", bg=COLORS["white"]).pack(side=tk.LEFT)
        
        tk.Label(row_gender_dob, text="Ngày sinh:", font=("Segoe UI", 10), bg=COLORS["white"], width=10, anchor="e").pack(side=tk.LEFT, padx=(10, 5))
        self.entry_dob = tk.Entry(row_gender_dob, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1, width=15)
        self.entry_dob.pack(side=tk.LEFT)
        
        # === Row 5: Email & SĐT ===
        self.entry_email, _ = create_entry(form_container, "Email:")
        self.entry_phone, _ = create_entry(form_container, "SĐT:")
        
        # === Row 6: Địa chỉ ===
        self.entry_address, _ = create_entry(form_container, "Địa chỉ:")
        
        # === Row 7: Chuyên ngành & Năm học ===
        self.entry_major, _ = create_entry(form_container, "Chuyên ngành:")
        self.entry_academic_year, _ = create_entry(form_container, "Năm học:")
        
        # === BUTTONS ===
        btn_frame = tk.Frame(form_container, bg=COLORS["white"])
        btn_frame.pack(fill=tk.X, pady=20)
        
        # Helper for buttons
        def create_btn(parent, text, color, cmd):
            return tk.Button(parent, text=text, font=("Segoe UI", 10, "bold"), bg=color, fg=COLORS["white"], 
                             relief=tk.FLAT, cursor="hand2", command=cmd, width=10, pady=5)

        center_btns = tk.Frame(btn_frame, bg=COLORS["white"])
        center_btns.pack(expand=True)
        
        self.btn_save = create_btn(center_btns, "Lưu", COLORS["btn_save"], self.save_student)
        self.btn_save.pack(side=tk.LEFT, padx=5)
        
        self.btn_edit = create_btn(center_btns, "Sửa", COLORS["btn_edit"], self.edit_student)
        self.btn_edit.pack(side=tk.LEFT, padx=5)
        
        self.btn_delete = create_btn(center_btns, "Xóa", COLORS["btn_delete"], self.delete_student)
        self.btn_delete.pack(side=tk.LEFT, padx=5)
        
        self.btn_new = create_btn(center_btns, "Làm mới", COLORS["btn_new"], self.clear_form)
        self.btn_new.pack(side=tk.LEFT, padx=5)
        
        # === EXTRA BUTTONS ===
        extra_btns = tk.Frame(form_container, bg=COLORS["white"])
        extra_btns.pack(fill=tk.X, pady=10)
        center_extra = tk.Frame(extra_btns, bg=COLORS["white"])
        center_extra.pack(expand=True)
        
        self.btn_capture = tk.Button(center_extra, text="📷 Lấy ảnh", font=("Segoe UI", 11, "bold"), bg=COLORS["btn_capture"], fg="white", relief=tk.FLAT, command=self.capture_photos, width=15, pady=5)
        self.btn_capture.pack(side=tk.LEFT, padx=5)
        
        self.btn_training = tk.Button(center_extra, text="🔄 Training", font=("Segoe UI", 11, "bold"), bg=COLORS["btn_training"], fg="white", relief=tk.FLAT, command=self.training_data, width=15, pady=5)
        self.btn_training.pack(side=tk.LEFT, padx=5)

        self.btn_view_images = tk.Button(center_extra, text="🖼️ Xem ảnh", font=("Segoe UI", 11, "bold"), bg=COLORS["btn_edit"], fg="white", relief=tk.FLAT, command=self.view_student_images, width=15, pady=5)
        self.btn_view_images.pack(side=tk.LEFT, padx=5)

        # ============================================================
        # RIGHT PANEL: HỆ THỐNG TÌM KIẾM + TABLE
        # ============================================================
        
        right_panel = tk.Frame(self.window, bg=COLORS["white"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        search_header = tk.Frame(right_panel, bg=COLORS["table_header"], height=50)
        search_header.pack(fill=tk.X)
        search_header.pack_propagate(False)
        tk.Label(search_header, text="Danh sách sinh viên", font=("Segoe UI", 14, "bold"), bg=COLORS["table_header"], fg=COLORS["white"]).pack(side=tk.LEFT, padx=15, pady=12)
        
        # Search
        search_controls = tk.Frame(right_panel, bg=COLORS["white"])
        search_controls.pack(fill=tk.X, padx=15, pady=15)
        
        self.search_type = ttk.Combobox(search_controls, values=["ID Sinh viên", "Tên sinh viên"], state="readonly", width=15)
        self.search_type.set("ID Sinh viên")
        self.search_type.pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_entry = tk.Entry(search_controls, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_students())
        
        tk.Button(search_controls, text="Tìm kiếm", bg=COLORS["btn_save"], fg="white", relief=tk.FLAT, command=self.search_students).pack(side=tk.LEFT, padx=5)
        tk.Button(search_controls, text="Tất cả", bg=COLORS["btn_new"], fg="white", relief=tk.FLAT, command=self.load_students).pack(side=tk.LEFT, padx=5)
        
        # Table
        table_container = tk.Frame(right_panel, bg=COLORS["white"])
        table_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        tree_scroll_y = ttk.Scrollbar(table_container, orient=tk.VERTICAL)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Updated Columns
        columns = ("STT", "ID", "Họ tên", "Lớp", "CMND", "SĐT", "Chuyên ngành", "Năm học")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set, height=20)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Headings
        for col in columns:
            self.tree.heading(col, text=col)
            
        # Widths
        self.tree.column("STT", width=40, anchor=tk.CENTER)
        self.tree.column("ID", width=80, anchor=tk.CENTER)
        self.tree.column("Họ tên", width=150)
        self.tree.column("Lớp", width=80, anchor=tk.CENTER)
        self.tree.column("CMND", width=100)
        self.tree.column("SĐT", width=100)
        self.tree.column("Chuyên ngành", width=100)
        self.tree.column("Năm học", width=80, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<ButtonRelease-1>', self.on_tree_select)
        self.tree.tag_configure('evenrow', background='#F8F9FA')
        self.tree.tag_configure('oddrow', background='#FFFFFF')

    def load_students(self):
        """Load tất cả sinh viên"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            students = self.api.get_students()
            for idx, s in enumerate(students, 1):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                self.tree.insert("", tk.END, values=(
                    idx,
                    s.get('student_id', ''),
                    s.get('full_name', ''),
                    s.get('class_name', ''), 
                    s.get('national_id', ''),
                    s.get('phone', ''),
                    s.get('major', ''),
                    s.get('academic_year', '')
                ), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách sinh viên:\n{str(e)}")

    def search_students(self):
        """Tìm kiếm sinh viên"""
        search_text = self.search_entry.get().strip().lower()
        if not search_text:
            self.load_students()
            return
            
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            students = self.api.get_students()
            search_type = self.search_type.get()
            
            filtered = []
            for s in students:
                val = s.get('student_id', '') if search_type == "ID Sinh viên" else s.get('full_name', '')
                if search_text in str(val).lower():
                    filtered.append(s)
            
            for idx, s in enumerate(filtered, 1):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                self.tree.insert("", tk.END, values=(
                    idx,
                    s.get('student_id', ''),
                    s.get('full_name', ''),
                    s.get('class_name', ''),
                    s.get('national_id', ''),
                    s.get('phone', ''),
                    s.get('major', ''),
                    s.get('academic_year', '')
                ), tags=(tag,))
        except Exception as e:
            print(f"Search error: {e}")

    def on_tree_select(self, event):
        """Khi click vào sinh viên trong bảng"""
        selected = self.tree.selection()
        if not selected: return
        
        item = self.tree.item(selected[0])
        values = item['values']
        if len(values) < 2: return
        
        student_id = str(values[1])
        try:
            students = self.api.get_students()
            student = next((s for s in students if str(s.get('student_id', '')) == student_id), None)
            if student:
                self.current_student = student
                self.populate_form(student)
        except Exception as e:
            print(f"Error selecting student: {e}")

    def populate_form(self, student):
        """Điền thông tin vào form"""
        self.clear_form_fields_only()
        try:
            self.entry_id.insert(0, str(student.get('student_id', '')))
            self.entry_name.insert(0, str(student.get('full_name', '')))
            self.combo_class.set(str(student.get('class_name', '')))
            self.entry_national_id.insert(0, str(student.get('national_id', '')))
            self.entry_dob.insert(0, str(student.get('date_of_birth', '')))
            self.entry_email.insert(0, str(student.get('email', '')))
            self.entry_phone.insert(0, str(student.get('phone', '')))
            self.entry_address.insert(0, str(student.get('address', '')))
            self.entry_major.insert(0, str(student.get('major', '')))
            self.entry_academic_year.insert(0, str(student.get('academic_year', '')))
            
            gender = student.get('gender', 'Nam')
            self.var_gender.set(gender if gender else 'Nam')
        except Exception as e:
            print(f"Error populating form: {e}")

    def clear_form_fields_only(self):
        """Xóa các field"""
        self.entry_id.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)
        self.combo_class.set('')
        self.entry_national_id.delete(0, tk.END)
        self.entry_dob.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)
        self.entry_address.delete(0, tk.END)
        self.entry_major.delete(0, tk.END)
        self.entry_academic_year.delete(0, tk.END)
        self.var_gender.set("Nam")

    def clear_form(self):
        self.clear_form_fields_only()
        self.current_student = None

    def save_student(self):
        """Lưu sinh viên"""
        student_id = self.entry_id.get().strip()
        full_name = self.entry_name.get().strip()
        
        if not student_id or not full_name:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập ID và Tên sinh viên!")
            return
            
        data = {
            "student_id": student_id,
            "full_name": full_name,
            "class_name": self.combo_class.get().strip() or None,
            "national_id": self.entry_national_id.get().strip() or None,
            "gender": self.var_gender.get(),
            "date_of_birth": self.entry_dob.get().strip() or None,
            "email": self.entry_email.get().strip() or None,
            "phone": self.entry_phone.get().strip() or None,
            "address": self.entry_address.get().strip() or None,
            "major": self.entry_major.get().strip() or None,
            "academic_year": self.entry_academic_year.get().strip() or None
        }
        
        try:
            if self.current_student:
                self.api.update_student(student_id, data)
                messagebox.showinfo("Thành công", "Cập nhật thành công!")
            else:
                self.api.create_student(data)
                messagebox.showinfo("Thành công", "Thêm mới thành công!")
            self.load_students()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu:\n{str(e)}")

    def edit_student(self):
        if not self.current_student:
            messagebox.showwarning("Cảnh báo", "Chọn sinh viên cần sửa!")
            return
        self.save_student()

    def delete_student(self):
        if not self.current_student:
            messagebox.showwarning("Cảnh báo", "Chọn sinh viên cần xóa!")
            return
        
        sid = self.current_student['student_id']
        if messagebox.askyesno("Xác nhận", f"Xóa sinh viên {sid}?"):
            try:
                self.api.delete_student(sid)
                messagebox.showinfo("Thành công", "Đã xóa!")
                self.load_students()
                self.clear_form()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa:\n{str(e)}")

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
            # 🔥 TRUYỀN CALLBACK để extract embeddings ngay sau khi chụp xong
            CameraCaptureWindow(
                self.window, 
                student_id, 
                full_name,
                on_complete=self.on_capture_complete  # ← Callback
            )
        except Exception as e:
            print(f"❌ Camera error: {e}")
            messagebox.showerror("Lỗi", f"Không thể mở camera:\n{str(e)}")
    
    def on_capture_complete(self, student_id):
        """Callback khi chụp ảnh hoàn thành - Tự động extract embeddings"""
        print(f"\n🎯 Capture complete for {student_id}. Starting embedding extraction...")
        
        try:
            # Import FaceRecognitionEngine
            from attendance_module import FaceRecognitionEngine
            
            # Tạo progress window
            progress_window = tk.Toplevel(self.window)
            progress_window.title("Trích xuất Embeddings")
            progress_window.geometry("450x150")
            progress_window.resizable(False, False)
            progress_window.transient(self.window)
            progress_window.grab_set()
            
            # Center
            progress_window.update_idletasks()
            x = (progress_window.winfo_screenwidth() // 2) - (450 // 2)
            y = (progress_window.winfo_screenheight() // 2) - (150 // 2)
            progress_window.geometry(f"+{x}+{y}")
            
            # Status label
            lbl_status = tk.Label(
                progress_window,
                text=f"Đang trích xuất embeddings cho {student_id}...",
                font=("Segoe UI", 11),
                pady=20,
                wraplength=400
            )
            lbl_status.pack()
            
            # Progress bar
            from tkinter import ttk
            progress_bar = ttk.Progressbar(
                progress_window,
                mode='determinate',
                length=400
            )
            progress_bar.pack(pady=10)
            
            def update_progress(current, total, message):
                """Update progress callback"""
                lbl_status.config(text=f"{message}")
                progress_bar['value'] = (current / total) * 100
                progress_window.update()
            
            def run_extraction():
                """Chạy extraction trong thread"""
                try:
                    engine = FaceRecognitionEngine()
                    
                    # 🔥 CHỈ EXTRACT CHO 1 SINH VIÊN (không rebuild toàn bộ)
                    result = engine.add_student_embeddings(
                        student_id, 
                        progress_callback=update_progress
                    )
                    
                    # Close progress window
                    progress_window.destroy()
                    
                    # Show result
                    if result['success']:
                        messagebox.showinfo(
                            "Thành công",
                            f"✅ Đã trích xuất embeddings!\n\n"
                            f"Sinh viên: {student_id}\n"
                            f"Ảnh xử lý: {result['images_processed']}\n"
                            f"Ảnh lỗi: {result['images_failed']}\n\n"
                            f"{result['message']}"
                        )
                    else:
                        messagebox.showerror(
                            "Lỗi",
                            f"❌ Trích xuất thất bại!\n\n{result['message']}"
                        )
                        
                except Exception as e:
                    progress_window.destroy()
                    messagebox.showerror("Lỗi", f"Lỗi trích xuất embeddings:\n{str(e)}")
                    import traceback
                    traceback.print_exc()
            
            # Run in thread
            from threading import Thread
            Thread(target=run_extraction, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể trích xuất embeddings:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def training_data(self):
        """Training data - Trích xuất embeddings cho sinh viên hiện tại"""
        # Kiểm tra đã chọn sinh viên chưa
        if not self.current_student:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sinh viên cần training!")
            return
        
        student_id = self.current_student['student_id']
        full_name = self.current_student['full_name']
        
        confirm = messagebox.askyesno(
            "Xác nhận",
            f"Trích xuất embeddings cho sinh viên:\n\n"
            f"MSSV: {student_id}\n"
            f"Họ tên: {full_name}\n\n"
            "Quá trình này sẽ:\n"
            "- Đọc tất cả ảnh của sinh viên này\n"
            "- Trích xuất embeddings\n"
            "- Cập nhật vào database\n\n"
            "Tiếp tục?"
        )
        
        if not confirm:
            return
        
        try:
            # Import FaceRecognitionEngine
            from attendance_module import FaceRecognitionEngine
            
            # Tạo progress dialog
            progress_window = tk.Toplevel(self.window)
            progress_window.title("Trích xuất Embeddings")
            progress_window.geometry("450x150")
            progress_window.resizable(False, False)
            progress_window.transient(self.window)
            progress_window.grab_set()
            
            # Center window
            progress_window.update_idletasks()
            x = (progress_window.winfo_screenwidth() // 2) - (450 // 2)
            y = (progress_window.winfo_screenheight() // 2) - (150 // 2)
            progress_window.geometry(f"+{x}+{y}")
            
            # Progress label
            lbl_status = tk.Label(
                progress_window,
                text=f"Đang trích xuất cho {student_id}...",
                font=("Segoe UI", 11),
                pady=20,
                wraplength=400
            )
            lbl_status.pack()
            
            # Progress bar
            from tkinter import ttk
            progress_bar = ttk.Progressbar(
                progress_window,
                mode='determinate',
                length=400
            )
            progress_bar.pack(pady=10)
            
            def update_progress(current, total, message):
                lbl_status.config(text=message)
                progress_bar['value'] = (current / total) * 100
                progress_window.update()
            
            def run_training():
                """Chạy training trong thread riêng"""
                try:
                    engine = FaceRecognitionEngine()
                    
                    # 🔥 CHỈ EXTRACT CHO SINH VIÊN HIỆN TẠI
                    result = engine.add_student_embeddings(
                        student_id,
                        progress_callback=update_progress
                    )
                    
                    progress_window.after(0, lambda: on_training_complete(result))
                    
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    progress_window.after(0, lambda: on_training_error(str(e)))
            
            def on_training_complete(result):
                """Callback khi training xong"""
                progress_window.destroy()
                
                if result.get("success"):
                    messagebox.showinfo(
                        "Thành công",
                        f"✅ Trích xuất embeddings hoàn tất!\n\n"
                        f"Sinh viên: {student_id}\n"
                        f"Họ tên: {full_name}\n"
                        f"Ảnh xử lý: {result['images_processed']}\n"
                        f"Ảnh lỗi: {result['images_failed']}\n\n"
                        f"{result['message']}"
                    )
                else:
                    messagebox.showerror(
                        "Lỗi",
                        f"❌ Trích xuất thất bại!\n\n{result.get('message', 'Unknown error')}"
                    )
            
            def on_training_error(error_msg):
                """Callback khi có lỗi"""
                progress_window.destroy()
                messagebox.showerror("Lỗi", f"Lỗi trích xuất:\n{error_msg}")
            
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
    
    def view_student_images(self):
        """Xem và quản lý ảnh của sinh viên đã chọn"""
        if not self.current_student:
            messagebox.showwarning(
                "Chưa chọn sinh viên",
                "Vui lòng chọn sinh viên từ danh sách!"
            )
            return
        
        student_id = self.current_student.get('student_id')
        full_name = self.current_student.get('full_name', 'Unknown')
        
        # Đường dẫn thư mục ảnh sinh viên (dùng config)
        from app.core.config import PATHS
        student_folder = PATHS["raw_dir"] / student_id
        student_folder = str(student_folder)  # Convert Path to string
        
        if not os.path.exists(student_folder):
            messagebox.showinfo(
                "Chưa có ảnh",
                f"Sinh viên {full_name} ({student_id}) chưa có ảnh nào.\n\n"
                "Vui lòng sử dụng '📷 Lấy ảnh sinh viên' để chụp ảnh."
            )
            return
        
        # Lấy danh sách file ảnh
        image_files = [f for f in os.listdir(student_folder) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if not image_files:
            messagebox.showinfo(
                "Chưa có ảnh",
                f"Thư mục của sinh viên {full_name} ({student_id}) không có ảnh nào."
            )
            return
        
        # Tạo cửa sổ xem ảnh
        ImageViewerWindow(self.window, student_id, full_name, student_folder, image_files)


# ============================================================================
# IMAGE VIEWER WINDOW
# ============================================================================

class ImageViewerWindow:
    """Cửa sổ xem và quản lý ảnh sinh viên"""
    
    def __init__(self, parent, student_id, full_name, folder_path, image_files):
        self.parent = parent
        self.student_id = student_id
        self.full_name = full_name
        self.folder_path = folder_path
        self.image_files = image_files
        self.selected_images = set()  # Set của các ảnh được chọn để xóa
        
        # Tạo window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Ảnh của sinh viên: {full_name} ({student_id})")
        self.window.geometry("1200x800")
        self.window.configure(bg=COLORS["light"])
        self.window.transient(parent)
        
        self.create_ui()
        self.load_images()
    
    def create_ui(self):
        """Tạo giao diện"""
        # Header
        header = tk.Frame(self.window, bg=COLORS["primary"], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text=f"📷 Ảnh của sinh viên: {self.full_name}",
            font=("Segoe UI", 16, "bold"),
            bg=COLORS["primary"],
            fg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(
            header,
            text=f"Tổng: {len(self.image_files)} ảnh",
            font=("Segoe UI", 12),
            bg=COLORS["primary"],
            fg=COLORS["white"]
        ).pack(side=tk.RIGHT, padx=20)
        
        # Button frame
        btn_frame = tk.Frame(self.window, bg=COLORS["light"])
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            btn_frame,
            text="🗑️ Xóa ảnh đã chọn",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_delete"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.delete_selected,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=20)
        
        tk.Button(
            btn_frame,
            text="🔄 Làm mới",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_new"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.refresh_images,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="✕ Đóng",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["btn_cancel"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.window.destroy,
            padx=20,
            pady=10
        ).pack(side=tk.RIGHT, padx=20)
        
        # Scrollable canvas cho grid ảnh
        canvas_container = tk.Frame(self.window, bg=COLORS["white"])
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas và scrollbar
        self.canvas = tk.Canvas(canvas_container, bg=COLORS["white"], highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar_x = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS["white"])
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Pack scrollbars và canvas
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mouse wheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Scroll với mouse wheel"""
        try:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except Exception:
            pass
    
    def load_images(self):
        """Load và hiển thị ảnh dạng grid"""
        # Clear previous images
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.selected_images.clear()
        self.image_refs = []  # Giữ reference để không bị garbage collected
        
        # Grid layout: 5 cột
        cols = 5
        img_width = 200
        img_height = 200
        
        for idx, filename in enumerate(self.image_files):
            row = idx // cols
            col = idx % cols
            
            image_path = os.path.join(self.folder_path, filename)
            
            # Frame cho mỗi ảnh
            img_frame = tk.Frame(
                self.scrollable_frame,
                bg=COLORS["white"],
                relief=tk.RAISED,
                borderwidth=2
            )
            img_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            try:
                # Load và resize ảnh
                img = Image.open(image_path)
                img.thumbnail((img_width, img_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # Label hiển thị ảnh
                img_label = tk.Label(
                    img_frame,
                    image=photo,
                    bg=COLORS["white"],
                    cursor="hand2"
                )
                img_label.image = photo  # Keep reference
                img_label.pack(padx=5, pady=5)
                self.image_refs.append(photo)
                
                # Checkbox để chọn ảnh
                var = tk.BooleanVar()
                checkbox = tk.Checkbutton(
                    img_frame,
                    text=filename,
                    variable=var,
                    font=("Segoe UI", 9),
                    bg=COLORS["white"],
                    command=lambda f=filename, v=var: self.toggle_selection(f, v)
                )
                checkbox.pack(pady=5)
                
                # Click vào ảnh để toggle checkbox
                img_label.bind('<Button-1>', lambda e, cb=checkbox: cb.invoke())
                
            except Exception as e:
                print(f"❌ Error loading image {filename}: {e}")
                tk.Label(
                    img_frame,
                    text=f"Lỗi:\n{filename}",
                    font=("Segoe UI", 9),
                    bg=COLORS["white"],
                    fg=COLORS["danger"]
                ).pack(padx=5, pady=5)
    
    def toggle_selection(self, filename, var):
        """Toggle chọn/bỏ chọn ảnh"""
        if var.get():
            self.selected_images.add(filename)
        else:
            self.selected_images.discard(filename)
    
    def delete_selected(self):
        """Xóa các ảnh đã chọn"""
        if not self.selected_images:
            messagebox.showwarning(
                "Chưa chọn ảnh",
                "Vui lòng chọn ít nhất 1 ảnh để xóa!"
            )
            return
        
        confirm = messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc muốn xóa {len(self.selected_images)} ảnh đã chọn?\n\n"
            "⚠️ Hành động này không thể hoàn tác!"
        )
        
        if not confirm:
            return
        
        # Xóa file
        deleted = 0
        failed = []
        
        for filename in self.selected_images:
            try:
                file_path = os.path.join(self.folder_path, filename)
                os.remove(file_path)
                self.image_files.remove(filename)
                deleted += 1
            except Exception as e:
                print(f"❌ Error deleting {filename}: {e}")
                failed.append(filename)
        
        # Hiển thị kết quả
        if failed:
            messagebox.showwarning(
                "Xóa một phần",
                f"✅ Đã xóa: {deleted} ảnh\n"
                f"❌ Thất bại: {len(failed)} ảnh\n\n"
                f"Ảnh lỗi: {', '.join(failed)}"
            )
        else:
            messagebox.showinfo(
                "Thành công",
                f"✅ Đã xóa {deleted} ảnh!"
            )
        
        # Refresh danh sách
        self.refresh_images()
    
    def refresh_images(self):
        """Làm mới danh sách ảnh"""
        # Đọc lại danh sách file
        self.image_files = [f for f in os.listdir(self.folder_path) 
                           if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if not self.image_files:
            messagebox.showinfo(
                "Không còn ảnh",
                f"Thư mục của sinh viên {self.full_name} đã hết ảnh."
            )
            self.window.destroy()
            return
        
        # Load lại ảnh
        self.load_images()


# ============================================================================
# BACKWARD COMPATIBILITY
# ============================================================================

# Alias để không phá code cũ
StudentModule = StudentModuleNew
