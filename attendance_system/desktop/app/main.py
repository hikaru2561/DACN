"""
Desktop Application - Main Entry Point
Attendance Management System
"""
import tkinter as tk
from tkinter import messagebox
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from old location for now
# TODO: Update these imports after refactoring is complete
try:
    from main import MainApplication, LoginWindow
    
    if __name__ == "__main__":
        root = tk.Tk()
        root.withdraw()
        
        # Show login
        login = LoginWindow(root)
        root.mainloop()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("⚠️  Please ensure old main.py exists until refactoring is complete")
    sys.exit(1)
