import tkinter as tk
from tkinter import ttk, messagebox
from app.core.colors import COLORS
from app.core.api_client import APIClient
from app.modules.user_management.capture_window import CaptureWindow
from app.core.trainer import ModelTrainer
import threading

class UserManagementWindow:
    def __init__(self, parent, stream_reader=None, dashboard=None):
        self.window = tk.Toplevel(parent)
        self.window.title("Quản lý Người dùng")
        self.window.geometry("900x600")
        self.window.configure(bg=COLORS["bg_light"])
        
        self.stream_reader = stream_reader  # Nhận stream từ Dashboard
        self.dashboard = dashboard  # Tham chiếu để pause/resume stream
        self.api = APIClient()
        self.create_ui()
        self.load_data()

    def create_ui(self):
        # Header
        header = tk.Frame(self.window, bg=COLORS["primary"], height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="QUẢN LÝ NGƯỜI DÙNG", font=("Segoe UI", 16, "bold"), 
                 bg=COLORS["primary"], fg="white").pack(pady=15)

        # Content
        content = tk.Frame(self.window, bg=COLORS["bg_light"])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Treeview
        columns = ("id", "name", "active")
        self.tree = ttk.Treeview(content, columns=columns, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Họ Tên")
        self.tree.heading("active", text="Trạng thái")
        
        self.tree.column("id", width=50)
        self.tree.column("name", width=200)
        self.tree.column("active", width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Buttons
        btn_frame = tk.Frame(content, bg=COLORS["bg_light"])
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(btn_frame, text="Thêm mới", bg=COLORS["success"], fg="white", 
                  command=self.add_user).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="📸 Chụp ảnh", bg=COLORS["deep_orange"], fg="white", 
                  command=self.open_capture).pack(side=tk.LEFT, padx=5)
        
        # Train Buttons
        tk.Button(btn_frame, text="🧠 Train User (Append)", bg=COLORS["info"], fg="white", 
                  command=self.train_selected_user).pack(side=tk.LEFT, padx=5)
                  
        tk.Button(btn_frame, text="🔄 Train All (Reset)", bg=COLORS["purple"], fg="white", 
                  command=self.train_model).pack(side=tk.LEFT, padx=5)
                  
        tk.Button(btn_frame, text="Xóa", bg=COLORS["danger"], fg="white", 
                  command=self.delete_user).pack(side=tk.LEFT, padx=5)
                  
        tk.Button(btn_frame, text="Làm mới", command=self.load_data).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            users = self.api.get("users/")
            if users:
                for u in users:
                    self.tree.insert("", tk.END, values=(
                        u['id'], u['full_name'], 
                        "Hoạt động" if u['is_active'] else "Khóa"
                    ))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}")

    def add_user(self):
        # Simple dialog to add user
        add_win = tk.Toplevel(self.window)
        add_win.title("Thêm người dùng")
        add_win.geometry("400x200")
        
        tk.Label(add_win, text="Họ tên:").pack(pady=5)
        entry_name = tk.Entry(add_win)
        entry_name.pack(pady=5)
        
        def save():
            name = entry_name.get()
            if name:
                data = {"full_name": name}
                try:
                    self.api.post("users/", data)
                    messagebox.showinfo("Thành công", "Đã thêm user!")
                    add_win.destroy()
                    self.load_data()
                except Exception as e:
                    messagebox.showerror("Lỗi", str(e))
            else:
                messagebox.showwarning("Lỗi", "Vui lòng nhập tên")
                
        tk.Button(add_win, text="Lưu", command=save, bg=COLORS["primary"], fg="white").pack(pady=20)

    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        user_id = item['values'][0]
        
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa user này?"):
            try:
                self.api.delete(f"users/{user_id}")
                messagebox.showinfo("Thành công", "Đã xóa user!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))

    def open_capture(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một người dùng để chụp ảnh!")
            return
            
        item = self.tree.item(selected[0])
        user_id = item['values'][0]
        user_name = item['values'][1]
        
        # Open capture window - Truyền stream_reader và dashboard
        capture_win = CaptureWindow(
            self.window, 
            str(user_id), 
            user_name, 
            self.stream_reader,
            self.dashboard
        )

    def train_selected_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một người dùng để train!")
            return
            
        item = self.tree.item(selected[0])
        user_id = str(item['values'][0])
        user_name = item['values'][1]
        
        if not messagebox.askyesno("Xác nhận", f"Train model cho user: {user_name} (ID: {user_id})?"):
            return

        # Show loading
        win = tk.Toplevel(self.window)
        win.title("Đang xử lý...")
        win.geometry("300x100")
        tk.Label(win, text=f"Đang cập nhật đặc trưng cho {user_name}...").pack(pady=20)
        progress = ttk.Progressbar(win, mode='indeterminate')
        progress.pack(fill=tk.X, padx=20)
        progress.start()
        
        def run_train():
            try:
                trainer = ModelTrainer()
                success, msg = trainer.train_user(user_id)
                
                # Reload dashboard recognizer
                if self.dashboard and self.dashboard.recognizer:
                    self.dashboard.recognizer.load_database()
                
                self.window.after(0, lambda: self._on_train_complete(win, success, msg))
            except Exception as e:
                self.window.after(0, lambda: self._on_train_complete(win, False, str(e)))
                
        threading.Thread(target=run_train, daemon=True).start()

    def train_model(self):
        if not messagebox.askyesno("Xác nhận", "Quá trình train sẽ quét toàn bộ thư mục dataset/raw và tạo lại database nhận diện. Bạn có muốn tiếp tục?"):
            return
            
        # Show loading
        win = tk.Toplevel(self.window)
        win.title("Đang xử lý...")
        win.geometry("300x100")
        tk.Label(win, text="Đang train model AI (Toàn bộ)... Vui lòng đợi.").pack(pady=20)
        progress = ttk.Progressbar(win, mode='indeterminate')
        progress.pack(fill=tk.X, padx=20)
        progress.start()
        
        def run_train():
            try:
                trainer = ModelTrainer()
                success, msg = trainer.train_all()
                
                # Reload dashboard recognizer
                if self.dashboard and self.dashboard.recognizer:
                    self.dashboard.recognizer.load_database()
                
                self.window.after(0, lambda: self._on_train_complete(win, success, msg))
            except Exception as e:
                self.window.after(0, lambda: self._on_train_complete(win, False, str(e)))
                
        threading.Thread(target=run_train, daemon=True).start()

    def _on_train_complete(self, win, success, msg):
        win.destroy()
        if success:
            messagebox.showinfo("Thành công", msg)
        else:
            messagebox.showerror("Lỗi", msg)
