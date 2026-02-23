def add(a, b):
    """Add two numbers and return the result."""
    return a + b

def subtract(a, b):
    """Subtract second number from first and return the result."""
    return a - b

def multiply(a, b):
    """Multiply two numbers and return the result."""
    return a * b

def divide(a, b):
    """Divide first number by second and return the result."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def get_number_input(prompt):
    """Get a valid number input from user."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")

def display_menu():
    """Display the calculator menu."""
    print("\n=== Python Calculator ===")
    print("1. Addition (+)")
    print("2. Subtraction (-)")
    print("3. Multiplication (*)")
    print("4. Division (/)")
    print("5. Exit")
    print("=" * 25)

def main():
    """Main calculator loop."""
    while True:
        display_menu()
        
        choice = input("Select operation (1-5): ").strip()
        
        if choice == '5':
            print("Thank you for using the calculator!")
            break
        
        if choice not in ['1', '2', '3', '4']:
            print("Invalid choice. Please select 1-5.")
            continue
        
        # Get numbers from user
        num1 = get_number_input("Enter first number: ")
        num2 = get_number_input("Enter second number: ")
        
        try:
            if choice == '1':
                result = add(num1, num2)
                operation = "+"
            elif choice == '2':
                result = subtract(num1, num2)
                operation = "-"
            elif choice == '3':
                result = multiply(num1, num2)
                operation = "*"
            elif choice == '4':
                result = divide(num1, num2)
                operation = "/"
            
            print(f"\nResult: {num1} {operation} {num2} = {result}")
            
        except ValueError as e:
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()