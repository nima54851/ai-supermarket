#!/usr/bin/env python3
"""
Pytest Runner with Coverage Tracking
Runs pytest with coverage, posts results to n8n or GitHub Actions.
"""
import subprocess
import json
import os
import sys
from datetime import datetime

COVERAGE_WARN = float(os.getenv("COVERAGE_WARN", "80"))
COVERAGE_FAIL = float(os.getenv("COVERAGE_FAIL", "70"))

def run_pytest():
    print(f"[Pytest] Running tests at {datetime.now().isoformat()}")
    
    result = subprocess.run(
        ["pytest", "--cov=.", "--cov-report=json:/tmp/coverage.json", "-v", "--tb=short"],
        capture_output=True,
        text=True
    )
    
    # Parse coverage
    try:
        with open("/tmp/coverage.json") as f:
            coverage = json.load(f)
        total = coverage["totals"]
        pct = total["percent_covered"]
    except Exception:
        pct = 0.0
    
    output = {
        "exit_code": result.returncode,
        "coverage_percent": round(pct, 2),
        "tests_passed": "passed" in result.stdout.lower(),
        "timestamp": datetime.now().isoformat(),
        "stdout": result.stdout[-2000:],
        "stderr": result.stderr[-1000:]
    }
    
    if pct < COVERAGE_FAIL:
        print(f"❌ FAIL: Coverage {pct}% < {COVERAGE_FAIL}% threshold")
        output["status"] = "fail"
    elif pct < COVERAGE_WARN:
        print(f"⚠️  WARN: Coverage {pct}% < {COVERAGE_WARN}% threshold")
        output["status"] = "warn"
    else:
        print(f"✅ OK: Coverage {pct}%")
        output["status"] = "pass"
    
    print(json.dumps(output, indent=2))
    return output

if __name__ == "__main__":
    run_pytest()
