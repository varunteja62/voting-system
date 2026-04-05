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

# HARDCODED FALLBACK FOR NEON
NEON_FALLBACK = "postgresql://neondb_owner:npg_tv7wdUNimg4h@ep-sweet-math-an4so7fu.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require"

if DATABASE_URL:
    # Use the full connection string if available (Render/Hugging Face/Production)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    DB_CONFIG = DATABASE_URL
    print(f"DATABASE_URL is set. Using production database.")
else:
    # Use Neon as primary fallback
    DB_CONFIG = NEON_FALLBACK
    print(f"DATABASE_URL not found in environment. Using hardcoded Neon fallback.")

class Config:
    """Application configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database Configuration moved to module level
    
    # CORS Configuration
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    
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

