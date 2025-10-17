"""
Reset database with optimized schema
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from core.config import settings

def reset_database():
    """Reset database with optimized schema"""
    try:
        # Use direct connection details
        username = "postgres"
        password = "Nguyenquang@2561"
        host = "localhost"
        port = "5432"
        database = "face_attendance"
        
        print(f"🔄 Connecting to database: {host}:{port}/{database}")
        
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Drop existing database
        print("🗑️ Dropping existing database...")
        cursor.execute(f"DROP DATABASE IF EXISTS {database}")
        
        # Create new database
        print("🆕 Creating new database...")
        cursor.execute(f"CREATE DATABASE {database}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        # Connect to new database
        print("🔗 Connecting to new database...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Read and execute schema
        print("📋 Executing optimized schema...")
        with open('database/schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        cursor.execute(schema_sql)
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("✅ Database reset successfully with optimized schema!")
        print("📊 Tables created:")
        print("   - users (id, name, student_code, department, is_active, created_at)")
        print("   - face_embeddings (id, user_id, embedding, confidence, created_at)")
        print("   - attendance_logs (id, user_id, timestamp, confidence, device_id)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting database: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎯 Face Recognition Attendance System - Database Reset (Optimized)")
    print("=" * 70)
    
    if reset_database():
        print("\n🎉 Database reset completed successfully!")
        print("You can now run the application with: python run_optimized.py")
    else:
        print("\n❌ Database reset failed!")
        print("Please check your database configuration and try again.")
