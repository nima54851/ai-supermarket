#!/usr/bin/env python3
"""
AI Incident Classifier
Classifies incoming alerts by severity and routes accordingly.
"""
import os
import json
import httpx
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are an expert SRE/incident response AI. 
Given an alert payload, classify it and return a JSON response:
{
  "severity": "P1|P2|P3|P4",
  "category": "performance|security|availability|data|other",
  "root_cause_candidates": ["..."],
  "suggested_fix": "...",
  "route_to": "ops|security|data|backend|frontend|null",
  "skip_escalation": true|false,
  "summary": "..."
}
Be conservative: default to higher severity when uncertain."""

def classify_alert(alert_payload: dict) -> dict:
    alert_text = json.dumps(alert_payload, indent=2)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Alert payload:\n{alert_text}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    return json.loads(response.choices[0].message.content)

def main():
    import sys
    payload = json.loads(sys.stdin.read())
    result = classify_alert(payload)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
