#!/usr/bin/env python3
"""
agent_memory_manager.py — AI Agent 长期记忆管理工具
支持向量存储召回、会话摘要、记忆遗忘策略
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Optional

DB_PATH = os.environ.get("MEMORY_DB", "/tmp/agent_memory.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            user_id TEXT,
            session_id TEXT,
            content TEXT NOT NULL,
            type TEXT DEFAULT 'context',
            importance REAL DEFAULT 0.5,
            created_at TEXT DEFAULT (datetime('now')),
            expires_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS memory_stats (
            agent_id TEXT PRIMARY KEY,
            total_memories INTEGER DEFAULT 0,
            last_recall_at TEXT,
            last_store_at TEXT
        )
    """)
    conn.commit()
    return conn


def store_memory(agent_id: str, content: str, user_id: str = None,
                 session_id: str = None, memory_type: str = "context",
                 importance: float = 0.5, ttl_days: int = 30) -> dict:
    """存储记忆"""
    conn = init_db()
    c = conn.cursor()
    expires_at = (datetime.now() + timedelta(days=ttl_days)).isoformat()

    c.execute("""
        INSERT INTO memories (agent_id, user_id, session_id, content, type, importance, expires_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (agent_id, user_id, session_id, content, memory_type, importance, expires_at))
    memory_id = c.lastrowid

    c.execute("""
        INSERT INTO memory_stats (agent_id, total_memories, last_store_at)
        VALUES (?, 1, datetime('now'))
        ON CONFLICT(agent_id) DO UPDATE SET
            total_memories = total_memories + 1,
            last_store_at = datetime('now')
    """, (agent_id,))
    conn.commit()
    conn.close()

    fingerprint = hashlib.md5(f"{agent_id}:{content[:100]}".encode()).hexdigest()
    return {
        "memory_id": memory_id,
        "agent_id": agent_id,
        "fingerprint": fingerprint,
        "stored": True
    }


def recall_memories(agent_id: str, query: str = None, user_id: str = None,
                    memory_type: str = None, limit: int = 10) -> list:
    """召回相关记忆（简单关键词匹配，实际生产用向量数据库）"""
    conn = init_db()
    c = conn.cursor()

    sql = "SELECT id, content, type, importance, created_at FROM memories WHERE agent_id = ? AND (expires_at IS NULL OR expires_at > datetime('now'))"
    params = [agent_id]

    if user_id:
        sql += " AND user_id = ?"
        params.append(user_id)
    if memory_type:
        sql += " AND type = ?"
        params.append(memory_type)
    if query:
        sql += " AND content LIKE ?"
        params.append(f"%{query}%")

    sql += " ORDER BY importance DESC, created_at DESC LIMIT ?"
    params.append(limit)

    c.execute(sql, params)
    rows = c.fetchall()
    conn.close()

    return [
        {"id": r[0], "content": r[1], "type": r[2], "importance": r[3], "created_at": r[4]}
        for r in rows
    ]


def cleanup_expired(agent_id: str = None) -> int:
    """清理过期记忆"""
    conn = init_db()
    c = conn.cursor()

    if agent_id:
        c.execute("DELETE FROM memories WHERE expires_at < datetime('now') AND agent_id = ?", (agent_id,))
    else:
        c.execute("DELETE FROM memories WHERE expires_at < datetime('now')")

    deleted = c.rowcount
    conn.commit()
    conn.close()
    return deleted


def get_memory_stats(agent_id: str) -> dict:
    """获取记忆统计"""
    conn = init_db()
    c = conn.cursor()
    c.execute("SELECT * FROM memory_stats WHERE agent_id = ?", (agent_id,))
    row = c.fetchone()
    c.execute("SELECT COUNT(*) FROM memories WHERE agent_id = ? AND (expires_at IS NULL OR expires_at > datetime('now'))", (agent_id,))
    active = c.fetchone()[0]
    conn.close()

    if not row:
        return {"agent_id": agent_id, "total_memories": 0, "active_memories": 0}

    return {
        "agent_id": row[0],
        "total_memories": row[1],
        "last_recall": row[2],
        "last_store": row[3],
        "active_memories": active
    }


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"

    if cmd == "store":
        result = store_memory(
            agent_id=sys.argv[2] if len(sys.argv) > 2 else "test-agent",
            content=sys.argv[3] if len(sys.argv) > 3 else "Test memory",
            memory_type=sys.argv[4] if len(sys.argv) > 4 else "context",
            importance=float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
        )
        print(json.dumps(result))
    elif cmd == "recall":
        results = recall_memories(
            agent_id=sys.argv[2] if len(sys.argv) > 2 else "test-agent",
            query=sys.argv[3] if len(sys.argv) > 3 else None
        )
        print(json.dumps(results, indent=2))
    elif cmd == "cleanup":
        deleted = cleanup_expired()
        print(f"Cleaned up {deleted} expired memories")
    elif cmd == "stats":
        stats = get_memory_stats(sys.argv[2] if len(sys.argv) > 2 else "test-agent")
        print(json.dumps(stats, indent=2))
