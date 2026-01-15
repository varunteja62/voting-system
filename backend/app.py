from flask import Flask, request, jsonify
from flask_cors import CORS
from psycopg2 import IntegrityError
from psycopg2.extras import RealDictCursor
import json
from db import get_db_connection, init_database
from face_utils import image_to_embedding, compare_embeddings, detect_eye_blink, detect_head_pose

app = Flask(__name__)
CORS(app)

@app.route('/api/check_head_pose', methods=['POST'])
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

@app.route('/api/register', methods=['POST'])
def register_voter():
    """Register a new voter"""
    try:
        data = request.json
        voter_id = data.get('voter_id')
        name = data.get('name')
        face_image = data.get('face_image')
        
        if not all([voter_id, name, face_image]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Convert face image to embedding
        face_embedding, error_msg = image_to_embedding(face_image, check_multiple_faces=True)
        if face_embedding is None:
            return jsonify({'error': error_msg or 'Failed to process face image. Ensure only one person is in frame.'}), 400
        
        # Store in database
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO voters (voter_id, name, face_embedding)
                VALUES (%s, %s, %s)
            """, (voter_id, name, face_embedding))
            conn.commit()
            return jsonify({'message': 'Voter registered successfully'}), 201
        except IntegrityError:
            return jsonify({'error': 'Voter ID already exists'}), 400
        finally:
            cur.close()
            conn.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify', methods=['POST'])
def verify_voter():
    """Verify voter identity before voting"""
    try:
        data = request.json
        voter_id = data.get('voter_id')
        face_image = data.get('face_image')
        
        if not all([voter_id, face_image]):
            return jsonify({'error': 'Missing required fields'}), 400
        
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
        
        face_match = compare_embeddings(voter['face_embedding'], face_embedding)
        if not face_match:
            return jsonify({'error': 'Face verification failed'}), 401
        
        return jsonify({'message': 'Voter verified successfully', 'verified': True}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/candidates', methods=['GET'])
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

@app.route('/api/liveness', methods=['POST'])
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

@app.route('/api/vote', methods=['POST'])
def cast_vote():
    """Cast a vote after verification"""
    try:
        data = request.json
        voter_id = data.get('voter_id')
        candidate = data.get('candidate')
        vote_data = data.get('vote_data', {})
        
        if not voter_id or not candidate:
            return jsonify({'error': 'Missing required fields'}), 400
        
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
        
        return jsonify({'message': 'Vote cast successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/votes', methods=['GET'])
def get_votes():
    """Get all votes for admin dashboard"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT v.voter_id, v.name, vt.candidate, vt.vote_data, vt.voted_at
            FROM votes vt
            JOIN voters v ON vt.voter_id = v.voter_id
            ORDER BY vt.voted_at DESC
        """)
        votes = cur.fetchall()
        cur.close()
        conn.close()
        
        # Convert to list of dicts
        votes_list = []
        for vote in votes:
            votes_list.append({
                'voter_id': vote['voter_id'],
                'name': vote['name'],
                'candidate': vote['candidate'],
                'vote_data': vote['vote_data'],
                'voted_at': vote['voted_at'].isoformat() if vote['voted_at'] else None
            })
        
        return jsonify({'votes': votes_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/stats', methods=['GET'])
def get_stats():
    """Get voting statistics"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Total votes
        cur.execute("SELECT COUNT(*) as total FROM votes")
        total_votes = cur.fetchone()['total']
        
        # Votes by candidate
        cur.execute("""
            SELECT candidate, COUNT(*) as count
            FROM votes
            GROUP BY candidate
            ORDER BY count DESC
        """)
        candidate_stats = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'total_votes': total_votes,
            'candidate_stats': [{'candidate': s['candidate'], 'count': s['count']} for s in candidate_stats]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_database()
    app.run(debug=True, port=5000)
