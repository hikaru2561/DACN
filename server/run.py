"""
Main script to run the Optimized Face Recognition Attendance System
"""
import asyncio
import uvicorn
import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import fastapi
        import streamlit
        import cv2
        import psycopg2
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_database():
    """Check database connection"""
    try:
        from models.database import get_db
        from sqlalchemy import text
        
        print("🔄 Testing database connection...")
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def run_api_server():
    """Run the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

def run_web_app():
    """Run the Streamlit web app"""
    print("🌐 Starting Streamlit web app...")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "web_app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])

def main():
    """Main function"""
    print("🎯 Face Recognition Attendance System - Optimized Version")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check database
    if not check_database():
        print("Please ensure PostgreSQL is running and configured correctly")
        return
    
    # Create necessary directories
    os.makedirs("uploads/faces", exist_ok=True)
    os.makedirs("uploads/attendance", exist_ok=True)
    
    print("\n🎉 System ready!")
    print("\n📋 Available commands:")
    print("1. python run_optimized.py api    - Run API server only")
    print("2. python run_optimized.py web    - Run test web interface only")
    print("3. python run_optimized.py both   - Run both (recommended)")
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "api":
            run_api_server()
        elif command == "web":
            run_web_app()
        elif command == "both":
            print("\n🚀 Starting both API server and test web interface...")
            print("API Server: http://localhost:8000")
            print("Test Web Interface: http://localhost:8501")
            print("API Docs: http://localhost:8000/docs")
            print("\n⚠️  Note: Please run API and Web separately:")
            print("1. Open new terminal and run: python run_optimized.py api")
            print("2. Open another terminal and run: python run_optimized.py web")
            print("\nOr use the web interface only for testing.")
        else:
            print("❌ Invalid command. Use: api, web, or both")
    else:
        print("\n💡 Usage: python run.py [api|web|both]")

if __name__ == "__main__":
    main()
