"""
FastAPI main application - Optimized Version
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import cv2
import numpy as np
from PIL import Image
import io
import logging
from datetime import datetime, timedelta

from core.config import settings
from models.database import get_db, init_database
from models.schemas import User, FaceEmbedding, AttendanceLog
from services.face_recognition_improved import improved_face_service as face_service
from services.database_service import DatabaseService
from models.pydantic_models import (
    UserCreate, UserResponse, AttendanceResponse, 
    FaceDetectionResponse, RecognitionResponse,
    StatsResponse, HealthResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Face Recognition Attendance System - Optimized",
    description="Optimized face recognition system for attendance tracking",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="uploads"), name="static")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting Face Recognition Attendance System - Optimized")
    
    # Test database connection
    try:
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise Exception("Database connection failed")
    
    # Initialize database tables
    if not await init_database():
        logger.error("❌ Failed to initialize database")
        raise Exception("Database initialization failed")
    
    # Initialize face recognition service
    if not await face_service.initialize():
        logger.error("❌ Failed to initialize face recognition")
        raise Exception("Face recognition initialization failed")
    
    logger.info("✅ All services initialized successfully")

# Health check
@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )

# Face detection endpoint
@app.post("/api/v1/detect-faces", response_model=FaceDetectionResponse)
async def detect_faces(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Detect faces in uploaded image"""
    try:
        # Validate file
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process image
        contents = await file.read()
        
        # Create image from bytes
        image = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        image_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Detect faces
        faces = face_service.detect_faces(image_array)
        
        return FaceDetectionResponse(
            faces=faces,
            count=len(faces),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Face detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Face detection failed: {str(e)}")

# User registration - Minimal
@app.post("/api/v1/register", response_model=UserResponse)
async def register_user(
    name: str = Form(...),
    student_code: str = Form(...),
    department: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Register new user with face image - Minimal info"""
    try:
        db_service = DatabaseService(db)
        
        # Check if user already exists
        existing_user = db_service.get_user_by_student_code(student_code)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this student code already exists")
        
        # Process image - read file content
        contents = await file.read()
        
        # Create image from bytes
        image = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        image_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Detect faces
        faces = face_service.detect_faces(image_array)
        if not faces:
            raise HTTPException(status_code=400, detail="No face detected in image")
        
        # Get best face (highest confidence)
        best_face = max(faces, key=lambda x: x['confidence'])
        
        # Check if face already exists in database
        query_embedding = np.array(best_face['embedding'])
        similar_faces = db_service.find_similar_faces(
            query_embedding, 
            threshold=0.4,  # Higher threshold for registration check
            limit=1
        )
        
        if similar_faces:
            existing_user = similar_faces[0][0]  # Get user from first match
            raise HTTPException(
                status_code=400, 
                detail=f"Face already registered for user: {existing_user.name} (Student Code: {existing_user.student_code})"
            )
        
        # Create user
        user = db_service.create_user(
            name=name,
            student_code=student_code,
            department=department
        )
        
        # Save face embedding
        embedding = np.array(best_face['embedding'])
        face_embedding = db_service.save_face_embedding(
            user_id=user.id,
            embedding=embedding,
            confidence=best_face['confidence']
        )
        
        return UserResponse(
            id=user.id,
            name=user.name,
            student_code=user.student_code,
            department=user.department,
            is_active=user.is_active,
            created_at=user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

# Face recognition and check-in - Optimized
@app.post("/api/v1/checkin", response_model=RecognitionResponse)
async def checkin_user(
    file: UploadFile = File(...),
    device_id: Optional[str] = Form("web"),
    db: Session = Depends(get_db)
):
    """Recognize face and log attendance"""
    try:
        db_service = DatabaseService(db)
        
        # Process image - read file content
        contents = await file.read()
        
        # Create image from bytes
        image = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        image_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Extract face embedding
        query_embedding = face_service.extract_embedding(image_array)
        if query_embedding is None:
            raise HTTPException(status_code=400, detail="No face detected in image")
        
        # Find similar faces with lower threshold for better matching
        similar_faces = db_service.find_similar_faces(
            query_embedding, 
            threshold=0.2,  # Lower threshold for better matching
            limit=3
        )
        
        if not similar_faces:
            raise HTTPException(status_code=404, detail="No matching user found")
        
        # Get best match
        best_match = similar_faces[0]
        user, face_embedding, similarity = best_match
        
        # Log attendance
        attendance = db_service.log_attendance(
            user_id=user.id,
            confidence=similarity,
            device_id=device_id
        )
        
        return RecognitionResponse(
            success=True,
            user=UserResponse(
                id=user.id,
                name=user.name,
                student_code=user.student_code,
                department=user.department,
                is_active=user.is_active,
                created_at=user.created_at
            ),
            confidence=similarity,
            timestamp=attendance.timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Check-in error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Check-in failed: {str(e)}")

# Get all users
@app.get("/api/v1/users", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    """Get all active users"""
    db_service = DatabaseService(db)
    users = db_service.get_all_users(active_only=True)
    
    return [
        UserResponse(
            id=user.id,
            name=user.name,
            student_code=user.student_code,
            department=user.department,
            is_active=user.is_active,
            created_at=user.created_at
        )
        for user in users
    ]

# Get attendance logs
@app.get("/api/v1/attendance/logs", response_model=List[AttendanceResponse])
async def get_attendance(
    user_id: Optional[int] = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get attendance logs"""
    db_service = DatabaseService(db)
    
    start_date = datetime.utcnow() - timedelta(days=days)
    logs = db_service.get_attendance_logs(
        user_id=user_id,
        start_date=start_date
    )
    
    # Get user info for each log
    result = []
    for log in logs:
        user = db_service.get_user_by_id(log.user_id)
        result.append({
            "id": log.id,
            "user_id": log.user_id,
            "user": {
                "id": user.id if user else None,
                "name": user.name if user else "Unknown",
                "student_code": user.student_code if user else "Unknown"
            },
            "timestamp": log.timestamp,
            "confidence": log.confidence,
            "device_id": log.device_id
        })
    
    return result

# Get statistics
@app.get("/api/v1/attendance/stats", response_model=StatsResponse)
async def get_stats(days: int = 30, db: Session = Depends(get_db)):
    """Get system statistics"""
    db_service = DatabaseService(db)
    stats = db_service.get_attendance_stats(days=days)
    
    return StatsResponse(**stats)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
