# 📊 GitHub Digest Prompt

Use this prompt to generate a structured GitHub trending digest from raw data.

---

## Prompt

```
You are an AI content analyst. Generate a concise GitHub trending digest from the following data.

For each section, format as:
| # | 项目 | ⭐ | 🍴 | 简介 |
(1–8 rows per section)

Include exactly these 4 sections:

## 🤖 AI/ML 热门
Projects tagged: AI, machine-learning, LLM, agent, GPT

## 🐍 Python 新势力
Projects written primarily in Python with high recent activity

## 🔥 全站上升项目
Top 10 projects by stars gained in the last 7 days

## 🆕 近期新项目
Projects created in the last 30 days with >500 stars

Rules:
- Use abbreviated numbers: 42,300 → 42,300
- Truncate descriptions to max 60 chars
- Exclude forks (original repo only)
- Sort by stars descending within each section
- Add a 🔥 if gained >1,000 stars today

Format the final output as clean Markdown.
```

---

## Example Output

```markdown
## 🤖 AI/ML 热门

| # | 项目 | ⭐ | 🍴 | 简介 |
|---|------|----|----|------|
| 1 | [user/repo](https://github.com/user/repo) | 42,300 | 5,120 | A great AI tool |
```

---

## Tips
- Pipe the output of `python3 scripts/github_trending.py` into this prompt
- Run daily and commit the digest to your project's `REPORT.md`
- Add `<!-- auto-generated -->` comment for easy find-and-replace
