---
name: agent-memory
description: Structured memory management for AI agents — persist context across sessions, build long-term knowledge, and enable learning from experience. Use when you need an agent that remembers.
---

# Agent Memory System

## PURPOSE

Give your AI agent a structured long-term memory. Agents forget between sessions — this skill provides a persistence layer so they accumulate knowledge and improve over time.

## ARCHITECTURE

```
Agent Session
  ↓ writes
Memory Store (JSON/SQLite files)
  ↓ reads
Next Session (context restored)
```

## MEMORY STRUCTURE

```json
{
  "agent_id": "lingxi",
  "sessions": [
    {
      "date": "2025-06-19",
      "summary": "User set up n8n, GitHub account",
      "decisions": ["n8n selected as automation engine"],
      "learnings": ["GitHub PAT needs write permissions"]
    }
  ],
  "knowledge": {
    "owner": {
      "name": "万",
      "timezone": "Asia/Shanghai",
      "preferences": {}
    },
    "projects": {
      "agent-studio": {"status": "active", "repo": "nima54851/agent-studio"}
    }
  },
  "skills": {}
}
```

## IMPLEMENTATION

### Memory Manager Class

```python
import json, os
from datetime import datetime

class AgentMemory:
    def __init__(self, memory_file=".agent_memory.json"):
        self.file = memory_file
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.file):
            with open(self.file) as f:
                return json.load(f)
        return {"sessions": [], "knowledge": {}, "created": datetime.now().isoformat()}

    def _save(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def record_session(self, summary, decisions=None, learnings=None):
        self.data["sessions"].append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "decisions": decisions or [],
            "learnings": learnings or []
        })
        self._save()

    def learn(self, key, value):
        if "knowledge" not in self.data:
            self.data["knowledge"] = {}
        self.data["knowledge"][key] = value
        self._save()

    def recall(self, key):
        return self.data.get("knowledge", {}).get(key)

    def recent_sessions(self, n=5):
        return self.data.get("sessions", [])[-n:]
```

## USAGE

```python
memory = AgentMemory()

# Record what happened today
memory.record_session(
    summary="Set up GitHub account and agent-studio repo",
    decisions=["Used agent-studio as main project name"],
    learnings=["GitHub PAT needs 'repo' scope for write access"]
)

# Remember facts
memory.learn("user_name", "万")
memory.learn("timezone", "Asia/Shanghai")

# Recall in next session
user = memory.recall("user_name")
past = memory.recent_sessions(3)
```

## SKILL INTEGRATION (OpenClaw)

Save as skill file and invoke at session start:

```
1. Load .agent_memory.json
2. Inject knowledge into context
3. End of session → record_session()
4. Significant learning → learn(key, value)
```

## AGENT CONTEXT PROMPT

When initializing an agent with memory:

> "Previous sessions: {recent_sessions}
> Long-term knowledge: {knowledge}
> Always reference past decisions before making new ones."

## USE CASES

- Personal AI assistant that remembers your projects and preferences
- Multi-agent systems with shared knowledge base
- Automated CI that tracks what it changed and why
- Customer-facing agents with conversation history

## FILES IN THIS SKILL

- `memory.py` — Core AgentMemory class
- `memory.json` — Example memory state
- `session_log.py` — Automated session recorder

---

*Part of [agent-studio](https://github.com/nima54851/agent-studio) · MIT License*
