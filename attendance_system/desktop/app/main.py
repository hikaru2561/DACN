"""
HỆ THỐNG QUẢN LÝ ĐIỂM DANH
Desktop Application - Main Entry Point
"""
import tkinter as tk
import sys
import os
from pathlib import Path

# Add project root to sys.path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent.parent  # d:\HUTECH\DACN
desktop_root = current_dir.parent  # d:\HUTECH\DACN\attendance_system\desktop

if str(desktop_root) not in sys.path:
    sys.path.insert(0, str(desktop_root))

from app.core.api_client import APIClient
from app.ui.login_window import LoginWindow
from app.modules.dashboard.dashboard_window import DashboardWindow

def start_app():
    """Khởi động ứng dụng"""
    # Initialize API client
    api = APIClient()
    
    # Create root window
    root = tk.Tk()
    
    # Login callback
    def on_login_success(username):
        # Create new root for main app
        main_root = tk.Tk()
        app = DashboardWindow(main_root, username)
        main_root.mainloop()
    
    # Show login window
    LoginWindow(root, api, on_login_success)
    root.mainloop()

if __name__ == "__main__":
    try:
        start_app()
    except KeyboardInterrupt:
        print("\n👋 Tạm biệt!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
