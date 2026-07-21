# Code Review Automation

> AI-powered code review for GitHub PRs — catches bugs, security issues, performance problems, and style violations before human reviewers look.

## What This Does

Automates the code review process on GitHub Pull Requests:
- Security vulnerability detection (OWASP Top 10)
- Bug pattern detection (race conditions, null dereferences, SQL injection)
- Performance anti-patterns (N+1 queries, memory leaks)
- Code quality scoring with actionable suggestions
- Automated approval for trivial/low-risk changes
- Review summary comments posted directly on PR

## When to Use

- Large PRs where manual review is time-consuming
- Enforcing consistent code quality across a team
- Catching security issues before production
- Reducing reviewer fatigue on repetitive changes
- Onboarding new team members with automated guidance

## Review Dimensions

### Security Checklist
```
- [ ] SQL injection: parameterized queries only
- [ ] XSS: no innerHTML, use textContent
- [ ] Auth bypass: all endpoints authenticated?
- [ ] Secrets: no hardcoded API keys or tokens
- [ ] Input validation: all user input sanitized?
- [ ] Rate limiting: endpoints protected?
- [ ] Dependencies: known CVEs in package.json/requirements.txt?
```

### Performance Checklist
```
- [ ] N+1 queries: eager load relationships
- [ ] Unbounded loops: pagination on large datasets
- [ ] Memory: streaming vs loading full files
- [ ] Caching: repeated expensive computations cached?
- [ ] Indexes: database queries use proper indexes?
- [ ] Async: I/O operations properly awaited?
```

### Best Practices Checklist
```
- [ ] Error handling: no bare try/except passes
- [ ] Types: TypeScript/Python type hints present
- [ ] Tests: new code has corresponding tests
- [ ] Documentation: complex logic explained
- [ ] Naming: variables/functions clearly named
- [ ] Single responsibility: functions do one thing
```

## GitHub Actions Integration

```yaml
name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: AI Code Review
        uses: nima54851/ai-code-reviewer@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          openai-key: ${{ secrets.OPENAI_API_KEY }}
          min-severity: medium  # low|medium|high|critical
          approve-trivial: true
```

## n8n Workflow

See `integrations/code-review-automation/` for the n8n workflow:
1. GitHub webhook on PR opened/updated
2. Fetch diff and file changes
3. LLM analysis across security/performance/style
4. Post structured review comment
5. Assign reviewers based on affected areas

## LLM Review Prompt

```
You are an expert code reviewer. Review the following pull request changes.

Repository language: {language}
PR title: {pr_title}
PR description: {pr_description}

DIFF:
{patch}

Respond with a structured JSON review:
{
  "overall_score": 1-10,
  "summary": "2-3 sentence summary",
  "issues": [
    {
      "file": "path/to/file",
      "line": 42,
      "severity": "critical|high|medium|low",
      "category": "security|performance|bug|style",
      "description": "what's wrong",
      "suggestion": "how to fix it",
      "rule": "OWASP A1 / PEP8 / etc"
    }
  ],
  "approved": boolean,
  "blocking_issues": count
}
```

## Quick Start

```python
# Standalone review script
import openai, subprocess, json

def review_pr(repo: str, pr_number: int, openai_key: str) -> dict:
    diff = subprocess.run(
        ["gh", "pr", "diff", repo, "--pr", str(pr_number)],
        capture_output=True, text=True
    ).stdout
    
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "system",
            "content": CODE_REVIEW_SYSTEM_PROMPT
        }, {
            "role": "user",
            "content": f"Review this PR diff:\n\n{diff[:15000]}"
        }]
    )
    return json.loads(response.choices[0].message.content)
```

## Scoring Rubric

| Score | Meaning |
|-------|---------|
| 9-10 | Production-ready, minimal issues |
| 7-8 | Good, minor suggestions |
| 5-6 | Needs work, several issues |
| 3-4 | Significant problems, blocking |
| 1-2 | Critical issues, do not merge |

## Metrics Tracked

- Average review score over time
- Most common issue types
- Time to first review
- Re-review rate (issues not addressed)

---

*Part of agent-studio | AI Agent Automation Toolkit*
