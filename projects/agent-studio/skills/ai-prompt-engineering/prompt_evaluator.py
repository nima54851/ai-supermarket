#!/usr/bin/env python3
"""
Prompt Evaluator — automated eval suite for prompt comparison
"""
import argparse, json, sys, os
from datetime import datetime

def score_response(response, criteria):
    """Simple heuristic scoring for demonstration."""
    score = 50  # baseline
    if len(response) > 50:
        score += 10
    if any(kw in response.lower() for kw in ["step", "because", "therefore", "thus"]):
        score += 15
    if "error" not in response.lower() or "no error" in response.lower():
        score += 10
    if response.count(".") > 2:
        score += 10
    return min(100, score)

def evaluate(prompt, test_cases):
    results = []
    for tc in test_cases:
        # Simulate evaluation — in production, call actual LLM
        score = score_response(f"Simulated response for: {tc.get('input', '')[:50]}", {})
        results.append({
            "test": tc.get("name", "unnamed"),
            "input": tc.get("input", ""),
            "expected": tc.get("expected", ""),
            "score": score,
            "pass": score >= 70
        })
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", nargs="+", required=True)
    parser.add_argument("--test-set", default="")
    args = parser.parse_args()
    
    test_cases = []
    if args.test_set and os.path.exists(args.test_set):
        with open(args.test_set) as f:
            test_cases = json.load(f)
    else:
        test_cases = [
            {"name": "basic", "input": "What is 2+2?", "expected": "4"},
            {"name": "code-review", "input": "Review: def foo(): pass", "expected": "No major issues"},
            {"name": "extraction", "input": "John is 30 and lives in NYC", "expected": '{"name":"John","age":"30","city":"NYC"}'},
        ]
    
    print(f"Evaluating {len(args.prompts)} prompt(s) against {len(test_cases)} test cases\n")
    for prompt_file in args.prompts:
        print(f"📝 {prompt_file}")
        results = evaluate(prompt_file, test_cases)
        avg = sum(r["score"] for r in results) / len(results)
        print(f"   Average score: {avg:.1f}/100")
        for r in results:
            status = "✅" if r["pass"] else "❌"
            print(f"   {status} {r['test']}: {r['score']}/100")
        print()

if __name__ == "__main__":
    main()
