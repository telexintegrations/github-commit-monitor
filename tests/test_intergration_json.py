import unittest
from app import app

class TestIntegrationJSON(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
    
    def test_integration_json_structure(self):
        """Test integration.json returns correct structure"""
        response = self.app.get('/integration.json')
        data = response.get_json()
        

        self.assertEqual(response.status_code, 200)
        self.assertIn('data', data)
        self.assertIn('descriptions', data['data'])
        self.assertIn('settings', data['data'])
        self.assertIn('target_url', data['data'])
        
        # More specific assertions
        descriptions = data['data']['descriptions']
        self.assertIn('app_name', descriptions)
        self.assertIn('app_description', descriptions)
        self.assertIn('app_logo', descriptions)
        self.assertIn('app_url', descriptions)