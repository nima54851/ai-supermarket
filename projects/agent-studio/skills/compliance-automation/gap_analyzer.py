#!/usr/bin/env python3
"""
Compliance Gap Analyzer
Compares current security posture against a compliance framework and generates a gap report.
"""
import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

FRAMEWORKS = {
    "gdpr": ["Art 15-22 rights", "DPO appointment", "DPA agreements", "Breach notification (72h)", "Privacy by design", "Consent management"],
    "soc2": ["CC1.1-CC1.4 (Control Environment)", "CC2.1-CC2.2 (Communication)", "CC3.1-CC3.4 (Risk Assessment)", "CC4.1-CC4.2 (Monitoring)", "CC5.1-CC5.3 (Controls)", "CC6.1-CC6.8 (Security)", "CC7.1-CC7.5 (Availability)", "CC8.1 (Confidentiality)"],
    "hipaa": ["Administrative safeguards", "Physical safeguards", "Technical safeguards", "Breach notification", "BAA agreements", "Risk analysis (164.308(a)(1)(ii)(A))"],
}

def analyze_gaps(current_controls: dict, framework: str = "gdpr") -> dict:
    """Analyze gaps between current controls and a compliance framework."""
    required = FRAMEWORKS.get(framework, FRAMEWORKS["gdpr"])
    controls_str = json.dumps(current_controls, indent=2)
    required_str = json.dumps(required, indent=2)
    prompt = f"""Compare current controls against the {framework.upper()} framework requirements.

Required controls ({framework.upper()}):
{required_str}

Current controls:
{controls_str}

Return a structured gap analysis JSON:
{{"framework": "...", "total_controls": N, "met": [...], "partial": [...], "missing": [...], "overall_score": "N%", "priority_gaps": [...]}}"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)

if __name__ == "__main__":
    import sys
    data = json.loads(sys.stdin.read())
    result = analyze_gaps(data.get("controls", {}), data.get("framework", "gdpr"))
    print(json.dumps(result, indent=2))
