"""
Module Quản lý Môn học (Subjects)
Chức năng: CRUD đầy đủ cho môn học
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
# SUBJECT MANAGEMENT WINDOW
# ============================================================================

class SubjectManagementWindow:
    """Cửa sổ quản lý môn học"""
    
    def __init__(self, parent):
        self.parent = parent
        self.api = APIClient()
        self.current_subject = None
        
        # Tạo window
        self.window = tk.Toplevel(parent)
        self.window.title("Quản lý Môn học")
        self.window.geometry("1400x800")
        self.window.configure(bg=COLORS["light"])
        self.window.transient(parent)
        
        self.create_ui()
        self.load_subjects()
    
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
            text="📚 QUẢN LÝ MÔN HỌC",
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
        form_header = tk.Frame(left_panel, bg="#3498DB", height=50)
        form_header.pack(fill=tk.X)
        form_header.pack_propagate(False)
        
        tk.Label(
            form_header,
            text="📝 Thông tin môn học",
            font=("Segoe UI", 14, "bold"),
            bg="#3498DB",
            fg=COLORS["white"]
        ).pack(pady=12)
        
        # Form Container với scrollbar
        form_container = tk.Frame(left_panel, bg=COLORS["white"])
        form_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # === MÃ MÔN HỌC ===
        tk.Label(
            form_container,
            text="Mã môn học *",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w"
        ).pack(fill=tk.X, pady=(10, 5))
        
        self.entry_subject_id = tk.Entry(
            form_container,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_subject_id.pack(fill=tk.X, ipady=8)
        
        # === TÊN MÔN HỌC ===
        tk.Label(
            form_container,
            text="Tên môn học *",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w"
        ).pack(fill=tk.X, pady=(15, 5))
        
        self.entry_subject_name = tk.Entry(
            form_container,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_subject_name.pack(fill=tk.X, ipady=8)
        
        # === SỐ TÍN CHỈ ===
        tk.Label(
            form_container,
            text="Số tín chỉ *",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w"
        ).pack(fill=tk.X, pady=(15, 5))
        
        self.entry_credits = tk.Entry(
            form_container,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.entry_credits.pack(fill=tk.X, ipady=8)
        self.entry_credits.insert(0, "3")  # Default value
        
        # === MÔ TẢ ===
        tk.Label(
            form_container,
            text="Mô tả",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"],
            anchor="w"
        ).pack(fill=tk.X, pady=(15, 5))
        
        self.text_description = tk.Text(
            form_container,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            borderwidth=1,
            height=5,
            wrap=tk.WORD
        )
        self.text_description.pack(fill=tk.X)
        
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
            command=self.save_subject,
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
            command=self.edit_subject,
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
            command=self.delete_subject,
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
        # RIGHT PANEL: DANH SÁCH MÔN HỌC
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
            command=self.search_subjects,
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
            command=self.load_subjects,
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
        columns = ("STT", "Mã môn", "Tên môn học", "Tín chỉ", "Trạng thái", "Ngày tạo")
        
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
        self.tree.heading("Mã môn", text="Mã môn")
        self.tree.heading("Tên môn học", text="Tên môn học")
        self.tree.heading("Tín chỉ", text="Tín chỉ")
        self.tree.heading("Trạng thái", text="Trạng thái")
        self.tree.heading("Ngày tạo", text="Ngày tạo")
        
        # Column widths
        self.tree.column("STT", width=50, anchor=tk.CENTER)
        self.tree.column("Mã môn", width=100, anchor=tk.CENTER)
        self.tree.column("Tên môn học", width=300)
        self.tree.column("Tín chỉ", width=80, anchor=tk.CENTER)
        self.tree.column("Trạng thái", width=120, anchor=tk.CENTER)
        self.tree.column("Ngày tạo", width=150, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind click event
        self.tree.bind('<ButtonRelease-1>', self.on_tree_select)
        
        # Alternating row colors
        self.tree.tag_configure('evenrow', background='#F8F9FA')
        self.tree.tag_configure('oddrow', background='#FFFFFF')
        self.tree.tag_configure('inactive', foreground='#95A5A6')
    
    def load_subjects(self):
        """Load danh sách môn học"""
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            subjects = self.api.get_subjects()
            
            for idx, subject in enumerate(subjects, 1):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                
                # Add inactive tag if not active
                tags = [tag]
                if not subject.get('is_active', True):
                    tags.append('inactive')
                
                status = "✅ Hoạt động" if subject.get('is_active', True) else "❌ Ngừng"
                created_at = subject.get('created_at', '')
                if created_at:
                    try:
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M')
                    except:
                        pass
                
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
        
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            subjects = self.api.get_subjects()
            filtered = [s for s in subjects 
                       if search_term in s.get('subject_id', '').lower() 
                       or search_term in s.get('subject_name', '').lower()]
            
            for idx, subject in enumerate(filtered, 1):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                tags = [tag]
                if not subject.get('is_active', True):
                    tags.append('inactive')
                
                status = "✅ Hoạt động" if subject.get('is_active', True) else "❌ Ngừng"
                created_at = subject.get('created_at', '')
                if created_at:
                    try:
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M')
                    except:
                        pass
                
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
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        values = item['values']
        
        if len(values) < 2:
            return
        
        subject_id = str(values[1])  # Mã môn
        
        try:
            # Fetch full subject data from API
            subject = self.api.get_subject(subject_id)
            
            if subject:
                self.current_subject = subject
                self.populate_form(subject)
            else:
                self.current_subject = None
        
        except Exception as e:
            print(f"❌ Error loading subject: {e}")
            self.current_subject = None
    
    def populate_form(self, subject):
        """Điền thông tin môn học vào form"""
        self.clear_form_fields_only()
        
        try:
            # Mã môn học
            if subject.get('subject_id'):
                self.entry_subject_id.insert(0, str(subject['subject_id']))
                self.entry_subject_id.config(state='readonly')  # Không cho sửa mã
            
            # Tên môn học
            if subject.get('subject_name'):
                self.entry_subject_name.insert(0, str(subject['subject_name']))
            
            # Số tín chỉ
            if subject.get('credits'):
                self.entry_credits.delete(0, tk.END)
                self.entry_credits.insert(0, str(subject['credits']))
            
            # Mô tả
            if subject.get('description'):
                self.text_description.insert('1.0', str(subject['description']))
            
            # Trạng thái
            self.var_active.set(subject.get('is_active', True))
        
        except Exception as e:
            print(f"❌ Error in populate_form: {e}")
            raise
    
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
        
        if not subject_id:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập mã môn học!")
            self.entry_subject_id.focus()
            return False
        
        # Validate mã môn học (chỉ chữ, số và không có khoảng trắng)
        if not re.match(r'^[A-Za-z0-9]+$', subject_id):
            messagebox.showwarning(
                "Mã không hợp lệ",
                "Mã môn học chỉ được chứa chữ cái và số, không có khoảng trắng!"
            )
            self.entry_subject_id.focus()
            return False
        
        if not subject_name:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên môn học!")
            self.entry_subject_name.focus()
            return False
        
        if not credits:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập số tín chỉ!")
            self.entry_credits.focus()
            return False
        
        try:
            credits_int = int(credits)
            if credits_int <= 0 or credits_int > 10:
                messagebox.showwarning(
                    "Số tín chỉ không hợp lệ",
                    "Số tín chỉ phải từ 1 đến 10!"
                )
                self.entry_credits.focus()
                return False
        except ValueError:
            messagebox.showwarning(
                "Số tín chỉ không hợp lệ",
                "Số tín chỉ phải là số nguyên!"
            )
            self.entry_credits.focus()
            return False
        
        return True
    
    def save_subject(self):
        """Lưu môn học mới"""
        if not self.validate_form():
            return
        
        subject_data = {
            "subject_id": self.entry_subject_id.get().strip().upper(),
            "subject_name": self.entry_subject_name.get().strip(),
            "credits": int(self.entry_credits.get().strip()),
            "description": self.text_description.get('1.0', tk.END).strip(),
            "is_active": self.var_active.get()
        }
        
        try:
            result = self.api.create_subject(subject_data)
            
            if result:
                messagebox.showinfo(
                    "Thành công",
                    f"Đã thêm môn học:\n{subject_data['subject_id']} - {subject_data['subject_name']}"
                )
                self.clear_form()
                self.load_subjects()
            else:
                messagebox.showerror("Lỗi", "Không thể thêm môn học. Mã môn có thể đã tồn tại.")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lưu môn học:\n{str(e)}")
    
    def edit_subject(self):
        """Cập nhật môn học"""
        if not self.current_subject:
            messagebox.showwarning(
                "Chưa chọn môn học",
                "Vui lòng chọn môn học từ danh sách để chỉnh sửa!"
            )
            return
        
        if not self.validate_form():
            return
        
        subject_id = self.current_subject['subject_id']
        
        subject_data = {
            "subject_name": self.entry_subject_name.get().strip(),
            "credits": int(self.entry_credits.get().strip()),
            "description": self.text_description.get('1.0', tk.END).strip(),
            "is_active": self.var_active.get()
        }
        
        try:
            result = self.api.update_subject(subject_id, subject_data)
            
            if result:
                messagebox.showinfo(
                    "Thành công",
                    f"Đã cập nhật môn học:\n{subject_id} - {subject_data['subject_name']}"
                )
                self.clear_form()
                self.load_subjects()
            else:
                messagebox.showerror("Lỗi", "Không thể cập nhật môn học.")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi cập nhật:\n{str(e)}")
    
    def delete_subject(self):
        """Xóa môn học"""
        if not self.current_subject:
            messagebox.showwarning(
                "Chưa chọn môn học",
                "Vui lòng chọn môn học từ danh sách để xóa!"
            )
            return
        
        subject_id = self.current_subject['subject_id']
        subject_name = self.current_subject['subject_name']
        
        confirm = messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc muốn xóa môn học:\n\n"
            f"{subject_id} - {subject_name}\n\n"
            f"⚠️ Hành động này không thể hoàn tác!"
        )
        
        if not confirm:
            return
        
        try:
            success = self.api.delete_subject(subject_id)
            
            if success:
                messagebox.showinfo(
                    "Thành công",
                    f"Đã xóa môn học: {subject_id}"
                )
                self.clear_form()
                self.load_subjects()
            else:
                messagebox.showerror("Lỗi", "Không thể xóa môn học.")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xóa:\n{str(e)}")


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide root window
    
    app = SubjectManagementWindow(root)
    root.mainloop()
