import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    database_url = os.getenv('DATABASE_URL')
    print(f"Testing connection to: {database_url.split('@')[-1] if database_url else 'None'}")
    
    try:
        if database_url:
            conn = psycopg2.connect(database_url)
        else:
            print("Error: DATABASE_URL not found in .env")
            return
            
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"Successfully connected to PostgreSQL! Version: {version[0]}")
        
        cur.execute("SELECT COUNT(*) FROM candidates;")
        count = cur.fetchone()[0]
        print(f"Found {count} candidates in the database.")
        
        cur.close()
        conn.close()
        print("Connection verification successful.")
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
