"""
Database Configuration
Kết nối PostgreSQL với SQLAlchemy
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Nguyenquang@2561@localhost:5432/attendance_system"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Kiểm tra connection trước khi dùng
    pool_size=10,        # Connection pool
    max_overflow=20,     # Max connections
    echo=False           # Set True để log SQL queries
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class cho models
Base = declarative_base()


def get_db():
    """
    Dependency để lấy database session
    Dùng trong FastAPI endpoints
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Test connection
if __name__ == "__main__":
    print("=" * 80)
    print("Testing Database Connection")
    print("=" * 80)
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL")
            print(f"   Version: {version}")
            
            # Check tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"\n📋 Found {len(tables)} tables:")
            for i, table in enumerate(tables, 1):
                print(f"   {i}. {table}")
        
        print("\n✅ Database connection successful!")
        
    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")
