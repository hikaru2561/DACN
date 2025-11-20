"""
FastAPI Main Application
Attendance Management System Backend
"""
import sys
import os
from pathlib import Path

# Add parent directory to sys.path if running from app directory
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import uvicorn

from app.core.database import get_db, engine, Base
from app.api import api_router

# Create tables (nếu chưa có)
# Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Attendance Management System API",
    description="Backend API cho hệ thống quản lý điểm danh khuôn mặt",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router)

# Root endpoints
@app.get("/", tags=["Root"])
def read_root():
    """API Root - Health check"""
    return {
        "message": "Attendance Management System API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", tags=["Root"])
def health_check(db: Session = Depends(get_db)):
    """Health check - kiểm tra kết nối database"""
    try:
        # Test query
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 Starting Attendance Management System API")
    print("=" * 80)
    print(f"📡 Server: http://localhost:8000")
    print(f"📚 Docs: http://localhost:8000/docs")
    print("=" * 80)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
