"""
Test PostgreSQL Database Connection
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

# ==========================================
# DATABASE CONFIG
# ==========================================
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'attendance_system',
    'user': 'postgres',
    'password': 'Nguyenquang@2561'  # ← THAY ĐỔI MẬT KHẨU
}


def test_connection():
    """Test basic connection"""
    print("\n" + "=" * 80)
    print("  TEST POSTGRESQL CONNECTION")
    print("=" * 80)
    
    try:
        print(f"\n📡 Connecting to: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. Check version
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"\n✅ PostgreSQL Version:")
        print(f"   {version[:80]}...")
        
        # 2. Count tables
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        table_count = cur.fetchone()[0]
        print(f"\n✅ Total Tables: {table_count}")
        
        # 3. List tables
        cur.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        tables = cur.fetchall()
        print("\n📋 Tables:")
        for idx, (table,) in enumerate(tables, 1):
            print(f"   {idx:2d}. {table}")
        
        # 4. Count users
        cur.execute("SELECT COUNT(*) FROM users;")
        user_count = cur.fetchone()[0]
        print(f"\n✅ Total Users: {user_count}")
        
        # 5. List users
        cur.execute("""
            SELECT username, email, role 
            FROM users 
            ORDER BY user_id;
        """)
        users = cur.fetchall()
        print("\n👥 Users:")
        for username, email, role in users:
            print(f"   - {username:15s} | {role:10s} | {email}")
        
        # 6. Check views
        cur.execute("""
            SELECT viewname 
            FROM pg_views 
            WHERE schemaname = 'public'
            ORDER BY viewname;
        """)
        views = cur.fetchall()
        print(f"\n✅ Total Views: {len(views)}")
        for (view,) in views:
            print(f"   - {view}")
        
        # 7. Check triggers
        cur.execute("""
            SELECT DISTINCT trigger_name 
            FROM information_schema.triggers 
            WHERE trigger_schema = 'public'
            ORDER BY trigger_name;
        """)
        triggers = cur.fetchall()
        print(f"\n✅ Total Triggers: {len(triggers)}")
        for (trigger,) in triggers:
            print(f"   - {trigger}")
        
        # Close
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("🎉 DATABASE CONNECTION SUCCESSFUL!")
        print("=" * 80)
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Connection Error:")
        print(f"   {e}")
        print("\n💡 Solutions:")
        print("   1. Check PostgreSQL is running")
        print("   2. Verify password in DB_CONFIG")
        print("   3. Check database 'attendance_system' exists")
        print("   4. Verify port 5432 is correct")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_sample_queries():
    """Test some sample queries"""
    print("\n" + "=" * 80)
    print("  TEST SAMPLE QUERIES")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query 1: Check students table structure
        print("\n1️⃣ Students table structure:")
        cur.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'students'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        print(f"   Columns: {len(columns)}")
        for col in columns[:5]:  # Show first 5
            print(f"   - {col['column_name']:20s} | {col['data_type']}")
        
        # Query 2: Check face_encodings table
        print("\n2️⃣ Face encodings table:")
        cur.execute("SELECT COUNT(*) as count FROM face_encodings;")
        result = cur.fetchone()
        print(f"   Total encodings: {result['count']}")
        
        # Query 3: Check attendance view
        print("\n3️⃣ Attendance statistics view:")
        cur.execute("SELECT * FROM v_attendance_statistics LIMIT 1;")
        result = cur.fetchone()
        if result:
            print(f"   Columns: {list(result.keys())}")
        else:
            print("   No data yet (expected)")
        
        cur.close()
        conn.close()
        
        print("\n✅ Queries executed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Query Error: {e}")
        return False


def main():
    """Main test function"""
    # Update password first
    if DB_CONFIG['password'] == 'your_password_here':
        print("\n⚠️  WARNING: Please update DB_CONFIG['password'] in this file!")
        password = input("\nEnter PostgreSQL password for user 'postgres': ").strip()
        if password:
            DB_CONFIG['password'] = password
        else:
            print("❌ Password required!")
            return
    
    # Test connection
    if test_connection():
        # Test queries
        test_sample_queries()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print("\n📚 Next steps:")
        print("   1. Insert sample data (students, teachers, subjects)")
        print("   2. Setup Backend API")
        print("   3. Integrate Face Recognition V2")
        print("=" * 80)


if __name__ == "__main__":
    main()
