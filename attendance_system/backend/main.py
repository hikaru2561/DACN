"""
FastAPI Main Application
Attendance Management System Backend
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import uvicorn

from database import get_db, engine
from models import Base
import schemas

# Create tables (nếu chưa có)
# Base.metadata.create_all(bind=engine)  # Comment vì đã có schema.sql

# Initialize FastAPI app
app = FastAPI(
    title="Attendance Management System API",
    description="Backend API cho hệ thống quản lý điểm danh khuôn mặt",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Desktop app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

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


# ============================================================================
# STUDENTS ENDPOINTS
# ============================================================================

@app.get("/api/students", response_model=List[schemas.StudentResponse], tags=["Students"])
def get_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lấy danh sách sinh viên"""
    from models import Student
    students = db.query(Student).offset(skip).limit(limit).all()
    return students


@app.get("/api/students/{student_id}", response_model=schemas.StudentResponse, tags=["Students"])
def get_student(student_id: str, db: Session = Depends(get_db)):
    """Lấy thông tin một sinh viên"""
    from models import Student
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.post("/api/students", response_model=schemas.StudentResponse, tags=["Students"])
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    """Tạo sinh viên mới"""
    from models import Student
    
    # Kiểm tra trùng student_id
    existing = db.query(Student).filter(Student.student_id == student.student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student ID already exists")
    
    # Tạo mới
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@app.put("/api/students/{student_id}", response_model=schemas.StudentResponse, tags=["Students"])
def update_student(
    student_id: str,
    student: schemas.StudentUpdate,
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin sinh viên"""
    from models import Student
    
    db_student = db.query(Student).filter(Student.student_id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Update fields
    for key, value in student.dict(exclude_unset=True).items():
        setattr(db_student, key, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student


@app.delete("/api/students/{student_id}", tags=["Students"])
def delete_student(student_id: str, db: Session = Depends(get_db)):
    """Xóa sinh viên"""
    from models import Student
    
    db_student = db.query(Student).filter(Student.student_id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(db_student)
    db.commit()
    return {"message": f"Student {student_id} deleted successfully"}


# ============================================================================
# TEACHERS ENDPOINTS
# ============================================================================

@app.get("/api/teachers", response_model=List[schemas.TeacherResponse], tags=["Teachers"])
def get_teachers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lấy danh sách giảng viên"""
    from models import Teacher
    teachers = db.query(Teacher).offset(skip).limit(limit).all()
    return teachers


@app.get("/api/teachers/{teacher_id}", response_model=schemas.TeacherResponse, tags=["Teachers"])
def get_teacher(teacher_id: str, db: Session = Depends(get_db)):
    """Lấy thông tin một giảng viên"""
    from models import Teacher
    teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher


# ============================================================================
# SUBJECTS ENDPOINTS
# ============================================================================

@app.get("/api/subjects", response_model=List[schemas.SubjectResponse], tags=["Subjects"])
def get_subjects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lấy danh sách môn học"""
    from models import Subject
    subjects = db.query(Subject).offset(skip).limit(limit).all()
    return subjects


# ============================================================================
# CLASSES ENDPOINTS
# ============================================================================

@app.get("/api/classes", response_model=List[schemas.ClassResponse], tags=["Classes"])
def get_classes(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """Lấy danh sách lớp học"""
    from models import Class
    
    query = db.query(Class)
    if is_active is not None:
        query = query.filter(Class.is_active == is_active)
    
    classes = query.offset(skip).limit(limit).all()
    return classes


@app.get("/api/classes/{class_id}", response_model=schemas.ClassResponse, tags=["Classes"])
def get_class(class_id: int, db: Session = Depends(get_db)):
    """Lấy thông tin một lớp học"""
    from models import Class
    class_obj = db.query(Class).filter(Class.class_id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_obj


# ============================================================================
# SESSIONS ENDPOINTS
# ============================================================================

@app.get("/api/sessions", response_model=List[schemas.SessionResponse], tags=["Sessions"])
def get_sessions(
    class_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lấy danh sách buổi học"""
    from models import Session as SessionModel
    
    query = db.query(SessionModel)
    if class_id:
        query = query.filter(SessionModel.class_id == class_id)
    
    sessions = query.offset(skip).limit(limit).all()
    return sessions


@app.get("/api/sessions/{session_id}", response_model=schemas.SessionResponse, tags=["Sessions"])
def get_session(session_id: int, db: Session = Depends(get_db)):
    """Lấy thông tin một buổi học"""
    from models import Session as SessionModel
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


# ============================================================================
# ATTENDANCE ENDPOINTS
# ============================================================================

@app.get("/api/attendance", response_model=List[schemas.AttendanceResponse], tags=["Attendance"])
def get_attendance(
    session_id: int = None,
    student_id: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lấy danh sách điểm danh"""
    from models import Attendance
    
    query = db.query(Attendance)
    if session_id:
        query = query.filter(Attendance.session_id == session_id)
    if student_id:
        query = query.filter(Attendance.student_id == student_id)
    
    attendance = query.offset(skip).limit(limit).all()
    return attendance


@app.post("/api/attendance", response_model=schemas.AttendanceResponse, tags=["Attendance"])
def create_attendance(attendance: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    """Tạo bản ghi điểm danh"""
    from models import Attendance
    from datetime import datetime
    
    # Kiểm tra đã điểm danh chưa
    existing = db.query(Attendance).filter(
        Attendance.session_id == attendance.session_id,
        Attendance.student_id == attendance.student_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Attendance already recorded")
    
    # Tạo mới
    db_attendance = Attendance(**attendance.dict())
    if not db_attendance.check_in_time:
        db_attendance.check_in_time = datetime.now()
    
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance


# ============================================================================
# CAMERAS ENDPOINTS
# ============================================================================

@app.get("/api/cameras", response_model=List[schemas.CameraDeviceResponse], tags=["Cameras"])
def get_cameras(
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """Lấy danh sách camera"""
    from models import CameraDevice
    
    query = db.query(CameraDevice)
    if is_active is not None:
        query = query.filter(CameraDevice.is_active == is_active)
    
    cameras = query.all()
    return cameras


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 Starting Attendance Management System API")
    print("=" * 80)
    print(f"📡 Server: http://localhost:8000")
    print(f"📚 Docs: http://localhost:8000/docs")
    print(f"📖 ReDoc: http://localhost:8000/redoc")
    print("=" * 80)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload khi code thay đổi
    )
