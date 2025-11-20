# 🧹 Hướng Dẫn Dọn Dẹp Files Không Sử Dụng

## 📋 Tổng Quan

Script `cleanup_unused_files.ps1` giúp dọn dẹp các file không còn được sử dụng trong hệ thống, giữ cho codebase sạch sẽ và dễ quản lý.

---

## 🗂️ Danh Sách Files Sẽ Dọn Dẹp

### 1. **student_module.py** (DEPRECATED)
- **Trạng thái**: Đã lỗi thời
- **Lý do**: Đã được thay thế hoàn toàn bởi `student_module_new.py`
- **Sử dụng**: Không còn được import trong `main.py`
- **Kích thước**: ~25 KB

**Chi tiết:**
```python
# main.py sử dụng:
from student_module_new import StudentModuleNew  # ✅ Mới

# KHÔNG sử dụng:
from student_module import StudentModule  # ❌ Cũ
```

---

### 2. **config_manager.py** (UNUSED)
- **Trạng thái**: Không sử dụng
- **Lý do**: Configuration đã được tích hợp trực tiếp vào `config.py`
- **Sử dụng**: Không có module nào import
- **Kích thước**: ~12 KB

**Chi tiết:**
- File này là GUI tool để cập nhật config
- Hiện tại config được quản lý trực tiếp qua `config.py`
- Không cần thiết cho hệ thống production

---

### 3. **update_camera.py** (UNUSED)
- **Trạng thái**: Không sử dụng
- **Lý do**: Có thể cập nhật trực tiếp trong `config.py`
- **Sử dụng**: Không có module nào import
- **Kích thước**: ~2 KB

**Chi tiết:**
- Script đơn giản để update camera URL
- Dễ dàng thay đổi trực tiếp trong `config.py`:
  ```python
  CAMERA_CONFIG = {
      "stream_url": "http://192.168.1.169/stream"  # Sửa trực tiếp ở đây
  }
  ```

---

### 4. **temp/** (EMPTY FOLDER)
- **Trạng thái**: Thư mục rỗng
- **Lý do**: Không chứa file nào, không được sử dụng
- **Kích thước**: 0 KB

---

## 🚀 Cách Sử Dụng Script

### Bước 1: Chạy Script

```powershell
cd D:\HUTECH\DACN\attendance_system
.\cleanup_unused_files.ps1
```

### Bước 2: Xem Danh Sách

Script sẽ hiển thị:
- ✅ Tên file
- 📊 Kích thước
- 📝 Lý do dọn dẹp
- ⚠️ Trạng thái

### Bước 3: Xác Nhận

```
Bạn có chắc muốn tiếp tục? (y/N): y
```

### Bước 4: Hoàn Tất

Script sẽ:
1. ✅ **Backup** tất cả files vào `backup_unused_files/[timestamp]/`
2. 🗑️ **Xóa** files khỏi thư mục gốc
3. 📝 **Tạo** file README trong backup

---

## 📁 Cấu Trúc Backup

```
attendance_system/
├── backup_unused_files/
│   └── 20251114_143022/          # Timestamp
│       ├── desktop/
│       │   ├── student_module.py
│       │   ├── config_manager.py
│       │   └── update_camera.py
│       ├── temp/
│       └── README.txt             # Hướng dẫn khôi phục
```

---

## 🔄 Cách Khôi Phục Files

### Khôi Phục Một File

```powershell
# Ví dụ: Khôi phục student_module.py
Copy-Item -Path "backup_unused_files\20251114_143022\desktop\student_module.py" `
          -Destination "desktop\student_module.py" -Force
```

### Khôi Phục Tất Cả

```powershell
# Khôi phục toàn bộ từ backup
Copy-Item -Path "backup_unused_files\20251114_143022\*" `
          -Destination "." -Recurse -Force
```

---

## ✅ Kiểm Tra Sau Khi Dọn Dẹp

### 1. Test Chức Năng Chính

```powershell
cd desktop
python main.py
```

**Kiểm tra:**
- ✅ Đăng nhập thành công
- ✅ Mở module "Quản lý Sinh viên" (dùng `student_module_new.py`)
- ✅ Thêm/Sửa/Xóa sinh viên
- ✅ Chụp ảnh sinh viên
- ✅ Điểm danh hoạt động bình thường

### 2. Kiểm Tra Import

```powershell
python -c "from student_module_new import StudentModuleNew; print('OK')"
# Output: OK
```

### 3. Kiểm Tra Config

```powershell
python -c "from config import CAMERA_CONFIG; print(CAMERA_CONFIG['stream_url'])"
# Output: http://192.168.1.169/stream
```

---

## 🗑️ Xóa Backup (Sau Khi Test)

Nếu hệ thống hoạt động tốt sau **3-7 ngày**, có thể xóa backup:

```powershell
# Xóa tất cả backup
Remove-Item -Path "backup_unused_files" -Recurse -Force

# Hoặc chỉ xóa backup cũ (giữ lại backup mới nhất)
Get-ChildItem "backup_unused_files" | 
    Sort-Object CreationTime | 
    Select-Object -SkipLast 1 | 
    Remove-Item -Recurse -Force
```

---

## 📊 Lợi Ích

### Trước Khi Dọn Dẹp
```
attendance_system/
├── desktop/
│   ├── student_module.py         # ❌ Cũ (25 KB)
│   ├── student_module_new.py     # ✅ Mới
│   ├── config_manager.py         # ❌ Unused (12 KB)
│   ├── update_camera.py          # ❌ Unused (2 KB)
│   └── ...
└── temp/                         # ❌ Empty
```

### Sau Khi Dọn Dẹp
```
attendance_system/
├── desktop/
│   ├── student_module_new.py     # ✅ Đang dùng
│   ├── config.py                 # ✅ Config chính
│   └── ...
└── backup_unused_files/          # 💾 Backup an toàn
    └── 20251114_143022/
```

**Tiết kiệm:**
- 📦 ~39 KB không gian
- 🧹 Code sạch sẽ hơn
- 🔍 Dễ tìm kiếm và bảo trì
- 📚 Không còn confusion giữa file cũ/mới

---

## ⚠️ Lưu Ý

### ✅ An Toàn
- Script **LUÔN backup** trước khi xóa
- Backup có **timestamp** rõ ràng
- Có **README.txt** hướng dẫn khôi phục

### ⚠️ Không Xóa
Script này **KHÔNG** xóa:
- Files đang được sử dụng
- Database files
- Model files
- Dataset files
- Log files
- Config files đang dùng

### 🔍 Xác Minh Trước Khi Chạy

Nếu không chắc chắn, kiểm tra file có được import không:

```powershell
# Tìm tất cả import của student_module.py
Get-ChildItem -Recurse -Filter "*.py" | 
    Select-String "import.*student_module[^_]|from.*student_module[^_]"

# Nếu không có kết quả → An toàn để xóa
```

---

## 📞 Hỗ Trợ

Nếu gặp vấn đề sau khi dọn dẹp:

1. **Khôi phục từ backup** (xem phần "Cách Khôi Phục Files")
2. **Kiểm tra logs** trong `attendance_system/logs/`
3. **Test lại** các module chính
4. **Liên hệ** dev team nếu cần hỗ trợ

---

## 📝 Changelog

### 2025-11-14
- ✅ Initial cleanup script
- 📋 Identified 4 unused files/folders
- 💾 Added safe backup mechanism
- 📚 Created documentation

---

## 🎯 Kế Hoạch Tương Lai

### Có Thể Dọn Dẹp Tiếp

Sau khi test ổn định, có thể xem xét:
- 📄 **Markdown files cũ** (GUIDE, README trùng lặp)
- 🗂️ **Backup folders cũ** (giữ lại 1-2 backup gần nhất)
- 📦 **__pycache__** folders (có thể recreate)

### Tự Động Hóa

Có thể tạo script tự động:
- 🔄 Dọn dẹp `__pycache__` định kỳ
- 📊 Phân tích files không dùng tự động
- 🧹 Clean up logs cũ

---

**💡 Best Practice**: Chạy cleanup script sau mỗi lần cập nhật lớn hoặc khi refactor code để giữ project sạch sẽ!
