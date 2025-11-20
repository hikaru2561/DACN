from fastapi import APIRouter
from .students import router as students_router
from .teachers import router as teachers_router
from .subjects import router as subjects_router
from .classes import router as classes_router
from .sessions import router as sessions_router
from .attendance import router as attendance_router
from .cameras import router as cameras_router
from .reports import router as reports_router

api_router = APIRouter(prefix="/api")

api_router.include_router(students_router)
api_router.include_router(teachers_router)
api_router.include_router(subjects_router)
api_router.include_router(classes_router)
api_router.include_router(sessions_router)
api_router.include_router(attendance_router)
api_router.include_router(cameras_router)
api_router.include_router(reports_router)
