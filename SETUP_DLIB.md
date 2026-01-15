# Setting up dlib Shape Predictor

The eye-blink liveness detection requires the dlib 68-point facial landmark predictor.

## Download Instructions

1. Download the shape predictor file:
   - Direct link: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
   - Or visit: http://dlib.net/files/

2. Extract the file:
   - On Windows: Use 7-Zip or WinRAR to extract the `.bz2` file
   - On Linux/Mac: `bzip2 -d shape_predictor_68_face_landmarks.dat.bz2`

3. Place the extracted file:
   - Copy `shape_predictor_68_face_landmarks.dat` to the `backend/` directory
   - The file should be at: `backend/shape_predictor_68_face_landmarks.dat`

## Alternative: Using face_recognition library's landmarks

If you have issues with dlib, you can modify the code to use face_recognition library's landmarks detection instead, though it may be less accurate for eye-blink detection.

## Verification

After placing the file, restart the Flask server. The application will check for the file on startup and display a warning if it's not found.

