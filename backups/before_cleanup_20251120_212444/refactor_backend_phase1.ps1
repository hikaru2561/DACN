<# 
===============================================================================
SCRIPT REFACTORING - PHASE 1: BACKEND
Tạo cấu trúc mới và di chuyển code
===============================================================================
#>

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  REFACTORING BACKEND - PROFESSIONAL STRUCTURE" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

# Kiểm tra
if (-not (Test-Path "attendance_system/backend")) {
    Write-Host "❌ LỖI: Thư mục backend không tồn tại!" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Bước 1: Tạo cấu trúc thư mục mới..." -ForegroundColor Yellow
Write-Host ""

$backendPath = "attendance_system/backend"
$newStructure = @(
    "$backendPath/app",
    "$backendPath/app/api",
    "$backendPath/app/models",
    "$backendPath/app/schemas",
    "$backendPath/app/core",
    "$backendPath/app/utils",
    "$backendPath/tests"
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

$initFiles = @(
    "$backendPath/app/__init__.py",
    "$backendPath/app/api/__init__.py",
    "$backendPath/app/models/__init__.py",
    "$backendPath/app/schemas/__init__.py",
    "$backendPath/app/core/__init__.py",
    "$backendPath/app/utils/__init__.py"
)

foreach ($file in $initFiles) {
    if (-not (Test-Path $file)) {
        "" | Out-File -FilePath $file -Encoding UTF8
        Write-Host "  ✅ Đã tạo: $file" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "📦 Bước 3: Tạo file cấu hình cơ bản..." -ForegroundColor Yellow
Write-Host ""

# app/core/config.py
$coreConfigContent = @'
"""
Core Configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:admin@localhost:5432/attendance_db"
    
    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Attendance Management System"
    
    # Security (future)
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
'@

$coreConfigPath = "$backendPath/app/core/config.py"
if (-not (Test-Path $coreConfigPath)) {
    $coreConfigContent | Out-File -FilePath $coreConfigPath -Encoding UTF8
    Write-Host "  ✅ Đã tạo: app/core/config.py" -ForegroundColor Green
}

# app/core/database.py
$databaseContent = @'
"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency to get database session
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'@

$databasePath = "$backendPath/app/core/database.py"
if (-not (Test-Path $databasePath)) {
    $databaseContent | Out-File -FilePath $databasePath -Encoding UTF8
    Write-Host "  ✅ Đã tạo: app/core/database.py" -ForegroundColor Green
}

# app/api/deps.py
$depsContent = @'
"""
API Dependencies
Shared dependencies for API routes
"""
from typing import Generator
from sqlalchemy.orm import Session
from app.core.database import get_db


# Re-export for convenience
def get_database() -> Generator:
    """Get database session dependency"""
    return get_db()
'@

$depsPath = "$backendPath/app/api/deps.py"
if (-not (Test-Path $depsPath)) {
    $depsContent | Out-File -FilePath $depsPath -Encoding UTF8
    Write-Host "  ✅ Đã tạo: app/api/deps.py" -ForegroundColor Green
}

# .env.example
$envExampleContent = @'
# Database
DATABASE_URL=postgresql://postgres:admin@localhost:5432/attendance_db

# API
API_V1_STR=/api
PROJECT_NAME=Attendance Management System

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (if needed)
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
'@

$envExamplePath = "$backendPath/.env.example"
if (-not (Test-Path $envExamplePath)) {
    $envExampleContent | Out-File -FilePath $envExamplePath -Encoding UTF8
    Write-Host "  ✅ Đã tạo: .env.example" -ForegroundColor Green
}

Write-Host ""
Write-Host "📚 Bước 4: Tạo file README mới..." -ForegroundColor Yellow
Write-Host ""

$readmeContent = @'
# Backend - Attendance Management System

FastAPI backend with PostgreSQL database.

## 📁 Structure

```
backend/
├── app/
│   ├── api/              # API routes (by feature)
│   ├── core/             # Core config & database
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   └── utils/            # Utilities
├── tests/                # Tests
├── .env                  # Environment variables (gitignored)
├── .env.example          # Example env file
└── requirements.txt      # Python dependencies
```

## 🚀 Setup

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` from `.env.example`:
```bash
cp .env.example .env
```

4. Update DATABASE_URL in `.env`

5. Run migrations (future):
```bash
alembic upgrade head
```

6. Start server:
```bash
python -m app.main
# or
uvicorn app.main:app --reload
```

## 📖 API Documentation

Visit: http://localhost:8000/docs

## 🧪 Testing

```bash
pytest
```
'@

$readmePath = "$backendPath/README.md"
$readmeContent | Out-File -FilePath $readmePath -Encoding UTF8
Write-Host "  ✅ Đã tạo: README.md" -ForegroundColor Green

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  KẾT QUẢ - PHASE 1" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Đã tạo cấu trúc thư mục mới cho Backend" -ForegroundColor Green
Write-Host "✅ Đã tạo các file cấu hình cơ bản" -ForegroundColor Green
Write-Host ""
Write-Host "📋 CẤU TRÚC MỚI:" -ForegroundColor Cyan
Write-Host ""
Write-Host "attendance_system/backend/" -ForegroundColor White
Write-Host "├── app/" -ForegroundColor White
Write-Host "│   ├── api/            # (empty - ready for routes)" -ForegroundColor Gray
Write-Host "│   ├── core/           # config.py, database.py ✅" -ForegroundColor Green
Write-Host "│   ├── models/         # (empty - ready for models)" -ForegroundColor Gray
Write-Host "│   ├── schemas/        # (empty - ready for schemas)" -ForegroundColor Gray
Write-Host "│   └── utils/          # (empty)" -ForegroundColor Gray
Write-Host "├── tests/              # (empty)" -ForegroundColor Gray
Write-Host "├── .env.example        # ✅" -ForegroundColor Green
Write-Host "└── README.md           # ✅" -ForegroundColor Green
Write-Host ""
Write-Host "📝 BƯỚC TIẾP THEO:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Di chuyển models từ models.py → app/models/" -ForegroundColor White
Write-Host "2. Di chuyển schemas từ schemas.py → app/schemas/" -ForegroundColor White
Write-Host "3. Tách routes từ main.py → app/api/" -ForegroundColor White
Write-Host "4. Tạo app/main.py mới (entry point)" -ForegroundColor White
Write-Host "5. Test API endpoints" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  LƯU Ý: Các file cũ (models.py, schemas.py, main.py) vẫn còn!" -ForegroundColor Yellow
Write-Host "   Chúng ta sẽ di chuyển code từ đó sang cấu trúc mới." -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 Sẵn sàng cho PHASE 2: Migration code" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Cyan
