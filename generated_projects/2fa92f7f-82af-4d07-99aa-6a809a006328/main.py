#!/usr/bin/env python3
"""
Simple demonstration application showing how to use generated code.
This script provides examples of common tasks you can do with Python code.
"""

import os
import sys
from pathlib import Path

def display_welcome():
    """Display welcome message and instructions."""
    print("=" * 50)
    print("🐍 PYTHON CODE DEMO APPLICATION")
    print("=" * 50)
    print("\nThis is a working Python application!")
    print("Here's what you can do with this code:\n")

def show_basic_operations():
    """Demonstrate basic Python operations."""
    print("1. BASIC OPERATIONS:")
    print(f"   - Python version: {sys.version}")
    print(f"   - Current directory: {os.getcwd()}")
    print(f"   - This file location: {__file__}")
    print()

def show_file_operations():
    """Demonstrate file operations."""
    print("2. FILE OPERATIONS:")
    
    # Create a sample file
    sample_file = Path("sample_output.txt")
    sample_file.write_text("Hello from generated Python code!\nTimestamp: " + str(Path(__file__).stat().st_mtime))
    
    print(f"   - Created file: {sample_file.name}")
    print(f"   - File exists: {sample_file.exists()}")
    print(f"   - File size: {sample_file.stat().st_size} bytes")
    print()

def show_data_processing():
    """Demonstrate data processing."""
    print("3. DATA PROCESSING:")
    
    # Sample data processing
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    squares = [n**2 for n in numbers]
    even_squares = [n for n in squares if n % 2 == 0]
    
    print(f"   - Original numbers: {numbers}")
    print(f"   - Squares: {squares}")
    print(f"   - Even squares: {even_squares}")
    print(f"   - Sum of even squares: {sum(even_squares)}")
    print()

def show_next_steps():
    """Show what to do next with the code."""
    print("4. WHAT TO DO NEXT:")
    print("   📝 Edit this file (main.py) to add your own functionality")
    print("   🏃 Run: python main.py")
    print("   📦 Install packages: pip install -r requirements.txt")
    print("   🔧 Add your own modules in separate .py files")
    print("   📚 Import and use external libraries")
    print("   🧪 Create tests in a tests/ directory")
    print("   🚀 Deploy to cloud platforms or create executables")
    print()

def main():
    """Main application entry point."""
    try:
        display_welcome()
        show_basic_operations()
        show_file_operations()
        show_data_processing()
        show_next_steps()
        
        print("✅ Application completed successfully!")
        print("Check the 'sample_output.txt' file that was created.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)