from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.class_ import Class, ClassEnrollment
from app.models.student import Student
from app.schemas.class_ import ClassResponse, ClassCreate, ClassUpdate
from app.schemas.student import StudentResponse

router = APIRouter(prefix="/classes", tags=["Classes"])

@router.get("/", response_model=List[ClassResponse])
def get_classes(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Lấy danh sách lớp học"""
    query = db.query(Class)
    if is_active is not None:
        query = query.filter(Class.is_active == is_active)
    
    classes = query.offset(skip).limit(limit).all()
    return classes

@router.get("/{class_id}", response_model=ClassResponse)
def get_class(class_id: int, db: Session = Depends(get_db)):
    """Lấy thông tin một lớp học"""
    class_obj = db.query(Class).filter(Class.class_id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_obj

@router.post("/", response_model=ClassResponse)
def create_class(class_data: ClassCreate, db: Session = Depends(get_db)):
    """Tạo lớp học mới"""
    db_class = Class(**class_data.dict())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

@router.put("/{class_id}", response_model=ClassResponse)
def update_class(class_id: int, class_data: ClassUpdate, db: Session = Depends(get_db)):
    """Cập nhật lớp học"""
    db_class = db.query(Class).filter(Class.class_id == class_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    
    for key, value in class_data.dict(exclude_unset=True).items():
        setattr(db_class, key, value)
    
    db.commit()
    db.refresh(db_class)
    return db_class

@router.delete("/{class_id}")
def delete_class(class_id: int, db: Session = Depends(get_db)):
    """Xóa lớp học"""
    db_class = db.query(Class).filter(Class.class_id == class_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    
    db.delete(db_class)
    db.commit()
    return {"message": f"Class {class_id} deleted successfully"}

@router.get("/{class_id}/students", response_model=List[StudentResponse])
def get_class_students(class_id: int, db: Session = Depends(get_db)):
    """Lấy danh sách sinh viên trong lớp"""
    class_obj = db.query(Class).filter(Class.class_id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    students = db.query(Student).join(
        ClassEnrollment,
        Student.student_id == ClassEnrollment.student_id
    ).filter(
        ClassEnrollment.class_id == class_id,
        ClassEnrollment.is_active == True
    ).all()
    
    return students

@router.post("/{class_id}/students")
def enroll_student(class_id: int, enrollment: dict, db: Session = Depends(get_db)):
    """Thêm sinh viên vào lớp"""
    student_id = str(enrollment.get("student_id"))
    
    class_obj = db.query(Class).filter(Class.class_id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    existing = db.query(ClassEnrollment).filter(
        ClassEnrollment.class_id == class_id,
        ClassEnrollment.student_id == student_id
    ).first()
    
    if existing:
        if existing.is_active:
            raise HTTPException(status_code=400, detail="Student already enrolled")
        else:
            existing.is_active = True
            db.commit()
            return {"message": "Student re-enrolled successfully"}
    
    db_enrollment = ClassEnrollment(
        class_id=class_id,
        student_id=student_id
    )
    db.add(db_enrollment)
    db.commit()
    
    return {"message": "Student enrolled successfully"}

@router.delete("/{class_id}/students/{student_id}")
def unenroll_student(class_id: int, student_id: str, db: Session = Depends(get_db)):
    """Xóa sinh viên khỏi lớp"""
    enrollment = db.query(ClassEnrollment).filter(
        ClassEnrollment.class_id == class_id,
        ClassEnrollment.student_id == student_id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    db.delete(enrollment)
    db.commit()
    
    return {"message": "Student unenrolled successfully"}
