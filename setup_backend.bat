@echo off
echo Setting up Backend...
echo.

cd backend

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Backend setup complete!
echo.
echo Next steps:
echo 1. Download shape_predictor_68_face_landmarks.dat from http://dlib.net/files/
echo 2. Place it in the backend directory
echo 3. Update DB_CONFIG in app.py with your PostgreSQL credentials
echo 4. Run: python app.py
echo.

pause

