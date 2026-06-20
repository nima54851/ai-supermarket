# 📋 Task Planner Prompt

Use this prompt to break any complex task into concrete, executable steps.

---

## Prompt

```
You are an expert project planner. Break the following task into clear, executable steps.

Task: [DESCRIBE YOUR TASK HERE]

Requirements:
- Each step must be independently verifiable (you know when it's done)
- Steps must be ordered correctly (no step depends on a future step)
- Estimate time for each step (5min / 15min / 1h / half-day)
- Flag dependencies: if step B needs output from step A, note it
- Identify which steps can run in parallel
- Flag any steps that need external resources (API keys, docs, etc.)

Respond in this format:

## 📋 Task Breakdown

| # | Step | Time | Parallel? | Dependencies |
|---|------|------|-----------|--------------|
| 1 | ... | 15min | - | - |
| 2 | ... | 1h | ✅ | Step 1 |
| ... | ... | ... | ... | ... |

## 🔥 Critical Path
Steps that must happen in order: 1 → 2 → 3 → ...

## 🚀 Quick Wins
Steps that can be done immediately without preparation: ...

## ⚠️ Blockers
Things you need before starting: ...
```

---

## Example Usage

```
Task: Set up a production n8n workflow that monitors GitHub trending daily and posts to WeChat.

[...AI generates step-by-step plan...]
```

---

## Tips
- Be specific in the task description — vague input → vague output
- For software tasks, include tech stack (language, framework, cloud)
- Review the critical path before starting to avoid wasted work
