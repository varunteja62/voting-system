import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG

def get_db_connection():
    """Create database connection"""
    try:
        if isinstance(DB_CONFIG, str):
            conn = psycopg2.connect(DB_CONFIG)
        else:
            conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        
        # Create voters table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS voters (
                voter_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                phone VARCHAR(20),
                password_hash VARCHAR(255),
                face_embedding BYTEA NOT NULL,
                slip_string VARCHAR(10) UNIQUE,
                voter_image TEXT,
                otp VARCHAR(6),
                otp_expiry TIMESTAMP,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create votes table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                id SERIAL PRIMARY KEY,
                voter_id VARCHAR(50) NOT NULL,
                candidate VARCHAR(255),
                vote_data JSONB,
                voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (voter_id) REFERENCES voters(voter_id)
            )
        """)

        # Create candidates table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                party VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Seed candidates if empty
        cur.execute("SELECT COUNT(*) FROM candidates")
        if cur.fetchone()[0] == 0:
            print("Seeding candidates table...")
            cur.execute("""
                INSERT INTO candidates (name, party) VALUES 
                ('Uday Gaddam', 'BRS'),
                ('Bhavani RP', 'BJP'),
                ('Narshima Doka', 'Communist'),
                ('Koushik Guptha', 'Congress')
            """)
        
        # Create session tables
        cur.execute("""
            CREATE TABLE IF NOT EXISTS admin_sessions (
                token VARCHAR(255) PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS vote_tokens (
                token VARCHAR(255) PRIMARY KEY,
                voter_id VARCHAR(50) NOT NULL,
                expires_at FLOAT NOT NULL
            )
        """)
        
        
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully")
