# AI Code Refactoring Automation

**Skill Name:** ai-code-refactoring  
**Author:** 灵犀 AI (nima54851)  
**Compatible:** OpenClaw + n8n + LLM (Claude/GPT/Ollama)  
**Tags:** refactoring, code-quality, python, javascript, typescript, clean-code

---

## What This Skill Does

Use AI to automatically refactor legacy code — improving readability, performance, and maintainability. Supports Python, JavaScript, TypeScript, Go, and Rust. Provides a structured workflow for AI-powered code reviews and refactoring with before/after diffs.

## Use Cases

- Break down large Python scripts into clean modules
- Convert callback-style JS to async/await
- Add type hints to Python dynamically
- Simplify complex nested conditionals
- Extract repeated code into reusable functions

## Core Scripts

### `ai_refactor.py`

```python
#!/usr/bin/env python3
"""AI-powered code refactoring via OpenAI/Claude/Ollama API."""
import os, sys, json, argparse

LLM_URL = os.environ.get("LLM_URL", "http://localhost:11434/api/generate")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3")

PROMPT = """You are an expert code refactorer. Refactor the following {lang} code for:
1. Readability (clean variable names, comments)
2. Performance (remove redundant operations)
3. Best practices (type hints, error handling)
4. DRY principle (extract duplication)

Return ONLY the refactored code in a markdown code block. No explanations outside the block.

```{lang}
{code}
```

Refactored code:"""

def refactor(code: str, lang: str = "python") -> str:
    prompt = PROMPT.format(lang=lang, code=code)
    if "localhost" in LLM_URL:
        import requests
        r = requests.post(LLM_URL, json={"model": LLM_MODEL, "prompt": prompt, "stream": False}, timeout=60)
        return r.json().get("response", "")
    # fallback to OpenAI
    import openai
    client = openai.OpenAI()
    resp = client.chat.completions.create(
        model="gpt-4o", messages=[{"role": "user", "content": prompt}], temperature=0.3
    )
    return resp.choices[0].message.content

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", help="Source file to refactor")
    p.add_argument("--lang", default="python", help="Language: python, javascript, typescript, go, rust")
    p.add_argument("--output", default="refactored.py", help="Output file")
    args = p.parse_args()

    with open(args.file) as f:
        code = f.read()

    print(f"🔄 Refactoring {args.file}...")
    result = refactor(code, args.lang)

    # Extract code block
    if "```" in result:
        start = result.index("```") + 3
        end = result.rindex("```")
        result = result[start:].split("\n", 1)[1] if "\n" in result[start:] else result[start:]
        result = result[:result.rfind("```")]

    with open(args.output, "w") as f:
        f.write(result.strip())
    print(f"✅ Refactored code saved: {args.output}")

if __name__ == "__main__":
    main()
```

### `check_quality.py`

```python
#!/usr/bin/env python3
"""Run quality checks before and after refactoring."""
import subprocess, sys

CHECKS = [
    ("pylint", ["pylint", "{file}", "-r", "n"]),
    ("ruff", ["ruff", "check", "{file}"]),
    ("mypy", ["mypy", "{file}", "--ignore-missing-imports"]),
    ("black", ["black", "--check", "{file}"]),
]

def run_checks(file: str):
    results = {}
    for name, cmd in CHECKS:
        cmd = [c.format(file=file) for c in cmd]
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=15)
            results[name] = "✅ PASS" if r.returncode == 0 else f"⚠️ ISSUES ({r.stderr.decode()[:200]})"
        except FileNotFoundError:
            results[name] = "⏭️  SKIP (not installed)"
        except Exception as e:
            results[name] = f"❌ ERROR: {e}"
    return results

if __name__ == "__main__":
    for result in run_checks(sys.argv[1] if len(sys.argv) > 1 else "."):
        print(result)
```

## Prompt Templates

### Python Refactoring Prompt

```
Review this Python code and refactor it following these rules:
1. Add type hints to all functions
2. Replace list comprehensions where loops are used
3. Extract magic numbers into constants
4. Add docstrings to all functions
5. Use dataclasses for structured data
6. Replace try/except/pass with specific exception handling

Apply only safe, backward-compatible changes. Return the refactored code.
```

### JavaScript Refactoring Prompt

```
Refactor this JavaScript/TypeScript code to:
1. Convert var → const/let
2. Replace callbacks with async/await
3. Add JSDoc comments
4. Use strict TypeScript types
5. Extract reusable utility functions
6. Remove console.log debugging statements

Only apply non-breaking changes. Return the refactored code.
```

## n8n Workflow: Automated Code Review + Refactor

```
GitHub PR opened → Webhook → Fetch diff → AI Refactor → Post comment with suggestions
```

## n8n Workflow JSON

```json
{
  "name": "AI Code Refactoring Pipeline",
  "nodes": [
    {
      "name": "GitHub Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": { "path": "github-pr", "httpMethod": "POST" }
    },
    {
      "name": "Extract PR Info",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "const pr = $json; $json.repo = pr.repository.full_name; $json.prNumber = pr.pull_request.number; $json.diffUrl = pr.pull_request.diff_url;"
      }
    },
    {
      "name": "Fetch Diff",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": { "url": "={{$json.diffUrl}}", "response": { "response": { "responseFormat": "text" } } }
    },
    {
      "name": "AI Refactor (Ollama)",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:11434/api/generate",
        "method": "POST",
        "bodyParameters": {
          "model": "llama3",
          "prompt": "Refactor this code:\n{{ $json }}"
        }
      }
    },
    {
      "name": "Post PR Comment",
      "type": "n8n-nodes-base.github",
      "parameters": {
        "operation": "createComment",
        "repository": "={{$json.repo}}",
        "issueNumber": "={{$json.prNumber}}",
        "body": "## 🤖 AI Code Review\n\nRefactored version:\n\n```\n{{ $json.response }}\n```"
      }
    }
  ],
  "connections": {
    "GitHub Webhook": { "main": [[{ "node": "Extract PR Info" }]] },
    "Extract PR Info": { "main": [[{ "node": "Fetch Diff" }]] },
    "Fetch Diff": { "main": [[{ "node": "AI Refactor (Ollama)" }]] },
    "AI Refactor (Ollama)": { "main": [[{ "node": "Post PR Comment" }]] }
  }
}
```

## Quick Start

```bash
# Refactor a Python file with Ollama (local)
python3 ai_refactor.py --file messy.py --lang python --output clean.py

# Run quality checks
python3 check_quality.py clean.py

# With OpenAI (set OPENAI_API_KEY env var)
export OPENAI_API_KEY=sk-...
python3 ai_refactor.py --file app.py --lang python --output app_clean.py
```

## Dependencies

- `requests` — Ollama API calls
- `openai` — OpenAI API (optional)
- `pylint`, `ruff`, `mypy`, `black` — quality tools (optional)
