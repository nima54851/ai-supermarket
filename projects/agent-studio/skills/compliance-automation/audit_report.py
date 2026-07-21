#!/usr/bin/env python3
"""
AI Audit Report Generator
Generates audit-ready compliance reports from evidence packages.
"""
import os
import json
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_audit_report(evidence: dict, framework: str) -> str:
    """Generate a structured audit report from evidence."""
    prompt = f"""Generate an audit-ready compliance report for {framework.upper()}.

Evidence package:
{json.dumps(evidence, indent=2, default=str)}

Include sections:
1. Executive Summary (compliance status, overall score)
2. Scope and Methodology
3. Control Assessment (per control: status, evidence, findings)
4. Gap Summary
5. Recommendations
6. Evidence Inventory

Format as Markdown. Be precise and audit-ready."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

def generate_executive_summary(gap_analysis: dict) -> dict:
    """Generate a high-level executive summary."""
    score = gap_analysis.get("overall_score", "0%")
    gaps = gap_analysis.get("priority_gaps", [])
    prompt = f"""Write a one-page executive summary for a compliance audit.
Overall compliance score: {score}
Priority gaps: {', '.join(gaps)}

Return JSON:
{{"summary_paragraph": "...", "risk_rating": "low|medium|high|critical", "key_findings": [...], "estimated_remediation_time": "..."}}"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)

if __name__ == "__main__":
    import sys
    data = json.loads(sys.stdin.read())
    report = generate_audit_report(data["evidence"], data.get("framework", "gdpr"))
    print(report)
