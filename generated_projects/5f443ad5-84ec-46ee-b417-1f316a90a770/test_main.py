#!/usr/bin/env python3
"""
Unit tests for main.py
"""

import unittest
from main import add_numbers, create_greeting, sum_list

class TestMainFunctions(unittest.TestCase):
    """Test cases for main functions"""
    
    def test_add_numbers(self):
        """Test addition function"""
        self.assertEqual(add_numbers(2, 3), 5)
        self.assertEqual(add_numbers(-1, 1), 0)
        self.assertEqual(add_numbers(0, 0), 0)
    
    def test_create_greeting(self):
        """Test greeting function"""
        self.assertEqual(create_greeting("World"), "Hello, World!")
        self.assertEqual(create_greeting("Alice"), "Hello, Alice!")
        self.assertEqual(create_greeting(""), "Hello, !")
    
    def test_sum_list(self):
        """Test sum list function"""
        self.assertEqual(sum_list([1, 2, 3, 4, 5]), 15)
        self.assertEqual(sum_list([]), 0)
        self.assertEqual(sum_list([-1, 1]), 0)
        self.assertEqual(sum_list([10]), 10)

if __name__ == "__main__":
    unittest.main()