class Calculator:
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        return a + b

    def subtract(self, a: float, b: float) -> float:
        """Subtract two numbers."""
        return a - b

    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        return a * b

    def divide(self, a: float, b: float) -> float:
        """Divide two numbers with error handling for division by zero."""
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        return a / b


def test_calculator():
    """Test the Calculator class with various operations."""
    calc = Calculator()
    test_cases = [
        ("Addition", calc.add, 10.5, 5.5, 16.0),
        ("Subtraction", calc.subtract, 10.5, 5.5, 5.0),
        ("Multiplication", calc.multiply, 10.5, 5.5, 57.75),
    ]
    
    print("Running Calculator Tests...")
    for operation, func, a, b, expected in test_cases:
        result = func(a, b)
        status = abs(result - expected) < 0.0001  # Handle floating point precision
        print(f"{operation}: {a} and {b} = {result:.2f} "
              f"(Expected: {expected:.2f}) - {'PASS' if status else 'FAIL'}")

    # Test division separately due to error handling
    try:
        result = calc.divide(10.5, 5.5)
        expected = 1.909090909
        status = abs(result - expected) < 0.0001
        print(f"Division: 10.5 / 5.5 = {result:.2f} "
              f"(Expected: {expected:.2f}) - {'PASS' if status else 'FAIL'}")
    except Exception as e:
        print(f"Division: Unexpected error - {str(e)} - FAIL")

    # Test division by zero
    try:
        calc.divide(10.5, 0)
        print("Division by zero: Test failed - No exception raised - FAIL")
    except ValueError as e:
        print(f"Division by zero: {str(e)} - PASS")


if __name__ == "__main__":
    test_calculator()