#!/usr/bin/env python3
"""
AI Commit Message Generator — generates semantic commits from diffs
Supports: Conventional Commits format, multi-line messages, breaking change detection
"""
import argparse, subprocess, sys, re

COMMIT_TYPES = {
    "feat": "🎸 new feature for users",
    "fix": "🐛 bug fix for users",
    "docs": "📝 documentation only changes",
    "style": "💄 code style (formatting, semicolons, etc)",
    "refactor": "♻️ code change that neither fixes a bug nor adds a feature",
    "test": "✅ adding or correcting tests",
    "chore": "🔧 maintenance tasks (deps, build, config)",
    "perf": "⚡ performance improvement",
    "ci": "👷 CI/CD changes",
    "revert": "⏪ revert a previous commit",
}

BREAKING_PATTERNS = [
    r"BREAKING[- ]CHANGE:",
    r"!\s*\(.*\):",
]

def detect_type(diff: str) -> str:
    """Infer commit type from diff content."""
    if any(k in diff for k in ["test", "spec", "__tests__"]):
        return "test"
    if any(k in diff for k in ["README", "CHANGELOG", "docs"]):
        return "docs"
    if any(k in diff for k in ["package.json", "requirements.txt", "go.mod", "Cargo.toml", ".github/workflows"]):
        return "chore"
    if re.search(r"(function|def|class|const|let|var|async|await)\s+\w+", diff):
        return "feat"  # code changes are feats until proven otherwise
    if "FIX" in diff or "bug" in diff.lower():
        return "fix"
    return "feat"

def detect_scope(diff: str) -> str:
    """Infer scope from file paths in diff."""
    files = re.findall(r"^\+\+\+ b/(.+)$", diff, re.MULTILINE)
    if not files:
        files = re.findall(r"^\+\+\+ b/(.+)$", diff, re.MULTILINE)
    if files:
        path = files[0]
        parts = path.split("/")
        if len(parts) > 1:
            return parts[-2] if parts[-1].startswith(parts[-2][:3]) else parts[-2]
        return parts[0].replace("-", "_")
    return "core"

def detect_breaking(diff: str) -> bool:
    return any(re.search(p, diff) for p in BREAKING_PATTERNS)

def generate_message(diff: str) -> str:
    """Generate a commit message from diff content."""
    ctype = detect_type(diff)
    scope = detect_scope(diff)
    breaking = detect_breaking(diff)
    
    # Generate short description from changed lines
    added_lines = [l[1:].strip() for l in diff.split("\n") if l.startswith("+") and not l.startswith("+++")]
    removed_lines = [l[1:].strip() for l in diff.split("\n") if l.startswith("-") and not l.startswith("---")]
    
    description = ""
    if added_lines:
        # Find meaningful changed lines (not just whitespace)
        meaningful = [l for l in added_lines if len(l) > 3 and not l.startswith("//")]
        if meaningful:
            first = meaningful[0]
            # Truncate long descriptions
            if len(first) > 72:
                first = first[:69] + "..."
            description = first
        else:
            description = f"update {len(added_lines)} lines"
    
    emoji = "🚀" if ctype == "feat" and breaking else "✨" if ctype == "feat" else "🔧" if ctype == "chore" else "📝"
    
    msg = f"{emoji} {ctype}({scope}): {description}"
    if breaking:
        msg += "\n\n⚠️ BREAKING CHANGE"
    
    return msg

def get_staged_diff() -> str:
    result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)
    return result.stdout

def main():
    parser = argparse.ArgumentParser(description="AI commit message generator")
    parser.add_argument("--diff-file", help="Path to diff file")
    parser.add_argument("--stdin", action="store_true", help="Read diff from stdin")
    parser.add_argument("--type", choices=list(COMMIT_TYPES.keys()), help="Override commit type")
    args = parser.parse_args()
    
    diff = ""
    if args.diff_file:
        with open(args.diff_file) as f:
            diff = f.read()
    elif args.stdin:
        diff = sys.stdin.read()
    else:
        diff = get_staged_diff()
    
    if not diff.strip():
        print("No diff content found. Stage some files with `git add` first.")
        sys.exit(1)
    
    msg = generate_message(diff)
    print("Generated commit message:\n")
    print(msg)
    print("\n\nTo use:")
    print(f'git commit -m "{msg}"')

if __name__ == "__main__":
    main()
