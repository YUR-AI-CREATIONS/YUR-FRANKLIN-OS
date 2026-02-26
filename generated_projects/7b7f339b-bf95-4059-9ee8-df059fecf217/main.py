#!/usr/bin/env python3
"""
Main entry point for confiem - can be used for testing
"""

from confiem import confirm, confirm_yes_no, confirm_with_options


def demo():
    """Demonstrate confiem functionality"""
    print("=== Confiem Demo ===\n")
    
    # Basic yes/no confirmation
    print("1. Basic confirmation:")
    result = confirm_yes_no("Do you like Python?")
    print(f"Result: {result}\n")
    
    # Confirmation with default
    print("2. Confirmation with default (Yes):")
    result = confirm("Continue with installation?", default=True)
    print(f"Result: {result}\n")
    
    # Multiple options
    print("3. Multiple choice:")
    options = ["Red", "Green", "Blue", "Yellow"]
    choice = confirm_with_options("Choose your favorite color:", options, default=0)
    print(f"You chose: {choice}\n")
    
    # Custom yes/no values
    print("4. Custom confirmation values:")
    result = confirm(
        "Proceed with deletion?",
        yes_values=['delete', 'remove', 'yes'],
        no_values=['keep', 'cancel', 'no'],
        default=False
    )
    print(f"Result: {result}")


if __name__ == "__main__":
    demo()