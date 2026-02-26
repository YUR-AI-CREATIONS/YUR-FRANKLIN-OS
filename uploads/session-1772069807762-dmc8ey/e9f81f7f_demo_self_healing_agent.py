#!/usr/bin/env python3
"""
Demo: Grok Self-Healing Agent in Action
Generates and executes Python code with automatic error fixing
"""

from grok_self_healing_agent import GrokSelfHealingAgent

if __name__ == "__main__":
    agent = GrokSelfHealingAgent()
    
    # Example 1: Generate a simple mathematical function
    print("\n" + "="*70)
    print("DEMO 1: Fibonacci Number Generator")
    print("="*70)
    
    mission_1 = """
    Create a Python script that:
    1. Implements a recursive function to calculate Fibonacci numbers
    2. Tests it with values 0 through 10
    3. Prints each result in format: "fib(n) = result"
    """
    
    agent.genesis_loop(mission_1, "demo_fibonacci.py")
    
    # Example 2: Generate a data processing script
    print("\n" + "="*70)
    print("DEMO 2: Simple Data Processor")
    print("="*70)
    
    mission_2 = """
    Create a Python script that:
    1. Generates a list of 100 random numbers between 0-100
    2. Calculates: mean, median, min, max, standard deviation
    3. Prints the statistics in a formatted table
    4. Saves results to a file called "stats_output.txt"
    """
    
    agent.genesis_loop(mission_2, "demo_stats.py")
    
    print("\n" + "="*70)
    print("Demo completed!")
    print("="*70)
