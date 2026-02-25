import unittest
import json
from app import app, Calculator

class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home_endpoint(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
    
    def test_health_endpoint(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_addition(self):
        response = self.app.post('/calculate', 
            json={'operation': 'add', 'operands': [5, 3]})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], 8)
    
    def test_subtraction(self):
        response = self.app.post('/calculate', 
            json={'operation': 'subtract', 'operands': [10, 4]})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], 6)
    
    def test_multiplication(self):
        response = self.app.post('/calculate', 
            json={'operation': 'multiply', 'operands': [3, 4]})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], 12)
    
    def test_division(self):
        response = self.app.post('/calculate', 
            json={'operation': 'divide', 'operands': [15, 3]})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], 5)
    
    def test_division_by_zero(self):
        response = self.app.post('/calculate', 
            json={'operation': 'divide', 'operands': [10, 0]})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_power(self):
        response = self.app.post('/scientific', 
            json={'operation': 'power', 'operands': [2, 3]})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], 8)
    
    def test_sqrt(self):
        response = self.app.post('/scientific', 
            json={'operation': 'sqrt', 'operands': [25]})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], 5)
    
    def test_sqrt_negative(self):
        response = self.app.post('/scientific', 
            json={'operation': 'sqrt', 'operands': [-25]})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_sin(self):
        response = self.app.post('/scientific', 
            json={'operation': 'sin', 'operands': [90]})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertAlmostEqual(data['result'], 1, places=10)
    
    def test_invalid_operation(self):
        response = self.app.post('/calculate', 
            json={'operation': 'invalid', 'operands': [1, 2]})
        self.assertEqual(response.status_code, 400)
    
    def test_missing_operands(self):
        response = self.app.post('/calculate', 
            json={'operation': 'add'})
        self.assertEqual(response.status_code, 400)
    
    def test_invalid_json(self):
        response = self.app.post('/calculate', data='invalid json')
        self.assertEqual(response.status_code, 400)

class TestCalculatorClass(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()
    
    def test_add(self):
        self.assertEqual(self.calc.add(2, 3), 5)
        self.assertEqual(self.calc.add(-1, 1), 0)
        self.assertEqual(self.calc.add(0.1, 0.2), 0.3)
    
    def test_subtract(self):
        self.assertEqual(self.calc.subtract(5, 3), 2)
        self.assertEqual(self.calc.subtract(0, 5), -5)
    
    def test_multiply(self):
        self.assertEqual(self.calc.multiply(4, 5), 20)
        self.assertEqual(self.calc.multiply(-2, 3), -6)
    
    def test_divide(self):
        self.assertEqual(self.calc.divide(10, 2), 5)
        self.assertEqual(self.calc.divide(7, 2), 3.5)
        
        with self.assertRaises(ValueError):
            self.calc.divide(10, 0)
    
    def test_power(self):
        self.assertEqual(self.calc.power(2, 3), 8)
        self.assertEqual(self.calc.power(5, 0), 1)
    
    def test_sqrt(self):
        self.assertEqual(self.calc.sqrt(16), 4)
        self.assertEqual(self.calc.sqrt(0), 0)
        
        with self.assertRaises(ValueError):
            self.calc.sqrt(-4)
    
    def test_log(self):
        self.assertAlmostEqual(self.calc.log(math.e), 1, places=10)
        self.assertEqual(self.calc.log(100, 10), 2)
        
        with self.assertRaises(ValueError):
            self.calc.log(0)
        
        with self.assertRaises(ValueError):
            self.calc.log(-1)

if __name__ == '__main__':
    import math
    unittest.main()