# Secure Online Voting System

A secure biometric-based online voting system with face recognition, and liveness detection.

## Features

- **Voter Registration**: Capture face image and  during registration
- **Face Recognition**: Uses FaceNet embeddings for accurate face matching
- **Liveness Detection**: Eye-blink detection to prevent photo/video spoofing
- **Real-time Admin Dashboard**: Monitor votes in real-time with statistics

## Tech Stack

### Backend
- Flask (Python web framework)
- PostgreSQL (Database)
- FaceNet (Face recognition)
- dlib (Eye blink detection)
- MTCNN (Face detection)

### Frontend
- React (UI framework)
- React Router (Navigation)
- React Webcam (Camera access)
- Axios (HTTP client)

## Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL 12+
- Webcam access

## Installation

### 1. Database Setup

```bash
# Create PostgreSQL database
createdb voting_system

# Or use psql
psql -U postgres
CREATE DATABASE voting_system;

# Run the database setup script
psql -U postgres -d voting_system -f backend/database_setup.sql
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Note: dlib is optional. The system uses MediaPipe for liveness detection by default.
# If you want to use dlib instead, see backend/INSTALL_DLIB.md for installation instructions.
```

**Note**: dlib installation can be tricky. On Windows, you may need:
- Visual Studio Build Tools
- CMake
- Or use conda: `conda install -c conda-forge dlib`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 4. Configure Database

Edit `backend/app.py` and update the `DB_CONFIG` dictionary with your PostgreSQL credentials:

```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'voting_system',
    'user': 'your_username',
    'password': 'your_password'
}
```

## Running the Application

### Start Backend Server

```bash
cd backend
python app.py
```

The backend will run on `http://localhost:5000`

### Start Frontend Server

```bash
cd frontend
npm start
```

The frontend will run on `http://localhost:3000`

## Usage

### Registration Flow

1. Navigate to Registration page
2. Enter Voter ID and Name
3. Capture face image using webcam (ensure only one person in frame)
4. Submit registration

### Voting Flow

1. Navigate to Vote page
2. Enter Voter ID  
3. Click "Next: Face Verification"
4. Capture face image for verification
5. System verifies face 
6. Perform liveness detection (blink your eyes)
7. Select candidate and cast vote

### Admin Dashboard

1. Navigate to Admin Dashboard
2. View real-time vote statistics
3. See all votes with voter details
4. Auto-refreshes every 5 seconds

## API Endpoints

- `POST /api/register` - Register a new voter
- `POST /api/verify` - Verify voter identity
- `POST /api/liveness` - Check liveness (eye blink)
- `POST /api/vote` - Cast a vote
- `GET /api/admin/votes` - Get all votes
- `GET /api/admin/stats` - Get voting statistics

## Security Considerations

- Face embeddings are stored as binary data
- Face verification uses cosine distance threshold (0.6)
- Liveness detection prevents photo/video spoofing
- One vote per voter enforced

## Troubleshooting

### dlib Installation Issues

**dlib is now optional!** The system uses MediaPipe for liveness detection by default, which is easier to install.

If you still want to use dlib:
- Use conda: `conda install -c conda-forge dlib` (recommended for Windows)
- Or see `backend/INSTALL_DLIB.md` for detailed instructions
- The system will work fine without dlib using MediaPipe

### Face Detection Not Working

- Ensure good lighting
- Face should be clearly visible
- Only one person in frame
- Check webcam permissions

### Database Connection Errors

- Verify PostgreSQL is running
- Check database credentials in `app.py`
- Ensure database exists

## License

This project is for educational purposes.
