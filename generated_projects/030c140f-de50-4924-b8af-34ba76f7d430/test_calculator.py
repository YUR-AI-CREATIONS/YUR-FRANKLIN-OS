import pytest
import math
from calculator import Calculator


class TestCalculator:
    """Test suite for the Calculator class."""
    
    def setup_method(self):
        """Setup a fresh calculator for each test."""
        self.calc = Calculator()
    
    # Basic Operations Tests
    def test_addition(self):
        assert self.calc.add(2, 3) == 5
        assert self.calc.add(-1, 1) == 0
        assert self.calc.add(0.1, 0.2) == pytest.approx(0.3)
    
    def test_subtraction(self):
        assert self.calc.subtract(5, 3) == 2
        assert self.calc.subtract(-1, -1) == 0
        assert self.calc.subtract(0.5, 0.2) == pytest.approx(0.3)
    
    def test_multiplication(self):
        assert self.calc.multiply(3, 4) == 12
        assert self.calc.multiply(-2, 3) == -6
        assert self.calc.multiply(0, 5) == 0
    
    def test_division(self):
        assert self.calc.divide(6, 2) == 3
        assert self.calc.divide(1, 3) == pytest.approx(0.333333, rel=1e-5)
        
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            self.calc.divide(5, 0)
    
    # Advanced Operations Tests
    def test_power(self):
        assert self.calc.power(2, 3) == 8
        assert self.calc.power(4, 0.5) == 2
        assert self.calc.power(10, -1) == 0.1
    
    def test_square_root(self):
        assert self.calc.square_root(16) == 4
        assert self.calc.square_root(0) == 0
        assert self.calc.square_root(2) == pytest.approx(1.414213)
        
        with pytest.raises(ValueError, match="Cannot take square root of negative number"):
            self.calc.square_root(-1)
    
    def test_factorial(self):
        assert self.calc.factorial(0) == 1
        assert self.calc.factorial(5) == 120
        assert self.calc.factorial(1) == 1
        
        with pytest.raises(ValueError, match="Factorial is not defined for negative numbers"):
            self.calc.factorial(-1)
    
    def test_logarithm(self):
        assert self.calc.logarithm(math.e) == pytest.approx(1)
        assert self.calc.logarithm(10, 10) == pytest.approx(1)
        assert self.calc.logarithm(8, 2) == pytest.approx(3)
        
        with pytest.raises(ValueError):
            self.calc.logarithm(-1)
        with pytest.raises(ValueError):
            self.calc.logarithm(10, -1)
    
    # Trigonometric Functions Tests
    def test_sin(self):
        assert self.calc.sin(0) == pytest.approx(0)
        assert self.calc.sin(90, degrees=True) == pytest.approx(1)
        assert self.calc.sin(math.pi/2) == pytest.approx(1)
    
    def test_cos(self):
        assert self.calc.cos(0) == pytest.approx(1)
        assert self.calc.cos(90, degrees=True) == pytest.approx(0, abs=1e-10)
        assert self.calc.cos(math.pi) == pytest.approx(-1)
    
    def test_tan(self):
        assert self.calc.tan(0) == pytest.approx(0)
        assert self.calc.tan(45, degrees=True) == pytest.approx(1)
        assert self.calc.tan(math.pi/4) == pytest.approx(1)
    
    # History and Memory Tests
    def test_history(self):
        self.calc.add(2, 3)
        self.calc.multiply(4, 5)
        
        history = self.calc.get_history()
        assert len(history) == 2
        assert "2 + 3 = 5" in history[0]
        assert "4 × 5 = 20" in history[1]
    
    def test_last_result(self):
        result = self.calc.add(10, 15)
        assert self.calc.get_last_result() == result
        assert self.calc.get_last_result() == 25
    
    def test_clear_history(self):
        self.calc.add(1, 1)
        self.calc.clear_history()
        assert len(self.calc.get_history()) == 0
    
    # Expression Evaluation Tests
    def test_evaluate_expression(self):
        assert self.calc.evaluate("2 + 3 * 4") == 14
        assert self.calc.evaluate("(2 + 3) * 4") == 20
        assert self.calc.evaluate("2 ** 3") == 8
        assert self.calc.evaluate("sqrt(16)") == 4
        
        with pytest.raises(ValueError):
            self.calc.evaluate("invalid_function()")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])