from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models.attendance import Attendance
from app.schemas.attendance import AttendanceResponse, AttendanceCreate, AttendanceUpdate

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.get("/", response_model=List[AttendanceResponse])
def get_attendance(
    session_id: Optional[int] = None,
    student_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lấy danh sách điểm danh"""
    query = db.query(Attendance)
    if session_id:
        query = query.filter(Attendance.session_id == session_id)
    if student_id:
        query = query.filter(Attendance.student_id == student_id)
    
    attendance = query.offset(skip).limit(limit).all()
    return attendance

@router.post("/", response_model=AttendanceResponse)
def create_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    """Tạo bản ghi điểm danh"""
    existing = db.query(Attendance).filter(
        Attendance.session_id == attendance.session_id,
        Attendance.student_id == attendance.student_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Attendance already recorded")
    
    db_attendance = Attendance(**attendance.dict())
    if not db_attendance.check_in_time:
        db_attendance.check_in_time = datetime.now()
    
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

@router.get("/{attendance_id}", response_model=AttendanceResponse)
def get_attendance_by_id(attendance_id: int, db: Session = Depends(get_db)):
    """Lấy thông tin một bản ghi điểm danh"""
    attendance = db.query(Attendance).filter(Attendance.attendance_id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return attendance

@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(attendance_id: int, attendance_data: AttendanceUpdate, db: Session = Depends(get_db)):
    """Cập nhật bản ghi điểm danh"""
    db_attendance = db.query(Attendance).filter(Attendance.attendance_id == attendance_id).first()
    if not db_attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    
    for key, value in attendance_data.dict(exclude_unset=True).items():
        setattr(db_attendance, key, value)
    
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

@router.delete("/{attendance_id}")
def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    """Xóa bản ghi điểm danh"""
    db_attendance = db.query(Attendance).filter(Attendance.attendance_id == attendance_id).first()
    if not db_attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    
    db.delete(db_attendance)
    db.commit()
    return {"message": "Attendance deleted successfully"}
