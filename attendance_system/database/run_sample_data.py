#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để import sample data vào database
Chỉ thêm: Giáo viên, Môn học, Lớp học, Tiết học, Camera
KHÔNG thêm dữ liệu sinh viên
"""

import psycopg2
from psycopg2 import sql
import os

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'attendance_system',
    'user': 'postgres',
    'password': 'Nguyenquang@2561'
}

# File paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DATA_FILE = os.path.join(CURRENT_DIR, 'insert_sample_data.sql')

def run_sample_data():
    """Import sample data vào database"""
    print("="*80)
    print("  INSERT SAMPLE DATA")
    print("="*80)
    print()
    
    try:
        # Connect to database
        print("📡 Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Read sample data SQL file
        print("📖 Reading insert_sample_data.sql...")
        with open(SAMPLE_DATA_FILE, 'r', encoding='utf-8') as f:
            sample_sql = f.read()
        print(f"   File size: {len(sample_sql)} characters")
        print()
        
        # Execute sample data
        print("⏳ Inserting data...")
        print("   - Giáo viên (Teachers)")
        print("   - Môn học (Subjects)")
        print("   - Lớp học (Classes)")
        print("   - Tiết học (Sessions)")
        print("   - Camera devices")
        print()
        
        cur.execute(sample_sql)
        conn.commit()
        
        print("✅ Sample data inserted successfully!")
        print()
        
        # Verify data
        print("🔍 Verifying data...")
        print()
        
        # Count teachers
        cur.execute("SELECT COUNT(*) FROM teachers")
        teacher_count = cur.fetchone()[0]
        print(f"✅ Teachers: {teacher_count}")
        
        # List teachers
        cur.execute("""
            SELECT teacher_id, full_name, department 
            FROM teachers 
            ORDER BY teacher_id
        """)
        teachers = cur.fetchall()
        for i, (tid, name, dept) in enumerate(teachers, 1):
            print(f"    {i}. {tid} - {name} ({dept})")
        print()
        
        # Count subjects
        cur.execute("SELECT COUNT(*) FROM subjects")
        subject_count = cur.fetchone()[0]
        print(f"✅ Subjects: {subject_count}")
        
        # List subjects
        cur.execute("""
            SELECT subject_id, subject_name, credits 
            FROM subjects 
            ORDER BY subject_id
        """)
        subjects = cur.fetchall()
        for i, (sid, name, credits) in enumerate(subjects, 1):
            print(f"    {i}. {sid} - {name} ({credits} tín chỉ)")
        print()
        
        # Count classes
        cur.execute("SELECT COUNT(*) FROM classes")
        class_count = cur.fetchone()[0]
        print(f"✅ Classes: {class_count}")
        
        # List classes
        cur.execute("""
            SELECT class_id, class_name, semester, academic_year, is_active 
            FROM classes 
            ORDER BY class_id
        """)
        classes = cur.fetchall()
        for i, (cid, name, sem, year, is_active) in enumerate(classes, 1):
            status_text = "Active" if is_active else "Inactive"
            print(f"    {i}. {cid} - {name}")
            print(f"       HK{sem} {year} - {status_text}")
        print()
        
        # Count sessions
        cur.execute("SELECT COUNT(*) FROM sessions")
        session_count = cur.fetchone()[0]
        print(f"✅ Sessions: {session_count}")
        
        # Sessions by class
        cur.execute("""
            SELECT c.class_name, COUNT(s.session_id) as total
            FROM classes c
            LEFT JOIN sessions s ON c.class_id = s.class_id
            GROUP BY c.class_name
            ORDER BY c.class_name
        """)
        session_stats = cur.fetchall()
        for name, total in session_stats:
            print(f"    - {name}: {total} buổi học")
        print()
        
        # Count cameras
        cur.execute("SELECT COUNT(*) FROM camera_devices")
        camera_count = cur.fetchone()[0]
        print(f"✅ Camera Devices: {camera_count}")
        
        # List cameras
        cur.execute("""
            SELECT device_name, location, is_active 
            FROM camera_devices 
            ORDER BY device_id
        """)
        cameras = cur.fetchall()
        for i, (name, loc, active) in enumerate(cameras, 1):
            marker = "🟢" if active else "🔴"
            print(f"    {i}. {marker} {name} - {loc}")
        print()
        
        # Students (should be 0)
        cur.execute("SELECT COUNT(*) FROM students")
        student_count = cur.fetchone()[0]
        print(f"✅ Students: {student_count} (Chưa thêm - đúng như yêu cầu)")
        print()
        
        cur.close()
        conn.close()
        
        print("="*80)
        print("🎉 SAMPLE DATA IMPORT SUCCESSFUL!")
        print("="*80)
        print()
        print("📊 Summary:")
        print(f"   - {teacher_count} giáo viên")
        print(f"   - {subject_count} môn học")
        print(f"   - {class_count} lớp học")
        print(f"   - {session_count} tiết học")
        print(f"   - {camera_count} thiết bị camera")
        print(f"   - {student_count} sinh viên (sẽ thêm sau khi train Face Recognition)")
        print()
        print("📚 Bước tiếp theo:")
        print("   1. Chụp ảnh sinh viên và train Face Recognition")
        print("   2. Thêm sinh viên vào database với face_encodings")
        print("   3. Tích hợp Face Recognition V2 với database")
        print("   4. Xây dựng Backend API")
        print("="*80)
        
    except FileNotFoundError:
        print(f"❌ Error: File not found: {SAMPLE_DATA_FILE}")
        print("   Please make sure insert_sample_data.sql exists!")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    run_sample_data()
