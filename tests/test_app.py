"""
Test the Flask application.
"""
import os
import sys
import unittest

# Add the parent directory to the path so we can import the app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

class TestApp(unittest.TestCase):
    """Test the Flask application."""
    
    def setUp(self):
        """Set up the test environment."""
        self.app = create_app({'TESTING': True})
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up the test environment."""
        self.app_context.pop()
    
    def test_index(self):
        """Test the index route."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'success')
        self.assertEqual(json_data['message'], 'Face Login API is running')
    
    def test_404(self):
        """Test 404 error handling."""
        response = self.client.get('/nonexistent-route')
        self.assertEqual(response.status_code, 404)
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'error')
        self.assertEqual(json_data['message'], 'Resource not found')
    
    def test_users_endpoint(self):
        """Test the users endpoint."""
        response = self.client.get('/api/users')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'success')
        self.assertIn('users', json_data['data'])
    
    def test_recognition_endpoints(self):
        """Test the recognition endpoints."""
        # Test the history endpoint
        response = self.client.get('/api/recognition/history')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'success')
        self.assertIn('history', json_data['data'])

if __name__ == '__main__':
    unittest.main()