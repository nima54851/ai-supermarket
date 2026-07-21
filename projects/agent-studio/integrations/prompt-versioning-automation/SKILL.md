# Prompt Versioning Automation

Version control your AI prompts like source code — track changes, diff versions, rollback bad experiments, A/B test, and manage prompt environments across staging and production.

## Why Prompt Versioning?

- Prompts are code — they change behavior without code changes
- Track every modification with commit messages
- Diff between versions to understand what changed
- Rollback instantly when a new prompt degrades
- A/B test prompts in production
- Environment promotion: dev → staging → production

## File Structure

```
integrations/prompt-versioning-automation/
├── SKILL.md                    # This file
├── prompt_store.py             # Prompt version storage (SQLite + git-style)
├── prompt_diff.py              # Diff two prompt versions
├── prompt_deployer.py          # Deploy prompts to environments
├── n8n-prompt-versioning.json  # n8n: prompt CRUD + rollback workflow
├── tests/
│   └── test_prompts.py        # Prompt unit tests
└── README.md
```

## Core: prompt_store.py

```python
"""
Prompt Version Store — git-like versioning for AI prompts
Stores in SQLite with full history, diffs, and rollback support
"""
import sqlite3
import hashlib
import json
import os
from datetime import datetime
from typing import Optional
from prompt_diff import diff_prompts

DB_PATH = os.environ.get("PROMPT_DB", "prompts.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            content TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            variables TEXT,  -- JSON: list of variable names
            model TEXT,
            temperature REAL,
            max_tokens INTEGER,
            environment TEXT DEFAULT 'dev',
            commit_message TEXT,
            created_by TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prompt_environments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_name_version ON prompts(name, version)
    """)
    conn.commit()
    return conn

def save_prompt(name: str, content: str, environment: str = "dev",
                commit_message: str = "", created_by: str = "system",
                model: str = None, temperature: float = None,
                max_tokens: int = None) -> int:
    """Save a new version of a prompt. Returns new version number."""
    conn = init_db()
    
    # Detect variables: {{var}} or {var}
    import re
    variables = re.findall(r'\{\{?(\w+)\}?\}', content)
    
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:12]
    
    # Get current latest version
    cur = conn.execute(
        "SELECT MAX(version) FROM prompts WHERE name=? AND environment=?",
        (name, environment)
    ).fetchone()[0]
    new_version = (cur or 0) + 1
    
    conn.execute("""
        INSERT INTO prompts 
        (name, version, content, content_hash, variables, model, temperature,
         max_tokens, environment, commit_message, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, new_version, content, content_hash, json.dumps(variables),
          model, temperature, max_tokens, environment, commit_message, created_by))
    conn.commit()
    conn.close()
    
    return new_version

def get_prompt(name: str, version: int = None, environment: str = "dev") -> dict:
    """Get a specific version or latest version of a prompt."""
    conn = init_db()
    
    if version:
        row = conn.execute(
            "SELECT * FROM prompts WHERE name=? AND version=? AND environment=?",
            (name, version, environment)
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT * FROM prompts WHERE name=? AND environment=? ORDER BY version DESC LIMIT 1",
            (name, environment)
        ).fetchone()
    
    if not row:
        conn.close()
        return None
    
    cols = [c[0] for c in conn.execute("PRAGMA table_info(prompts)").fetchall()]
    conn.close()
    return dict(zip(cols, row))

def list_versions(name: str, environment: str = "dev") -> list:
    """List all versions of a prompt."""
    conn = init_db()
    rows = conn.execute("""
        SELECT version, content_hash, commit_message, created_by, created_at
        FROM prompts WHERE name=? AND environment=?
        ORDER BY version DESC
    """, (name, environment)).fetchall()
    conn.close()
    return [{"version": r[0], "hash": r[1], "message": r[2],
             "author": r[3], "at": r[4]} for r in rows]

def diff_versions(name: str, v1: int, v2: int, environment: str = "dev") -> str:
    """Diff two versions of a prompt."""
    p1 = get_prompt(name, v1, environment)
    p2 = get_prompt(name, v2, environment)
    if not p1 or not p2:
        return "Version not found"
    return diff_prompts(p1["content"], p2["content"])

def rollback(name: str, target_version: int, environment: str = "dev",
             commit_message: str = "") -> int:
    """Rollback to a specific version (creates new version with old content)."""
    old = get_prompt(name, target_version, environment)
    if not old:
        raise ValueError(f"Version {target_version} not found for {name}")
    
    return save_prompt(
        name=name,
        content=old["content"],
        environment=environment,
        commit_message=commit_message or f"Rollback to v{target_version}",
        model=old["model"],
        temperature=old["temperature"],
        max_tokens=old["max_tokens"]
    )

def promote(name: str, from_env: str, to_env: str, commit_message: str = "") -> int:
    """Promote a prompt from one environment to another."""
    latest = get_prompt(name, environment=from_env)
    if not latest:
        raise ValueError(f"No prompts found for {name} in {from_env}")
    
    return save_prompt(
        name=name,
        content=latest["content"],
        environment=to_env,
        commit_message=commit_message or f"Promoted from {from_env} (v{latest['version']})",
        model=latest["model"],
        temperature=latest["temperature"],
        max_tokens=latest["max_tokens"]
    )

if __name__ == "__main__":
    init_db()
    print("Prompt store initialized at", DB_PATH)
    
    # Example
    v1 = save_prompt("customer-reply", 
                     "You are a helpful customer support agent. Reply to: {{inquiry}}",
                     commit_message="Initial prompt", created_by="alice")
    print(f"Created v{v1}")
    
    v2 = save_prompt("customer-reply",
                     "You are an expert customer support agent specializing in {{topic}}. "
                     "Reply professionally to: {{inquiry}}. Keep it under 100 words.",
                     commit_message="Added topic variable and word limit",
                     created_by="bob")
    print(f"Created v{v2}")
    
    diff = diff_versions("customer-reply", v1, v2)
    print("Diff:\n", diff)
```

## n8n Workflow: Prompt Versioning

The `n8n-prompt-versioning.json` workflow handles:
- `POST /webhook/prompt/save` — Save new prompt version
- `GET /webhook/prompt/get` — Retrieve prompt (with optional version/env)
- `POST /webhook/prompt/diff` — Diff two versions
- `POST /webhook/prompt/rollback` — Rollback to specific version
- `POST /webhook/prompt/promote` — Promote across environments
- `GET /webhook/prompt/list` — List all versions

## Usage in AI Agent Code

```python
from prompt_store import get_prompt

# Load latest production prompt
reply_prompt = get_prompt("customer-reply", environment="prod")
print(reply_prompt["content"])  # Use in your LLM call

# Use with variables
content = reply_prompt["content"]
content = content.replace("{{inquiry}}", user_input)
content = content.replace("{{topic}}", detected_topic)
```

## Environment Strategy

```
dev  →  staging  →  production
(Alice)    (QA)         (live)
```

| Environment | Purpose |
|---|---|
| `dev` | Active development and experiments |
| `staging` | QA testing and A/B comparison |
| `prod` | Live production prompts |

## Integration with n8n LLM Nodes

Use the prompt version in n8n Code node:

```javascript
// n8n Expression or Code node
const db = require('/path/to/prompt_store.py');  // or call via webhook
const prompt = getPrompt("customer-reply", "prod");
// Then use in LLM node: {{ $json.prompt.content }}
```
