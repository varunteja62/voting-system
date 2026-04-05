"""
Configuration file for the Voting System
Loads configuration from environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Use the full connection string if available (Render/Hugging Face/Production)
    # Ensure it starts with postgresql:// (psycopg2 preference)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    DB_CONFIG = DATABASE_URL
    print(f"DATABASE_URL is set. Using production database.")
else:
    # Use individual components as fallback (Local)
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'voting_system'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'varun8115'),
        'port': os.getenv('DB_PORT', '5432')
    }
    print(f"WARNING: DATABASE_URL not found. Falling back to {DB_CONFIG['host']}")

class Config:
    """Application configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'sfDjKX7Ttm7V1g82LskoFRt2BtLb0Cfl_voter_sec')
    
    # Database Configuration moved to module level
    
    # CORS Configuration
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'https://voting-system-proto.vercel.app,*').split(',')
    
    # Admin Configuration
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'varun')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'varun8115')
    
    # Security Settings
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_TIME = 300  # 5 minutes in seconds
    RATE_LIMIT_PER_MINUTE = 60
    
    # Face Recognition Settings
    FACE_MATCH_THRESHOLD = 0.36
    
    # Logging
    LOG_FILE = 'voting_system.log'

