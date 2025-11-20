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


@app.post("/api/teachers", response_model=schemas.TeacherResponse, tags=["Teachers"])
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    """Tạo giảng viên mới"""
    from models import Teacher
    
    # Kiểm tra trùng teacher_id
    existing = db.query(Teacher).filter(Teacher.teacher_id == teacher.teacher_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Teacher ID already exists")
    
    # Tạo mới
    db_teacher = Teacher(**teacher.dict())
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


@app.put("/api/teachers/{teacher_id}", response_model=schemas.TeacherResponse, tags=["Teachers"])
def update_teacher(
    teacher_id: str,
    teacher: schemas.TeacherUpdate,
    db: Session = Depends(get_db)
):
    """Cập nhật giảng viên"""
    from models import Teacher
    
    db_teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # Update fields
    for key, value in teacher.dict(exclude_unset=True).items():
        setattr(db_teacher, key, value)
    
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


@app.delete("/api/teachers/{teacher_id}", tags=["Teachers"])
def delete_teacher(teacher_id: str, db: Session = Depends(get_db)):
    """Xóa giảng viên"""
    from models import Teacher
    
    db_teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    db.delete(db_teacher)
    db.commit()
    return {"message": f"Teacher {teacher_id} deleted successfully"}


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


@app.get("/api/subjects/{subject_id}", response_model=schemas.SubjectResponse, tags=["Subjects"])
def get_subject(subject_id: str, db: Session = Depends(get_db)):
    """Lấy thông tin một môn học"""
    from models import Subject
    subject = db.query(Subject).filter(Subject.subject_id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@app.post("/api/subjects", response_model=schemas.SubjectResponse, tags=["Subjects"])
def create_subject(subject: schemas.SubjectCreate, db: Session = Depends(get_db)):
    """Tạo môn học mới"""
    from models import Subject
    
    # Kiểm tra trùng subject_id
    existing = db.query(Subject).filter(Subject.subject_id == subject.subject_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Subject ID already exists")
    
    # Tạo mới
    db_subject = Subject(**subject.dict())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject


@app.put("/api/subjects/{subject_id}", response_model=schemas.SubjectResponse, tags=["Subjects"])
def update_subject(
    subject_id: str,
    subject: schemas.SubjectUpdate,
    db: Session = Depends(get_db)
):
    """Cập nhật môn học"""
    from models import Subject
    
    db_subject = db.query(Subject).filter(Subject.subject_id == subject_id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Update fields
    for key, value in subject.dict(exclude_unset=True).items():
        setattr(db_subject, key, value)
    
    db.commit()
    db.refresh(db_subject)
    return db_subject


@app.delete("/api/subjects/{subject_id}", tags=["Subjects"])
def delete_subject(subject_id: str, db: Session = Depends(get_db)):
    """Xóa môn học"""
    from models import Subject
    
    db_subject = db.query(Subject).filter(Subject.subject_id == subject_id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    db.delete(db_subject)
    db.commit()
    return {"message": f"Subject {subject_id} deleted successfully"}


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


@app.post("/api/classes", response_model=schemas.ClassResponse, tags=["Classes"])
def create_class(class_data: schemas.ClassCreate, db: Session = Depends(get_db)):
    """Tạo lớp học mới"""
    from models import Class
    
    # Tạo mới
    db_class = Class(**class_data.dict())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class


@app.put("/api/classes/{class_id}", response_model=schemas.ClassResponse, tags=["Classes"])
def update_class(
    class_id: int,
    class_data: schemas.ClassUpdate,
    db: Session = Depends(get_db)
):
    """Cập nhật lớp học"""
    from models import Class
    
    db_class = db.query(Class).filter(Class.class_id == class_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Update fields
    for key, value in class_data.dict(exclude_unset=True).items():
        setattr(db_class, key, value)
    
    db.commit()
    db.refresh(db_class)
    return db_class


@app.delete("/api/classes/{class_id}", tags=["Classes"])
def delete_class(class_id: int, db: Session = Depends(get_db)):
    """Xóa lớp học"""
    from models import Class
    
    db_class = db.query(Class).filter(Class.class_id == class_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    
    db.delete(db_class)
    db.commit()
    return {"message": f"Class {class_id} deleted successfully"}


@app.get("/api/classes/{class_id}/students", response_model=List[schemas.StudentResponse], tags=["Classes"])
def get_class_students(class_id: int, db: Session = Depends(get_db)):
    """Lấy danh sách sinh viên trong lớp"""
    from models import Class, ClassEnrollment, Student
    
    # Kiểm tra lớp tồn tại
    class_obj = db.query(Class).filter(Class.class_id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Lấy sinh viên qua bảng enrollment
    students = db.query(Student).join(
        ClassEnrollment,
        Student.student_id == ClassEnrollment.student_id
    ).filter(
        ClassEnrollment.class_id == class_id,
        ClassEnrollment.is_active == True
    ).all()
    
    return students


@app.post("/api/classes/{class_id}/students", tags=["Classes"])
def enroll_student(
    class_id: int,
    enrollment: dict,
    db: Session = Depends(get_db)
):
    """Thêm sinh viên vào lớp"""
    from models import Class, Student, ClassEnrollment
    
    student_id = str(enrollment.get("student_id"))  # Convert to string
    
    # Kiểm tra lớp tồn tại
    class_obj = db.query(Class).filter(Class.class_id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Kiểm tra sinh viên tồn tại
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Kiểm tra đã đăng ký chưa
    existing = db.query(ClassEnrollment).filter(
        ClassEnrollment.class_id == class_id,
        ClassEnrollment.student_id == student_id
    ).first()
    
    if existing:
        if existing.is_active:
            raise HTTPException(status_code=400, detail="Student already enrolled")
        else:
            # Kích hoạt lại
            existing.is_active = True
            db.commit()
            return {"message": "Student re-enrolled successfully"}
    
    # Tạo enrollment mới
    db_enrollment = ClassEnrollment(
        class_id=class_id,
        student_id=student_id
    )
    db.add(db_enrollment)
    db.commit()
    
    return {"message": "Student enrolled successfully"}


@app.delete("/api/classes/{class_id}/students/{student_id}", tags=["Classes"])
def unenroll_student(class_id: int, student_id: str, db: Session = Depends(get_db)):
    """Xóa sinh viên khỏi lớp"""
    from models import ClassEnrollment
    
    enrollment = db.query(ClassEnrollment).filter(
        ClassEnrollment.class_id == class_id,
        ClassEnrollment.student_id == student_id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    db.delete(enrollment)
    db.commit()
    
    return {"message": "Student unenrolled successfully"}


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


@app.post("/api/sessions", response_model=schemas.SessionResponse, tags=["Sessions"])
def create_session(session_data: schemas.SessionCreate, db: Session = Depends(get_db)):
    """Tạo buổi học mới"""
    from models import Session as SessionModel, Class
    
    # Kiểm tra lớp tồn tại
    class_obj = db.query(Class).filter(Class.class_id == session_data.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Tạo mới
    db_session = SessionModel(**session_data.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@app.put("/api/sessions/{session_id}", response_model=schemas.SessionResponse, tags=["Sessions"])
def update_session(
    session_id: int,
    session_data: schemas.SessionUpdate,
    db: Session = Depends(get_db)
):
    """Cập nhật buổi học"""
    from models import Session as SessionModel
    
    db_session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update fields
    for key, value in session_data.dict(exclude_unset=True).items():
        setattr(db_session, key, value)
    
    db.commit()
    db.refresh(db_session)
    return db_session


@app.delete("/api/sessions/{session_id}", tags=["Sessions"])
def delete_session(session_id: int, db: Session = Depends(get_db)):
    """Xóa buổi học"""
    from models import Session as SessionModel
    
    db_session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(db_session)
    db.commit()
    return {"message": f"Session {session_id} deleted successfully"}


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


@app.get("/api/attendance/{attendance_id}", response_model=schemas.AttendanceResponse, tags=["Attendance"])
def get_attendance_by_id(attendance_id: int, db: Session = Depends(get_db)):
    """Lấy thông tin một bản ghi điểm danh"""
    from models import Attendance
    
    attendance = db.query(Attendance).filter(Attendance.attendance_id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return attendance


@app.put("/api/attendance/{attendance_id}", response_model=schemas.AttendanceResponse, tags=["Attendance"])
def update_attendance(
    attendance_id: int,
    attendance_data: schemas.AttendanceUpdate,
    db: Session = Depends(get_db)
):
    """Cập nhật bản ghi điểm danh"""
    from models import Attendance
    
    db_attendance = db.query(Attendance).filter(Attendance.attendance_id == attendance_id).first()
    if not db_attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    
    # Update fields
    for key, value in attendance_data.dict(exclude_unset=True).items():
        setattr(db_attendance, key, value)
    
    db.commit()
    db.refresh(db_attendance)
    return db_attendance


@app.delete("/api/attendance/{attendance_id}", tags=["Attendance"])
def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    """Xóa bản ghi điểm danh"""
    from models import Attendance
    
    db_attendance = db.query(Attendance).filter(Attendance.attendance_id == attendance_id).first()
    if not db_attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    
    db.delete(db_attendance)
    db.commit()
    return {"message": "Attendance deleted successfully"}


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
