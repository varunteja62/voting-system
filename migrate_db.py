import psycopg2
from config import DB_CONFIG

def migrate():
    try:
        if isinstance(DB_CONFIG, str):
            conn = psycopg2.connect(DB_CONFIG)
        else:
            conn = psycopg2.connect(**DB_CONFIG)
        
        cur = conn.cursor()
        
        # Check if password_hash column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='voters' AND column_name='password_hash'
        """)
        
        if not cur.fetchone():
            print("Adding password_hash column to voters table...")
            cur.execute("ALTER TABLE voters ADD COLUMN password_hash VARCHAR(255)")
            # For existing users, we'll set a temporary placeholder if needed, 
            # but usually it's better to make it NOT NULL after seeding or handle it in logic.
            # Here we'll just add it.
            print("Migration successful.")
        else:
            print("password_hash column already exists.")
            
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    migrate()
