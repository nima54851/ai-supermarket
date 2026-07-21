#!/usr/bin/env python3
"""
PagerDuty Responder
Triggers acknowledgments, escalations, and resolutions via PagerDuty REST API v2.
"""
import os
import json
import httpx

PAGERDUTY_TOKEN = os.environ.get("PAGERDUTY_TOKEN")
PD_BASE = "https://api.pagerduty.com"

HEADERS = {
    "Authorization": f"Token token={PAGERDUTY_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/vnd.pagerduty+json;version=2",
}

def acknowledge_incident(incident_id: str, note: str = "Auto-acknowledged by AI agent"):
    """Acknowledge an incident."""
    payload = {
        "incident": {
            "type": "incident_reference",
            "status": "acknowledged",
            "incident_key": incident_id,
        },
        "深层通知": [{"type": "note", "content": note}],
    }
    with httpx.Client() as client:
        r = client.put(
            f"{PD_BASE}/incidents/{incident_id}",
            headers=HEADERS,
            json=payload,
        )
    return r.json()

def resolve_incident(incident_id: str, resolution: str = "Resolved by AI agent"):
    """Resolve an incident."""
    payload = {
        "incident": {
            "type": "incident_reference",
            "status": "resolved",
        }
    }
    with httpx.Client() as client:
        r = client.put(
            f"{PD_BASE}/incidents/{incident_id}",
            headers=HEADERS,
            json=payload,
        )
    return r.json()

def get_oncall_engineers():
    """List current on-call engineers."""
    with httpx.Client() as client:
        r = client.get(f"{PD_BASE}/oncalls", headers=HEADERS)
    return r.json()

if __name__ == "__main__":
    print("PagerDuty Responder — import and use as a module")
