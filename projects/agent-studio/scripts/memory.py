#!/usr/bin/env python3
"""
Agent Memory Manager
Persist context across AI agent sessions — structured long-term memory.
Usage:
    memory = AgentMemory("memory.json")
    memory.learn("user_name", "万")
    memory.record_session("Did something", decisions=["choice A"])
"""
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
        return {
            "agent_id": None,
            "sessions": [],
            "knowledge": {},
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat()
        }

    def _save(self):
        self.data["updated"] = datetime.now().isoformat()
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def set_agent_id(self, agent_id):
        self.data["agent_id"] = agent_id
        self._save()

    def record_session(self, summary, decisions=None, learnings=None, tags=None):
        """Record what happened in this session"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "summary": summary,
            "decisions": decisions or [],
            "learnings": learnings or [],
            "tags": tags or []
        }
        self.data["sessions"].append(entry)
        self._save()
        return entry

    def learn(self, key, value):
        """Store a persistent fact"""
        self.data["knowledge"][key] = {
            "value": value,
            "learned_at": datetime.now().isoformat()
        }
        self._save()

    def recall(self, key):
        """Retrieve a stored fact"""
        return self.data.get("knowledge", {}).get(key, {}).get("value")

    def forget(self, key):
        """Remove a fact"""
        if key in self.data.get("knowledge", {}):
            del self.data["knowledge"][key]
            self._save()

    def recent_sessions(self, n=5):
        """Get last N sessions"""
        return self.data.get("sessions", [])[-n:]

    def search_sessions(self, keyword):
        """Find sessions containing a keyword"""
        results = []
        for s in self.data.get("sessions", []):
            if keyword.lower() in s.get("summary", "").lower():
                results.append(s)
        return results

    def knowledge_summary(self):
        """Get all stored knowledge as readable text"""
        lines = []
        for key, entry in self.data.get("knowledge", {}).items():
            lines.append(f"- **{key}**: {entry.get('value')} _(learned {entry.get('learned_at', '?')})_")
        return "\n".join(lines) if lines else "_No knowledge stored yet_"

    def export(self):
        """Export full memory state"""
        return self.data

    def stats(self):
        """Memory statistics"""
        return {
            "total_sessions": len(self.data.get("sessions", [])),
            "knowledge_items": len(self.data.get("knowledge", {})),
            "first_session": self.data.get("sessions", [{}])[0].get("date", "none"),
            "last_updated": self.data.get("updated"),
            "agent_id": self.data.get("agent_id")
        }


if __name__ == "__main__":
    # Demo
    m = AgentMemory("/tmp/demo_memory.json")
    m.set_agent_id("agent-studio-demo")
    m.learn("project", "agent-studio")
    m.learn("owner", "nima54851")
    m.record_session(
        "Initialized agent-studio repo",
        decisions=["Chose MIT license"],
        learnings=["GitHub PAT needs write scope"],
        tags=["setup", "github"]
    )
    print("Stats:", m.stats())
    print("Summary:", m.knowledge_summary())
    print("Recent:", m.recent_sessions(1))
