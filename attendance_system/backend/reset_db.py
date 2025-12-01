import sys
import os
from sqlalchemy import create_engine

# Add current directory to path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# HARDCODED URL TO BE 100% SURE
DB_URL = "postgresql://postgres:Nguyenquang%402561@localhost:5432/access_control_db"

print(f"🔥 FORCING DATABASE URL: {DB_URL}")

from app.core.database import Base
# Import models to register them with Base
from app.models.user import User
from app.models.access_log import AccessLog

def reset_db():
    print("🔄 Connecting to database...")
    engine = create_engine(DB_URL)
    
    print("🔄 Dropping all tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("✅ Tables dropped.")
        
        print("🔄 Creating new tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        
        # Verify
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"👀 Tables in DB: {tables}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    reset_db()
