import unittest
import json
from app import app

class TestErrorHandling(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_invalid_signature(self):
        """Test webhook request with invalid signature"""
        payload = {
            "head_commit": {
                "message": "test commit",
                "author": {"name": "Test User"}
            }
        }
        headers = {
            'X-Hub-Signature-256': 'invalid_signature',
            'Content-Type': 'application/json'
        }
        response = self.app.post(
            '/github-webhook',
            data=json.dumps(payload),
            headers=headers
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid signature', response.get_json()['error'])

    def test_missing_signature(self):
        """Test webhook request without signature header"""
        response = self.app.post(
            '/github-webhook',
            data=json.dumps({}),
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn('No signature provided', response.get_json()['error'])

    def test_method_not_allowed(self):
        """Test GET request to webhook endpoint"""
        response = self.app.get('/github-webhook')
        self.assertEqual(response.status_code, 405)