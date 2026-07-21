#!/usr/bin/env python3
"""
SOC 2 Evidence Collector
Automatically collects evidence for SOC 2 Type II trust service criteria.
"""
import os
import json
import subprocess
from datetime import datetime, timedelta

def collect_aws_evidence() -> dict:
    """Collect AWS configuration evidence for CC6, CC7, CC9."""
    import boto3
    iam = boto3.client("iam")
    logs = boto3.client("cloudtrail")
    # Collect IAM users, roles, policies
    users = iam.list_users()["Users"]
    roles = iam.list_roles()["Roles"]
    policies = iam.list_policies(Scope="Local")["Policies"]
    return {
        "timestamp": datetime.now().isoformat(),
        "iam_users": [{"arn": u["Arn"], "create": u["CreateDate"].isoformat()} for u in users],
        "iam_roles": [{"arn": r["Arn"], "trusted": r.get("AssumeRolePolicyDocument", {}).get("Statement", [])} for r in roles],
        "policies_count": len(policies),
    }

def collect_github_evidence(org: str) -> dict:
    """Collect GitHub security evidence."""
    import httpx
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    with httpx.Client() as c:
        r = c.get(f"https://api.github.com/orgs/{org}/repos", headers=headers)
        repos = r.json()
    return {
        "timestamp": datetime.now().isoformat(),
        "repo_count": len(repos),
        "public_repos": sum(1 for r in repos if not r.get("private")),
        "private_repos": sum(1 for r in repos if r.get("private")),
    }

def collect_log_evidence(start: datetime, end: datetime) -> dict:
    """Collect log evidence for CC7 (availability) and CC6 (security)."""
    # Placeholder — integrate with Splunk, Elastic, or CloudWatch
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "events_collected": 0,
        "note": "Integrate with your log aggregator",
    }

def generate_evidence_package() -> str:
    """Generate a complete evidence package for SOC 2 audit."""
    pkg = {
        "generated_at": datetime.now().isoformat(),
        "aws_evidence": collect_aws_evidence(),
        "github_evidence": collect_github_evidence(os.environ.get("GITHUB_ORG", "myorg")),
        "note": "Add your log aggregator, database audit logs, and network flow logs",
    }
    return json.dumps(pkg, indent=2, default=str)

if __name__ == "__main__":
    print(generate_evidence_package())
