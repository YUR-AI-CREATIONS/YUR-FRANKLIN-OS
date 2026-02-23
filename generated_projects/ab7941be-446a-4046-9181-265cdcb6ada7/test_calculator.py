import unittest
from calculator import add, subtract, multiply, divide

class TestCalculator(unittest.TestCase):
    
    def test_add(self):
        self.assertEqual(add(5, 3), 8)
        self.assertEqual(add(-2, 7), 5)
        self.assertEqual(add(0, 0), 0)
        self.assertEqual(add(-5, -3), -8)
    
    def test_subtract(self):
        self.assertEqual(subtract(10, 4), 6)
        self.assertEqual(subtract(5, 8), -3)
        self.assertEqual(subtract(0, 0), 0)
        self.assertEqual(subtract(-5, -3), -2)
    
    def test_multiply(self):
        self.assertEqual(multiply(4, 5), 20)
        self.assertEqual(multiply(-3, 4), -12)
        self.assertEqual(multiply(0, 10), 0)
        self.assertEqual(multiply(-2, -6), 12)
    
    def test_divide(self):
        self.assertEqual(divide(15, 3), 5)
        self.assertEqual(divide(-12, 4), -3)
        self.assertEqual(divide(0, 5), 0)
        self.assertEqual(divide(-10, -2), 5)
    
    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            divide(10, 0)
        with self.assertRaises(ValueError):
            divide(-5, 0)

if __name__ == "__main__":
    unittest.main()