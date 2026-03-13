from db import get_db_connection
from psycopg2.extras import RealDictCursor
import time

def create_admin_session(token, username):
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO admin_sessions (token, username) VALUES (%s, %s)", (token, username))
        conn.commit()
        cur.close()
        conn.close()

def get_admin_session(token):
    conn = get_db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT username FROM admin_sessions WHERE token = %s", (token,))
        res = cur.fetchone()
        cur.close()
        conn.close()
        if res:
            return res['username']
    return None

def delete_admin_session(token):
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM admin_sessions WHERE token = %s", (token,))
        conn.commit()
        cur.close()
        conn.close()

def create_vote_session(token, voter_id, expires_at):
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO vote_tokens (token, voter_id, expires_at) VALUES (%s, %s, %s)", (token, voter_id, expires_at))
        conn.commit()
        cur.close()
        conn.close()

def get_vote_session(token):
    conn = get_db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT voter_id, expires_at FROM vote_tokens WHERE token = %s", (token,))
        res = cur.fetchone()
        cur.close()
        conn.close()
        return res
    return None

def delete_vote_session(token):
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM vote_tokens WHERE token = %s", (token,))
        conn.commit()
        cur.close()
        conn.close()
