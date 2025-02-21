import unittest
import concurrent.futures
import requests

class TestLoad(unittest.TestCase):
    def setUp(self):
        self.base_url = "https://github-commit-monitor-4a53c549b932.herokuapp.com"
    
    def test_concurrent_webhook_requests(self):
        """Test handling multiple concurrent webhook requests"""
        def make_request():
            return requests.get(f"{self.base_url}/integration.json")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            for future in concurrent.futures.as_completed(futures):
                self.assertEqual(future.result().status_code, 200)