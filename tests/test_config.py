import unittest
import os
from dotenv import load_dotenv

class TestEnvironmentConfig(unittest.TestCase):
    def setUp(self):
        load_dotenv()
        
    def test_environment_variables_exist(self):
        """Test that required environment variables are set"""
        self.assertIsNotNone(os.getenv('MY_GITHUB_SECRET'))
        self.assertIsNotNone(os.getenv('CHANNEL_ID'))