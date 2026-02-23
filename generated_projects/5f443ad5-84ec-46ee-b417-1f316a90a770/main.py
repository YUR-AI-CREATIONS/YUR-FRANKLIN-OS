#!/usr/bin/env python3
"""
Simple test application
"""

def main():
    """Main function to run tests"""
    print("Running tests...")
    
    # Basic functionality test
    result = add_numbers(2, 3)
    assert result == 5, f"Expected 5, got {result}"
    print("✓ Addition test passed")
    
    # String test
    greeting = create_greeting("World")
    assert greeting == "Hello, World!", f"Expected 'Hello, World!', got '{greeting}'"
    print("✓ Greeting test passed")
    
    # List test
    numbers = [1, 2, 3, 4, 5]
    total = sum_list(numbers)
    assert total == 15, f"Expected 15, got {total}"
    print("✓ Sum list test passed")
    
    print("\nAll tests passed! ✓")

def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

def create_greeting(name: str) -> str:
    """Create a greeting message"""
    return f"Hello, {name}!"

def sum_list(numbers: list[int]) -> int:
    """Sum all numbers in a list"""
    return sum(numbers)

if __name__ == "__main__":
    main()