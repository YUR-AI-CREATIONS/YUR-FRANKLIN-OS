"""
TransitionGuard: Zero-Trust Transition Protocol (ZTTP) middleware.

This module provides a composable guard that runs three gates before a payload
is allowed to move from Station N to Station N+1:
  - Gate A: Automated Smoke Test (async-friendly)
  - Gate B: Logic Verification (sync)
  - Gate C: Debug Certification (sync)

All gates are pluggable callables to keep the guard generic across stations.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional


# Gate function signatures
SmokeTestFn = Callable[[Dict[str, Any], Dict[str, Any]], Awaitable[bool]]
LogicCheckFn = Callable[[Dict[str, Any], Dict[str, Any]], bool]
DebugCheckFn = Callable[[Dict[str, Any], Dict[str, Any]], bool]


@dataclass
class TransitionDecision:
    station: str
    next_station: str
    allowed: bool
    reason: str
    retries: int = 0
    payload: Optional[Dict[str, Any]] = None


class TransitionGuard:
    """
    Zero-Trust inter-node guard. Each call enforces the tri-gate:
      1) Smoke test (async) - dry-run against next station schema
      2) Logic verification (sync) - domain invariants
      3) Debug certification (sync) - state/memory hygiene
    """

    def __init__(
        self,
        smoke_test: SmokeTestFn,
        logic_check: LogicCheckFn,
        debug_check: DebugCheckFn,
        max_retries: int = 1,
    ):
        self.smoke_test = smoke_test
        self.logic_check = logic_check
        self.debug_check = debug_check
        self.max_retries = max_retries

    async def guard(
        self,
        station: str,
        next_station: str,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> TransitionDecision:
        ctx = context or {}
        retries = 0

        while retries <= self.max_retries:
            # Gate A: Smoke test
            ok_smoke = await self.smoke_test(payload, ctx)
            if not ok_smoke:
                return TransitionDecision(
                    station, next_station, False, "smoke_test_failed", retries, payload
                )

            # Gate B: Logic verification
            ok_logic = self.logic_check(payload, ctx)
            if not ok_logic:
                return TransitionDecision(
                    station, next_station, False, "logic_verification_failed", retries, payload
                )

            # Gate C: Debug certification
            ok_debug = self.debug_check(payload, ctx)
            if ok_debug:
                return TransitionDecision(
                    station, next_station, True, "passed", retries, payload
                )

            # If debug check failed, attempt retry after cleanup
            retries += 1
            await self._attempt_cleanup(ctx)

        return TransitionDecision(
            station, next_station, False, "debug_certification_failed", retries, payload
        )

    @staticmethod
    async def _attempt_cleanup(context: Dict[str, Any]):
        # Placeholder cleanup; callers can extend via context hooks.
        gc_hook: Optional[Callable[[], Awaitable[None]]] = context.get("gc_hook")
        if gc_hook:
            await gc_hook()
        else:
            await asyncio.sleep(0)  # yield control
