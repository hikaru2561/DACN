"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from core.config import settings
import redis.asyncio as redis
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

# Database engine
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis connection
redis_client = None

async def get_redis() -> redis.Redis:
    """Get Redis connection"""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_database():
    """Initialize database tables"""
    try:
        from models.schemas import Base
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully (Optimized Version)")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {str(e)}")
        return False

async def test_connections():
    """Test database and Redis connections"""
    try:
        # Test database
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("✅ Database connection successful")
        
        # Test Redis
        redis_conn = await get_redis()
        await redis_conn.ping()
        logger.info("✅ Redis connection successful")
        
        return True
    except Exception as e:
        logger.error(f"❌ Connection test failed: {str(e)}")
        return False
