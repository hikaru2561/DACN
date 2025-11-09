"""
Run Schema - Import schema.sql vào database
"""
import psycopg2
from pathlib import Path

# ==========================================
# CONFIG
# ==========================================
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'attendance_system',
    'user': 'postgres',
    'password': 'Nguyenquang@2561'
}

SCHEMA_FILE = Path(__file__).parent / 'schema.sql'


def run_schema():
    """Execute schema.sql"""
    print("\n" + "=" * 80)
    print("  IMPORT SCHEMA.SQL")
    print("=" * 80)
    
    if not SCHEMA_FILE.exists():
        print(f"\n❌ File không tồn tại: {SCHEMA_FILE}")
        return False
    
    try:
        print(f"\n📡 Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False  # Use transaction
        cur = conn.cursor()
        
        # Read schema file
        print(f"\n📖 Reading schema.sql...")
        with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        print(f"   File size: {len(schema_sql)} characters")
        
        # Execute schema
        print(f"\n⏳ Executing schema...")
        print(f"   (This may take a few seconds...)")
        
        try:
            cur.execute(schema_sql)
            conn.commit()
            print(f"✅ Schema executed successfully!")
        except Exception as e:
            conn.rollback()
            print(f"❌ Error executing schema: {e}")
            return False
        
        # Verify tables created
        print(f"\n🔍 Verifying tables...")
        cur.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        tables = cur.fetchall()
        
        print(f"\n✅ Created {len(tables)} tables:")
        for idx, (table,) in enumerate(tables, 1):
            print(f"   {idx:2d}. {table}")
        
        # Check views
        cur.execute("""
            SELECT viewname 
            FROM pg_views 
            WHERE schemaname = 'public'
            ORDER BY viewname;
        """)
        views = cur.fetchall()
        
        print(f"\n✅ Created {len(views)} views:")
        for (view,) in views:
            print(f"   - {view}")
        
        # Check triggers
        cur.execute("""
            SELECT DISTINCT trigger_name 
            FROM information_schema.triggers 
            WHERE trigger_schema = 'public'
            ORDER BY trigger_name;
        """)
        triggers = cur.fetchall()
        
        print(f"\n✅ Created {len(triggers)} triggers:")
        for (trigger,) in triggers:
            print(f"   - {trigger}")
        
        # Check users
        cur.execute("SELECT COUNT(*) FROM users;")
        user_count = cur.fetchone()[0]
        print(f"\n✅ Sample users: {user_count}")
        
        if user_count > 0:
            cur.execute("SELECT username, role FROM users ORDER BY user_id;")
            users = cur.fetchall()
            for username, role in users:
                print(f"   - {username} ({role})")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("🎉 SCHEMA IMPORT SUCCESSFUL!")
        print("=" * 80)
        print("\n📚 Bước tiếp theo:")
        print("   1. Import sample data:")
        print("      python run_sample_data.py")
        print("\n   2. Test connection:")
        print("      python test_connection.py")
        print("=" * 80)
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Connection Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        run_schema()
    except KeyboardInterrupt:
        print("\n\n⚠️  Dừng bởi người dùng")
