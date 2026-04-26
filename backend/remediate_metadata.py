import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG
import random
import string

def remediate_missing_details():
    try:
        if isinstance(DB_CONFIG, str):
            conn = psycopg2.connect(DB_CONFIG)
        else:
            conn = psycopg2.connect(**DB_CONFIG)
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Find voters missing slip_string
        cur.execute("SELECT voter_id FROM voters WHERE slip_string IS NULL")
        voters_to_fix = cur.fetchall()
        
        print(f"Found {len(voters_to_fix)} voters requiring slip_string remediation.")
        
        for v in voters_to_fix:
            vid = v['voter_id']
            new_slip = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            cur.execute("UPDATE voters SET slip_string = %s WHERE voter_id = %s", (new_slip, vid))
            print(f"Fixed SIP string for {vid}")
            
        conn.commit()
        cur.close()
        conn.close()
        print("Remediation complete.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    remediate_missing_details()
