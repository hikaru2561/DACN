"""
Module Quản lý Môn học (Subjects)
Chức năng: CRUD đầy đủ cho môn học
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app.core.api_client import APIClient
import re

# ============================================================================
# COLOR SCHEME
# ============================================================================

COLORS = {
    "form_header": "#F39C12", # Orange for Subjects
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
# SUBJECT MANAGEMENT WINDOW
# ============================================================================

class SubjectManagementWindow:
    """Cửa sổ quản lý môn học"""
    
    def __init__(self, parent, api_client):
        self.parent = parent
        self.api = api_client
        self.current_subject = None
        
        # Tạo window
        self.window = tk.Toplevel(parent)
        self.window.title("Quản lý Môn học")
        self.window.geometry("1400x800")
        self.window.configure(bg=COLORS["light"])
        
        # Remove transient to allow minimize/maximize
        # self.window.transient(parent)
        
        self.create_ui()
        self.load_subjects()
    
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
            text="Thông tin môn học",
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
        self.entry_subject_id = create_entry(form_container, "Mã môn *:")
        self.entry_subject_name = create_entry(form_container, "Tên môn *:")
        self.entry_credits = create_entry(form_container, "Số tín chỉ *:", "3")
        
        # Mô tả (Text area)
        tk.Label(form_container, text="Mô tả:", font=("Segoe UI", 10), bg=COLORS["white"], anchor="w").pack(fill=tk.X, pady=(10, 5))
        self.text_description = tk.Text(form_container, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1, height=5)
        self.text_description.pack(fill=tk.X)
        
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
        
        create_btn(center_btns, "Lưu", COLORS["btn_save"], self.save_subject).pack(side=tk.LEFT, padx=5)
        create_btn(center_btns, "Sửa", COLORS["btn_edit"], self.edit_subject).pack(side=tk.LEFT, padx=5)
        create_btn(center_btns, "Xóa", COLORS["btn_delete"], self.delete_subject).pack(side=tk.LEFT, padx=5)
        create_btn(center_btns, "Làm mới", COLORS["btn_new"], self.clear_form).pack(side=tk.LEFT, padx=5)

        # ============================================================
        # RIGHT PANEL: DANH SÁCH MÔN HỌC
        # ============================================================
        right_panel = tk.Frame(self.window, bg=COLORS["white"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        search_header = tk.Frame(right_panel, bg=COLORS["table_header"], height=50)
        search_header.pack(fill=tk.X)
        search_header.pack_propagate(False)
        tk.Label(search_header, text="Danh sách môn học", font=("Segoe UI", 14, "bold"), bg=COLORS["table_header"], fg=COLORS["white"]).pack(side=tk.LEFT, padx=15, pady=12)
        
        # Search
        search_controls = tk.Frame(right_panel, bg=COLORS["white"])
        search_controls.pack(fill=tk.X, padx=15, pady=15)
        
        self.entry_search = tk.Entry(search_controls, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1, width=30)
        self.entry_search.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_search.bind('<Return>', lambda e: self.search_subjects())
        
        tk.Button(search_controls, text="Tìm kiếm", bg=COLORS["btn_save"], fg="white", relief=tk.FLAT, command=self.search_subjects).pack(side=tk.LEFT, padx=5)
        tk.Button(search_controls, text="Tất cả", bg=COLORS["btn_new"], fg="white", relief=tk.FLAT, command=self.load_subjects).pack(side=tk.LEFT, padx=5)
        
        # Table
        table_container = tk.Frame(right_panel, bg=COLORS["white"])
        table_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        tree_scroll_y = ttk.Scrollbar(table_container, orient=tk.VERTICAL)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ("STT", "Mã môn", "Tên môn học", "Tín chỉ", "Trạng thái", "Ngày tạo")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set, height=20)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        for col in columns:
            self.tree.heading(col, text=col)
            
        self.tree.column("STT", width=50, anchor=tk.CENTER)
        self.tree.column("Mã môn", width=100, anchor=tk.CENTER)
        self.tree.column("Tên môn học", width=300)
        self.tree.column("Tín chỉ", width=80, anchor=tk.CENTER)
        self.tree.column("Trạng thái", width=120, anchor=tk.CENTER)
        self.tree.column("Ngày tạo", width=150, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<ButtonRelease-1>', self.on_tree_select)
        self.tree.tag_configure('evenrow', background='#F8F9FA')
        self.tree.tag_configure('oddrow', background='#FFFFFF')
        self.tree.tag_configure('inactive', foreground='#95A5A6')

    def load_subjects(self):
        """Load danh sách môn học"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            subjects = self.api.get_subjects()
            for idx, subject in enumerate(subjects, 1):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                tags = [tag]
                if not subject.get('is_active', True):
                    tags.append('inactive')
                
                status = "Hoạt động" if subject.get('is_active', True) else "Ngừng"
                created_at = subject.get('created_at', '')
                if created_at:
                    try:
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime('%d/%m/%Y')
                    except: pass
                
                self.tree.insert("", tk.END, values=(
                    idx,
                    subject.get('subject_id', ''),
                    subject.get('subject_name', ''),
                    subject.get('credits', 3),
                    status,
                    created_at
                ), tags=tuple(tags))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách môn học:\n{str(e)}")

    def search_subjects(self):
        """Tìm kiếm môn học"""
        search_term = self.entry_search.get().strip().lower()
        if not search_term:
            self.load_subjects()
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            subjects = self.api.get_subjects()
            filtered = [s for s in subjects 
                       if search_term in str(s.get('subject_id', '')).lower() 
                       or search_term in str(s.get('subject_name', '')).lower()]
            
            for idx, subject in enumerate(filtered, 1):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                tags = [tag]
                if not subject.get('is_active', True):
                    tags.append('inactive')
                
                status = "Hoạt động" if subject.get('is_active', True) else "Ngừng"
                created_at = subject.get('created_at', '')
                if created_at:
                    try:
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime('%d/%m/%Y')
                    except: pass
                
                self.tree.insert("", tk.END, values=(
                    idx,
                    subject.get('subject_id', ''),
                    subject.get('subject_name', ''),
                    subject.get('credits', 3),
                    status,
                    created_at
                ), tags=tuple(tags))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tìm kiếm:\n{str(e)}")

    def on_tree_select(self, event):
        """Xử lý khi chọn môn học từ table"""
        selected = self.tree.selection()
        if not selected: return
        
        item = self.tree.item(selected[0])
        values = item['values']
        if len(values) < 2: return
        
        subject_id = str(values[1])
        try:
            subject = self.api.get_subject(subject_id)
            if subject:
                self.current_subject = subject
                self.populate_form(subject)
        except Exception as e:
            print(f"❌ Error loading subject: {e}")

    def populate_form(self, subject):
        """Điền thông tin môn học vào form"""
        self.clear_form_fields_only()
        try:
            self.entry_subject_id.insert(0, str(subject.get('subject_id', '')))
            self.entry_subject_id.config(state='readonly')
            self.entry_subject_name.insert(0, str(subject.get('subject_name', '')))
            self.entry_credits.delete(0, tk.END)
            self.entry_credits.insert(0, str(subject.get('credits', '3')))
            self.text_description.insert('1.0', str(subject.get('description', '')))
            self.var_active.set(subject.get('is_active', True))
        except Exception as e:
            print(f"❌ Error in populate_form: {e}")

    def clear_form_fields_only(self):
        """Xóa các field trong form"""
        self.entry_subject_id.config(state='normal')
        self.entry_subject_id.delete(0, tk.END)
        self.entry_subject_name.delete(0, tk.END)
        self.entry_credits.delete(0, tk.END)
        self.entry_credits.insert(0, "3")
        self.text_description.delete('1.0', tk.END)
        self.var_active.set(True)

    def clear_form(self):
        """Làm mới form"""
        self.clear_form_fields_only()
        self.current_subject = None
        self.tree.selection_remove(*self.tree.selection())

    def validate_form(self):
        """Validate dữ liệu form"""
        subject_id = self.entry_subject_id.get().strip()
        subject_name = self.entry_subject_name.get().strip()
        credits = self.entry_credits.get().strip()
        
        if not subject_id or not subject_name or not credits:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ Mã môn, Tên môn và Số tín chỉ!")
            return False
            
        if not re.match(r'^[A-Za-z0-9]+$', subject_id):
            messagebox.showwarning("Mã không hợp lệ", "Mã môn học chỉ được chứa chữ cái và số!")
            return False
            
        try:
            c = int(credits)
            if c <= 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Lỗi", "Số tín chỉ phải là số nguyên dương!")
            return False
            
        return True

    def save_subject(self):
        """Lưu môn học mới"""
        if not self.validate_form(): return
        
        data = {
            "subject_id": self.entry_subject_id.get().strip().upper(),
            "subject_name": self.entry_subject_name.get().strip(),
            "credits": int(self.entry_credits.get().strip()),
            "description": self.text_description.get('1.0', tk.END).strip(),
            "is_active": self.var_active.get()
        }
        
        try:
            if self.api.create_subject(data):
                messagebox.showinfo("Thành công", "Đã thêm môn học!")
                self.clear_form()
                self.load_subjects()
            else:
                messagebox.showerror("Lỗi", "Không thể thêm môn học (có thể mã đã tồn tại).")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lưu:\n{str(e)}")

    def edit_subject(self):
        """Cập nhật môn học"""
        if not self.current_subject:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn môn học cần sửa!")
            return
        
        data = {
            "subject_name": self.entry_subject_name.get().strip(),
            "credits": int(self.entry_credits.get().strip()),
            "description": self.text_description.get('1.0', tk.END).strip(),
            "is_active": self.var_active.get()
        }
        
        try:
            if self.api.update_subject(self.current_subject['subject_id'], data):
                messagebox.showinfo("Thành công", "Cập nhật thành công!")
                self.clear_form()
                self.load_subjects()
            else:
                messagebox.showerror("Lỗi", "Cập nhật thất bại.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi cập nhật:\n{str(e)}")

    def delete_subject(self):
        """Xóa môn học"""
        if not self.current_subject:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn môn học cần xóa!")
            return
            
        sid = self.current_subject['subject_id']
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa môn học {sid}?"):
            try:
                if self.api.delete_subject(sid):
                    messagebox.showinfo("Thành công", "Đã xóa môn học!")
                    self.clear_form()
                    self.load_subjects()
                else:
                    messagebox.showerror("Lỗi", "Xóa thất bại.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa:\n{str(e)}")
