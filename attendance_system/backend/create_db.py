import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Config
DB_USER = "postgres"
DB_PASS = "Nguyenquang@2561"
DB_HOST = "localhost"
DB_NAMES = ["access_control_db", "attendance_system"]

def create_database():
    try:
        # Connect to default 'postgres' database
        print("🔄 Connecting to 'postgres' database...")
        con = psycopg2.connect(dbname='postgres', user=DB_USER, host=DB_HOST, password=DB_PASS)
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        
        for db_name in DB_NAMES:
            # Check if DB exists
            cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
            exists = cur.fetchone()
            
            if not exists:
                print(f"✨ Creating database '{db_name}'...")
                cur.execute(f"CREATE DATABASE {db_name}")
                print(f"✅ Database '{db_name}' created successfully!")
            else:
                print(f"⚠️ Database '{db_name}' already exists.")
            
        cur.close()
        con.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_database()
