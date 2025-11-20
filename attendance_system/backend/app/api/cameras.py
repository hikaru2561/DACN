from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.camera import CameraDevice
from app.schemas.camera import CameraDeviceResponse, CameraDeviceCreate, CameraDeviceUpdate

router = APIRouter(prefix="/cameras", tags=["Cameras"])

@router.get("/", response_model=List[CameraDeviceResponse])
def get_cameras(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Lấy danh sách camera"""
    query = db.query(CameraDevice)
    if is_active is not None:
        query = query.filter(CameraDevice.is_active == is_active)
    
    cameras = query.all()
    return cameras

@router.get("/{device_id}", response_model=CameraDeviceResponse)
def get_camera(device_id: int, db: Session = Depends(get_db)):
    """Lấy thông tin một camera"""
    camera = db.query(CameraDevice).filter(CameraDevice.device_id == device_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

@router.post("/", response_model=CameraDeviceResponse)
def create_camera(camera: CameraDeviceCreate, db: Session = Depends(get_db)):
    """Thêm camera mới"""
    existing = db.query(CameraDevice).filter(CameraDevice.device_code == camera.device_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Device code already exists")
    
    db_camera = CameraDevice(**camera.dict())
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera

@router.put("/{device_id}", response_model=CameraDeviceResponse)
def update_camera(device_id: int, camera: CameraDeviceUpdate, db: Session = Depends(get_db)):
    """Cập nhật thông tin camera"""
    db_camera = db.query(CameraDevice).filter(CameraDevice.device_id == device_id).first()
    if not db_camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    for key, value in camera.dict(exclude_unset=True).items():
        setattr(db_camera, key, value)
    
    db.commit()
    db.refresh(db_camera)
    return db_camera

@router.delete("/{device_id}")
def delete_camera(device_id: int, db: Session = Depends(get_db)):
    """Xóa camera"""
    db_camera = db.query(CameraDevice).filter(CameraDevice.device_id == device_id).first()
    if not db_camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    db.delete(db_camera)
    db.commit()
    return {"message": "Camera deleted successfully"}
