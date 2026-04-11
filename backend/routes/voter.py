from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg2 import IntegrityError
from psycopg2.extras import RealDictCursor
import json
import uuid
import time
from db import get_db_connection
from face_utils import image_to_embedding, compare_embeddings, detect_eye_blink, detect_head_pose, detect_spoofing, get_eye_state
from session_store import create_vote_session, get_vote_session, delete_vote_session
from decorators import rate_limit, csrf_protect
import numpy as np

voter_bp = Blueprint('voter', __name__)

@voter_bp.route('/check_head_pose', methods=['POST'])
def check_head_pose():
    """Check head pose direction"""
    try:
        data = request.json
        face_image = data.get('face_image')
        
        if not face_image:
            return jsonify({'error': 'Missing face image'}), 400
            
        pose = detect_head_pose(face_image)
        
        if pose == 'Error':
            return jsonify({'error': 'Face detection failed. Ensure face is well-lit and clearly visible.'}), 400
            
        return jsonify({
            'pose': pose,
            'message': f'Head pose detected: {pose}'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voter_bp.route('/register', methods=['POST'])
@rate_limit(5, 60) # 5 attempts per minute
@csrf_protect
def register_voter():
    """Register a new voter"""
    try:
        data = request.json
        voter_id = data.get('voter_id')
        name = data.get('name')
        password = data.get('password')
        face_images = data.get('face_images', []) # expecting an array of 3 images
        
        if not all([voter_id, name, password]) or len(face_images) == 0:
            return jsonify({'error': 'Missing required fields or images'}), 400
        
        # Check if voter already exists
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cur = conn.cursor()
        cur.execute("SELECT voter_id FROM voters WHERE voter_id = %s", (voter_id,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({'error': f'Voter ID {voter_id} is already registered. You cannot register again.'}), 400
        
        cur.close()
        conn.close()

        # Process all images
        embeddings = []
        for i, img in enumerate(face_images):
            # Perform Spoof Detection Check on each
            is_spoof, conf, reason = detect_spoofing(img)
            if is_spoof:
                return jsonify({'error': f'Liveness verification failed on image {i+1}: {reason}'}), 403
            
            # Convert face image to embedding
            emb, error_msg = image_to_embedding(img, check_multiple_faces=True)
            if emb is None:
                return jsonify({'error': error_msg or f'Failed to process face image {i+1}. Ensure only one person is in frame.'}), 400
            
            # Convert bytes back to numpy for averaging
            embeddings.append(np.frombuffer(emb, dtype=np.float32))
            
        # Average the embeddings for multi-angle robustness
        avg_embedding = np.mean(embeddings, axis=0)
        avg_embedding = avg_embedding / np.linalg.norm(avg_embedding)
        final_embedding_bytes = avg_embedding.tobytes()
        
        # Store in database
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        password_hash = generate_password_hash(password)
        
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO voters (voter_id, name, password_hash, face_embedding)
                VALUES (%s, %s, %s, %s)
            """, (voter_id, name, password_hash, final_embedding_bytes))
            conn.commit()
            return jsonify({'message': 'Voter registered successfully'}), 201
        except IntegrityError:
            return jsonify({'error': 'Voter ID already exists'}), 400
        finally:
            cur.close()
            conn.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voter_bp.route('/login', methods=['POST'])
@rate_limit(10, 60) # 10 attempts per minute
def login_voter():
    """Login a voter using ID and password"""
    try:
        data = request.json
        voter_id = data.get('voter_id')
        password = data.get('password')
        
        if not all([voter_id, password]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT voter_id, name, password_hash FROM voters WHERE voter_id = %s", (voter_id,))
        voter = cur.fetchone()
        cur.close()
        conn.close()
        
        if not voter:
            return jsonify({'error': 'Voter not found'}), 404
            
        # Verify password
        if not check_password_hash(voter['password_hash'], password):
            return jsonify({'error': 'Invalid password'}), 401
            
        return jsonify({
            'message': 'Login successful',
            'voter': {
                'id': voter['voter_id'],
                'name': voter['name']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voter_bp.route('/verify', methods=['POST'])
@rate_limit(10, 60) # 10 attempts per minute
@csrf_protect
def verify_voter():
    """Verify voter identity before voting"""
    try:
        data = request.json
        voter_id = data.get('voter_id')
        face_image = data.get('face_image')
        
        if not all([voter_id, face_image]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Perform Spoof Detection Check
        is_spoof, confidence, reason = detect_spoofing(face_image)
        if is_spoof:
            print(f"DEBUG: Verification rejected due to spoofing. Reason: {reason} (Confidence: {confidence:.4f})")
            return jsonify({'error': f'Liveness verification failed: {reason}'}), 403
        
        # Get voter from database
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT face_embedding FROM voters WHERE voter_id = %s", (voter_id,))
        voter = cur.fetchone()
        cur.close()
        conn.close()
        
        if not voter:
            return jsonify({'error': 'Voter not found'}), 404
        
        # Verify face
        face_embedding, error_msg = image_to_embedding(face_image, check_multiple_faces=False)
        if face_embedding is None:
            return jsonify({'error': error_msg or 'Failed to process face image'}), 400
        
        base_threshold = current_app.config['FACE_MATCH_THRESHOLD']
        # Relax threshold slightly if we are highly confident it's a real live person
        dynamic_threshold = base_threshold + (0.02 if confidence > 0.9 else 0)
        
        face_match, distance, conf = compare_embeddings(
            voter['face_embedding'], 
            face_embedding, 
            threshold=dynamic_threshold
        )
        
        print(f"DEBUG: Face verification distance: {distance:.4f} (Dynamic Threshold: {dynamic_threshold:.3f}), Confidence: {conf}%")
        
        if not face_match:
            return jsonify({
                'error': 'Face verification failed',
                'distance': round(float(distance), 4),
                'confidence': conf,
                'verified': False
            }), 401
        
        return jsonify({
            'message': 'Voter verified successfully',
            'verified': True,
            'confidence': conf,
            'distance': round(float(distance), 4)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voter_bp.route('/candidates', methods=['GET'])
def get_candidates():
    """Get list of candidates"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, name, party FROM candidates ORDER BY name")
        candidates = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({'candidates': [dict(c) for c in candidates]}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voter_bp.route('/liveness', methods=['POST'])
def check_liveness():
    """Perform liveness detection using eye blink"""
    try:
        data = request.json
        face_image = data.get('face_image')
        
        if not face_image:
            return jsonify({'error': 'Missing face image'}), 400
        
        # Detect eye blink
        blink_detected = detect_eye_blink(face_image)
        
        return jsonify({
            'liveness_detected': blink_detected,
            'message': 'Liveness check completed'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voter_bp.route('/secure_verify', methods=['POST'])
@rate_limit(10, 60)
@csrf_protect
def secure_verify_voter():
    """
    Strict 2-step verification:
    1. Validate Identity (against DB)
    2. Validate Liveness (Open vs Closed eyes + Same person)
    Returns a one-time vote_token.
    """
    try:
        data = request.json
        voter_id = data.get('voter_id')
        img_open = data.get('image_open')
        img_closed = data.get('image_closed')
        
        if not all([voter_id, img_open, img_closed]):
            return jsonify({'error': 'Missing required fields: voter_id, image_open, image_closed'}), 400
            
        # 1. Fetch Registered Voter
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT face_embedding FROM voters WHERE voter_id = %s", (voter_id,))
        voter = cur.fetchone()
        cur.close()
        conn.close()
        
        if not voter:
            return jsonify({'error': 'Voter not found'}), 404
            
        # 2. Process Images and Check Liveness States
        # Check OPEN image
        state_open, ear_open, msg_open = get_eye_state(img_open)
        if state_open != 'OPEN':
            return jsonify({'error': f'Liveness Check Failed: First image must have eyes OPEN. Detected: {state_open} ({msg_open})'}), 400

        # Check CLOSED image
        state_closed, ear_closed, msg_closed = get_eye_state(img_closed)
        if state_closed != 'CLOSED':
            return jsonify({'error': f'Liveness Check Failed: Second image must have eyes CLOSED (Blink). Detected: {state_closed} ({msg_closed})'}), 400
            
        # 3. Spoof Detection (Double Check)
        is_spoof, conf_spoof, reason = detect_spoofing(img_open)
        if is_spoof:
             return jsonify({'error': f'Spoof detected on open-eye image: {reason}'}), 403
             
        # 4. Generate Embeddings for Identity Binding
        emb_open, err1 = image_to_embedding(img_open, check_multiple_faces=False)
        if not emb_open: return jsonify({'error': f'Face processing error (Open): {err1}'}), 400
        
        emb_closed, err2 = image_to_embedding(img_closed, check_multiple_faces=False)
        if not emb_closed: return jsonify({'error': f'Face processing error (Closed): {err2}'}), 400
        
        # 5. Verify Identity (Match Registered Face)
        # We verify the OPEN image primarily against the DB
        base_threshold = current_app.config['FACE_MATCH_THRESHOLD']
        # Relax threshold slightly if we are highly confident it's a real live person
        dynamic_threshold = base_threshold + (0.02 if conf_spoof > 0.9 else 0)

        match_db, dist_db, conf_db = compare_embeddings(
            voter['face_embedding'], 
            emb_open, 
            threshold=dynamic_threshold
        )
        
        if not match_db:
             return jsonify({'error': f'Identity Verification Failed: Face does not match registered voter. (Confidence: {conf_db}%)'}), 401
             
        # 6. Verify Binding (Match Open vs Closed)
        # Ensure the person blinking is the SAME person who was verified
        match_binding, dist_binding, conf_binding = compare_embeddings(
            emb_open,
            emb_closed,
            threshold=current_app.config['FACE_MATCH_THRESHOLD']
        )
        
        if not match_binding:
            return jsonify({'error': 'Security Alert: The person blinking is NOT the same as the person verified. Request denied.'}), 403
            
        # 7. Success! Issue Token
        vote_token = str(uuid.uuid4())
        create_vote_session(vote_token, voter_id, time.time() + 300)
        
        return jsonify({
            'message': 'Secure verification successful',
            'verified': True,
            'vote_token': vote_token,
            'confidence': conf_db
        }), 200

    except Exception as e:
        print(f"Secure Verify Error: {e}")
        return jsonify({'error': str(e)}), 500

@voter_bp.route('/vote', methods=['POST'])
@rate_limit(5, 60)
@csrf_protect
def cast_vote():
    """Cast a vote after verification"""
    try:
        data = request.json
        vote_token = data.get('vote_token')
        candidate = data.get('candidate')
        vote_data = data.get('vote_data', {})
        
        if not vote_token or not candidate:
            return jsonify({'error': 'Missing required fields: vote_token, candidate'}), 400
            
        # Validate Token
        session = get_vote_session(vote_token)
        if not session:
            return jsonify({'error': 'Invalid or expired vote token. Please verify again.'}), 401
            
        if time.time() > session['expires_at']:
            delete_vote_session(vote_token)
            return jsonify({'error': 'Vote token expired. Please verify again.'}), 401
            
        voter_id = session['voter_id']
        
        # Check if voter has already voted
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cur = conn.cursor()
        cur.execute("SELECT id FROM votes WHERE voter_id = %s", (voter_id,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({'error': 'Voter has already voted'}), 400
        
        # Record vote
        cur.execute("""
            INSERT INTO votes (voter_id, candidate, vote_data)
            VALUES (%s, %s, %s)
        """, (voter_id, candidate, json.dumps(vote_data)))
        conn.commit()
        cur.close()
        conn.close()
        
        # Burn the token to prevent replay
        delete_vote_session(vote_token)
        
        return jsonify({'message': 'Vote cast successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
