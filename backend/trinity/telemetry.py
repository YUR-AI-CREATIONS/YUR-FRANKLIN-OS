"""Telemetry utilities for Trinity AI orchestrator.

Provides:
 - JSON line logger for orchestration events
 - Prometheus metrics (optional; no-op if package unavailable)
"""
import json
import time
from pathlib import Path

try:
    from prometheus_client import Counter, Histogram
except Exception:  # prometheus-client may be absent until installed
    Counter = Histogram = None

LOG_PATH = Path("trinity_telemetry.log")

if Counter and Histogram:
    ORCH_REQUESTS = Counter("trinity_requests_total", "Total Trinity engine requests")
    ORCH_FAILURES = Counter("trinity_failures_total", "Total Trinity engine failures", ["engine", "error"])
    ORCH_SUCCESSES = Counter("trinity_successes_total", "Total Trinity engine successes", ["engine"])
    ORCH_LATENCY = Histogram("trinity_latency_seconds", "Latency per engine invocation", ["engine"])
else:
    # Fallback lightweight stubs
    class _Stub:
        def labels(self, *_, **__): return self
        def inc(self, *_ , **__): pass
        def observe(self, *_ , **__): pass
    ORCH_REQUESTS = ORCH_FAILURES = ORCH_SUCCESSES = ORCH_LATENCY = _Stub()


def log_event(event: dict):
    """Append a JSON event to telemetry log (append-only)."""
    event.setdefault("ts", time.strftime("%Y-%m-%dT%H:%M:%S"))
    line = json.dumps(event, ensure_ascii=False) + "\n"
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line)


def record_success(engine: str, latency: float):
    ORCH_SUCCESSES.labels(engine=engine).inc()
    ORCH_LATENCY.labels(engine=engine).observe(latency)
    log_event({"type": "success", "engine": engine, "latency": latency})


def record_failure(engine: str, error: str):
    ORCH_FAILURES.labels(engine=engine, error=error.split("\n")[0][:120]).inc()
    log_event({"type": "failure", "engine": engine, "error": error})


def record_request(prompt: str):
    ORCH_REQUESTS.inc()
    log_event({"type": "request", "prompt": prompt[:300]})
