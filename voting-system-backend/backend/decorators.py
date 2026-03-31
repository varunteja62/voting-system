from functools import wraps
from flask import request, jsonify
from session_store import get_admin_session

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not get_admin_session(token):
            return jsonify({'error': 'Unauthorized access. Please login as admin.'}), 401
        return f(*args, **kwargs)
    return decorated

import time

rate_limits = {}

def rate_limit(limit, per):
    """Simple in-memory rate limiter"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()
            if ip not in rate_limits:
                rate_limits[ip] = []
            
            # Remove requests older than the 'per' time window
            rate_limits[ip] = [t for t in rate_limits[ip] if now - t < per]
            
            if len(rate_limits[ip]) >= limit:
                return jsonify({'error': 'Too many requests. Please try again later.'}), 429
                
            rate_limits[ip].append(now)
            return f(*args, **kwargs)
        return decorated
    return decorator

def csrf_protect(f):
    """Basic CSRF protection requiring X-Requested-With header"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return jsonify({'error': 'CSRF token missing or incorrect.'}), 403
        return f(*args, **kwargs)
    return decorated
