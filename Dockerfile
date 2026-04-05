FROM python:3.9-slim

# Set working directory to /app
WORKDIR /app

# Install system dependencies for OpenCV and MediaPipe
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend files
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend code
COPY backend/ .

# Set environment variables
ENV FLASK_APP=app.py
ENV PORT=7860

# Hugging Face Spaces expect app to run on port 7860
EXPOSE 7860

# Run with Gunicorn for production or python for development
CMD ["python", "app.py"]
