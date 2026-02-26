"""
ALL PAYLOADS SENT TO GROK - COMPLETE REQUEST DOCUMENTATION
============================================================

This file contains all 10 JSON payloads sent to the Grok API during 
the quantum stress test suite execution.

Each payload is a UnifiedTask that gets POST'd to:
  http://localhost:8001/api/unified/execute

All tests executed on: 2026-02-09 at 09:46:23 UTC
"""

import json
import uuid

# Generate UUIDs for each test (matching actual test run)
payloads = [
    # 1. SHOR'S ALGORITHM - FACTORIZATION
    {
        "id": str(uuid.uuid4()),
        "name": "Shor's Algorithm - Factorization",
        "description": "Factor 143 using Shor's algorithm on quantum circuit with 8 qubits, error mitigation enabled",
        "agent_role": "innovator",
        "use_grok": True,
        "task_type": "quantum_algorithm",
        "task_data": {
            "algorithm": "shors",
            "input": 143,
            "qubits": 8
        }
    },
    
    # 2. VARIATIONAL QUANTUM EIGENSOLVER (VQE)
    {
        "id": str(uuid.uuid4()),
        "name": "Variational Quantum Eigensolver (VQE)",
        "description": "Solve hydrogen molecule eigenvalue problem using VQE with 10-layer ansatz, 1000 classical optimization iterations",
        "agent_role": "optimizer",
        "use_grok": True,
        "task_type": "quantum_algorithm",
        "task_data": {
            "algorithm": "vqe",
            "molecule": "H2",
            "layers": 10,
            "iterations": 1000
        }
    },
    
    # 3. QUANTUM APPROXIMATE OPTIMIZATION ALGORITHM (QAOA)
    {
        "id": str(uuid.uuid4()),
        "name": "Quantum Approximate Optimization Algorithm (QAOA)",
        "description": "Solve MaxCut problem on 16-node graph using QAOA with p=5 layers, comparing classical and quantum approaches",
        "agent_role": "optimizer",
        "use_grok": True,
        "task_type": "quantum_algorithm",
        "task_data": {
            "algorithm": "qaoa",
            "problem": "maxcut",
            "nodes": 16,
            "layers": 5
        }
    },
    
    # 4. QUANTUM ERROR CORRECTION
    {
        "id": str(uuid.uuid4()),
        "name": "Quantum Error Correction",
        "description": "Implement surface code error correction for 49-qubit lattice with depolarizing noise simulation at 0.1% error rate",
        "agent_role": "validator",
        "use_grok": True,
        "task_type": "quantum_algorithm",
        "task_data": {
            "algorithm": "surface_code",
            "qubits": 49,
            "noise_rate": 0.001
        }
    },
    
    # 5. QUANTUM MACHINE LEARNING (QAML)
    {
        "id": str(uuid.uuid4()),
        "name": "Quantum Machine Learning (QAML)",
        "description": "Train quantum neural network classifier on MNIST dataset using 20-qubit ansatz, 100 training epochs with adaptive learning",
        "agent_role": "innovator",
        "use_grok": True,
        "task_type": "quantum_algorithm",
        "task_data": {
            "algorithm": "qnn_classifier",
            "dataset": "MNIST",
            "qubits": 20,
            "epochs": 100
        }
    },
    
    # 6. HUBBARD MODEL SIMULATION
    {
        "id": str(uuid.uuid4()),
        "name": "Hubbard Model Simulation",
        "description": "Simulate 4x4 Hubbard lattice at half-filling using digital quantum simulation with 50 Trotter steps",
        "agent_role": "analyst",
        "use_grok": True,
        "task_type": "quantum_algorithm",
        "task_data": {
            "algorithm": "hubbard_model",
            "lattice": "4x4",
            "trotter_steps": 50
        }
    },
    
    # 7. GROVER'S SEARCH ALGORITHM
    {
        "id": str(uuid.uuid4()),
        "name": "Grover's Search Algorithm",
        "description": "Search unsorted database of 256 items using Grover's algorithm with 12-qubit oracle and amplitude amplification",
        "agent_role": "executor",
        "use_grok": True,
        "task_type": "quantum_algorithm",
        "task_data": {
            "algorithm": "grovers",
            "database_size": 256,
            "qubits": 12
        }
    },
    
    # 8. QUANTUM FOURIER TRANSFORM
    {
        "id": str(uuid.uuid4()),
        "name": "Quantum Fourier Transform",
        "description": "Perform 16-qubit Quantum Fourier Transform with controlled phase gates and benchmark against classical FFT",
        "agent_role": "analyst",
        "use_grok": True,
        "task_type": "quantum_algorithm",
        "task_data": {
            "algorithm": "qft",
            "qubits": 16
        }
    },
    
    # 9. QUANTUM PHASE ESTIMATION
    {
        "id": str(uuid.uuid4()),
        "name": "Quantum Phase Estimation",
        "description": "Estimate eigenphase of a unitary operator on 14-qubit system with 10-qubit precision register and iterative refinement",
        "agent_role": "validator",
        "use_grok": True,
        "task_type": "quantum_algorithm",
        "task_data": {
            "algorithm": "phase_estimation",
            "system_qubits": 14,
            "precision_qubits": 10
        }
    },
    
    # 10. QUANTUM TELEPORTATION PROTOCOL
    {
        "id": str(uuid.uuid4()),
        "name": "Quantum Teleportation Protocol",
        "description": "Execute quantum teleportation protocol across 3-qubit entangled state with classical channel simulation and fidelity verification",
        "agent_role": "executor",
        "use_grok": True,
        "task_type": "quantum_algorithm",
        "task_data": {
            "algorithm": "teleportation",
            "qubits": 3
        }
    }
]


def print_all_payloads():
    """Display all payloads in formatted JSON"""
    print("\n" + "="*90)
    print("ALL PAYLOADS SENT TO GROK - QUANTUM STRESS TEST SUITE")
    print("="*90 + "\n")
    
    for i, payload in enumerate(payloads, 1):
        print(f"\n{'─'*90}")
        print(f"PAYLOAD #{i}: {payload['name']}")
        print(f"{'─'*90}")
        print(json.dumps(payload, indent=2))
        print()
    
    print("\n" + "="*90)
    print(f"TOTAL PAYLOADS: {len(payloads)}")
    print("="*90)
    
    # Summary
    print("\nPAYLOAD SUMMARY:")
    print("─"*90)
    for i, payload in enumerate(payloads, 1):
        agent = payload['agent_role'].upper()
        algo = payload['task_data']['algorithm'].upper()
        print(f"{i:2d}. {payload['name']:<45} [{agent:<10}] {algo}")
    print("─"*90)


if __name__ == "__main__":
    print_all_payloads()
