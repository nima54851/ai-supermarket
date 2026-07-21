#!/usr/bin/env python3
"""
Accessibility Reporter
Generates HTML/JSON accessibility reports with trend tracking.
"""
import os
import json
from datetime import datetime

def generate_html_report(violations: list, url: str, score: int = None) -> str:
    """Generate a styled HTML accessibility report."""
    severity_colors = {"critical": "#d32f2f", "serious": "#f57c00", "moderate": "#fbc02d", "minor": "#388e3c"}
    rows = ""
    for v in violations:
        color = severity_colors.get(v.get("impact", "minor"), "#9e9e9e")
        rows += f"""<tr>
            <td style="color:{color};font-weight:bold">{v.get('impact','minor').upper()}</td>
            <td>{v.get('id','')}</td>
            <td>{v.get('description','')[:100]}</td>
            <td><a href="{v.get('helpUrl','')}">WCAG Ref</a></td>
        </tr>"""
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>A11y Report: {url}</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,sans-serif;max-width:900px;margin:0 auto;padding:20px}}
h1{{color:#1a1a2e}}table{{width:100%;border-collapse:collapse;margin-top:20px}}
th{{background:#1a1a2e;color:#fff;padding:12px;text-align:left}}
td{{padding:10px;border-bottom:1px solid #eee}}
.score{{font-size:48px;font-weight:bold;color:{"#4caf50" if (score or 0)>=90 else "#ff9800" if (score or 0)>=70 else "#d32f2f"}}}
</style></head><body>
<h1>♿ Accessibility Report</h1>
<p><strong>URL:</strong> {url} | <strong>Scanned:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
<p><strong>Score:</strong> <span class="score">{score or "N/A"}</span></p>
<h2>Violations ({len(violations)})</h2>
<table><thead><tr><th>Severity</th><th>Rule ID</th><th>Description</th><th>Reference</th></tr></thead>
<tbody>{rows}</tbody></table></body></html>"""
    return html

def generate_json_report(violations: list, url: str, metadata: dict = None) -> dict:
    """Generate a JSON report."""
    return {
        "url": url,
        "scanned_at": datetime.now().isoformat(),
        "total_violations": len(violations),
        "by_severity": {
            s: len([v for v in violations if v.get("impact") == s])
            for s in ["critical", "serious", "moderate", "minor"]
        },
        "violations": violations,
        "metadata": metadata or {},
    }

if __name__ == "__main__":
    print("A11y Reporter — import and use as a module")
