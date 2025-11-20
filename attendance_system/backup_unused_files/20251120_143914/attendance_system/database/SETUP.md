# Setup PostgreSQL Database - Step by Step

## 📋 Yêu cầu

- PostgreSQL 14+ installed
- pgAdmin 4 (hoặc command line)
- Python 3.8+ (để test connection)

---

## 🚀 BƯỚC 1: Cài đặt PostgreSQL

### Windows

1. Download từ: https://www.postgresql.org/download/windows/
2. Chạy installer
3. Chọn components:
   - ✅ PostgreSQL Server
   - ✅ pgAdmin 4
   - ✅ Command Line Tools
4. Set password cho user `postgres` (nhớ password này!)
5. Port mặc định: `5432`

### Verify Installation

```powershell
# Check PostgreSQL version
psql --version

# Login vào PostgreSQL
psql -U postgres
```

---

## 🗄️ BƯỚC 2: Tạo Database

### Option 1: Using pgAdmin 4

1. Mở **pgAdmin 4**
2. Connect to server (localhost:5432)
3. Right-click **Databases** → **Create** → **Database**
   - Database name: `attendance_system`
   - Owner: `postgres`
   - Encoding: `UTF8`
4. Click **Save**

### Option 2: Using psql (Command Line)

```powershell
# Login
psql -U postgres

# Tạo database
CREATE DATABASE attendance_system
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8';

# Switch to database
\c attendance_system

# Exit
\q
```

---

## 📝 BƯỚC 3: Import Schema

### Option 1: Using pgAdmin 4

1. Click vào database `attendance_system`
2. Menu **Tools** → **Query Tool**
3. Open file `schema.sql`
4. Click **Execute** (F5)

### Option 2: Using psql

```powershell
# Chạy từ thư mục database/
cd D:\HUTECH\DACN\attendance_system\database

# Import schema
psql -U postgres -d attendance_system -f schema.sql
```

---

## ✅ BƯỚC 4: Verify Database

### Check tables

```sql
-- List all tables
\dt

-- Count tables
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public';

-- Expected output: ~15 tables
```

### Check sample data

```sql
-- List users
SELECT * FROM users;

-- Expected: 1 admin, 1 teacher
```

### Check triggers

```sql
-- List triggers
SELECT trigger_name, event_object_table 
FROM information_schema.triggers 
WHERE trigger_schema = 'public';
```

---

## 🔐 BƯỚC 5: Tạo Application User

### Create dedicated user (bảo mật hơn)

```sql
-- Tạo user mới
CREATE ROLE attendance_app WITH LOGIN PASSWORD 'YourSecurePassword123!';

-- Grant permissions
GRANT CONNECT ON DATABASE attendance_system TO attendance_app;
GRANT USAGE ON SCHEMA public TO attendance_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO attendance_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO attendance_app;

-- Test login
\c attendance_system attendance_app
```

---

## 🐍 BƯỚC 6: Test Connection từ Python

### Install dependencies

```powershell
pip install psycopg2-binary
```

### Test script

Create `test_connection.py`:

```python
import psycopg2
from psycopg2 import sql

# Connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'attendance_system',
    'user': 'postgres',  # Hoặc 'attendance_app'
    'password': 'your_password_here'
}

try:
    # Connect
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Test query
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"✅ Connected to: {version[0]}")
    
    # Count tables
    cur.execute("""
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema = 'public';
    """)
    table_count = cur.fetchone()[0]
    print(f"✅ Tables: {table_count}")
    
    # Count users
    cur.execute("SELECT COUNT(*) FROM users;")
    user_count = cur.fetchone()[0]
    print(f"✅ Users: {user_count}")
    
    # Close
    cur.close()
    conn.close()
    
    print("\n🎉 Database connection successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
```

Run:
```powershell
python test_connection.py
```

Expected output:
```
✅ Connected to: PostgreSQL 14.x...
✅ Tables: 15
✅ Users: 2
🎉 Database connection successful!
```

---

## 🛠️ Troubleshooting

### Lỗi: "password authentication failed"
→ Check password của user `postgres`
→ Hoặc sửa trong `pg_hba.conf`:
  - Windows: `C:\Program Files\PostgreSQL\14\data\pg_hba.conf`
  - Đổi method từ `md5` → `trust` (development only!)

### Lỗi: "database does not exist"
→ Chạy lại BƯỚC 2

### Lỗi: "permission denied for table"
→ Chạy lại GRANT commands ở BƯỚC 5

### Port 5432 bị chiếm
→ Check trong `postgresql.conf`:
  - Windows: `C:\Program Files\PostgreSQL\14\data\postgresql.conf`
  - Đổi `port = 5433`

---

## 📚 Next Steps

Sau khi database setup xong:

1. ✅ Tích hợp với Face Recognition V2
2. ✅ Tạo Backend API (Flask/FastAPI)
3. ✅ Tạo Frontend Desktop App
4. ✅ Module điểm danh tự động

---

## 📄 File Structure

```
attendance_system/
└── database/
    ├── schema.sql         # ← Main schema (CHẠY FILE NÀY)
    ├── ERD.md             # Documentation
    ├── SETUP.md           # ← File này
    └── test_connection.py # Test script
```

---

## 🔑 Default Credentials

**Admin:**
- Username: `admin`
- Password: `admin123`

**Teacher:**
- Username: `teacher1`
- Password: `teacher123`

⚠️ **CẢNH BÁO**: Đổi passwords trước khi deploy production!

---

Bạn muốn tôi tiếp tục với BƯỚC tiếp theo không? (Backend API hoặc tích hợp Face Recognition)
