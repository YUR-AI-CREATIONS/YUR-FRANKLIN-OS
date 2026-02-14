#!/usr/bin/env python3
import sys
import argparse
from calculator import add, subtract, multiply, divide, get_operation_function

def interactive_mode():
    """Run calculator in interactive mode."""
    print("Python Calculator")
    print("Available operations: +, -, *, /")
    print("Type 'quit' or 'exit' to stop")
    print("-" * 30)
    
    while True:
        try:
            user_input = input("\nEnter calculation (e.g., 5 + 3): ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
                
            # Parse input
            parts = user_input.split()
            if len(parts) != 3:
                print("Error: Please enter in format: number operator number")
                continue
            
            try:
                num1 = float(parts[0])
                operator = parts[1]
                num2 = float(parts[2])
            except ValueError:
                print("Error: Please enter valid numbers")
                continue
            
            # Get operation function
            operation_func = get_operation_function(operator)
            if operation_func is None:
                print("Error: Unsupported operation. Use +, -, *, or /")
                continue
            
            # Calculate result
            result = operation_func(num1, num2)
            print(f"Result: {num1} {operator} {num2} = {result}")
            
        except ValueError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")

def command_line_mode(args):
    """Run calculator with command line arguments."""
    try:
        num1 = float(args.num1)
        num2 = float(args.num2)
        
        operation_func = get_operation_function(args.operation)
        if operation_func is None:
            print(f"Error: Unsupported operation '{args.operation}'. Use +, -, *, or /")
            sys.exit(1)
        
        result = operation_func(num1, num2)
        print(f"{num1} {args.operation} {num2} = {result}")
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Python Calculator - Perform basic arithmetic operations",
        epilog="Examples:\n"
               "  python main.py 5 + 3\n"
               "  python main.py 10 - 4\n"
               "  python main.py 7 * 8\n"
               "  python main.py 15 / 3\n"
               "  python main.py (interactive mode)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('num1', nargs='?', help='First number')
    parser.add_argument('operation', nargs='?', 
                       choices=['+', '-', '*', '/', 'add', 'subtract', 'multiply', 'divide'],
                       help='Operation: +, -, *, / (or add, subtract, multiply, divide)')
    parser.add_argument('num2', nargs='?', help='Second number')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # If no arguments or interactive flag, run interactive mode
    if args.interactive or not all([args.num1, args.operation, args.num2]):
        interactive_mode()
    else:
        command_line_mode(args)

if __name__ == "__main__":
    main()