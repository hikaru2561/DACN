from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CameraDeviceBase(BaseModel):
    device_name: str
    device_code: str
    stream_url: str
    location: Optional[str] = None
    room: Optional[str] = None


class CameraDeviceCreate(CameraDeviceBase):
    pass


class CameraDeviceUpdate(BaseModel):
    device_name: Optional[str] = None
    stream_url: Optional[str] = None
    location: Optional[str] = None
    room: Optional[str] = None
    is_active: Optional[bool] = None


class CameraDeviceResponse(CameraDeviceBase):
    device_id: int
    is_active: bool
    last_heartbeat: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True
