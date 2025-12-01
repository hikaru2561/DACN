from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class AccessLogBase(BaseModel):
    user_id: Optional[int] = None
    status: str # GRANTED, DENIED, UNKNOWN
    similarity_score: Optional[float] = None
    note: Optional[str] = None

class AccessLogCreate(AccessLogBase):
    snapshot_path: Optional[str] = None

class AccessLog(AccessLogBase):
    id: int
    timestamp: datetime
    snapshot_path: Optional[str] = None
    
    # Có thể include thông tin user rút gọn nếu cần
    user_name: Optional[str] = None

    class Config:
        from_attributes = True
