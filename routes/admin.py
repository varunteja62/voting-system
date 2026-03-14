<<<<<<< Updated upstream
from flask import Blueprint, request, jsonify, current_app
from psycopg2.extras import RealDictCursor
import secrets
from db import get_db_connection
from session_store import create_admin_session, delete_admin_session
from decorators import admin_required, rate_limit, csrf_protect

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['POST'])
@rate_limit(5, 300) # 5 attempts per 5 minutes
@csrf_protect
def admin_login():
    """Verify admin credentials"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if username == current_app.config['ADMIN_USERNAME'] and password == current_app.config['ADMIN_PASSWORD']:
            token = secrets.token_hex(16)
            create_admin_session(token, username)
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'authenticated': True
            }), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/logout', methods=['POST'])
@csrf_protect
def admin_logout():
    token = request.headers.get('Authorization')
    if token:
        delete_admin_session(token)
    return jsonify({'message': 'Logged out successfully'}), 200

@admin_bp.route('/votes', methods=['GET'])
@admin_required
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

@admin_bp.route('/stats', methods=['GET'])
@admin_required
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
=======
from flask import Blueprint, request, jsonify, current_app
from psycopg2.extras import RealDictCursor
import secrets
from db import get_db_connection
from session_store import create_admin_session, delete_admin_session
from decorators import admin_required, rate_limit, csrf_protect

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['POST'])
@rate_limit(5, 300) # 5 attempts per 5 minutes
@csrf_protect
def admin_login():
    """Verify admin credentials"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if username == current_app.config['ADMIN_USERNAME'] and password == current_app.config['ADMIN_PASSWORD']:
            token = secrets.token_hex(16)
            create_admin_session(token, username)
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'authenticated': True
            }), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/logout', methods=['POST'])
@csrf_protect
def admin_logout():
    token = request.headers.get('Authorization')
    if token:
        delete_admin_session(token)
    return jsonify({'message': 'Logged out successfully'}), 200

@admin_bp.route('/votes', methods=['GET'])
@admin_required
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

@admin_bp.route('/stats', methods=['GET'])
@admin_required
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
>>>>>>> Stashed changes
