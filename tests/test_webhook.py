import unittest
import json
from app import app
import hmac
import hashlib
import os
from dotenv import load_dotenv

class TestWebhook(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        load_dotenv()
        self.github_secret = os.getenv('MY_GITHUB_SECRET')
        
    def generate_signature(self, payload):
        """Generate GitHub signature for payload"""
        return 'sha256=' + hmac.new(
            self.github_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
    def test_valid_webhook_request(self):
        """Test successful webhook processing"""
        payload = {
            "head_commit": {
                "message": "test: add new feature",
                "author": {"name": "Test User"},
            },
            "repository": {"name": "test-repo"}
        }
        
        headers = {
            'X-Hub-Signature-256': self.generate_signature(json.dumps(payload)),
            'Content-Type': 'application/json'
        }
        
        response = self.app.post(
            '/github-webhook',
            data=json.dumps(payload),
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)