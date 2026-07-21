#!/usr/bin/env python3
"""
Feature Flag Recommender
Suggests new feature flags from GitHub PR diffs using AI.
"""
import os
import json
import httpx
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_pr_diff(owner: str, repo: str, pr_number: int) -> str:
    """Fetch PR diff from GitHub."""
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3.diff"}
    with httpx.Client() as c:
        r = c.get(
            f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}",
            headers=headers,
        )
    return r.text

def suggest_flags(diff: str, context: str = "") -> list:
    """Use AI to suggest feature flags from a code diff."""
    prompt = f"""Analyze this code diff and suggest feature flags that should be created before merging.

Diff:
{diff[:8000]}

{context}

For each suggested flag, provide:
- flag_key: lowercase_with_underscores
- name: human-readable name
- targeting: who should see this (all users, beta users, specific %)
- kill_switch: should this have an emergency kill switch?
- rollout: recommended rollout strategy (gradual/immediate)

Return JSON array of flags.
Example: [{{"flag_key": "new_checkout_v2", "name": "New Checkout Flow", "targeting": "5% rollout", "kill_switch": true, "rollout": "gradual"}}]"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    data = json.loads(response.choices[0].message.content)
    return data.get("flags", data.get("suggested_flags", []))

if __name__ == "__main__":
    import sys
    flags = suggest_flags(sys.stdin.read())
    print(json.dumps(flags, indent=2))
