#!/usr/bin/env python3
"""
circuit_breaker.py — 熔断器实现
线程安全，支持 Closed / Open / Half-Open 三态
"""

import time
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable, TypeVar, Any

T = TypeVar("T")


@dataclass
class CircuitState:
    status: str = "closed"  # closed | open | half-open
    failures: int = 0
    successes: int = 0
    last_failure: float = 0.0
    last_success: float = 0.0
    half_open_attempts: int = 0


class CircuitBreaker:
    """
    熔断器：保护系统免受级联故障

    Closed → 正常调用，失败累计
             达到 failure_threshold → Open（熔断打开）
    Open → 直接拒绝，等待 recovery_timeout 后进入 Half-Open
    Half-Open → 允许一次探测请求
                成功 → Closed（恢复）
                失败 → Open（重新熔断）
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3,
        name: str = "default",
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.name = name
        self._state = CircuitState()
        self._lock = threading.RLock()

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            with self._lock:
                state = self._state

                if state.status == "closed":
                    pass  # proceed

                elif state.status == "open":
                    elapsed = time.time() - state.last_failure
                    if elapsed >= self.recovery_timeout:
                        self._transition("half-open")
                    else:
                        raise CircuitOpen(
                            f"Circuit [{self.name}] is OPEN. "
                            f"Retry in {self.recovery_timeout - elapsed:.1f}s"
                        )

                elif state.status == "half-open":
                    if state.half_open_attempts >= self.half_open_max_calls:
                        raise CircuitOpen(
                            f"Circuit [{self.name}] is HALF-OPEN. "
                            f"All {self.half_open_max_calls} probe attempts exhausted."
                        )
                    state.half_open_attempts += 1

            # Execute outside lock
            try:
                result = func(*args, **kwargs)
                self._record_success()
                return result
            except Exception as e:
                self._record_failure()
                raise

        wrapper._circuit_breaker = self  # allow inspection
        return wrapper

    def _transition(self, new_status: str):
        self._state.status = new_status
        if new_status == "closed":
            self._state.failures = 0
            self._state.half_open_attempts = 0
        elif new_status == "half-open":
            self._state.half_open_attempts = 0

    def _record_success(self):
        with self._lock:
            self._state.successes += 1
            self._state.last_success = time.time()
            if self._state.status == "half-open":
                self._transition("closed")

    def _record_failure(self):
        with self._lock:
            self._state.failures += 1
            self._state.last_failure = time.time()
            if self._state.status == "half-open":
                self._transition("open")
            elif self._state.status == "closed" and self._state.failures >= self.failure_threshold:
                self._transition("open")

    @property
    def state(self) -> dict:
        with self._lock:
            return {
                "name": self.name,
                "status": self._state.status,
                "failures": self._state.failures,
                "successes": self._state.successes,
                "failure_threshold": self.failure_threshold,
                "recovery_timeout_s": self.recovery_timeout,
            }


class CircuitOpen(Exception):
    """熔断器打开时抛出的异常"""
    pass


# Demo
if __name__ == "__main__":
    import random

    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=5.0, name="demo")

    @cb
    def unreliable_api():
        if random.random() < 0.6:
            raise RuntimeError("API timeout")
        return {"result": "success"}

    print("Circuit Breaker Demo")
    print("-" * 40)

    for i in range(10):
        try:
            result = unreliable_api()
            print(f"  Call {i+1}: ✅ {result}")
        except CircuitOpen as e:
            print(f"  Call {i+1}: 🔴 CIRCUIT OPEN → {e}")
            break
        except RuntimeError as e:
            print(f"  Call {i+1}: ⚠️  API Error → {e}")
        time.sleep(0.5)

    print(f"\n  Circuit state: {cb.state}")
