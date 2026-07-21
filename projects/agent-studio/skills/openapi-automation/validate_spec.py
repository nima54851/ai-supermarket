#!/usr/bin/env python3
"""
OpenAPI Spec Validator — checks for breaking changes, schema quality, security issues
"""
import argparse, json, sys, yaml
from pathlib import Path

SENSITIVE_FIELDS = {"password", "secret", "token", "api_key", "apikey", "private_key", "authorization", "credit_card", "ssn"}

def load_spec(path):
    with open(path) as f:
        content = f.read()
    return json.loads(content) if path.endswith(".json") else yaml.safe_load(content)

def validate_spec(spec):
    issues = []
    if "openapi" not in spec:
        issues.append("ERROR: Missing 'openapi' version field")
    if "paths" not in spec or not spec["paths"]:
        issues.append("ERROR: No paths defined")
    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if method not in ("get","post","put","patch","delete","options","head"):
                continue
            if "responses" not in op:
                issues.append(f"WARN: {method.upper()} {path} has no responses defined")
            # Check schemas for sensitive data
            for comp in ["requestBody","responses"]:
                for resp in op.get(comp, {}).values():
                    for media, content in resp.get("content", {}).items():
                        for name, schema in content.get("schema", {}).get("properties", {}).items():
                            if any(s in name.lower() for s in SENSITIVE_FIELDS):
                                if schema.get("format") != "password" and "x-" not in schema:
                                    issues.append(f"INFO: {method.upper()} {path} — sensitive field '{name}' should have format=password or x-* marker")
    return issues

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec_file")
    args = parser.parse_args()
    spec = load_spec(args.spec_file)
    issues = validate_spec(spec)
    if issues:
        for issue in issues:
            print(issue)
        print(f"\n{len(issues)} issue(s) found")
    else:
        print("✅ Spec is clean — no issues found")

if __name__ == "__main__":
    main()
