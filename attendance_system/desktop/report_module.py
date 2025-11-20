"""
Module Báo cáo Thống kê
Chức năng: Xem thống kê điểm danh theo lớp, xuất báo cáo
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime
from api_client import APIClient

# ============================================================================
# COLOR SCHEME
# ============================================================================

COLORS = {
    "header": "#8E44AD", # Purple for Reports
    "card_bg": "#FFFFFF",
    "text": "#2C3E50",
    "white": "#FFFFFF",
    "light": "#F8F9FA",
    "success": "#27AE60",
    "warning": "#F39C12",
    "danger": "#E74C3C",
    "info": "#3498DB",
    "btn_export": "#27AE60",
    "btn_refresh": "#3498DB",
    "btn_close": "#95A5A6"
}

# ============================================================================
# REPORT WINDOW
# ============================================================================

class ReportWindow:
    """Cửa sổ báo cáo thống kê"""
    
    def __init__(self, parent, api_client):
        self.parent = parent
        self.api = api_client
        self.stats_data = []
        
        # Window
        self.window = tk.Toplevel(parent)
        self.window.title("Báo cáo Thống kê")
        self.window.geometry("1400x800")
        self.window.configure(bg=COLORS["light"])
        
        self.create_ui()
        self.load_data()
    
    def create_ui(self):
        """Tạo giao diện"""
        # Header
        header = tk.Frame(self.window, bg=COLORS["header"], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📊 BÁO CÁO THỐNG KÊ ĐIỂM DANH",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["header"],
            fg=COLORS["white"]
        ).pack(side=tk.LEFT, padx=30)
        
        # Toolbar
        toolbar = tk.Frame(self.window, bg=COLORS["white"], height=60)
        toolbar.pack(fill=tk.X, padx=20, pady=10)
        toolbar.pack_propagate(False)
        
        tk.Button(
            toolbar,
            text="🔄 Làm mới dữ liệu",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["btn_refresh"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            command=self.load_data,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Button(
            toolbar,
            text="📥 Xuất báo cáo (CSV)",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["btn_export"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            command=self.export_csv,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Button(
            toolbar,
            text="✕ Đóng",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["btn_close"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            command=self.window.destroy,
            padx=15,
            pady=8
        ).pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Summary Cards
        self.cards_frame = tk.Frame(self.window, bg=COLORS["light"])
        self.cards_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.card_classes = self.create_card("Tổng số lớp", "0", COLORS["info"])
        self.card_classes.pack(side=tk.LEFT, padx=10)
        
        self.card_sessions = self.create_card("Tổng buổi học", "0", COLORS["warning"])
        self.card_sessions.pack(side=tk.LEFT, padx=10)
        
        self.card_students = self.create_card("Tổng sinh viên", "0", COLORS["success"])
        self.card_students.pack(side=tk.LEFT, padx=10)
        
        self.card_rate = self.create_card("Tỷ lệ đi học TB", "0%", COLORS["header"])
        self.card_rate.pack(side=tk.LEFT, padx=10)
        
        # Table
        table_frame = tk.Frame(self.window, bg=COLORS["white"])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(
            table_frame,
            text="Chi tiết theo lớp học phần",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["white"],
            fg=COLORS["text"]
        ).pack(anchor=tk.W, padx=10, pady=10)
        
        columns = (
            "ID Lớp", "Tên Lớp", "Môn Học", "Giảng Viên", 
            "Số Buổi", "Số SV", "Tổng lượt điểm danh", "Tỷ lệ đi học"
        )
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Headings & Columns
        col_widths = {
            "ID Lớp": 60,
            "Tên Lớp": 150,
            "Môn Học": 200,
            "Giảng Viên": 180,
            "Số Buổi": 80,
            "Số SV": 80,
            "Tổng lượt điểm danh": 120,
            "Tỷ lệ đi học": 100
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 100), anchor=tk.CENTER if "Số" in col or "ID" in col or "Tỷ lệ" in col else tk.W)
            
        # Tags for coloring rows
        self.tree.tag_configure('high', foreground=COLORS["success"])
        self.tree.tag_configure('medium', foreground=COLORS["warning"])
        self.tree.tag_configure('low', foreground=COLORS["danger"])
    
    def create_card(self, title, value, color):
        """Tạo card thống kê"""
        card = tk.Frame(self.cards_frame, bg=color, width=250, height=100)
        card.pack_propagate(False)
        
        tk.Label(
            card,
            text=title,
            font=("Segoe UI", 11),
            bg=color,
            fg=COLORS["white"]
        ).pack(pady=(15, 5))
        
        value_label = tk.Label(
            card,
            text=value,
            font=("Segoe UI", 24, "bold"),
            bg=color,
            fg=COLORS["white"]
        )
        value_label.pack(pady=5)
        
        card.value_label = value_label
        return card
    
    def load_data(self):
        """Load dữ liệu thống kê"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            self.stats_data = self.api.get_attendance_stats()
            
            total_classes = len(self.stats_data)
            total_sessions = sum(item['total_sessions'] for item in self.stats_data)
            total_students = sum(item['total_students'] for item in self.stats_data)
            avg_rate = sum(item['attendance_rate'] for item in self.stats_data) / total_classes if total_classes > 0 else 0
            
            # Update cards
            self.card_classes.value_label.config(text=str(total_classes))
            self.card_sessions.value_label.config(text=str(total_sessions))
            self.card_students.value_label.config(text=str(total_students))
            self.card_rate.value_label.config(text=f"{avg_rate:.1f}%")
            
            # Populate table
            for item in self.stats_data:
                rate = item['attendance_rate']
                tag = 'high' if rate >= 80 else 'medium' if rate >= 50 else 'low'
                
                self.tree.insert("", tk.END, values=(
                    item['class_id'],
                    item['class_name'],
                    item['subject_name'],
                    item['teacher_name'],
                    item['total_sessions'],
                    item['total_students'],
                    item['total_attendance_records'],
                    f"{rate:.1f}%"
                ), tags=(tag,))
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải báo cáo:\n{str(e)}")
    
    def export_csv(self):
        """Xuất báo cáo ra CSV"""
        if not self.stats_data:
            messagebox.showwarning("Không có dữ liệu", "Không có dữ liệu để xuất!")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Lưu báo cáo CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"attendance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # Header
                headers = [
                    "ID Lớp", "Tên Lớp", "Môn Học", "Giảng Viên", 
                    "Tổng số buổi", "Tổng số SV", "Tổng lượt điểm danh", "Tỷ lệ đi học (%)"
                ]
                writer.writerow(headers)
                
                # Data
                for item in self.stats_data:
                    writer.writerow([
                        item['class_id'],
                        item['class_name'],
                        item['subject_name'],
                        item['teacher_name'],
                        item['total_sessions'],
                        item['total_students'],
                        item['total_attendance_records'],
                        item['attendance_rate']
                    ])
            
            messagebox.showinfo("Thành công", f"Đã xuất báo cáo ra file:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất file:\n{str(e)}")
