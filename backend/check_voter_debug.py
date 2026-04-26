import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG

def check_voter(voter_id):
    try:
        if isinstance(DB_CONFIG, str):
            conn = psycopg2.connect(DB_CONFIG)
        else:
            conn = psycopg2.connect(**DB_CONFIG)
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT voter_id, name, length(voter_image) as img_len, slip_string FROM voters WHERE voter_id = %s", (voter_id,))
        voter = cur.fetchone()
        cur.close()
        conn.close()
        
        if voter:
            print(f"Voter ID: {voter['voter_id']}")
            print(f"Name: {voter['name']}")
            print(f"Image Length: {voter['img_len']}")
            print(f"Slip String: {voter['slip_string']}")
        else:
            print("Voter not found")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_voter("23C31A6755")
