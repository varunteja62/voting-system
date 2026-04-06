import numpy as np
import base64
import cv2
from PIL import Image
import io
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from scipy.spatial.distance import cosine
import os
import torchvision.models as models
from torchvision.models import MobileNet_V2_Weights
import torchvision.transforms as transforms
from scipy.fftpack import fft2
from numpy.fft import fftshift

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

# Initialize FaceNet model with higher sensitivity and margin
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
mtcnn = MTCNN(
    image_size=160, 
    margin=14, 
    min_face_size=20, 
    thresholds=[0.6, 0.7, 0.7], # Standard thresholds
    post_process=True,
    device=device
)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

# Initialize MobileNetV2 for anti-spoofing
# We use the pre-trained weights to extract high-level features
spoof_model = models.mobilenet_v2(weights=MobileNet_V2_Weights.DEFAULT).eval().to(device)

# Transform for CNN spoof detection
spoof_transform = transforms.Compose([
    transforms.Resize(224),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

import traceback

# Initialize liveness detection (dlib or mediapipe)
detector = None
predictor = None
mp_face_mesh = None

if DLIB_AVAILABLE:
    predictor_path = 'shape_predictor_68_face_landmarks.dat'
    if os.path.exists(predictor_path):
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(predictor_path)
        print("Using dlib for eye blink detection")

if MEDIAPIPE_AVAILABLE:
    mp_face_mesh = mp.solutions.face_mesh
    print("MediaPipe initialized for head pose and liveness fallback")

if not detector and not MEDIAPIPE_AVAILABLE:
    print("Warning: No liveness detection method available. Basic verification will be used.")

def align_face(img, landmarks):
    """Align face based on eye landmarks"""
    try:
        # Landmarks: [Left Eye, Right Eye, Nose, Left Mouth, Right Mouth]
        left_eye = landmarks[0]
        right_eye = landmarks[1]
        
        # Calculate angle between eyes
        dY = right_eye[1] - left_eye[1]
        dX = right_eye[0] - left_eye[0]
        angle = np.degrees(np.arctan2(dY, dX))
        
        # Desired center of eyes
        eyes_center = ((left_eye[0] + right_eye[0]) // 2, (left_eye[1] + right_eye[1]) // 2)
        
        # Get rotation matrix
        M = cv2.getRotationMatrix2D(eyes_center, angle, 1.0)
        
        # Align image
        (h, w) = img.shape[:2]
        aligned_img = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC)
        
        return aligned_img
    except Exception as e:
        print(f"Alignment error: {e}")
        return img

def image_to_embedding(image_data, check_multiple_faces=True):
    """Convert image to FaceNet embedding"""
    try:
        parts = image_data.split(',')
        b64_string = parts[1] if len(parts) > 1 else parts[0]
        
        # Add padding if necessary
        missing_padding = len(b64_string) % 4
        if missing_padding:
            b64_string += '=' * (4 - missing_padding)
            
        image_bytes = base64.b64decode(b64_string)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert pilgrimage image to numpy array
        img_array = np.array(image)
        
        # --- [NEW] Detection Hardening: CLAHE Preprocessing ---
        # Improve contrast to help detection in dark or backlit scenes
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        processed_img = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
        
        # --- [NEW] Quality Check: Blur Detection ---
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < 15:
            print(f"DEBUG: Image rejected due to low quality/blur ({laplacian_var:.2f})")
            return None, "Image is too blurry. Please ensure good lighting and hold steady."

        detect_img = processed_img 
        
        # Detect faces and landmarks first for alignment
        boxes, probs, points = mtcnn.detect(detect_img, landmarks=True)
        
        # Check for multiple faces if requested (for registration)
        if check_multiple_faces:
            if boxes is not None and len(boxes) > 1:
                return None, "Multiple people in the frame. Only one person should be in the frame."
        
        if boxes is not None and len(boxes) > 0:
            # Align the face using landmarks
            aligned_img = align_face(detect_img, points[0])
            # Re-detect on aligned image for final crop (or just crop manually)
            face = mtcnn(aligned_img)
        else:
            face = None

        # If MTCNN fails or alignment results in no face, try one more time with high sensitivity
        if face is None:
            print("DEBUG: MTCNN/Alignment failed, retry with high sensitivity...")
            mtcnn_sensitive = MTCNN(image_size=160, margin=14, thresholds=[0.5, 0.6, 0.6], device=device)
            face = mtcnn_sensitive(detect_img)
        
        if face is None:
            return None, "Face detection failed. Please try again with better lighting."
        
        # Check resolution/size of detected face (rough estimate from MTCNN output)
        # face is a tensor [3, 160, 160] but we checked the source face detection
        # boxes, probs, points = mtcnn.detect(detect_img, landmarks=True)
        # if boxes is not None:
        #     box = boxes[0]
        #     width = box[2] - box[0]
        #     height = box[3] - box[1]
        #     if width < 80 or height < 80:
        #         return None, "Face is too far from the camera. Please move closer."
        
        # Get embedding
        face_tensor = face.unsqueeze(0).to(device)
        with torch.no_grad():
            embedding = resnet(face_tensor)
        
        # Convert to numpy and normalize
        embedding = embedding.cpu().numpy().flatten().astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding.tobytes(), None
    except Exception as e:
        print(f"Error converting image to embedding: {e}")
        return None, str(e)

def calculate_confidence(distance, threshold=0.40):
    """
    Convert distance to a confidence percentage.
    0.0 distance = 100% confidence
    threshold distance = 50% confidence
    > 2*threshold = 0% confidence
    """
    if distance <= 0:
        return 100.0
    
    if distance < threshold:
        # 100% down to 50%
        confidence = 100 - (distance / threshold) * 50
    else:
        # 50% down to 0%
        confidence = max(0, 50 - ((distance - threshold) / threshold) * 50)
        
    return round(confidence, 2)

def compare_embeddings(embedding1_bytes, embedding2_bytes, threshold=0.40):
    """Compare two FaceNet embeddings and return match status, distance, and confidence"""
    try:
        embedding1 = np.frombuffer(embedding1_bytes, dtype=np.float32)
        embedding2 = np.frombuffer(embedding2_bytes, dtype=np.float32)
        
        # Calculate cosine distance
        distance = cosine(embedding1, embedding2)
        
        # Calculate confidence
        confidence = calculate_confidence(distance, threshold)
        
        # Return True if distance is below threshold
        is_match = distance < threshold
        print(f"DEBUG: Comparing embeddings - Distance: {distance:.4f}, Threshold: {threshold}, Match: {is_match}, Confidence: {confidence}%")
        
        return is_match, distance, confidence
    except Exception as e:
        print(f"Error comparing embeddings: {e}")
        return False, 1.0, 0.0

def compare_embeddings_multi(reference_embeddings_list, probe_embedding_bytes, threshold=0.40):
    """
    Compare a probe embedding against multiple reference samples (Best-of-N / KNN-lite).
    Returns (is_match, best_distance, confidence_score, best_index)
    """
    try:
        probe = np.frombuffer(probe_embedding_bytes, dtype=np.float32)
        distances = []
        
        for ref_bytes in reference_embeddings_list:
            if not ref_bytes: continue
            ref = np.frombuffer(ref_bytes, dtype=np.float32)
            distances.append(cosine(ref, probe))
            
        if not distances:
            return False, 1.0, 0.0, -1
            
        best_distance = min(distances)
        best_index = distances.index(best_distance)
        
        is_match = best_distance < threshold
        confidence = calculate_confidence(best_distance, threshold)
        
        print(f"DEBUG: Multi-sample comparison - Best Distance: {best_distance:.4f}, Samples: {len(distances)}, Match: {is_match}, Confidence: {confidence}%")
        
        return is_match, best_distance, confidence, best_index
    except Exception as e:
        print(f"Error in multi-sample comparison: {e}")
        return False, 1.0, 0.0, -1

def get_eye_state(image_data):
    """
    Analyze eye state (Open/Closed) using EAR.
    Returns: (state, ear_value, message)
    state: 'OPEN', 'CLOSED', 'UNKNOWN'
    """
    try:
        # Decode base64 image
        parts = image_data.split(',')
        b64_string = parts[1] if len(parts) > 1 else parts[0]
        missing_padding = len(b64_string) % 4
        if missing_padding:
            b64_string += '=' * (4 - missing_padding)
            
        image_bytes = base64.b64decode(b64_string)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return "UNKNOWN", 0.0, "Failed to decode image"
        
        ear = 0.0
        
        # Method 1: Use dlib if available
        if detector is not None and predictor is not None:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)
            
            if len(faces) == 0:
                return "UNKNOWN", 0.0, "No face detected"
            
            # Get facial landmarks
            landmarks = predictor(gray, faces[0])
            # ... (Logic identical to original but returning state)
            # Simplified for brevity in this specific replacement, relying on original logic flow
            # We need to reimplement the EAR calcs here as we are replacing the function
            
            landmarks_np = np.array([[p.x, p.y] for p in landmarks.parts()])
            left_eye = landmarks_np[36:42]
            right_eye = landmarks_np[42:48]
            
            def eye_aspect_ratio(eye):
                A = np.linalg.norm(eye[1] - eye[5])
                B = np.linalg.norm(eye[2] - eye[4])
                C = np.linalg.norm(eye[0] - eye[3])
                ear = (A + B) / (2.0 * C)
                return ear
            
            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)
            ear = (left_ear + right_ear) / 2.0
            
        # Method 2: Use MediaPipe if available
        elif MEDIAPIPE_AVAILABLE:
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            with mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5
            ) as face_mesh_local:
                results = face_mesh_local.process(rgb_img)
                
                if not results.multi_face_landmarks:
                    return "UNKNOWN", 0.0, "No face detected"
                
                face_landmarks = results.multi_face_landmarks[0]
                
                # MediaPipe eye landmark indices (Simplified using vertical/horizontal distance)
                left_eye_top = face_landmarks.landmark[159].y
                left_eye_bottom = face_landmarks.landmark[145].y
                left_eye_left = face_landmarks.landmark[33].x
                left_eye_right = face_landmarks.landmark[133].x
                
                right_eye_top = face_landmarks.landmark[386].y
                right_eye_bottom = face_landmarks.landmark[374].y
                right_eye_left = face_landmarks.landmark[362].x
                right_eye_right = face_landmarks.landmark[263].x
                
                left_eye_vertical = abs(left_eye_top - left_eye_bottom)
                left_eye_horizontal = abs(left_eye_left - left_eye_right)
                right_eye_vertical = abs(right_eye_top - right_eye_bottom)
                right_eye_horizontal = abs(right_eye_left - right_eye_right)
                
                if left_eye_horizontal > 0 and right_eye_horizontal > 0:
                    left_ear = left_eye_vertical / left_eye_horizontal
                    right_ear = right_eye_vertical / right_eye_horizontal
                    ear = (left_ear + right_ear) / 2.0
                else:
                    return "UNKNOWN", 0.0, "Could not calculate eye aspect ratio"
        
        else:
            return "UNKNOWN", 0.0, "No blink detection method available"

        # Define Thresholds
        # CLOSED if EAR < 0.20 (Strict blink)
        # OPEN if EAR > 0.30 (Clearly open)
        # INDETERMINATE in between
        
        if ear < 0.20:
            return "CLOSED", ear, "Eyes appear closed"
        elif ear > 0.28: # Slightly relaxed threshold for 'open' to avoid false negatives
            return "OPEN", ear, "Eyes appear open"
        else:
            return "INDETERMINATE", ear, "Eye state unclear (partially open/closed)"

    except Exception as e:
        print(f"Error checking eye state: {e}")
        return "ERROR", 0.0, str(e)

def detect_eye_blink(image_data):
    """
    Legacy wrapper for backward compatibility if needed.
    Returns True if blink detected (Eyes Closed).
    """
    state, _, _ = get_eye_state(image_data)
    return state == "CLOSED"

def detect_head_pose(image_data):
    """Detect head pose (Left, Right, Center) using MediaPipe"""
    try:
        parts = image_data.split(',')
        b64_string = parts[1] if len(parts) > 1 else parts[0]
        
        # Add padding if necessary
        missing_padding = len(b64_string) % 4
        if missing_padding:
            b64_string += '=' * (4 - missing_padding)

        image_bytes = base64.b64decode(b64_string)
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
            
            # --- [NEW] Landmark Ratio Method (Robust & Resolution Independent) ---
            # We use the horizontal position of the nose relative to the eyes
            # Landmark 1: Nose Tip
            # Landmark 33: Left Eye (Outer)
            # Landmark 263: Right Eye (Outer)
            
            nose = face_landmarks.landmark[1]
            left_eye = face_landmarks.landmark[33]
            right_eye = face_landmarks.landmark[263]
            
            # Calculate horizontal distances (normalized coordinates are fine)
            dist_left = abs(nose.x - left_eye.x)
            dist_right = abs(nose.x - right_eye.x)
            
            # Avoid division by zero
            if dist_right == 0: dist_right = 0.001
            ratio = dist_left / dist_right
            
            print(f"DEBUG: Head Pose Ratio: {ratio:.3f} (L:{dist_left:.3f}, R:{dist_right:.3f})")

            # Determine pose based on ratio
            # If nose is much closer to right eye, head is turned Left
            if ratio > 1.8:
                return "Left"
            # If nose is much closer to left eye, head is turned Right
            elif ratio < 0.55:
                return "Right"
            else:
                return "Center"
            
    except Exception as e:
        print(f"CRITICAL: Error checking head pose: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}"

def detect_spoofing(image_data):
    """
    Detect if the image is a spoof (photo/screen) using CNN features and texture analysis.
    Returns: (is_spoof, confidence, reason)
    """
    try:
        # 1. Decode Image
        parts = image_data.split(',')
        b64_string = parts[1] if len(parts) > 1 else parts[0]
        
        # Add padding if necessary
        missing_padding = len(b64_string) % 4
        if missing_padding:
            b64_string += '=' * (4 - missing_padding)
            
        image_bytes = base64.b64decode(b64_string)
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # 2. Texture Analysis (Improved Frequency Domain)
        # Screens often have periodic noise (Moiré patterns) showing as high-freq spikes
        f_transform = fft2(gray)
        f_shift = fftshift(f_transform)
        magnitude_spectrum = 20 * np.log(np.abs(f_shift) + 1)
        
        rows, cols = gray.shape
        crow, ccol = rows // 2, cols // 2
        
        # High-frequency mask
        mask = np.ones((rows, cols), np.uint8)
        r = 45 # Increased from 30 to better ignore mid-frequencies in standard webcams
        mask[crow-r:crow+r, ccol-r:ccol+r] = 0
        
        # Calculate energy ratio on raw magnitudes for better physical representation
        magnitudes = np.abs(f_shift)
        total_energy = np.sum(magnitudes)
        hf_energy = np.sum(magnitudes * mask)
        hf_ratio = hf_energy / total_energy if total_energy > 0 else 0
        
        # We also keep the high_freq_mean of the log-spectrum for texture checking
        high_freq_mean = np.mean(magnitude_spectrum[mask == 1])
        high_freq_max = np.max(magnitude_spectrum)
        
        print(f"DEBUG: Spoof Metrics - HF Ratio (Raw): {hf_ratio:.4f}, HF Mean (Log): {high_freq_mean:.2f}, HF Max: {high_freq_max:.2f}")

        # 3. CNN Feature Analysis (MobileNetV2)
        input_tensor = spoof_transform(image).unsqueeze(0).to(device)
        with torch.no_grad():
            output = spoof_model(input_tensor)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            max_prob = torch.max(probabilities).item()
            
        print(f"DEBUG: CNN Confidence: {max_prob:.4f}")

        # 4. Color Variation / Flatness Analysis
        # Real skin has specific variance patterns. Screens/Photos are often "too flat" or have pixel noise.
        var_r = np.var(img_array[:,:,0])
        var_g = np.var(img_array[:,:,1])
        var_b = np.var(img_array[:,:,2])
        avg_var = (var_r + var_g + var_b) / 3.0
        
        # 5. Specular Reflection Detection (Mobile Screen Hardening)
        # Mobile screens are glass and reflect room lights as sharp bright spots
        # This isn't perfect for all environments, but helps detect "screen-in-front-of-camera"
        _, thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)
        specular_pixels = np.sum(thresh == 255)
        specular_ratio = specular_pixels / (img_array.shape[0] * img_array.shape[1])
        
        # 6. Laplacian Variance (Blur/Flatness Detection)
        # Low variance of Laplacian indicates a blurred image (common in photos/screens)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        print(f"DEBUG: Spoof Metrics - Color Variance: {avg_var:.2f}, Laplacian Variance: {laplacian_var:.2f}, Specular Ratio: {specular_ratio:.4f}")

        # Balanced Re-Calibration for Block/Allow Precision:
        # User Real Face Values: HF_Ratio: 0.48, HF_Mean: 130, Laplacian: 42
        
        is_spoof = False
        reason = ""
        
        # 1. Screen Pattern (FFT / Moire)
        # Moire patterns often have very sharp spikes
        hf_peaks = np.sum(magnitude_spectrum > 275) # Slightly lowered to be more sensitive to subtle moire
        
        # Final thresholds (Refined for Mobile Photo Detection)
        if hf_ratio > 0.70 or high_freq_mean > 152 or hf_peaks > 85:
            is_spoof = True
            reason = "Mobile screen or photo pattern detected (High-frequency noise)"
            
        # 2. Specular Reflection (Screen Glass)
        elif specular_ratio > 0.35: # Increased from 0.15 to allow better lighting scenes
            is_spoof = True
            reason = "Screen reflection detected"

        # 3. Blur / Flatness Check
        elif laplacian_var < 15: # Lowered from 18 to allow slightly softer focus
            is_spoof = True
            reason = "Image blur characteristic of non-live source"

        # 4. Low Color Variation
        elif avg_var < 10: # Lowered from 12
            is_spoof = True
            reason = "Insufficient depth/detail (possible non-live source)"
        
        # 5. CNN Uncertainty (Stays at 0.01)
        elif max_prob < 0.01: # Lowered from 0.02
            is_spoof = True
            reason = "Texture characteristics inconsistent with live face"

        return is_spoof, max_prob, reason

    except Exception as e:
        print(f"Error in spoof detection: {e}")
        return False, 1.0, f"Detection error: {str(e)}"
