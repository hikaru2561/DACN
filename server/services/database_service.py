"""
Database service - Optimized Version
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, text
from models.schemas import User, FaceEmbedding, AttendanceLog
from typing import List, Optional, Tuple
import numpy as np
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db
    
    # User operations - Minimal
    def create_user(self, name: str, student_code: str, department: str = None) -> User:
        """Create new user with minimal info"""
        user = User(
            name=name,
            student_code=student_code,
            department=department
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_student_code(self, student_code: str) -> Optional[User]:
        """Get user by student code"""
        return self.db.query(User).filter(User.student_code == student_code).first()
    
    def get_all_users(self, active_only: bool = True) -> List[User]:
        """Get all users"""
        query = self.db.query(User)
        if active_only:
            query = query.filter(User.is_active == True)
        return query.order_by(User.name).all()
    
    # Face embedding operations - Optimized
    def save_face_embedding(self, user_id: int, embedding: np.ndarray, 
                          confidence: float = 0.0) -> FaceEmbedding:
        """Save face embedding for user"""
        face_embedding = FaceEmbedding(
            user_id=user_id,
            embedding=embedding.tolist(),
            confidence=confidence
        )
        self.db.add(face_embedding)
        self.db.commit()
        self.db.refresh(face_embedding)
        return face_embedding
    
    def find_similar_faces(self, query_embedding: np.ndarray, 
                          threshold: float = 0.3, limit: int = 3) -> List[Tuple[User, FaceEmbedding, float]]:
        """Find similar faces using vector similarity search - Optimized"""
        # Convert embedding to string format for PostgreSQL
        embedding_str = '[' + ','.join(map(str, query_embedding.tolist())) + ']'
        
        results = self.db.execute(text(f"""
            SELECT u.*, fe.*, 
                   (fe.embedding <=> '{embedding_str}'::vector) as distance,
                   1 - (fe.embedding <=> '{embedding_str}'::vector) as similarity
            FROM users u
            JOIN face_embeddings fe ON u.id = fe.user_id
            WHERE u.is_active = true
            AND 1 - (fe.embedding <=> '{embedding_str}'::vector) >= {threshold}
            ORDER BY fe.embedding <=> '{embedding_str}'::vector
            LIMIT {limit}
        """))
        
        similar_faces = []
        rows = results.fetchall()
        
        for row in rows:
            # Access by index (order: u.*, fe.*, distance, similarity)
            # u.*: id, name, student_code, department, is_active, created_at
            # fe.*: id, user_id, embedding, confidence, created_at
            user = User(
                id=row[0],  # u.id
                name=row[1],  # u.name
                student_code=row[2],  # u.student_code
                department=row[3],  # u.department
                is_active=row[4],  # u.is_active
                created_at=row[5]  # u.created_at
            )
            
            embedding = FaceEmbedding(
                id=row[6],  # fe.id
                user_id=row[7],  # fe.user_id
                embedding=row[8],  # fe.embedding
                confidence=row[9],  # fe.confidence
                created_at=row[10]  # fe.created_at
            )
            
            similarity = float(row[12])  # similarity (index 12)
            similar_faces.append((user, embedding, similarity))
        
        return similar_faces
    
    # Attendance operations - Minimal
    def log_attendance(self, user_id: int, confidence: float = None, 
                      device_id: str = "web") -> AttendanceLog:
        """Log attendance for user"""
        attendance = AttendanceLog(
            user_id=user_id,
            confidence=confidence,
            device_id=device_id
        )
        self.db.add(attendance)
        self.db.commit()
        self.db.refresh(attendance)
        return attendance
    
    def get_attendance_logs(self, user_id: int = None, 
                           start_date: datetime = None, 
                           end_date: datetime = None,
                           limit: int = 100) -> List[AttendanceLog]:
        """Get attendance logs with filters"""
        query = self.db.query(AttendanceLog)
        
        if user_id:
            query = query.filter(AttendanceLog.user_id == user_id)
        
        if start_date:
            query = query.filter(AttendanceLog.timestamp >= start_date)
        
        if end_date:
            query = query.filter(AttendanceLog.timestamp <= end_date)
        
        return query.order_by(desc(AttendanceLog.timestamp)).limit(limit).all()
    
    def get_attendance_stats(self, days: int = 30) -> dict:
        """Get attendance statistics - Optimized"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Total attendance count
        total_attendance = self.db.query(AttendanceLog).filter(
            and_(
                AttendanceLog.timestamp >= start_date,
                AttendanceLog.timestamp <= end_date
            )
        ).count()
        
        # Unique users who attended
        unique_users = self.db.query(AttendanceLog.user_id).filter(
            and_(
                AttendanceLog.timestamp >= start_date,
                AttendanceLog.timestamp <= end_date
            )
        ).distinct().count()
        
        # Daily breakdown
        daily_stats = self.db.execute(text("""
            SELECT DATE(timestamp) as date, COUNT(*) as count
            FROM attendance_logs
            WHERE timestamp >= :start_date AND timestamp <= :end_date
            GROUP BY DATE(timestamp)
            ORDER BY date
        """), {"start_date": start_date, "end_date": end_date})
        
        daily_data = [{"date": str(row.date), "count": row.count} for row in daily_stats]
        
        return {
            "total_attendance": total_attendance,
            "unique_users": unique_users,
            "daily_breakdown": daily_data,
            "period_days": days
        }
