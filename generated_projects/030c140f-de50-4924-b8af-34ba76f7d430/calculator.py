import math
from typing import Union

class Calculator:
    """A comprehensive calculator with basic and advanced operations."""
    
    def __init__(self):
        self.history = []
        self.last_result = 0
    
    def _record_operation(self, operation: str, result: float) -> float:
        """Record operation in history and update last result."""
        self.history.append(f"{operation} = {result}")
        self.last_result = result
        return result
    
    # Basic Operations
    def add(self, a: float, b: float) -> float:
        """Addition operation."""
        result = a + b
        return self._record_operation(f"{a} + {b}", result)
    
    def subtract(self, a: float, b: float) -> float:
        """Subtraction operation."""
        result = a - b
        return self._record_operation(f"{a} - {b}", result)
    
    def multiply(self, a: float, b: float) -> float:
        """Multiplication operation."""
        result = a * b
        return self._record_operation(f"{a} × {b}", result)
    
    def divide(self, a: float, b: float) -> float:
        """Division operation."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        return self._record_operation(f"{a} ÷ {b}", result)
    
    # Advanced Operations
    def power(self, base: float, exponent: float) -> float:
        """Power operation."""
        result = base ** exponent
        return self._record_operation(f"{base}^{exponent}", result)
    
    def square_root(self, x: float) -> float:
        """Square root operation."""
        if x < 0:
            raise ValueError("Cannot take square root of negative number")
        result = math.sqrt(x)
        return self._record_operation(f"√{x}", result)
    
    def factorial(self, n: int) -> int:
        """Factorial operation."""
        if n < 0:
            raise ValueError("Factorial is not defined for negative numbers")
        if not isinstance(n, int):
            raise ValueError("Factorial requires an integer")
        result = math.factorial(n)
        return self._record_operation(f"{n}!", result)
    
    def logarithm(self, x: float, base: float = math.e) -> float:
        """Logarithm operation."""
        if x <= 0:
            raise ValueError("Logarithm is not defined for non-positive numbers")
        if base <= 0 or base == 1:
            raise ValueError("Logarithm base must be positive and not equal to 1")
        
        if base == math.e:
            result = math.log(x)
            operation = f"ln({x})"
        else:
            result = math.log(x, base)
            operation = f"log_{base}({x})"
        
        return self._record_operation(operation, result)
    
    # Trigonometric Functions
    def sin(self, x: float, degrees: bool = False) -> float:
        """Sine function."""
        if degrees:
            x = math.radians(x)
        result = math.sin(x)
        unit = "°" if degrees else " rad"
        return self._record_operation(f"sin({x}{unit})", result)
    
    def cos(self, x: float, degrees: bool = False) -> float:
        """Cosine function."""
        if degrees:
            x = math.radians(x)
        result = math.cos(x)
        unit = "°" if degrees else " rad"
        return self._record_operation(f"cos({x}{unit})", result)
    
    def tan(self, x: float, degrees: bool = False) -> float:
        """Tangent function."""
        if degrees:
            x = math.radians(x)
        result = math.tan(x)
        unit = "°" if degrees else " rad"
        return self._record_operation(f"tan({x}{unit})", result)
    
    # Memory and History
    def get_history(self) -> list:
        """Get calculation history."""
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Clear calculation history."""
        self.history.clear()
    
    def get_last_result(self) -> float:
        """Get the last calculation result."""
        return self.last_result
    
    # Expression Evaluation
    def evaluate(self, expression: str) -> float:
        """Evaluate a mathematical expression safely."""
        # Replace common mathematical symbols
        expression = expression.replace("^", "**")
        expression = expression.replace("×", "*")
        expression = expression.replace("÷", "/")
        
        # Define allowed names for eval
        allowed_names = {
            "__builtins__": {},
            "abs": abs,
            "pow": pow,
            "round": round,
            "max": max,
            "min": min,
            "sum": sum,
            "math": math,
            "pi": math.pi,
            "e": math.e,
        }
        
        try:
            result = eval(expression, allowed_names, {})
            self._record_operation(expression, result)
            return result
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")


def main():
    """Interactive calculator interface."""
    calc = Calculator()
    
    print("🧮 Python Calculator")
    print("=" * 50)
    print("Commands:")
    print("  Basic: +, -, *, /, ** (power)")
    print("  Functions: sqrt(x), sin(x), cos(x), tan(x), log(x)")
    print("  Special: history, clear, last, quit")
    print("  Example: 2 + 3 * 4, sqrt(16), sin(30)")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n>>> ").strip().lower()
            
            if user_input in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
            elif user_input == 'history':
                history = calc.get_history()
                if history:
                    print("\n📊 Calculation History:")
                    for i, operation in enumerate(history[-10:], 1):  # Show last 10
                        print(f"  {i}. {operation}")
                else:
                    print("No calculations in history.")
                continue
            elif user_input == 'clear':
                calc.clear_history()
                print("History cleared! 🗑️")
                continue
            elif user_input == 'last':
                print(f"Last result: {calc.get_last_result()}")
                continue
            elif user_input == '':
                continue
            
            # Handle special function inputs
            if user_input.startswith('sqrt('):
                value = float(user_input[5:-1])
                result = calc.square_root(value)
            elif user_input.startswith('sin('):
                value = float(user_input[4:-1])
                result = calc.sin(value, degrees=True)
            elif user_input.startswith('cos('):
                value = float(user_input[4:-1])
                result = calc.cos(value, degrees=True)
            elif user_input.startswith('tan('):
                value = float(user_input[4:-1])
                result = calc.tan(value, degrees=True)
            elif user_input.startswith('log('):
                value = float(user_input[4:-1])
                result = calc.logarithm(value, 10)  # Base 10 log
            elif user_input.endswith('!') and user_input[:-1].isdigit():
                value = int(user_input[:-1])
                result = calc.factorial(value)
            else:
                # Try to evaluate as expression
                result = calc.evaluate(user_input)
            
            print(f"Result: {result}")
            
        except ValueError as e:
            print(f"❌ Error: {e}")
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()