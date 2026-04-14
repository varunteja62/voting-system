import psycopg2
from config import DB_CONFIG

def migrate():
    try:
        if isinstance(DB_CONFIG, str):
            conn = psycopg2.connect(DB_CONFIG)
        else:
            conn = psycopg2.connect(**DB_CONFIG)
        
        cur = conn.cursor()
        
        # Check if slip_string column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='voters' AND column_name='slip_string'
        """)
        
        if not cur.fetchone():
            print("Adding slip_string column to voters table...")
            cur.execute("ALTER TABLE voters ADD COLUMN slip_string VARCHAR(10) UNIQUE")
            print("slip_string column added.")
        
        # Check if voter_image column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='voters' AND column_name='voter_image'
        """)
        
        if not cur.fetchone():
            print("Adding voter_image column to voters table...")
            cur.execute("ALTER TABLE voters ADD COLUMN voter_image TEXT")
            print("voter_image column added.")
            
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    migrate()
