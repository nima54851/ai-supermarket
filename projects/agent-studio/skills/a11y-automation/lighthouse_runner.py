#!/usr/bin/env python3
"""
Lighthouse CI Accessibility Runner
Runs Lighthouse accessibility audits and tracks trends.
"""
import os
import json
import subprocess
from datetime import datetime

def run_lighthouse(url: str, output_path: str = "/tmp/lh-report.json") -> dict:
    """Run Lighthouse CI accessibility audit."""
    cmd = [
        "lhci", "autorun",
        "--config=.lighthouserc.json",
        f"--url={url}",
        f"--output=json",
        f"--output-path={output_path}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        with open(output_path) as f:
            return json.load(f)
    except Exception:
        return {"error": result.stderr or result.stdout, "returncode": result.returncode}

def parse_a11y_score(lh_report: dict) -> dict:
    """Extract accessibility score from Lighthouse report."""
    categories = lh_report.get("categories", {})
    a11y = categories.get("accessibility", {})
    return {
        "score": int(a11y.get("score", 0) * 100),
        "title": a11y.get("title", "Accessibility"),
        "description": a11y.get("description", ""),
        "audits": [a.get("id") for a in a11y.get("auditRefs", []) if a.get("weight", 0) > 0],
    }

def compare_scores(current: dict, baseline: dict) -> dict:
    """Compare current accessibility score with baseline."""
    diff = current["score"] - baseline["score"]
    return {
        "current": current["score"],
        "baseline": baseline["score"],
        "delta": diff,
        "improved": diff > 0,
        "regression": diff < 0,
    }

if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    report = run_lighthouse(url)
    print(json.dumps(report, indent=2, default=str))
