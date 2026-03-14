import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 1. Mock face_utils BEFORE importing app to avoid loading heavy models (PyTorch, MTCNN, etc.)
mock_face_utils = MagicMock()
sys.modules['face_utils'] = mock_face_utils

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app import app, vote_sessions

class TestSecureVoting(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Clear sessions
        vote_sessions.clear()

    @patch('app.get_eye_state')
    @patch('app.image_to_embedding')
    @patch('app.compare_embeddings')
    @patch('app.detect_spoofing')
    @patch('app.get_db_connection')
    def test_secure_flow_success(self, mock_db, mock_spoof, mock_compare, mock_embed, mock_eye):
        # 1. Setup Mocks
        # DB returns a voter
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'face_embedding': b'fake_bytes'} 
        
        # Spoof detection passes
        mock_spoof.return_value = (False, 99.9, "Real")
        
        # Eye State: First OPEN, Second CLOSED
        mock_eye.side_effect = [
            ('OPEN', 0.35, "Open"),
            ('CLOSED', 0.15, "Closed")
        ]
        
        # Embeddings succeed
        mock_embed.side_effect = [
            (b'embed_open', None),
            (b'embed_closed', None)
        ]
        
        # Comparison succeeds (Identity and Binding)
        # 1. Identity Check (True)
        # 2. Binding Check (True)
        mock_compare.side_effect = [
            (True, 0.1, 90.0), # Identity
            (True, 0.1, 90.0)  # Binding
        ]

        # 2. Call Secure Verify
        payload = {
            'voter_id': 'test_voter',
            'image_open': 'data:image/png;base64,open',
            'image_closed': 'data:image/png;base64,closed'
        }
        response = self.app.post('/api/secure_verify', json=payload)
        
        # Debug response if it fails
        if response.status_code != 200:
             print(f"FAILED Response: {response.get_json()}")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        print(f"\n[Success Test] Response: {data}")
        self.assertTrue(data['verified'])
        self.assertIn('vote_token', data)
        
        token = data['vote_token']
        
        # 3. Vote with Token
        # Reset DB mock for vote check
        mock_cursor.fetchone.return_value = None # No previous vote
        
        vote_payload = {
            'vote_token': token,
            'candidate': 'Candidate A'
        }
        vote_response = self.app.post('/api/vote', json=vote_payload)
        
        if vote_response.status_code != 201:
             print(f"FAILED Vote Response: {vote_response.get_json()}")
             
        self.assertEqual(vote_response.status_code, 201)
        print(f"[Vote Test] Vote Response: {vote_response.get_json()}")

    def test_vote_without_token(self):
        response = self.app.post('/api/vote', json={'voter_id': 'test', 'candidate': 'A'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing required fields', response.get_json()['error'])

    @patch('app.get_eye_state')
    @patch('app.get_db_connection')
    def test_verify_fails_if_eyes_not_closed(self, mock_db, mock_eye):
        # DB setup
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'face_embedding': b'fake'}

        # Eye State: First OPEN, Second OPEN (No blink)
        mock_eye.side_effect = [
            ('OPEN', 0.35, "Open"),
            ('OPEN', 0.35, "Open - Fail")
        ]

        payload = {
            'voter_id': 'test_voter',
            'image_open': 'data:image/png;base64,open',
            'image_closed': 'data:image/png;base64,open'
        }
        response = self.app.post('/api/secure_verify', json=payload)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Second image must have eyes CLOSED', response.get_json()['error'])
        print(f"\n[Fail Test] Expected Error: {response.get_json()['error']}")

if __name__ == '__main__':
    unittest.main()
