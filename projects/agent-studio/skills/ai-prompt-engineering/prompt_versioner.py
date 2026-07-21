#!/usr/bin/env python3
"""
Prompt Versioner — git-like version control for prompts
Stores versions in .prompt_versions/ directory
"""
import argparse, os, sys, hashlib
from datetime import datetime
from pathlib import Path

VERSION_DIR = Path(".prompt_versions")

def init():
    VERSION_DIR.mkdir(exist_ok=True)
    print(f"Initialized prompt version store at {VERSION_DIR}")

def save(name, content):
    VERSION_DIR.mkdir(exist_ok=True)
    version_file = VERSION_DIR / f"{name}.md"
    if version_file.exists():
        # Compute previous hash
        with open(version_file) as f:
            prev_content = f.read()
        prev_hash = hashlib.sha256(prev_content.encode()).hexdigest()[:8]
    else:
        prev_hash = "0000000"
    
    hash_val = hashlib.sha256(content.encode()).hexdigest()[:8]
    meta_file = VERSION_DIR / f"{name}.meta"
    meta = {}
    if meta_file.exists():
        meta = dict(line.strip().split("=") for line in open(meta_file) if "=" in line)
    
    version_num = meta.get("version", "0")
    new_version = int(version_num) + 1
    
    with open(version_file, "w") as f:
        f.write(content)
    
    with open(meta_file, "w") as f:
        f.write(f"name={name}\nversion={new_version}\nprev_hash={hash_val}\ncurrent_hash={hash_val}\nupdated={datetime.now().isoformat()}\n")
    
    print(f"✅ Saved {name} v{new_version} (hash: {hash_val})")
    return new_version

def log(name):
    meta_file = VERSION_DIR / f"{name}.meta"
    if not meta_file.exists():
        print(f"No version history for '{name}'")
        return
    meta = dict(line.strip().split("=") for line in open(meta_file) if "=" in line)
    print(f"Prompt: {name}")
    print(f"Current version: v{meta.get('version','?')}")
    print(f"Last updated: {meta.get('updated','?')}")
    print(f"Hash: {meta.get('current_hash','?')}")

def diff(name):
    print(f"Diff for {name} — (simplified, shows current content)")
    version_file = VERSION_DIR / f"{name}.md"
    if version_file.exists():
        with open(version_file) as f:
            print(f.read()[:500])

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    sub.add_parser("init")
    save_p = sub.add_parser("save")
    save_p.add_argument("name")
    save_p.add_argument("--content", default="")
    log_p = sub.add_parser("log")
    log_p.add_argument("name")
    diff_p = sub.add_parser("diff")
    diff_p.add_argument("name")
    args = parser.parse_args()
    
    if hasattr(args, "name"):
        if hasattr(args, "content") and args.content:
            save(args.name, args.content)
        else:
            content = sys.stdin.read() if not sys.stdin.isatty() else ""
            if content:
                save(args.name, content)
            else:
                log(args.name)
    else:
        init()

if __name__ == "__main__":
    main()
