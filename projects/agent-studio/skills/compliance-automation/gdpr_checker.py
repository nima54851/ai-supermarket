#!/usr/bin/env python3
"""
GDPR Compliance Checker
Checks data processing activities for GDPR Article 15-22 compliance.
"""
import os
import json
import httpx
from openai import OpenAI
from datetime import datetime, timedelta

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

GDPR_ARTICLES = {
    "Art_15": "Right of access",
    "Art_16": "Right to rectification",
    "Art_17": "Right to erasure (RTBF)",
    "Art_18": "Right to restriction",
    "Art_19": "Right to notification",
    "Art_20": "Right to data portability",
    "Art_21": "Right to object",
    "Art_22": "Automated decision-making",
}

def check_right_of_access(data_systems: list) -> dict:
    """Check if data subjects can exercise right of access."""
    prompt = f"""Audit the following data systems for GDPR Article 15 (Right of Access) compliance.
Systems: {json.dumps(data_systems, indent=2)}
Return JSON:
{{"compliant": true|false, "gaps": [...], "evidence_needed": [...], "risk_level": "low|medium|high"}}"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)

def check_data_breach_notification(logs: str) -> dict:
    """Scan logs for potential data breaches requiring 72h notification."""
    prompt = f"""Analyze these system logs for potential GDPR data breaches.
Look for: unauthorized access, data exfiltration, credential misuse, database anomalies.
Return a structured report with: breach_detected (bool), evidence_snippets, notification_deadline, affected_data_categories.
\n\n{logs[:3000]}"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)

def generate_data_processing_agreement(entity_a: str, entity_b: str, data_types: list) -> str:
    """Generate a DPA (Data Processing Agreement) clause using AI."""
    prompt = f"""Write a GDPR-compliant Data Processing Agreement (DPA) clause between {entity_a} (Data Controller) and {entity_b} (Data Processor).
Data types processed: {', '.join(data_types)}
Include: processing scope, security measures, sub-processor restrictions, breach notification obligations, data subject rights assistance."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    print("GDPR Checker — import and use as a module")
