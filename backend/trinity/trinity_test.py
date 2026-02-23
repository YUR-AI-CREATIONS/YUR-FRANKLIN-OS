"""Lightweight integration harness using unified orchestrator.

Runs a small prompt suite through `trinity_engine` to verify routing and
basic end-to-end behavior without duplicating client setup logic.
"""
from trinity_orchestrator_unified import trinity_engine

PROMPTS = [
    "Generate a concise image concept: a serene AI-operated greenhouse at dawn.",
    "Analyze the benefits of multi-model AI routing in 3 bullet points.",
    "Explain the philosophical implications of delegated cognition in 25 words."
]

def run_suite():
    for p in PROMPTS:
        print("\n=== Prompt ===\n" + p)
        try:
            res = trinity_engine(p)
            print(f"Source: {res['engine']} | Latency: {res['latency']}s")
            print(res['text'][:600])
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run_suite()

