#!/usr/bin/env python3
"""
yur_financial_model.py - Wealth Abundance Velocity (WAV) Analysis
This script models wealth growth over a specified time horizon with varying
retained yields and growth sensitivities.
"""

def format_currency(amount):
    """Format number as currency with commas and 2 decimal places."""
    return f"${amount:,.2f}"

def calculate_wav(initial_capital, years, retained_yield, annual_growth):
    """Calculate year-by-year balance for given parameters."""
    balance = initial_capital
    results = []
    for year in range(1, years + 1):
        growth = balance * (annual_growth / 100)
        retained = balance * (retained_yield / 100)
        balance += growth - retained
        results.append((year, balance))
    return results

def print_balance_table(scenario_name, results):
    """Print formatted table of year-by-year balances."""
    print(f"\n{scenario_name}")
    print("-" * 80)
    print(f"{'Year':<10} {'Balance':>30}")
    print("-" * 80)
    for year, balance in results:
        print(f"{year:<10} {format_currency(balance):>30}")
    print("-" * 80)

def print_sensitivity_analysis(initial_capital, years, retained_yield, growth_rates):
    """Print sensitivity analysis for different growth rates."""
    print(f"\nSensitivity Analysis (Retained Yield: {retained_yield}%)")
    print("-" * 80)
    print(f"{'Growth Rate':<15} {'Final Balance':>30}")
    print("-" * 80)
    for rate in growth_rates:
        balance = initial_capital
        for _ in range(years):
            growth = balance * (rate / 100)
            retained = balance * (retained_yield / 100)
            balance += growth - retained
        print(f"{rate}%{'':<15} {format_currency(balance):>30}")
    print("-" * 80)

def calculate_summary_stats(results):
    """Calculate summary statistics for a scenario."""
    final_balance = results[-1][1]
    initial_balance = results[0][1] if len(results) > 1 else final_balance
    total_growth = final_balance - initial_balance
    avg_annual_growth = (final_balance / initial_balance) ** (1 / len(results)) - 1
    return {
        "final_balance": final_balance,
        "total_growth": total_growth,
        "avg_annual_growth": avg_annual_growth * 100
    }

def main():
    # Parameters
    INITIAL_CAPITAL = 100_000_000_000  # $100 billion
    TIME_HORIZON = 10  # years
    RETAINED_YIELDS = [1.0, 2.0]  # 1% and 2%
    BASE_GROWTH_RATE = 65.0  # 65% annual growth
    GROWTH_SENSITIVITIES = [60.0, 65.0, 70.0]  # for sensitivity analysis

    print("Wealth Abundance Velocity (WAV) Analysis")
    print("=" * 80)
    print(f"Initial Capital: {format_currency(INITIAL_CAPITAL)}")
    print(f"Time Horizon: {TIME_HORIZON} years")
    print("=" * 80)

    # Run scenarios for each retained yield
    all_stats = {}
    for yield_rate in RETAINED_YIELDS:
        scenario_name = f"Scenario - Retained Yield {yield_rate}%"
        results = calculate_wav(INITIAL_CAPITAL, TIME_HORIZON, yield_rate, BASE_GROWTH_RATE)
        print_balance_table(scenario_name, results)
        all_stats[scenario_name] = calculate_summary_stats(results)

    # Sensitivity analysis for each retained yield
    for yield_rate in RETAINED_YIELDS:
        print_sensitivity_analysis(INITIAL_CAPITAL, TIME_HORIZON, yield_rate, GROWTH_SENSITIVITIES)

    # Summary Statistics
    print("\nSummary Statistics")
    print("-" * 80)
    for scenario, stats in all_stats.items():
        print(f"\n{scenario}")
        print(f"Final Balance: {format_currency(stats['final_balance']):>30}")
        print(f"Total Growth: {format_currency(stats['total_growth']):>30}")
        print(f"Avg Annual Growth Rate: {stats['avg_annual_growth']:.2f}%")
    print("-" * 80)

    # Verification of ~$15 trillion at 65% growth (for 1% retained yield)
    target_scenario = "Scenario - Retained Yield 1.0%"
    final_balance = all_stats[target_scenario]["final_balance"]
    target = 15_000_000_000_000  # $15 trillion
    print(f"\nVerification Check:")
    print(f"Target Balance (~$15T) Reached: {final_balance >= target}")
    print(f"Actual Balance: {format_currency(final_balance)}")

if __name__ == "__main__":
    main()
