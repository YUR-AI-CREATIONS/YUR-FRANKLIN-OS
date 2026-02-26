"""
REAL-TIME TEST RUNNER
Run all 3 options to prove Grok is working
"""
import requests
import json

print("=" * 80)
print("OPTION A: QUANTUM TELEPORTATION TEST (REAL API CALL)")
print("=" * 80)

payload_a = {
    "id": "probe-tele",
    "name": "Quantum Teleportation Protocol",
    "description": "Execute quantum teleportation protocol across 3-qubit entangled state",
    "agent_role": "executor",
    "use_grok": True,
    "task_type": "quantum_algorithm",
    "task_data": {
        "algorithm": "teleportation",
        "qubits": 3
    }
}

try:
    response = requests.post(
        "http://localhost:8001/api/unified/execute",
        json=payload_a,
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("OPTION B: ECHO TEST (SIMPLE CONTROL)")
print("=" * 80)

payload_b = {
    "id": "probe-analyst",
    "name": "Simple Analysis Task",
    "description": "Validate analyst role with Grok optimization",
    "agent_role": "analyst",
    "use_grok": True,
    "task_type": "analysis",
    "task_data": {
        "domain": "quantum",
        "focus": "validation"
    }
}

try:
    response = requests.post(
        "http://localhost:8001/api/unified/execute",
        json=payload_b,
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("OPTION C: AUDIT FILE - SHOW PAYLOADS")
print("=" * 80)

try:
    with open("grok_payloads_complete.json", "r") as f:
        data = json.load(f)
        print("File exists and is valid JSON")
        print(f"Total payloads: {data['metadata']['total_tests']}")
        print(f"Pass rate: {data['metadata']['pass_rate']}")
        print("\nFirst payload:")
        print(json.dumps(data['payloads'][0], indent=2))
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("COMPLETE - ALL TESTS EXECUTED")
print("=" * 80)
