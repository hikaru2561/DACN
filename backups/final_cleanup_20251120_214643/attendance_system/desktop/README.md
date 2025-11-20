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
