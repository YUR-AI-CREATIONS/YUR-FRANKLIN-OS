import json

with open('test-results/quantum_stress_test_report.json') as f:
    data = json.load(f)
    
print("\n" + "="*80)
print("QUANTUM STRESS TEST RESULTS - GROK TRINITY SYSTEM")
print("="*80)

summary = data['summary']
print(f"\n📊 SUMMARY:")
print(f"   Total Tests:      {summary['total_tests']}")
print(f"   Passed:           {summary['passed']} ✓")
print(f"   Failed:           {summary['failed']} ✗")
print(f"   Timeouts:         {summary['timeout']} ⏱")
print(f"   Pass Rate:        {summary['pass_rate']}")
print(f"   Total Time:       {summary['total_execution_time_seconds']:.2f}s")

print(f"\n🧪 INDIVIDUAL TESTS:")
print("-"*80)

for i, result in enumerate(data['results'], 1):
    status_icon = "✓" if result['status'] == "PASS" else "✗"
    exec_time = result.get('execution_time_ms', 0)
    print(f"{i:2}. {status_icon} {result['test']:<42} {exec_time:7.2f}ms")

print("-"*80)
print("="*80 + "\n")
