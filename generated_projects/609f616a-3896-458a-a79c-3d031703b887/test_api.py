import unittest
import json
from app import app, db, User

class APITestCase(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.app = app.test_client()
        self.app.testing = True
        
        with app.app_context():
            db.create_all()
            
    def tearDown(self):
        """Clean up after tests"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_create_user(self):
        """Test creating a new user"""
        user_data = {
            'name': 'John Doe',
            'email': 'john@example.com'
        }
        response = self.app.post('/api/users',
                               data=json.dumps(user_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'John Doe')
        self.assertEqual(data['email'], 'john@example.com')
    
    def test_get_users(self):
        """Test getting all users"""
        response = self.app.get('/api/users')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_get_user_by_id(self):
        """Test getting a specific user"""
        # First create a user
        user_data = {
            'name': 'Jane Doe',
            'email': 'jane@example.com'
        }
        create_response = self.app.post('/api/users',
                                      data=json.dumps(user_data),
                                      content_type='application/json')
        created_user = json.loads(create_response.data)
        
        # Then get the user by ID
        response = self.app.get(f'/api/users/{created_user["id"]}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Jane Doe')

if __name__ == '__main__':
    unittest.main()