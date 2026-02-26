"""
Capture raw Grok API response for proof of execution
"""
import asyncio
import json
import uuid
import httpx

async def test_single_algorithm():
    """Execute one quantum algorithm and capture full response"""
    payload = {
        "id": str(uuid.uuid4()),
        "name": "Shor's Algorithm - Factorization",
        "description": "Factor 143 using Shor's algorithm on quantum circuit with 8 qubits, error mitigation enabled",
        "agent_role": "innovator",
        "use_grok": True,
        "task_type": "quantum_algorithm",
        "task_data": {"algorithm": "shors", "input": 143, "qubits": 8}
    }
    
    async with httpx.AsyncClient(timeout=30) as client:
        print("="*80)
        print("SENDING REQUEST TO GROK:")
        print("="*80)
        print(json.dumps(payload, indent=2))
        print()
        
        response = await client.post("http://localhost:8001/api/unified/execute", json=payload)
        
        print("="*80)
        print(f"GROK RESPONSE STATUS: {response.status_code}")
        print("="*80)
        print("RAW GROK RESPONSE DATA:")
        print("="*80)
        
        try:
            data = response.json()
            print(json.dumps(data, indent=2))
        except:
            print(response.text)
        
        print()
        print("="*80)
        print("RESPONSE ANALYSIS:")
        print("="*80)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {data.get('status')}")
            print(f"✓ Task ID: {data.get('task_id')}")
            print(f"✓ Agent Role: {data.get('agent_role')}")
            print(f"✓ Execution Time: {data.get('execution_time_ms')}ms")
            print(f"✓ Result: {json.dumps(data.get('result'), indent=2)}")
            if data.get('steps'):
                print(f"✓ Processing Steps: {len(data.get('steps'))} steps executed")
                for i, step in enumerate(data.get('steps', [])[:3], 1):
                    print(f"   Step {i}: {step.get('description')}")
        else:
            print(f"✗ Error: {response.status_code}")

if __name__ == "__main__":
    asyncio.run(test_single_algorithm())
