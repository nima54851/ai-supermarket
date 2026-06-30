#!/usr/bin/env python3
"""
Secret Scanner — 扫描代码中的敏感信息泄露
Usage: python3 secret_scanner.py --path <dir> [--scan-git]
"""

import argparse
import os
import re
from pathlib import Path

# 检测规则
SECRET_PATTERNS = [
    ("AWS Key",               re.compile(r'AKIA[0-9A-Z]{16}')),
    ("GitHub Token",          re.compile(r'gh[pousr]_[A-Za-z0-9_]{36,}')),
    ("GitHub OAuth",          re.compile(r'gho_[A-Za-z0-9_]{36}')),
    ("Private Key Header",    re.compile(r'-----BEGIN.*PRIVATE KEY-----')),
    ("Generic API Key",       re.compile(r'["\'][aA][pP][iI]_?[kK][eE][yY]["\'].*?["\'][A-Za-z0-9]{20,}["\']', re.I)),
    ("Generic Secret",        re.compile(r'["\'][sS][eE][cC][rR][eE][tT]["\']\s*[=:]\s*["\'][^"\']{8,}["\']', re.I)),
    ("Password Assignment",   re.compile(r'["\']?password["\']?\s*[=:]\s*["\'][^"\']{3,}["\']', re.I)),
    ("Bearer Token",          re.compile(r'Bearer\s+[A-Za-z0-9_\-\.]+')),
    ("Basic Auth URL",        re.compile(r'https?://[^:]+:[^@]+@')),
    ("Slack Token",           re.compile(r'xox[baprs]-[0-9]{10,}')),
    ("OpenAI API Key",        re.compile(r'sk-[A-Za-z0-9]{48}')),
    ("JWT Token",             re.compile(r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*')),
    ("Database URL",          re.compile(r'(mysql|postgres|postgresql|mongodb)://[^@\s]+:[^@\s]+@', re.I)),
    ("SendGrid API Key",      re.compile(r'SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}')),
    ("Stripe Key",            re.compile(r'sk_live_[A-Za-z0-9]{24}')),
    ("Telegram Bot Token",    re.compile(r'\d{8,10}:[A-Za-z0-9_-]{35}')),
]

# 跳过目录
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', '.tox', 'dist', 'build', '.pytest_cache'}

# 跳过文件
SKIP_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.zip', '.tar', '.gz', '.mp4', '.mp3', '.wav', '.ttf', '.woff', '.woff2'}

def scan_file(filepath, scan_content=True):
    findings = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for lineno, line in enumerate(f, 1):
                if not scan_content and 'SECRET' in filepath.upper():
                    findings.append((lineno, 'hardcoded secret', filepath))
                    continue
                for name, pattern in SECRET_PATTERNS:
                    if pattern.search(line):
                        findings.append((lineno, name, line.strip()[:80]))
    except Exception:
        pass
    return findings

def scan_directory(root_path, scan_git=False):
    all_findings = []
    scanned_files = 0

    for dirpath, dirnames, filenames in os.walk(root_path):
        # 过滤跳过目录
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for filename in filenames:
            filepath = Path(dirpath) / filename

            # 跳过二进制文件
            if filepath.suffix.lower() in SKIP_EXTENSIONS:
                continue

            # 跳过 .git 内部（除非显式扫描）
            if '.git' in filepath.parts and not scan_git:
                continue

            findings = scan_file(filepath)
            if findings:
                for lineno, name, preview in findings:
                    all_findings.append((str(filepath), lineno, name, preview))
            scanned_files += 1

    return all_findings, scanned_files

def print_report(findings, scanned_files, root_path):
    print(f"\n{'='*60}")
    print(f"  🔒 Security Audit Report")
    print(f"{'='*60}")
    print(f"  Scanned:  {root_path}")
    print(f"  Files:    {scanned_files}")
    print(f"  Findings: {len(findings)}")
    print(f"{'='*60}")

    if not findings:
        print("  ✅ No secrets detected.")
    else:
        critical = [f for f in findings if any(k in f[2] for k in ['Key', 'Token', 'Password', 'Secret', 'JWT'])]
        warnings  = [f for f in findings if f not in critical]

        if critical:
            print(f"\n  🚨 CRITICAL ({len(critical)})")
            for filepath, lineno, name, preview in critical:
                print(f"    [{name}] {filepath}:{lineno}")
                print(f"      → {preview}")

        if warnings:
            print(f"\n  ⚠️  WARNING ({len(warnings)})")
            for filepath, lineno, name, preview in warnings[:10]:
                print(f"    [{name}] {filepath}:{lineno}")

    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Secret Scanner")
    parser.add_argument("--path", default=".", help="Directory to scan")
    parser.add_argument("--scan-git", action="store_true", help="Also scan .git directory")
    args = parser.parse_args()

    findings, scanned_files = scan_directory(args.path, scan_git=args.scan_git)
    print_report(findings, scanned_files, args.path)
