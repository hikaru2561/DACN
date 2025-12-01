from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Nullable cho trường hợp người lạ
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    similarity_score = Column(Float, nullable=True)
    snapshot_path = Column(String, nullable=True)
    
    status = Column(String, nullable=False) # GRANTED, DENIED, UNKNOWN
    note = Column(Text, nullable=True)

    # Relationship
    user = relationship("User", backref="access_logs")
