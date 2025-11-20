# REFACTORING PLAN - Professional Project Structure

## 🎯 Mục tiêu
Xây dựng lại project với:
- ✅ **Backend**: Feature-based architecture (dễ scale, maintain)
- ✅ **Desktop**: Module-based organization (clear separation)
- ✅ **Clean code**: Follow best practices
- ✅ **Testable**: Dễ dàng viết unit tests

---

## 📊 Cấu trúc mới

```
DACN/
├── attendance_system/
│   │
│   ├── backend/                        # ⭐ BACKEND (FastAPI)
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py                 # Entry point
│   │   │   ├── config.py               # Configuration
│   │   │   │
│   │   │   ├── api/                    # 🔥 API Routes (by feature)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── deps.py             # Dependencies (get_db, etc)
│   │   │   │   ├── students.py         # Student endpoints
│   │   │   │   ├── teachers.py         # Teacher endpoints
│   │   │   │   ├── subjects.py         # Subject endpoints
│   │   │   │   ├── classes.py          # Class endpoints
│   │   │   │   ├── sessions.py         # Session endpoints
│   │   │   │   ├── attendance.py       # Attendance endpoints
│   │   │   │   ├── cameras.py          # Camera endpoints
│   │   │   │   └── reports.py          # Report endpoints
│   │   │   │
│   │   │   ├── models/                 # 🔥 Database Models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py             # Base model
│   │   │   │   ├── user.py
│   │   │   │   ├── student.py
│   │   │   │   ├── teacher.py
│   │   │   │   ├── subject.py
│   │   │   │   ├── class_.py
│   │   │   │   ├── session.py
│   │   │   │   ├── attendance.py
│   │   │   │   └── camera.py
│   │   │   │
│   │   │   ├── schemas/                # 🔥 Pydantic Schemas
│   │   │   │   ├── __init__.py
│   │   │   │   ├── student.py
│   │   │   │   ├── teacher.py
│   │   │   │   ├── subject.py
│   │   │   │   ├── class_.py
│   │   │   │   ├── session.py
│   │   │   │   ├── attendance.py
│   │   │   │   ├── camera.py
│   │   │   │   └── report.py
│   │   │   │
│   │   │   ├── core/                   # 🔥 Core utilities
│   │   │   │   ├── __init__.py
│   │   │   │   ├── database.py         # DB connection
│   │   │   │   ├── security.py         # Auth (future)
│   │   │   │   └── config.py           # Settings
│   │   │   │
│   │   │   └── utils/                  # Helpers
│   │   │       └── __init__.py
│   │   │
│   │   ├── tests/                      # Backend tests
│   │   ├── alembic/                    # DB migrations (future)
│   │   ├── requirements.txt
│   │   └── .env.example
│   │
│   ├── desktop/                        # ⭐ DESKTOP (Tkinter)
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py                 # Entry point
│   │   │   ├── config.py               # UI Config
│   │   │   │
│   │   │   ├── core/                   # 🔥 Core components
│   │   │   │   ├── __init__.py
│   │   │   │   ├── api_client.py       # Backend API client
│   │   │   │   ├── colors.py           # Color schemes
│   │   │   │   └── constants.py        # Constants
│   │   │   │
│   │   │   ├── modules/                # 🔥 UI Modules (by feature)
│   │   │   │   ├── __init__.py
│   │   │   │   │
│   │   │   │   ├── student/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── student_window.py
│   │   │   │   │   └── image_viewer.py
│   │   │   │   │
│   │   │   │   ├── teacher/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── teacher_window.py
│   │   │   │   │
│   │   │   │   ├── subject/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── subject_window.py
│   │   │   │   │
│   │   │   │   ├── class_/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── class_window.py
│   │   │   │   │   └── students_window.py
│   │   │   │   │
│   │   │   │   ├── session/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── session_window.py
│   │   │   │   │
│   │   │   │   ├── attendance/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── session_selection.py
│   │   │   │   │   ├── live_attendance.py
│   │   │   │   │   ├── recognition.py
│   │   │   │   │   └── history.py
│   │   │   │   │
│   │   │   │   ├── camera/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── camera_window.py
│   │   │   │   │   └── capture.py
│   │   │   │   │
│   │   │   │   └── report/
│   │   │   │       ├── __init__.py
│   │   │   │       └── report_window.py
│   │   │   │
│   │   │   ├── components/             # 🔥 Reusable UI components
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_window.py      # Base window class
│   │   │   │   ├── data_table.py       # Reusable table
│   │   │   │   └── dialogs.py          # Common dialogs
│   │   │   │
│   │   │   └── utils/                  # Utilities
│   │   │       ├── __init__.py
│   │   │       ├── validators.py
│   │   │       └── helpers.py
│   │   │
│   │   ├── assets/                     # Images, icons
│   │   ├── tests/                      # Desktop tests
│   │   └── requirements.txt
│   │
│   └── database/
│       ├── schema.sql
│       ├── migrations/
│       └── seeds/
│
├── client/                             # ESP32 clients
├── esp32-camera/                       # Firmware
├── dataset/                            # Data
├── docs/                               # Documentation
└── scripts/                            # Utility scripts
```

---

## 🔄 MIGRATION STRATEGY

### Phase 1: Backend Refactoring (PRIORITY)

#### Step 1: Create new structure
```powershell
cd attendance_system/backend
mkdir -p app/{api,models,schemas,core,utils}
```

#### Step 2: Split models.py
Current: `models.py` (600+ lines)
New: Individual model files

**Mapping:**
- `models.py` → `app/models/user.py`, `student.py`, `teacher.py`, etc.

#### Step 3: Split schemas.py
Current: `schemas.py` (380+ lines)
New: Individual schema files

#### Step 4: Split main.py routes
Current: `main.py` (700+ lines with routes)
New: `app/main.py` (entry) + `app/api/*.py` (routes)

#### Step 5: Extract database config
Current: `database.py`
New: `app/core/database.py`

---

### Phase 2: Desktop Refactoring

#### Step 1: Create module structure
```powershell
cd attendance_system/desktop
mkdir -p app/{core,modules,components,utils}
mkdir -p app/modules/{student,teacher,subject,class_,session,attendance,camera,report}
```

#### Step 2: Reorganize modules
**Mapping:**
- `student_module_new.py` → `app/modules/student/student_window.py`
- `teacher_module.py` → `app/modules/teacher/teacher_window.py`
- `attendance_*.py` → `app/modules/attendance/*.py`
- etc.

#### Step 3: Extract shared components
- Create `BaseWindow` class
- Create `DataTable` component
- Create `APIClient` wrapper

---

## 📝 IMPLEMENTATION CHECKLIST

### Backend:
- [ ] Create new directory structure
- [ ] Split `models.py` into individual files
- [ ] Split `schemas.py` into individual files
- [ ] Split routes from `main.py` into `api/` folder
- [ ] Move `database.py` to `core/`
- [ ] Create `deps.py` for dependencies
- [ ] Update all imports
- [ ] Test API endpoints
- [ ] Update `requirements.txt`

### Desktop:
- [ ] Create new directory structure
- [ ] Move modules to feature folders
- [ ] Extract `APIClient` to `core/`
- [ ] Extract colors to `core/colors.py`
- [ ] Create `BaseWindow` component
- [ ] Update all imports
- [ ] Test all windows open correctly
- [ ] Update `requirements.txt`

### General:
- [ ] Update README with new structure
- [ ] Create `.env.example`
- [ ] Add type hints consistently
- [ ] Add docstrings
- [ ] Git commit after each major step

---

## ⚠️ RISKS & MITIGATION

### Risks:
1. ❌ Import errors after restructuring
2. ❌ Breaking existing functionality
3. ❌ Lost work if not careful

### Mitigation:
1. ✅ Create a backup branch first
2. ✅ Migrate one module at a time
3. ✅ Test after each step
4. ✅ Keep old files until 100% sure new structure works

---

## 🚀 EXECUTION PLAN

### Recommended approach:
1. **Create backup branch**
   ```bash
   git checkout -b refactor/professional-structure
   ```

2. **Start with Backend** (simpler, less UI dependencies)
   - Migrate step by step
   - Test each API endpoint after migration

3. **Then Desktop** (after backend is stable)
   - Migrate one module at a time
   - Keep old files during transition

4. **Final cleanup**
   - Remove old files
   - Update documentation
   - Merge to main

---

## 📚 NEXT STEPS

Tôi sẽ tạo:
1. **Migration scripts** - PowerShell scripts để tự động tạo cấu trúc
2. **Sample refactored files** - Ví dụ file đã refactor
3. **Testing checklist** - Checklist để test sau khi migrate

Bạn muốn tôi bắt đầu từ đâu trước?
- A) Backend refactoring (KHUYẾN NGHỊ - ít rủi ro hơn)
- B) Desktop refactoring
- C) Cả hai song song (nâng cao)
