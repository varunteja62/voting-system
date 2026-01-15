# Installing dlib (Optional)

dlib is optional for this voting system. The system will work without it using MediaPipe for liveness detection.

## Why dlib is optional

The system now uses MediaPipe as the primary liveness detection method, which is easier to install and works cross-platform. dlib is only needed if you prefer its eye-blink detection algorithm.

## Installation Options (if you want dlib)

### Option 1: Using Conda (Easiest for Windows)

```bash
conda install -c conda-forge dlib
```

### Option 2: Pre-built Wheel (Windows)

1. Download a pre-built wheel from: https://github.com/sachadee/Dlib/releases
2. Install using pip:
   ```bash
   pip install path/to/dlib-19.24.2-cpXX-cpXX-win_amd64.whl
   ```

### Option 3: Build from Source (Advanced)

Requires:
- Visual Studio Build Tools (C++ compiler)
- CMake
- Python development headers

```bash
pip install cmake
pip install dlib
```

## Current Setup

The system is configured to work without dlib:
- ✅ Uses MediaPipe for eye-blink detection (installed via requirements.txt)
- ✅ Falls back to basic face detection if neither dlib nor MediaPipe is available
- ✅ All core functionality works without dlib

## Shape Predictor File

If you install dlib and want to use it, download:
- File: `shape_predictor_68_face_landmarks.dat`
- From: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
- Extract and place in `backend/` directory

The system will automatically detect and use dlib if available, otherwise it will use MediaPipe.

