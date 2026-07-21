#!/usr/bin/env python3
"""
Auto Post-mortem Generator
Generates structured post-mortem reports from incident data.
"""
import os
import json
import httpx
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

PROMPT_TEMPLATE = """Generate a structured post-mortem report for the following incident.

Incident Summary:
- Title: {title}
- Severity: {severity}
- Start Time: {start_time}
- End Time: {end_time}
- Duration: {duration}

Timeline (chronological):
{timeline}

Root Cause: {root_cause}

Resolution: {resolution}

Return JSON:
{{
  "title": "...",
  "severity": "...",
  "impact": "...",
  "timeline": [...],
  "root_cause": "...",
  "resolution": "...",
  "lessons_learned": ["...", "..."],
  "action_items": [
    {{"task": "...", "priority": "high|medium|low", "owner": "..."}}
  ],
  "metrics": {{"mttd": "...", "mttr": "..."}}
}}"""

def generate_postmortem(incident_data: dict) -> dict:
    timeline = "\n".join([f"- {t}" for t in incident_data.get("timeline", [])])
    prompt = PROMPT_TEMPLATE.format(
        title=incident_data.get("title", "Unknown"),
        severity=incident_data.get("severity", "P2"),
        start_time=incident_data.get("start_time", "Unknown"),
        end_time=incident_data.get("end_time", datetime.now().isoformat()),
        duration=incident_data.get("duration", "Unknown"),
        timeline=timeline or "No timeline available",
        root_cause=incident_data.get("root_cause", "Under investigation"),
        resolution=incident_data.get("resolution", "Fixed"),
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)

if __name__ == "__main__":
    import sys
    data = json.loads(sys.stdin.read())
    report = generate_postmortem(data)
    print(json.dumps(report, indent=2))
