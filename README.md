---
title: Voting System Backend
emoji: 🗳️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Secure Online Voting System

A secure biometric-based online voting system with face recognition and liveness detection.

## Features

- **Voter Registration**: Capture face image and during registration
- **Face Recognition**: Uses FaceNet embeddings for accurate face matching
- **Liveness Detection**: Eye-blink detection to prevent photo/video spoofing
- **Real-time Admin Dashboard**: Monitor votes in real-time with statistics

## Tech Stack

### Backend
- Flask (Python web framework)
- PostgreSQL (Database)
- FaceNet (Face recognition)
- MediaPipe (Eye blink and head pose detection)
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
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm start
```