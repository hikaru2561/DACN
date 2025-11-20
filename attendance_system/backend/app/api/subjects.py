from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.subject import Subject
from app.schemas.subject import SubjectResponse, SubjectCreate, SubjectUpdate

router = APIRouter(prefix="/subjects", tags=["Subjects"])

@router.get("/", response_model=List[SubjectResponse])
def get_subjects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lấy danh sách môn học"""
    subjects = db.query(Subject).offset(skip).limit(limit).all()
    return subjects

@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject(subject_id: str, db: Session = Depends(get_db)):
    """Lấy thông tin một môn học"""
    subject = db.query(Subject).filter(Subject.subject_id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@router.post("/", response_model=SubjectResponse)
def create_subject(subject: SubjectCreate, db: Session = Depends(get_db)):
    """Tạo môn học mới"""
    existing = db.query(Subject).filter(Subject.subject_id == subject.subject_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Subject ID already exists")
    
    db_subject = Subject(**subject.dict())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(subject_id: str, subject: SubjectUpdate, db: Session = Depends(get_db)):
    """Cập nhật môn học"""
    db_subject = db.query(Subject).filter(Subject.subject_id == subject_id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    for key, value in subject.dict(exclude_unset=True).items():
        setattr(db_subject, key, value)
    
    db.commit()
    db.refresh(db_subject)
    return db_subject

@router.delete("/{subject_id}")
def delete_subject(subject_id: str, db: Session = Depends(get_db)):
    """Xóa môn học"""
    db_subject = db.query(Subject).filter(Subject.subject_id == subject_id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    db.delete(db_subject)
    db.commit()
    return {"message": f"Subject {subject_id} deleted successfully"}
