#!/usr/bin/env python3
"""
AI Model Cost Tracker.
Tracks token usage across multiple LLM providers and generates cost reports.
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

TRACKER_FILE = Path.home() / '.openclaw' / 'workspace' / 'projects' / 'agent-studio' / '.cost_tracker.jsonl'

MODEL_COSTS = {
    'gpt-4o':              {'input': 0.015, 'output': 0.060},
    'gpt-4o-mini':         {'input': 0.0004, 'output': 0.0016},
    'gpt-4-turbo':         {'input': 0.030, 'output': 0.090},
    'claude-opus-4-20250514': {'input': 0.015, 'output': 0.075},
    'claude-sonnet-4-20250514': {'input': 0.003, 'output': 0.015},
    'claude-3-5-sonnet':   {'input': 0.003, 'output': 0.015},
    'gemini-pro':           {'input': 0.005, 'output': 0.015},
    'gemini-flash':         {'input': 0.00035, 'output': 0.00035},
}

def load_entries():
    entries = []
    if TRACKER_FILE.exists():
        with open(TRACKER_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    return entries

def save_entry(entry):
    TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TRACKER_FILE, 'a') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

def log_request(model: str, input_tokens: int, output_tokens: int, cost_usd: float = None):
    if cost_usd is None:
        costs = MODEL_COSTS.get(model, {'input': 0.01, 'output': 0.03})
        cost_usd = (input_tokens / 1000 * costs['input']) + (output_tokens / 1000 * costs['output'])

    entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'model': model,
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'total_tokens': input_tokens + output_tokens,
        'cost_usd': round(cost_usd, 6),
    }
    save_entry(entry)
    print(f"✅ Logged: {model} | {input_tokens}+{output_tokens} tokens | ${cost_usd:.4f}")
    return entry

def generate_report(days: int = 7):
    entries = load_entries()
    cutoff = datetime.now(timezone.utc).timestamp() - (days * 86400)
    recent = [e for e in entries if datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00')).timestamp() > cutoff]

    if not recent:
        print(f"No data in the last {days} days.")
        return

    total_cost = sum(e['cost_usd'] for e in recent)
    total_tokens = sum(e['total_tokens'] for e in recent)
    by_model = {}
    for e in recent:
        m = e['model']
        by_model.setdefault(m, {'cost': 0, 'tokens': 0, 'calls': 0})
        by_model[m]['cost'] += e['cost_usd']
        by_model[m]['tokens'] += e['total_tokens']
        by_model[m]['calls'] += 1

    print(f"\n📊 Cost Report — Last {days} days")
    print(f"{'='*50}")
    print(f"Total Requests: {len(recent)}")
    print(f"Total Tokens:   {total_tokens:,}")
    print(f"Total Cost:     ${total_cost:.4f}")
    print(f"\nBy Model:")
    for model, stats in sorted(by_model.items(), key=lambda x: -x[1]['cost']):
        print(f"  {model}: ${stats['cost']:.4f} | {stats['tokens']:,} tokens | {stats['calls']} calls")

def main():
    parser = argparse.ArgumentParser(description='AI Model Cost Tracker')
    sub = parser.add_subparsers(dest='cmd')

    log_p = sub.add_parser('log', help='Log a request')
    log_p.add_argument('--model', required=True)
    log_p.add_argument('--input-tokens', type=int, required=True)
    log_p.add_argument('--output-tokens', type=int, required=True)
    log_p.add_argument('--cost', type=float, help='Override cost (USD)')

    report_p = sub.add_parser('report', help='Generate cost report')
    report_p.add_argument('--days', type=int, default=7)

    args = parser.parse_args()

    if args.cmd == 'log':
        log_request(args.model, args.input_tokens, args.output_tokens, args.cost)
    elif args.cmd == 'report':
        generate_report(args.days)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
