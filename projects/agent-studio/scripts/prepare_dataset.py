#!/usr/bin/env python3
"""
Fine-tuning dataset preparation script.
Cleans, deduplicates, and formats data for LLM fine-tuning.
Supports: JSONL, CSV, plain text → OpenAI fine-tuning format.
"""
import argparse
import json
import re
import sys
from pathlib import Path

def clean_text(text: str) -> str:
    """Remove noise, normalize whitespace."""
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def load_jsonl(path: Path):
    """Load JSONL file."""
    items = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items

def load_csv(path: Path, prompt_col: str, completion_col: str):
    """Load CSV and convert to JSONL format."""
    import csv
    items = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append({
                'messages': [
                    {'role': 'system', 'content': 'You are a helpful AI assistant.'},
                    {'role': 'user', 'content': clean_text(row.get(prompt_col, ''))},
                    {'role': 'assistant', 'content': clean_text(row.get(completion_col, ''))}
                ]
            })
    return items

def deduplicate(items: list) -> list:
    """Remove duplicate prompt-completion pairs."""
    seen = set()
    unique = []
    for item in items:
        key = json.dumps(item.get('messages') or item, ensure_ascii=False)
        if key not in seen:
            seen.add(key)
            unique.append(item)
    print(f"  Deduplicated: {len(items)} → {len(unique)} ({len(items) - len(unique)} removed)")
    return unique

def validate_item(item: dict) -> bool:
    """Validate fine-tuning format."""
    messages = item.get('messages', [])
    if not messages:
        return False
    if len(messages) < 2:
        return False
    if messages[0].get('role') not in ('system', 'user'):
        return False
    if messages[-1].get('role') != 'assistant':
        return False
    for msg in messages:
        if not msg.get('content'):
            return False
    return True

def main():
    parser = argparse.ArgumentParser(description='Prepare fine-tuning datasets')
    parser.add_argument('--input', '-i', required=True, help='Input file (JSONL or CSV)')
    parser.add_argument('--output', '-o', required=True, help='Output JSONL file')
    parser.add_argument('--deduplicate', '-d', action='store_true', help='Remove duplicate entries')
    parser.add_argument('--min-len', type=int, default=10, help='Minimum completion length')
    parser.add_argument('--format', choices=['openai', 'chatml'], default='openai', help='Output format')
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    print(f"Loading: {input_path}")
    if input_path.suffix == '.jsonl':
        items = load_jsonl(input_path)
    elif input_path.suffix == '.csv':
        items = load_csv(input_path, prompt_col='prompt', completion_col='completion')
    else:
        print(f"Unsupported format: {input_path.suffix}")
        sys.exit(1)

    print(f"Loaded {len(items)} items")

    if args.deduplicate:
        items = deduplicate(items)

    # Filter valid items
    valid = [item for item in items if validate_item(item)]
    print(f"Valid items: {len(valid)}/{len(items)}")

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in valid:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"✅ Written: {output_path} ({len(valid)} items)")

if __name__ == '__main__':
    main()
