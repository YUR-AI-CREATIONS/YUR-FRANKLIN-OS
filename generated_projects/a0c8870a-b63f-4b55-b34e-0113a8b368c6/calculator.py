def add(a, b):
    """Add two numbers and return the result."""
    return a + b

def subtract(a, b):
    """Subtract second number from first number and return the result."""
    return a - b

def multiply(a, b):
    """Multiply two numbers and return the result."""
    return a * b

def divide(a, b):
    """Divide first number by second number and return the result."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def get_operation_function(operation):
    """Return the appropriate function based on operation string."""
    operations = {
        '+': add,
        'add': add,
        '-': subtract,
        'subtract': subtract,
        '*': multiply,
        'multiply': multiply,
        '/': divide,
        'divide': divide
    }
    return operations.get(operation.lower())