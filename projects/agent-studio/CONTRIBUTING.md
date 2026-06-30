# Contributing to agent-studio 🤝

Great that you're here! Here's how to contribute.

## Ways to Contribute

### 1. Add a Skill
Skills are the core of agent-studio. To add one:

```
skills/<your-skill-name>/
├── SKILL.md           # Required: name + description + core workflow
├── scripts/           # Optional: Python/Bash automation
├── references/        # Optional: API docs, schemas, guides
└── assets/           # Optional: templates, configs
```

See [`skills/skill-builder`](skills/skill-builder) for the full skill creation guide.

**Skill naming rules:**
- Lowercase letters, digits, and hyphens only
- Short, action-led names (e.g., `coding-tutor`, `test-master`)
- Max 64 characters

### 2. Share a Workflow
Add production-ready workflows to:
- `integrations/` — Discord/Telegram/n8n pipelines
- `workflows/` — n8n JSON workflows
- `.github/workflows/` — GitHub Actions automation

### 3. Improve Documentation
- Fix typos and broken links
- Add real examples to existing skills
- Translate to other languages
- Improve the README and docs/

### 4. Star & Share
The best contribution you can make:
```bash
# Star the repo
gh repo clone nima54851/agent-studio && cd agent-studio && gh repo star

# Share on social
# "Just found agent-studio — a free AI agent toolkit with 12 production skills"
```

## Commit Message Convention

```
<type>: <short description>

Types: feat | fix | docs | style | refactor | test | chore
```

Examples:
- `feat: add coding-tutor skill`
- `fix: correct webhook endpoint path`
- `docs: improve README quick start`

## Pull Request Checklist

- [ ] Skill follows the naming convention
- [ ] SKILL.md has a clear `description` (what triggers this skill)
- [ ] SKILL.md body is concise (< 500 lines)
- [ ] Scripts are tested and working
- [ ] No README/INSTALL/CHANGELOG files in the skill folder

## Questions?

Open an [Issue](https://github.com/nima54851/agent-studio/issues) — response within 24h.
