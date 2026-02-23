#!/usr/bin/env python3
"""
wav_sim.py - Wealth Abundance Velocity Model Simulation
Simulates wealth growth using compound interest with a 65% annual growth rate over 10 years.
"""

def simulate_wealth_growth(initial_balance, growth_rate, years):
    """
    Simulate wealth growth using compound interest.
    
    Args:
        initial_balance (float): Starting amount of money
        growth_rate (float): Annual growth rate as a decimal (e.g., 0.65 for 65%)
        years (int): Number of years to simulate
    
    Returns:
        list: List of dictionaries containing yearly data
    """
    data = []
    balance = initial_balance
    
    for year in range(1, years + 1):
        start_balance = balance
        growth = start_balance * growth_rate
        end_balance = start_balance + growth
        
        data.append({
            'year': year,
            'start_balance': start_balance,
            'growth': growth,
            'end_balance': end_balance
        })
        
        balance = end_balance
        
    return data

def print_results(data):
    """
    Print a formatted table of the simulation results.
    
    Args:
        data (list): List of dictionaries with yearly simulation data
    """
    # Table header
    header = f"{'Year':<6} {'Start Balance':<20} {'Growth':<20} {'End Balance':<20}"
    print("\nWealth Abundance Velocity Simulation")
    print("=" * 66)
    print(header)
    print("-" * 66)
    
    # Table rows
    for row in data:
        print(f"{row['year']:<6} "
              f"${row['start_balance']:>18,.2f} "
              f"${row['growth']:>18,.2f} "
              f"${row['end_balance']:>18,.2f}")
    
    print("=" * 66)

def main():
    # Simulation parameters
    INITIAL_BALANCE = 1000.0
    GROWTH_RATE = 0.65  # 65% growth rate
    YEARS = 10
    
    # Run simulation
    results = simulate_wealth_growth(INITIAL_BALANCE, GROWTH_RATE, YEARS)
    
    # Display results
    print_results(results)

if __name__ == "__main__":
    main()
