from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SubjectBase(BaseModel):
    subject_id: str
    subject_name: str
    credits: int = 3
    description: Optional[str] = None


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    subject_name: Optional[str] = None
    credits: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SubjectResponse(SubjectBase):
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
