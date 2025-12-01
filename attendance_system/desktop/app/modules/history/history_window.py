import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import csv
from datetime import datetime
import os
from app.core.colors import COLORS
from app.core.api_client import APIClient
from app.core.config import PATHS

class HistoryWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Lịch sử Điểm danh & Ra vào")
        self.window.geometry("1200x700")
        self.window.configure(bg=COLORS["bg_light"])
        
        self.api = APIClient()
        self.logs = []
        
        self.create_ui()
        self.load_data()

    def create_ui(self):
        # Header
        header = tk.Frame(self.window, bg=COLORS["primary"], height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="QUẢN LÝ LỊCH SỬ RA VÀO", font=("Segoe UI", 16, "bold"), 
                 bg=COLORS["primary"], fg="white").pack(pady=15)

        # Toolbar
        toolbar = tk.Frame(self.window, bg=COLORS["bg_light"])
        toolbar.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(toolbar, text="🔄 Làm mới", command=self.load_data, bg=COLORS["info"], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="🗑️ Xóa log", command=self.delete_log, bg=COLORS["danger"], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="🖼️ Xem ảnh", command=self.view_photo, bg=COLORS["warning"], fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="📤 Xuất Excel/CSV", command=self.export_csv, bg=COLORS["success"], fg="white").pack(side=tk.LEFT, padx=5)
        
        # Search
        tk.Label(toolbar, text="Tìm kiếm:", bg=COLORS["bg_light"]).pack(side=tk.LEFT, padx=(20, 5))
        self.entry_search = tk.Entry(toolbar, width=30)
        self.entry_search.pack(side=tk.LEFT, padx=5)
        self.entry_search.bind('<KeyRelease>', self.filter_data)

        # Main Content (Split View)
        content = tk.PanedWindow(self.window, orient=tk.HORIZONTAL, bg=COLORS["bg_light"])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Left: List
        list_frame = tk.Frame(content)
        content.add(list_frame, width=800)
        
        cols = ("id", "time", "user", "status", "score", "note")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("time", text="Thời gian")
        self.tree.heading("user", text="Người dùng")
        self.tree.heading("status", text="Trạng thái")
        self.tree.heading("score", text="Độ chính xác")
        self.tree.heading("note", text="Ghi chú")
        
        self.tree.column("id", width=50)
        self.tree.column("time", width=150)
        self.tree.column("user", width=150)
        self.tree.column("status", width=100)
        self.tree.column("score", width=100)
        self.tree.column("note", width=200)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        # Right: Details & Preview
        detail_frame = tk.Frame(content, bg="white", bd=1, relief=tk.RIDGE)
        content.add(detail_frame)
        
        tk.Label(detail_frame, text="Chi tiết & Ảnh chụp", font=("Segoe UI", 12, "bold"), bg="white").pack(pady=10)
        
        # Photo frame with fixed size (tăng lên để hiển thị ảnh 800x600)
        photo_frame = tk.Frame(detail_frame, bg="#eee", width=400, height=300)
        photo_frame.pack(padx=10, pady=10)
        photo_frame.pack_propagate(False)  # Prevent resize
        
        self.lbl_photo = tk.Label(photo_frame, text="[Không có ảnh]", bg="#eee")
        self.lbl_photo.pack(fill=tk.BOTH, expand=True)
        
        self.txt_details = tk.Text(detail_frame, height=6, width=40, bg="white", font=("Consolas", 9))
        self.txt_details.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Stats Bar
        self.lbl_stats = tk.Label(self.window, text="Tổng số: 0 | Thành công: 0 | Thất bại: 0", 
                                  bg=COLORS["bg_dark"], fg="white", font=("Segoe UI", 10))
        self.lbl_stats.pack(fill=tk.X, side=tk.BOTTOM)

    def load_data(self):
        try:
            # Load last 1000 logs
            self.logs = self.api.get("access-logs/?limit=1000")
            self.update_tree(self.logs)
            self.update_stats(self.logs)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}")

    def update_tree(self, data):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not data:
            return
            
        for log in data:
            dt = datetime.fromisoformat(log['timestamp'])
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            user_name = log.get('user_name', 'Unknown')
            
            self.tree.insert("", tk.END, values=(
                log['id'], time_str, user_name, 
                log['status'], f"{log['similarity_score']:.2f}" if log['similarity_score'] else "N/A",
                log.get('note', '')
            ))

    def filter_data(self, event=None):
        query = self.entry_search.get().lower()
        if not query:
            self.update_tree(self.logs)
            return
            
        filtered = [
            log for log in self.logs 
            if query in (log.get('user_name', '') or '').lower() or 
               query in str(log['id']) or
               query in log['timestamp']
        ]
        self.update_tree(filtered)

    def update_stats(self, data):
        total = len(data)
        success = sum(1 for x in data if x['status'] == 'GRANTED')
        fail = total - success
        self.lbl_stats.config(text=f"Tổng số: {total} | Thành công: {success} | Thất bại/Khác: {fail}")

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
            
        item = self.tree.item(selected[0])
        log_id = item['values'][0]
        
        # Find log data
        log = next((x for x in self.logs if x['id'] == log_id), None)
        if not log: return
        
        # Show details
        details = f"ID: {log['id']}\n"
        details += f"Time: {log['timestamp']}\n"
        details += f"User: {log.get('user_name', 'Unknown')}\n"
        details += f"Status: {log['status']}\n"
        details += f"Score: {log['similarity_score']}\n"
        details += f"Note: {log.get('note', '')}\n"
        details += f"Snapshot: {log.get('snapshot_path', 'None')}\n"
        
        self.txt_details.delete(1.0, tk.END)
        self.txt_details.insert(tk.END, details)
        
        # Show photo
        self.show_snapshot(log.get('snapshot_path'))

    def show_snapshot(self, path_str):
        if not path_str or not os.path.exists(path_str):
            self.lbl_photo.config(image="", text="[Không có ảnh]")
            self.lbl_photo.image = None
            return
            
        try:
            img = Image.open(path_str)
            
            # Resize to fit in 380x280 box (for 800x600 images, aspect ratio 4:3)
            img.thumbnail((380, 280), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            self.lbl_photo.config(image=photo, text="")
            self.lbl_photo.image = photo  # Keep reference
        except Exception as e:
            self.lbl_photo.config(image="", text=f"[Lỗi: {str(e)}]")
            self.lbl_photo.image = None

    def view_photo(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        log_id = item['values'][0]
        log = next((x for x in self.logs if x['id'] == log_id), None)
        
        if log and log.get('snapshot_path') and os.path.exists(log['snapshot_path']):
            os.startfile(log['snapshot_path']) # Open in default viewer
        else:
            messagebox.showinfo("Thông báo", "Không có ảnh snapshot cho log này.")

    def delete_log(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn log để xóa")
            return
            
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa log này?"):
            return
            
        item = self.tree.item(selected[0])
        log_id = item['values'][0]
        
        try:
            self.api.delete(f"access-logs/{log_id}")
            messagebox.showinfo("Thành công", "Đã xóa log!")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def export_csv(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not filename:
            return
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Timestamp", "User ID", "User Name", "Status", "Score", "Note", "Snapshot Path"])
                
                for log in self.logs:
                    writer.writerow([
                        log['id'],
                        log['timestamp'],
                        log['user_id'],
                        log.get('user_name', ''),
                        log['status'],
                        log['similarity_score'],
                        log.get('note', ''),
                        log.get('snapshot_path', '')
                    ])
            messagebox.showinfo("Thành công", f"Đã xuất file: {filename}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất file: {e}")
