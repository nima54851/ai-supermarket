#!/usr/bin/env python3
"""
LaunchDarkly Feature Flag Manager
CRUD operations, targeting rules, and rollout management via LaunchDarkly API.
"""
import os
import json
import httpx
from datetime import datetime

LD_SDK_KEY = os.environ.get("LAUNCHDARKLY_SDK_KEY")
LD_API_KEY = os.environ.get("LAUNCHDARKLY_API_KEY")
LD_BASE = "https://app.launchdarkly.com/api/v2"

HEADERS = {"Authorization": LD_API_KEY, "Content-Type": "application/json"}

def create_flag(project_key: str, flag_key: str, name: str, description: str = "") -> dict:
    """Create a new feature flag."""
    payload = {
        "key": flag_key,
        "name": name,
        "description": description,
        "kind": "boolean",
        "variationType": "boolean",
        "variations": [{"value": True, "name": "True"}, {"value": False, "name": "False"}],
    }
    with httpx.Client() as c:
        r = c.post(
            f"{LD_BASE}/flags/{project_key}",
            headers=HEADERS,
            json=payload,
        )
    return r.json()

def update_targeting(flag_key: str, rules: list) -> dict:
    """Update targeting rules for a flag."""
    payload = {
        "patch": [{"op": "replace", "path": "/targets", "value": rules}]
    }
    with httpx.Client() as c:
        r = c.patch(
            f"{LD_BASE}/flags/default/{flag_key}/targeting",
            headers=HEADERS,
            json=payload,
        )
    return r.json()

def gradual_rollout(flag_key: str, start_pct: int, end_pct: int, steps: int = 5) -> list:
    """Generate a gradual rollout schedule."""
    schedule = []
    step_size = (end_pct - start_pct) / steps
    for i in range(steps + 1):
        pct = int(start_pct + i * step_size)
        schedule.append({"percentage": pct, "wait_minutes": 15})
    return schedule

def set_percentage_rollout(flag_key: str, percentage: int, rollout_id: str = None) -> dict:
    """Set a simple percentage rollout."""
    payload = {
        "targets": [],
        "rules": [{
            "rollout": {
                "variations": [
                    {"variation": 1, "weight": percentage * 10},  # LD uses 0-100000
                    {"variation": 0, "weight": (100 - percentage) * 10}
                ]
            },
            "clauses": [{"contextKind": "userKey", "op": "segmentMatch", "values": []}],
        }]
    }
    with httpx.Client() as c:
        r = c.patch(
            f"{LD_BASE}/flags/default/{flag_key}/targeting",
            headers=HEADERS,
            json=payload,
        )
    return r.json()

def toggle_flag(flag_key: str, enabled: bool) -> dict:
    """Enable or disable a feature flag (kill switch)."""
    payload = {
        "on": enabled,
        "variations": [{"value": enabled}, {"value": not enabled}],
    }
    with httpx.Client() as c:
        r = c.patch(
            f"{LD_BASE}/flags/default/{flag_key}",
            headers=HEADERS,
            json=payload,
        )
    return r.json()

if __name__ == "__main__":
    print("LaunchDarkly Manager — import and use as a module")
