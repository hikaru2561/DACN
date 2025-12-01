from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.access_log import AccessLog
from app.models.user import User
from app.schemas import access_log as log_schema

router = APIRouter()

@router.get("/", response_model=List[log_schema.AccessLog])
def read_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve access logs.
    """
    logs = db.query(AccessLog).order_by(AccessLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    # Enrich with user name
    for log in logs:
        if log.user:
            log.user_name = log.user.full_name
            
    return logs

@router.post("/", response_model=log_schema.AccessLog)
def create_log(
    *,
    db: Session = Depends(get_db),
    log_in: log_schema.AccessLogCreate
) -> Any:
    """
    Create new access log.
    """
    log = AccessLog(
        user_id=log_in.user_id,
        status=log_in.status,
        similarity_score=log_in.similarity_score,
        snapshot_path=log_in.snapshot_path,
        note=log_in.note
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

@router.delete("/{log_id}", response_model=log_schema.AccessLog)
def delete_log(
    *,
    db: Session = Depends(get_db),
    log_id: int
) -> Any:
    """
    Delete an access log.
    """
    log = db.query(AccessLog).filter(AccessLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    db.delete(log)
    db.commit()
    return log
