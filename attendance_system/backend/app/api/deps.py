"""
API Dependencies
Shared dependencies for API routes
"""
from typing import Generator
from sqlalchemy.orm import Session
from app.core.database import get_db


# Re-export for convenience
def get_database() -> Generator:
    """Get database session dependency"""
    return get_db()
