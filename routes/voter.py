from flask import Blueprint, request, jsonify, current_app
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
        face_images = data.get('face_images', []) # expecting an array of 3 images
        
        if not all([voter_id, name]) or len(face_images) == 0:
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
        
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO voters (voter_id, name, face_embedding)
                VALUES (%s, %s, %s)
            """, (voter_id, name, final_embedding_bytes))
            conn.commit()
            return jsonify({'message': 'Voter registered successfully'}), 201
        except IntegrityError:
            return jsonify({'error': 'Voter ID already exists'}), 400
        finally:
            cur.close()
            conn.close()
            
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
    """
    Perform liveness detection using eye blink AND verify identity.
    This prevents 'Person A' from verifying and 'Person B' from blinking.
    """
    try:
        data = request.json
        voter_id = data.get('voter_id')
        face_image = data.get('face_image')
        
        if not all([voter_id, face_image]):
            return jsonify({'error': 'Missing required fields: voter_id, face_image'}), 400
        
        # 1. Identity Check (Binding)
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
            
        # Generate embedding for current frame
        current_embedding, error_msg = image_to_embedding(face_image, check_multiple_faces=False)
        if current_embedding is None:
            return jsonify({'error': error_msg or 'Failed to process face image during liveness'}), 400
            
        # Compare with registered face
        face_match, distance, conf = compare_embeddings(
            voter['face_embedding'], 
            current_embedding, 
            threshold=current_app.config['FACE_MATCH_THRESHOLD']
        )
        
        print(f"DEBUG: Liveness identity check - Distance: {distance:.4f} (Threshold: {current_app.config['FACE_MATCH_THRESHOLD']}), Result: {'MATCH' if face_match else 'MISMATCH'}")
        
        if not face_match:
            return jsonify({
                'error': 'Security Alert: Identity mismatch during liveness check. Please ensure the same person is in frame.',
                'verified': False
            }), 403

        # 2. Liveness Check (Eye Blink)
        blink_detected = detect_eye_blink(face_image)
        
        vote_token = None
        if blink_detected:
            # IDENTITY + BLINK MATCHED on same frame. Issue License to Vote.
            vote_token = str(uuid.uuid4())
            # Token expires in 5 minutes (300 seconds)
            create_vote_session(vote_token, voter_id, time.time() + 300)
            print(f"DEBUG: Security Chain Secured. Issued vote_token for {voter_id}")
        
        return jsonify({
            'liveness_detected': blink_detected,
            'identity_verified': True,
            'vote_token': vote_token,
            'message': 'Liveness and Identity verification completed' if blink_detected else 'Identity verified, waiting for blink...'
        }), 200
        
    except Exception as e:
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
        
        if not all([vote_token, candidate]):
            return jsonify({'error': 'Missing required fields: vote_token, candidate'}), 400
            
        # 1. Validate the digital 'License to Vote' (The Token)
        session = get_vote_session(vote_token)
        if not session:
            return jsonify({'error': 'Invalid or expired vote token. Please perform liveness check again.'}), 401
            
        if time.time() > session['expires_at']:
            delete_vote_session(vote_token)
            return jsonify({'error': 'Vote token expired. Please perform liveness check again.'}), 401
            
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
        
        # 2. Burn the token so it can't be used again
        delete_vote_session(vote_token)
        
        return jsonify({'message': 'Vote cast successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
