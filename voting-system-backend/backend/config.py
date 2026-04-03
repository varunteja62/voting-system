"""
Configuration file for the Voting System
Loads configuration from environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'dpg-d6rh9275r7bs7390j3s0-a.oregon-postgres.render.com'),
    'database': os.getenv('DB_NAME', 'voting_db_s0zo'),
    'user': os.getenv('DB_USER', 'voting_db_s0zo_user'),
    'password': os.getenv('DB_PASSWORD', 'sfDjKX7Ttm7V1g82LskoFRt2BtLb0Cfl'),
    'port': os.getenv('DB_PORT', '5432')
}

class Config:
    """Application configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'sfDjKX7Ttm7V1g82LskoFRt2BtLb0Cfl_voter_sec')
    
    # Database Configuration moved to module level
    
    # CORS Configuration
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
    
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

