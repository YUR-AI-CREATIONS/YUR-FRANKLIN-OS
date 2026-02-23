def add(x, y):
    """Add two numbers and return the result."""
    return x + y

def subtract(x, y):
    """Subtract second number from first number and return the result."""
    return x - y

def multiply(x, y):
    """Multiply two numbers and return the result."""
    return x * y

def divide(x, y):
    """Divide first number by second number and return the result."""
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y

def display_menu():
    """Display the calculator menu."""
    print("\n=== Simple Calculator ===")
    print("1. Add")
    print("2. Subtract") 
    print("3. Multiply")
    print("4. Divide")
    print("5. Exit")

def get_numbers():
    """Get two numbers from user input."""
    try:
        num1 = float(input("Enter first number: "))
        num2 = float(input("Enter second number: "))
        return num1, num2
    except ValueError:
        print("Error: Please enter valid numbers")
        return None, None

def main():
    """Main calculator function."""
    while True:
        display_menu()
        
        try:
            choice = input("\nEnter your choice (1-5): ")
            
            if choice == '5':
                print("Thank you for using the calculator!")
                break
            
            if choice not in ['1', '2', '3', '4']:
                print("Error: Invalid choice. Please select 1-5.")
                continue
            
            num1, num2 = get_numbers()
            if num1 is None or num2 is None:
                continue
            
            if choice == '1':
                result = add(num1, num2)
                print(f"Result: {num1} + {num2} = {result}")
            
            elif choice == '2':
                result = subtract(num1, num2)
                print(f"Result: {num1} - {num2} = {result}")
            
            elif choice == '3':
                result = multiply(num1, num2)
                print(f"Result: {num1} * {num2} = {result}")
            
            elif choice == '4':
                try:
                    result = divide(num1, num2)
                    print(f"Result: {num1} / {num2} = {result}")
                except ValueError as e:
                    print(f"Error: {e}")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()