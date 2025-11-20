"""
Module Quản lý Camera
Chức năng: Thêm, sửa, xóa, xem danh sách camera
"""
import tkinter as tk
from tkinter import ttk, messagebox
from app.core.api_client import APIClient

# ============================================================================
# COLOR SCHEME
# ============================================================================

COLORS = {
    "form_header": "#2C3E50", # Dark Blue for Camera
    "table_header": "#34495E",
    "btn_save": "#27AE60",
    "btn_edit": "#F39C12",
    "btn_delete": "#C0392B",
    "btn_new": "#2980B9",
    "white": "#FFFFFF",
    "light": "#F8F9FA",
    "border": "#BDC3C7",
    "text": "#2C3E50",
    "success": "#27AE60",
    "danger": "#E74C3C",
    "btn_cancel": "#95A5A6",
    "primary": "#3498DB",
    "warning": "#F39C12",
    "info": "#3498DB",
}

# ============================================================================
# CAMERA MANAGEMENT WINDOW
# ============================================================================

class CameraManagementWindow:
    """Cửa sổ quản lý Camera"""
    
    def __init__(self, parent, api_client):
        self.parent = parent
        self.api = api_client
        self.cameras = []
        
        # Window
        self.window = tk.Toplevel(parent)
        self.window.title("Quản lý Camera")
        self.window.geometry("1400x800")
        self.window.configure(bg=COLORS["light"])
        
        # Layout
        self.create_ui()
        self.load_cameras()
    
    def create_ui(self):
        """Tạo giao diện"""
        # Main container
        main_container = tk.Frame(self.window, bg=COLORS["light"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ============================================================
        # LEFT PANEL: FORM
        # ============================================================
        left_panel = tk.Frame(main_container, bg=COLORS["white"], width=400, relief=tk.RIDGE, borderwidth=1)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Header
        header_frame = tk.Frame(left_panel, bg=COLORS["form_header"], height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="THÔNG TIN CAMERA",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["form_header"],
            fg=COLORS["white"]
        ).pack(expand=True)
        
        # Form Content
        form_content = tk.Frame(left_panel, bg=COLORS["white"])
        form_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # ID (Hidden/Readonly)
        tk.Label(form_content, text="ID Camera:", font=("Segoe UI", 10, "bold"), bg=COLORS["white"]).pack(anchor=tk.W, pady=(0, 5))
        self.entry_id = tk.Entry(form_content, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1, state='readonly')
        self.entry_id.pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # Device Name
        tk.Label(form_content, text="Tên thiết bị: *", font=("Segoe UI", 10, "bold"), bg=COLORS["white"]).pack(anchor=tk.W, pady=(0, 5))
        self.entry_name = tk.Entry(form_content, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1)
        self.entry_name.pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # Device Code
        tk.Label(form_content, text="Mã thiết bị: *", font=("Segoe UI", 10, "bold"), bg=COLORS["white"]).pack(anchor=tk.W, pady=(0, 5))
        self.entry_code = tk.Entry(form_content, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1)
        self.entry_code.pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # Stream URL
        tk.Label(form_content, text="Stream URL: *", font=("Segoe UI", 10, "bold"), bg=COLORS["white"]).pack(anchor=tk.W, pady=(0, 5))
        self.entry_url = tk.Entry(form_content, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1)
        self.entry_url.pack(fill=tk.X, pady=(0, 15), ipady=5)
        self.entry_url.insert(0, "http://192.168.1.x/stream")
        
        # Location
        tk.Label(form_content, text="Vị trí lắp đặt:", font=("Segoe UI", 10, "bold"), bg=COLORS["white"]).pack(anchor=tk.W, pady=(0, 5))
        self.entry_location = tk.Entry(form_content, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1)
        self.entry_location.pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # Room
        tk.Label(form_content, text="Phòng học:", font=("Segoe UI", 10, "bold"), bg=COLORS["white"]).pack(anchor=tk.W, pady=(0, 5))
        self.entry_room = tk.Entry(form_content, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1)
        self.entry_room.pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # Is Active
        self.var_active = tk.BooleanVar(value=True)
        tk.Checkbutton(
            form_content,
            text="Đang hoạt động",
            variable=self.var_active,
            font=("Segoe UI", 10),
            bg=COLORS["white"],
            activebackground=COLORS["white"]
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Buttons
        btn_frame = tk.Frame(left_panel, bg=COLORS["white"])
        btn_frame.pack(fill=tk.X, padx=20, pady=20, side=tk.BOTTOM)
        
        tk.Button(
            btn_frame,
            text="Làm mới",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["btn_new"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            command=self.clear_form,
            width=15
        ).pack(pady=5)
        
        tk.Button(
            btn_frame,
            text="Lưu Camera",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["btn_save"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            command=self.save_camera,
            width=15
        ).pack(pady=5)
        
        # ============================================================
        # RIGHT PANEL: TABLE
        # ============================================================
        right_panel = tk.Frame(main_container, bg=COLORS["white"], relief=tk.RIDGE, borderwidth=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Header
        table_header = tk.Frame(right_panel, bg=COLORS["table_header"], height=60)
        table_header.pack(fill=tk.X)
        table_header.pack_propagate(False)
        
        tk.Label(
            table_header,
            text="DANH SÁCH CAMERA",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["table_header"],
            fg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=20)
        
        # Toolbar
        toolbar = tk.Frame(right_panel, bg=COLORS["light"], height=50)
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            toolbar,
            text="Tải lại danh sách",
            font=("Segoe UI", 9),
            bg=COLORS["info"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            command=self.load_cameras
        ).pack(side=tk.LEFT)
        
        tk.Button(
            toolbar,
            text="Xóa Camera",
            font=("Segoe UI", 9),
            bg=COLORS["btn_delete"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            command=self.delete_camera
        ).pack(side=tk.RIGHT)
        
        # Table
        table_frame = tk.Frame(right_panel, bg=COLORS["white"])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        columns = ("ID", "Tên thiết bị", "Mã thiết bị", "URL", "Vị trí", "Phòng", "Trạng thái")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Headings
        for col in columns:
            self.tree.heading(col, text=col)
            
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Tên thiết bị", width=150)
        self.tree.column("Mã thiết bị", width=100)
        self.tree.column("URL", width=200)
        self.tree.column("Vị trí", width=150)
        self.tree.column("Phòng", width=80, anchor=tk.CENTER)
        self.tree.column("Trạng thái", width=100, anchor=tk.CENTER)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Tags
        self.tree.tag_configure('active', foreground=COLORS["success"])
        self.tree.tag_configure('inactive', foreground=COLORS["danger"])
    
    def load_cameras(self):
        """Load danh sách camera từ API"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            self.cameras = self.api.get_cameras()
            
            for cam in self.cameras:
                status = "Hoạt động" if cam.get('is_active') else "Ngừng"
                tag = 'active' if cam.get('is_active') else 'inactive'
                
                self.tree.insert("", tk.END, values=(
                    cam.get('device_id'),
                    cam.get('device_name'),
                    cam.get('device_code'),
                    cam.get('stream_url'),
                    cam.get('location'),
                    cam.get('room'),
                    status
                ), tags=(tag,))
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách camera:\n{str(e)}")
    
    def on_select(self, event):
        """Chọn camera từ bảng"""
        selected = self.tree.selection()
        if not selected:
            return
            
        values = self.tree.item(selected[0])['values']
        device_id = values[0]
        
        # Find camera data
        camera = next((c for c in self.cameras if c['device_id'] == device_id), None)
        if camera:
            self.entry_id.config(state='normal')
            self.entry_id.delete(0, tk.END)
            self.entry_id.insert(0, str(camera['device_id']))
            self.entry_id.config(state='readonly')
            
            self.entry_name.delete(0, tk.END)
            self.entry_name.insert(0, camera['device_name'])
            
            self.entry_code.delete(0, tk.END)
            self.entry_code.insert(0, camera['device_code'])
            
            self.entry_url.delete(0, tk.END)
            self.entry_url.insert(0, camera['stream_url'])
            
            self.entry_location.delete(0, tk.END)
            if camera.get('location'):
                self.entry_location.insert(0, camera['location'])
                
            self.entry_room.delete(0, tk.END)
            if camera.get('room'):
                self.entry_room.insert(0, camera['room'])
                
            self.var_active.set(camera['is_active'])
    
    def clear_form(self):
        """Xóa form"""
        self.entry_id.config(state='normal')
        self.entry_id.delete(0, tk.END)
        self.entry_id.config(state='readonly')
        
        self.entry_name.delete(0, tk.END)
        self.entry_code.delete(0, tk.END)
        self.entry_url.delete(0, tk.END)
        self.entry_url.insert(0, "http://192.168.1.x/stream")
        self.entry_location.delete(0, tk.END)
        self.entry_room.delete(0, tk.END)
        self.var_active.set(True)
        
        # Deselect table
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
    
    def save_camera(self):
        """Lưu thông tin camera"""
        name = self.entry_name.get().strip()
        code = self.entry_code.get().strip()
        url = self.entry_url.get().strip()
        location = self.entry_location.get().strip()
        room = self.entry_room.get().strip()
        is_active = self.var_active.get()
        
        if not name or not code or not url:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Tên, Mã và URL!")
            return
        
        data = {
            "device_name": name,
            "device_code": code,
            "stream_url": url,
            "location": location,
            "room": room,
            "is_active": is_active
        }
        
        device_id = self.entry_id.get()
        
        try:
            if device_id:
                # Update
                if self.api.update_camera(int(device_id), data):
                    messagebox.showinfo("Thành công", "Cập nhật camera thành công!")
                    self.clear_form()
                    self.load_cameras()
                else:
                    messagebox.showerror("Lỗi", "Cập nhật thất bại!")
            else:
                # Create
                if self.api.create_camera(data):
                    messagebox.showinfo("Thành công", "Thêm camera thành công!")
                    self.clear_form()
                    self.load_cameras()
                else:
                    messagebox.showerror("Lỗi", "Thêm mới thất bại!")
                    
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lưu:\n{str(e)}")
    
    def delete_camera(self):
        """Xóa camera"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn camera cần xóa!")
            return
            
        values = self.tree.item(selected[0])['values']
        device_id = values[0]
        name = values[1]
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa camera: {name}?"):
            try:
                if self.api.delete_camera(device_id):
                    messagebox.showinfo("Thành công", "Đã xóa camera!")
                    self.clear_form()
                    self.load_cameras()
                else:
                    messagebox.showerror("Lỗi", "Xóa thất bại!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa:\n{str(e)}")
