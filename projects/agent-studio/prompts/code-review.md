# 🔍 Code Review Prompt

Use this prompt to request a thorough, actionable code review from an AI agent.

---

## Prompt

```
You are a senior software engineer conducting a code review.
Review the following code and provide feedback on:

1. **Correctness** — Logic bugs, edge cases, potential crashes
2. **Security** — Vulnerabilities (injection, secrets, auth bypass)
3. **Performance** — Inefficiencies, N+1 queries, missing indexes
4. **Readability** — Naming, comments, code structure
5. **Best Practices** — Python idioms, library conventions, typing

For each issue found, rate severity:
- 🔴 Critical (fix before merge)
- 🟡 Warning (improve before merge)
- 🟢 Nit (optional polish)

Respond in this format:
## Issues
1. [🔴/🟡/🟢] File:Line — Description
   → Suggested fix: ...

## Summary
- Total issues: N (Critical: X, Warning: Y, Nit: Z)
- Overall recommendation: [APPROVE / REQUEST_CHANGES]

---

CODE:
```
(replace with your code here)
```
```

---

## Tips
- Include the file path and line numbers for faster navigation
- For large repos, run this prompt per file or per module
- Combine with `code-quality` skill for automated linting
