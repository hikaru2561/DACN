from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/attendance-stats")
def get_attendance_stats(db: Session = Depends(get_db)):
    """Lấy thống kê điểm danh (từ View)"""
    try:
        result = db.execute(text("SELECT * FROM v_attendance_statistics"))
        stats = []
        for row in result:
            stats.append({
                "class_id": row.class_id,
                "class_name": row.class_name,
                "subject_name": row.subject_name,
                "teacher_name": row.teacher_name,
                "total_sessions": row.total_sessions,
                "total_students": row.total_students,
                "total_attendance_records": row.total_attendance_records,
                "attendance_rate": float(row.attendance_rate) if row.attendance_rate else 0.0
            })
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")
