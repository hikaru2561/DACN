"""
FastAPI Main Application - NEW STRUCTURE
Attendance Management System Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import configuration
from app.core.config import settings
from app.core.database import engine, Base

# TODO: Import routers when they are created
# from app.api import students, teachers, subjects, classes, sessions, attendance, cameras, reports

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
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

# Root endpoint
@app.get("/", tags=["Root"])
def read_root():
    """API Root - Health check"""
    return {
        "message": "Attendance Management System API - NEW STRUCTURE",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health", tags=["Root"])
def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "message": "NEW STRUCTURE - Routes coming soon"
    }

# TODO: Include routers
# app.include_router(students.router, prefix="/api/students", tags=["Students"])
# app.include_router(teachers.router, prefix="/api/teachers", tags=["Teachers"])
# ... etc

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 Starting Attendance Management System API - NEW STRUCTURE")
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
