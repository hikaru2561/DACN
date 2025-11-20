from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.teacher import Teacher
from app.schemas.teacher import TeacherResponse, TeacherCreate, TeacherUpdate

router = APIRouter(prefix="/teachers", tags=["Teachers"])

@router.get("/", response_model=List[TeacherResponse])
def get_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lấy danh sách giảng viên"""
    teachers = db.query(Teacher).offset(skip).limit(limit).all()
    return teachers

@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(teacher_id: str, db: Session = Depends(get_db)):
    """Lấy thông tin một giảng viên"""
    teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

@router.post("/", response_model=TeacherResponse)
def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    """Tạo giảng viên mới"""
    existing = db.query(Teacher).filter(Teacher.teacher_id == teacher.teacher_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Teacher ID already exists")
    
    db_teacher = Teacher(**teacher.dict())
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

@router.put("/{teacher_id}", response_model=TeacherResponse)
def update_teacher(teacher_id: str, teacher: TeacherUpdate, db: Session = Depends(get_db)):
    """Cập nhật giảng viên"""
    db_teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    for key, value in teacher.dict(exclude_unset=True).items():
        setattr(db_teacher, key, value)
    
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

@router.delete("/{teacher_id}")
def delete_teacher(teacher_id: str, db: Session = Depends(get_db)):
    """Xóa giảng viên"""
    db_teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    db.delete(db_teacher)
    db.commit()
    return {"message": f"Teacher {teacher_id} deleted successfully"}
