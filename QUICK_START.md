# Quick Start Guide

## Fixing the dlib Installation Error

The dlib installation error you encountered is now **resolved**! The system has been updated to work without dlib.

## What Changed

1. ✅ **dlib is now optional** - The system uses MediaPipe instead (much easier to install)
2. ✅ **Graceful fallback** - System works even if dlib fails to install
3. ✅ **Updated requirements.txt** - dlib is commented out, MediaPipe is included

## Installation Steps

### 1. Install Backend Dependencies (Without dlib)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- Flask and all web framework dependencies
- FaceNet for face recognition
- MediaPipe for liveness detection (replaces dlib)
- All other required packages

**Note**: If you see any errors about face_recognition or facenet-pytorch, those are normal warnings during installation. They should install successfully.

### 2. Verify Installation

```bash
python -c "import flask; import mediapipe; print('Installation successful!')"
```

### 3. Start the Backend

```bash
python app.py
```

You should see:
```
Database initialized successfully
Using MediaPipe for eye blink detection
 * Running on http://127.0.0.1:5000
```

### 4. Start the Frontend

In a new terminal:
```bash
cd frontend
npm install
npm start
```

## What Works Now

✅ **Face Recognition** - Uses FaceNet (no dlib needed)
✅ **Liveness Detection** - Uses MediaPipe (easier than dlib)
✅ **All API Endpoints** - Fully functional
✅ **Admin Dashboard** - Real-time vote monitoring

## If You Still Want dlib (Optional)

If you prefer dlib's eye-blink detection, see `backend/INSTALL_DLIB.md` for installation options. The system will automatically use dlib if it's available, otherwise it uses MediaPipe.

## Troubleshooting

### MediaPipe Installation Issues
If MediaPipe fails to install:
```bash
pip install --upgrade pip setuptools wheel
pip install mediapipe
```

### Face Recognition Issues
If face_recognition fails:
```bash
# On Windows, you might need:
pip install cmake
pip install dlib  # This might still fail, but face_recognition can work without it
pip install face-recognition
```

### Database Connection
Make sure PostgreSQL is running and update credentials in `backend/app.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'voting_system',
    'user': 'postgres',
    'password': 'varun8115'  # Your password
}
```

## Testing the System

1. **Registration**: Go to http://localhost:3000/register
2. **Voting**: Go to http://localhost:3000/vote
3. **Admin**: Go to http://localhost:3000/admin

The system should work completely without dlib!

