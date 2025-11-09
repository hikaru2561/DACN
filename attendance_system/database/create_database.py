"""
Create Database - Tạo database attendance_system
Chạy script này TRƯỚC khi chạy schema.sql
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# ==========================================
# CONFIG
# ==========================================
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'Nguyenquang@2561'  # Password của bạn
}

DATABASE_NAME = 'attendance_system'


def create_database():
    """Tạo database attendance_system"""
    print("\n" + "=" * 80)
    print("  CREATE DATABASE")
    print("=" * 80)
    
    try:
        # Connect to default 'postgres' database
        print(f"\n📡 Connecting to PostgreSQL server...")
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='postgres'  # Connect to default DB first
        )
        
        # Set isolation level for CREATE DATABASE
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("""
            SELECT 1 FROM pg_database WHERE datname = %s;
        """, (DATABASE_NAME,))
        
        exists = cur.fetchone()
        
        if exists:
            print(f"\n⚠️  Database '{DATABASE_NAME}' đã tồn tại!")
            
            # Ask to drop
            drop = input(f"\nBạn có muốn XÓA và tạo lại database '{DATABASE_NAME}'? (yes/no): ").strip().lower()
            
            if drop == 'yes':
                print(f"\n🗑️  Dropping database '{DATABASE_NAME}'...")
                
                # Terminate all connections first
                cur.execute(f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = '{DATABASE_NAME}'
                    AND pid <> pg_backend_pid();
                """)
                
                # Drop database
                cur.execute(sql.SQL("DROP DATABASE {}").format(
                    sql.Identifier(DATABASE_NAME)
                ))
                print(f"✅ Dropped!")
                
                # Create new
                print(f"\n🔨 Creating database '{DATABASE_NAME}'...")
                cur.execute(sql.SQL("CREATE DATABASE {} ENCODING 'UTF8'").format(
                    sql.Identifier(DATABASE_NAME)
                ))
                print(f"✅ Created!")
            else:
                print("\n⏭️  Bỏ qua tạo database. Sử dụng database hiện có.")
        else:
            # Create database
            print(f"\n🔨 Creating database '{DATABASE_NAME}'...")
            cur.execute(sql.SQL("CREATE DATABASE {} ENCODING 'UTF8'").format(
                sql.Identifier(DATABASE_NAME)
            ))
            print(f"✅ Database '{DATABASE_NAME}' đã được tạo!")
        
        # List all databases
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;")
        databases = cur.fetchall()
        
        print("\n📋 Danh sách databases:")
        for idx, (db,) in enumerate(databases, 1):
            marker = "👉" if db == DATABASE_NAME else "  "
            print(f"   {marker} {idx}. {db}")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ SUCCESS!")
        print("=" * 80)
        print(f"\n📚 Bước tiếp theo:")
        print(f"   1. Chạy schema.sql để tạo tables:")
        print(f"      python run_schema.py")
        print(f"\n   2. Hoặc thủ công:")
        print(f"      psql -U postgres -d {DATABASE_NAME} -f schema.sql")
        print("=" * 80)
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Connection Error:")
        print(f"   {e}")
        print("\n💡 Solutions:")
        print("   1. Kiểm tra PostgreSQL đã chạy chưa:")
        print("      - Mở Services (Win+R → services.msc)")
        print("      - Tìm 'postgresql-x64-17'")
        print("      - Status phải là 'Running'")
        print("\n   2. Kiểm tra password trong DB_CONFIG")
        print("\n   3. Kiểm tra port 5432:")
        print("      netstat -an | findstr 5432")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        create_database()
    except KeyboardInterrupt:
        print("\n\n⚠️  Dừng bởi người dùng")
