from fastapi import APIRouter
from app.api import users, access_logs, control

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(access_logs.router, prefix="/access-logs", tags=["access-logs"])
api_router.include_router(control.router, prefix="/control", tags=["control"])
