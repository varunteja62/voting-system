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

        # Check for email column
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='voters' AND column_name='email'")
        if not cur.fetchone():
            print("Adding email column...")
            cur.execute("ALTER TABLE voters ADD COLUMN email VARCHAR(255)")
            
        # Check for phone column
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='voters' AND column_name='phone'")
        if not cur.fetchone():
            print("Adding phone column...")
            cur.execute("ALTER TABLE voters ADD COLUMN phone VARCHAR(20)")
            
        # Check for otp column
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='voters' AND column_name='otp'")
        if not cur.fetchone():
            print("Adding otp column...")
            cur.execute("ALTER TABLE voters ADD COLUMN otp VARCHAR(6)")
            
        # Check for otp_expiry column
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='voters' AND column_name='otp_expiry'")
        if not cur.fetchone():
            print("Adding otp_expiry column...")
            cur.execute("ALTER TABLE voters ADD COLUMN otp_expiry TIMESTAMP")
            
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    migrate()
