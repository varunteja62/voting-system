import numpy as np
import base64
import cv2
from PIL import Image
import io
import face_recognition
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from scipy.spatial.distance import cosine
import os

# Try to import dlib (optional - can use alternative method)
try:
    import dlib
    DLIB_AVAILABLE = True
except ImportError:
    DLIB_AVAILABLE = False
    print("Warning: dlib not available. Using alternative liveness detection method.")

# Try to import mediapipe as alternative for liveness detection
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("Warning: mediapipe not available. Basic liveness detection will be used.")

# Initialize FaceNet model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
mtcnn = MTCNN(image_size=160, margin=0, min_face_size=20, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

# Initialize liveness detection (dlib or mediapipe)
detector = None
predictor = None
mp_face_mesh = None

if DLIB_AVAILABLE:
    predictor_path = 'shape_predictor_68_face_landmarks.dat'
    # Check if the file exists, but since we deleted it in cleanup, this will likely fail or skip.
    if os.path.exists(predictor_path):
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(predictor_path)
        print("Using dlib for eye blink detection")
    else:
        # print("Warning: shape_predictor_68_face_landmarks.dat not found. Trying alternative method.")
        detector = None
        predictor = None

if (detector is None or predictor is None) and MEDIAPIPE_AVAILABLE:
    mp_face_mesh = mp.solutions.face_mesh
    print("Using MediaPipe for eye blink and head pose detection (Initialized on demand)")

if detector is None and not MEDIAPIPE_AVAILABLE:
    print("Warning: No liveness detection method available. Basic verification will be used.")

def image_to_embedding(image_data, check_multiple_faces=True):
    """Convert image to FaceNet embedding"""
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert PIL to numpy array
        img_array = np.array(image)
        
        # Check for multiple faces if requested (for registration)
        if check_multiple_faces:
            # Use face_recognition to detect all faces
            try:
                face_locations = face_recognition.face_locations(img_array)
                if len(face_locations) > 1:
                    return None, "Multiple faces detected. Please ensure only one person is in the frame."
                elif len(face_locations) == 0:
                    return None, "No face detected. Please ensure your face is clearly visible."
            except Exception as e:
                print(f"Face detection check error: {e}")
                # Continue with MTCNN if face_recognition fails
        
        # Detect and align face using MTCNN
        face = mtcnn(img_array)
        
        if face is None:
            return None, "Face detection failed. Please try again with better lighting."
        
        # Get embedding
        face_tensor = face.unsqueeze(0).to(device)
        with torch.no_grad():
            embedding = resnet(face_tensor)
        
        # Convert to numpy and normalize
        embedding = embedding.cpu().numpy().flatten()
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding.tobytes(), None
    except Exception as e:
        print(f"Error converting image to embedding: {e}")
        return None, str(e)

def compare_embeddings(embedding1_bytes, embedding2_bytes, threshold=0.6):
    """Compare two FaceNet embeddings"""
    try:
        embedding1 = np.frombuffer(embedding1_bytes, dtype=np.float32)
        embedding2 = np.frombuffer(embedding2_bytes, dtype=np.float32)
        
        # Calculate cosine distance
        distance = cosine(embedding1, embedding2)
        
        # Return True if distance is below threshold
        return distance < threshold
    except Exception as e:
        print(f"Error comparing embeddings: {e}")
        return False

def detect_eye_blink(image_data):
    """Detect eye blink using dlib, mediapipe, or basic face detection"""
    
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return False
        
        # Method 1: Use dlib if available (likely skipped now)
        if detector is not None and predictor is not None:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)
            
            if len(faces) == 0:
                return False
            
            # Get facial landmarks
            landmarks = predictor(gray, faces[0])
            landmarks = np.array([[p.x, p.y] for p in landmarks.parts()])
            
            # Calculate eye aspect ratio (EAR)
            # Left eye: points 36-41
            # Right eye: points 42-47
            left_eye = landmarks[36:42]
            right_eye = landmarks[42:48]
            
            def eye_aspect_ratio(eye):
                A = np.linalg.norm(eye[1] - eye[5])
                B = np.linalg.norm(eye[2] - eye[4])
                C = np.linalg.norm(eye[0] - eye[3])
                ear = (A + B) / (2.0 * C)
                return ear
            
            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)
            ear = (left_ear + right_ear) / 2.0
            
            # EAR threshold for blink detection
            return ear < 0.25
        
        # Method 2: Use MediaPipe if available
        elif MEDIAPIPE_AVAILABLE:
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            with mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            ) as face_mesh_local:
                results = face_mesh_local.process(rgb_img)
                
                if not results.multi_face_landmarks:
                    return False
                
                face_landmarks = results.multi_face_landmarks[0]
                
                # MediaPipe eye landmark indices
                # Left eye: [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
                # Right eye: [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
                # Simplified: use key points for EAR calculation
                left_eye_top = face_landmarks.landmark[159].y
                left_eye_bottom = face_landmarks.landmark[145].y
                left_eye_left = face_landmarks.landmark[33].x
                left_eye_right = face_landmarks.landmark[133].x
                
                right_eye_top = face_landmarks.landmark[386].y
                right_eye_bottom = face_landmarks.landmark[374].y
                right_eye_left = face_landmarks.landmark[362].x
                right_eye_right = face_landmarks.landmark[263].x
                
                # Calculate vertical and horizontal distances
                left_eye_vertical = abs(left_eye_top - left_eye_bottom)
                left_eye_horizontal = abs(left_eye_left - left_eye_right)
                right_eye_vertical = abs(right_eye_top - right_eye_bottom)
                right_eye_horizontal = abs(right_eye_left - right_eye_right)
                
                # Calculate EAR
                if left_eye_horizontal > 0 and right_eye_horizontal > 0:
                    left_ear = left_eye_vertical / left_eye_horizontal
                    right_ear = right_eye_vertical / right_eye_horizontal
                    ear = (left_ear + right_ear) / 2.0
                    return ear < 0.25
        
        # Method 3: Basic face detection fallback
        # If face is detected, assume liveness (less secure but functional)
        else:
            # Use face_recognition as fallback
            try:
                face_locations = face_recognition.face_locations(img)
                if len(face_locations) > 0:
                    return True
            except:
                pass
            
            return False
        
    except Exception as e:
        print(f"Error detecting eye blink: {e}")
        return False

def detect_head_pose(image_data):
    """Detect head pose (Left, Right, Center) using MediaPipe"""
    try:
        image_bytes = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return None
            
        if not MEDIAPIPE_AVAILABLE:
            return "Unknown"
            
        img_h, img_w, _ = img.shape
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Initialize FaceMesh locally for thread safety
        with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as face_mesh_local:
            results = face_mesh_local.process(rgb_img)
            
            if not results.multi_face_landmarks:
                return "No Face"
                
            face_landmarks = results.multi_face_landmarks[0]
            
            face_3d = []
            face_2d = []
            
            # Landmarks: Left Eye, Right Eye, Nose, Left Mouth, Right Mouth, Chin
            landmarks_indices = [33, 263, 1, 61, 291, 152]
            
            for idx in landmarks_indices:
                lm = face_landmarks.landmark[idx]
                x, y = int(lm.x * img_w), int(lm.y * img_h)
                face_2d.append([x, y])
                face_3d.append([x, y, lm.z])
                
            face_2d = np.array(face_2d, dtype=np.float64)
            face_3d = np.array(face_3d, dtype=np.float64)
            
            # Camera matrix
            focal_length = 1 * img_w
            cam_matrix = np.array([
                [focal_length, 0, img_h / 2],
                [0, focal_length, img_w / 2],
                [0, 0, 1]
            ])
            
            # Distance matrix
            dist_matrix = np.zeros((4, 1), dtype=np.float64)
            
            # Solve PnP
            success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
            
            # Get rotational matrix
            rmat, jac = cv2.Rodrigues(rot_vec)
            
            # Get angles
            angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
            
            # angles[0] = pitch, angles[1] = yaw, angles[2] = roll
            x = angles[0] * 360
            y = angles[1] * 360
            
            print(f"DEBUG: Head Pose Angles - Pitch(x): {x:.2f}, Yaw(y): {y:.2f}")

            # Determine orientation
            if y < -10:
                return "Left"
            elif y > 10:
                return "Right"
            else:
                return "Center"
            
    except Exception as e:
        print(f"Error checking head pose: {e}")
        return "Error"
