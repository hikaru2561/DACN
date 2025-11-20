<# 
===============================================================================
SCRIPT REFACTORING - PHASE 1: DESKTOP
Tạo cấu trúc mới cho Desktop application
===============================================================================
#>

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  REFACTORING DESKTOP - PROFESSIONAL STRUCTURE" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path "attendance_system/desktop")) {
    Write-Host "❌ LỖI: Thư mục desktop không tồn tại!" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Bước 1: Tạo cấu trúc thư mục mới..." -ForegroundColor Yellow
Write-Host ""

$desktopPath = "attendance_system/desktop"
$newStructure = @(
    "$desktopPath/app",
    "$desktopPath/app/core",
    "$desktopPath/app/modules",
    "$desktopPath/app/modules/student",
    "$desktopPath/app/modules/teacher",
    "$desktopPath/app/modules/subject",
    "$desktopPath/app/modules/class_",
    "$desktopPath/app/modules/session",
    "$desktopPath/app/modules/attendance",
    "$desktopPath/app/modules/camera",
    "$desktopPath/app/modules/report",
    "$desktopPath/app/components",
    "$desktopPath/app/utils",
    "$desktopPath/assets",
    "$desktopPath/tests"
)

foreach ($dir in $newStructure) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✅ Đã tạo: $dir" -ForegroundColor Green
    } else {
        Write-Host "  ⊘ Đã tồn tại: $dir" -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host "📝 Bước 2: Tạo file __init__.py..." -ForegroundColor Yellow
Write-Host ""

$initDirs = @(
    "app",
    "app/core",
    "app/modules",
    "app/modules/student",
    "app/modules/teacher",
    "app/modules/subject",
    "app/modules/class_",
    "app/modules/session",
    "app/modules/attendance",
    "app/modules/camera",
    "app/modules/report",
    "app/components",
    "app/utils"
)

foreach ($dir in $initDirs) {
    $file = "$desktopPath/$dir/__init__.py"
    if (-not (Test-Path $file)) {
        "" | Out-File -FilePath $file -Encoding UTF8
        Write-Host "  ✅ Đã tạo: $file" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "📦 Bước 3: Tạo file core..." -ForegroundColor Yellow
Write-Host ""

# app/core/colors.py
$colorsContent = @'
"""
UI Color Scheme
Centralized color definitions for consistent UI
"""

COLORS = {
    # Primary colors
    "primary": "#2196F3",
    "primary_dark": "#1976D2",
    "success": "#4CAF50",
    "success_dark": "#388E3C",
    "danger": "#F44336",
    "danger_dark": "#D32F2F",
    "warning": "#FF9800",
    "warning_dark": "#F57C00",
    "info": "#00BCD4",
    "info_dark": "#0097A7",
    
    # Module-specific colors
    "student": "#2196F3",      # Blue
    "teacher": "#4CAF50",      # Green
    "subject": "#FF9800",      # Orange
    "class": "#9C27B0",        # Purple
    "session": "#1976D2",      # Dark Blue
    "attendance": "#4CAF50",   # Green
    "camera": "#FF5722",       # Deep Orange
    "report": "#607D8B",       # Blue Grey
    
    # Neutral colors
    "dark": "#212121",
    "light": "#FAFAFA",
    "white": "#FFFFFF",
    "text": "#212121",
    "text_secondary": "#757575",
    "border": "#E0E0E0",
    
    # Button colors
    "btn_save": "#27AE60",
    "btn_edit": "#F39C12",
    "btn_delete": "#C0392B",
    "btn_cancel": "#95A5A6",
    "btn_new": "#2980B9",
}
'@

$colorsPath = "$desktopPath/app/core/colors.py"
if (-not (Test-Path $colorsPath)) {
    $colorsContent | Out-File -FilePath $colorsPath -Encoding UTF8
    Write-Host "  ✅ Đã tạo: app/core/colors.py" -ForegroundColor Green
}

# app/core/constants.py
$constantsContent = @'
"""
Application Constants
"""
from pathlib import Path

# Application info
APP_NAME = "Attendance Management System"
APP_VERSION = "1.0.0"

# Paths
APP_ROOT = Path(__file__).parent.parent.parent
DATASET_ROOT = APP_ROOT.parent.parent / "dataset"
DATASET_PROCESSED = DATASET_ROOT / "processed"
EMBEDDINGS_FILE = DATASET_ROOT / "face_embeddings.pkl"

# API
API_BASE_URL = "http://localhost:8000"

# Window sizes
WINDOW_SIZES = {
    "main": "1000x700",
    "management": "1400x800",
    "attendance": "1400x800",
}
'@

$constantsPath = "$desktopPath/app/core/constants.py"
if (-not (Test-Path $constantsPath)) {
    $constantsContent | Out-File -FilePath $constantsPath -Encoding UTF8
    Write-Host "  ✅ Đã tạo: app/core/constants.py" -ForegroundColor Green
}

# app/core/config.py
$configContent = @'
"""
Application Configuration
"""
from .colors import COLORS
from .constants import *

# UI Configuration
UI_CONFIG = {
    "colors": COLORS,
    "fonts": {
        "default": ("Segoe UI", 10),
        "bold": ("Segoe UI", 10, "bold"),
        "header": ("Segoe UI", 14, "bold"),
        "title": ("Segoe UI", 18, "bold"),
    },
    "window_sizes": WINDOW_SIZES,
}
'@

$configPath = "$desktopPath/app/core/config.py"
if (-not (Test-Path $configPath)) {
    $configContent | Out-File -FilePath $configPath -Encoding UTF8
    Write-Host "  ✅ Đã tạo: app/core/config.py" -ForegroundColor Green
}

Write-Host ""
Write-Host "📚 Bước 4: Tạo README..." -ForegroundColor Yellow
Write-Host ""

$readmeContent = @'
# Desktop Application - Attendance Management

Tkinter-based desktop application for managing attendance system.

## 📁 Structure

```
desktop/
├── app/
│   ├── core/             # Core configuration
│   │   ├── api_client.py # Backend API client
│   │   ├── colors.py     # Color scheme
│   │   ├── constants.py  # Constants
│   │   └── config.py     # App configuration
│   │
│   ├── modules/          # Feature modules
│   │   ├── student/      # Student management
│   │   ├── teacher/      # Teacher management
│   │   ├── subject/      # Subject management
│   │   ├── class_/       # Class management
│   │   ├── session/      # Session management
│   │   ├── attendance/   # Attendance (session, live, history)
│   │   ├── camera/       # Camera management
│   │   └── report/       # Reports & statistics
│   │
│   ├── components/       # Reusable UI components
│   │   ├── base_window.py
│   │   └── data_table.py
│   │
│   ├── utils/            # Utilities
│   └── main.py           # Entry point
│
├── assets/               # Images, icons
├── tests/                # Tests
└── requirements.txt      # Dependencies
```

## 🚀 Setup

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure backend is running:
```bash
# In backend directory
python -m app.main
```

4. Run desktop app:
```bash
python -m app.main
```

## 🎨 Features

- **Student Management**: Add, edit, view students
- **Teacher Management**: Manage teachers
- **Subject Management**: Manage subjects
- **Class Management**: Create and manage classes
- **Session Management**: Schedule sessions
- **Attendance**: Real-time face recognition attendance
- **Reports**: View attendance statistics

## 📖 Module Structure

Each module follows this pattern:

```
modules/feature/
├── __init__.py
├── feature_window.py    # Main window
└── components.py        # Feature-specific components (optional)
```

## 🧪 Testing

```bash
pytest
```
'@

$readmePath = "$desktopPath/README.md"
$readmeContent | Out-File -FilePath $readmePath -Encoding UTF8
Write-Host "  ✅ Đã tạo: README.md" -ForegroundColor Green

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  KẾT QUẢ - DESKTOP PHASE 1" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Đã tạo cấu trúc thư mục mới cho Desktop" -ForegroundColor Green
Write-Host "✅ Đã tạo các file core (colors, constants, config)" -ForegroundColor Green
Write-Host ""
Write-Host "📋 CẤU TRÚC MỚI:" -ForegroundColor Cyan
Write-Host ""
Write-Host "attendance_system/desktop/" -ForegroundColor White
Write-Host "├── app/" -ForegroundColor White
Write-Host "│   ├── core/           # colors.py, constants.py, config.py ✅" -ForegroundColor Green
Write-Host "│   ├── modules/        # student/, teacher/, ... (ready)" -ForegroundColor Gray
Write-Host "│   ├── components/     # (empty - for reusable UI)" -ForegroundColor Gray
Write-Host "│   └── utils/          # (empty)" -ForegroundColor Gray
Write-Host "├── assets/             # (empty - for images)" -ForegroundColor Gray
Write-Host "├── tests/              # (empty)" -ForegroundColor Gray
Write-Host "└── README.md           # ✅" -ForegroundColor Green
Write-Host ""
Write-Host "📝 BƯỚC TIẾP THEO:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Di chuyển api_client.py → app/core/" -ForegroundColor White
Write-Host "2. Di chuyển modules → app/modules/[feature]/" -ForegroundColor White
Write-Host "3. Tạo app/main.py mới (entry point)" -ForegroundColor White
Write-Host "4. Update import statements" -ForegroundColor White
Write-Host "5. Test tất cả windows" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  LƯU Ý: Các file cũ vẫn còn!" -ForegroundColor Yellow
Write-Host "   Chúng ta sẽ di chuyển code sang cấu trúc mới từng bước." -ForegroundColor Yellow
Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
