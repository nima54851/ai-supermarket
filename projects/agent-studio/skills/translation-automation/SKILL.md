# Translation Automation

## Overview
AI-powered multilingual content translation and localization pipeline. Uses DeepL, Google Translate, or OpenAI for context-aware translations with quality scoring.

## What It Does
- **Batch Translation**: Translate entire content repositories, docs, or product strings
- **Context-Aware**: AI understands context — product docs vs. marketing vs. legal
- **Quality Scoring**: Each translation scored for accuracy, fluency, terminology consistency
- **Terminology Lock**: Enforce consistent domain-specific terminology across languages
- **Review Workflow**: Flag low-confidence translations for human review before publishing
- **RTL Support**: Full RTL language support (Arabic, Hebrew, Persian)

## Supported Languages (50+)
Spanish, French, German, Italian, Portuguese, Russian, Chinese (Simplified/Traditional), Japanese, Korean, Arabic, Hindi, Thai, Vietnamese, Turkish, Polish, Dutch, Swedish, Danish, Norwegian, Finnish, Czech, Romanian, Greek, Hungarian, Ukrainian, Hebrew, Persian, and more.

## Workflow Pipeline
```
Content Source (GitHub/CMS/API/JSON files)
  → n8n Webhook Trigger
  → AI Agent detects language and content type
  → Terminology lookup (Redis cache)
  → Translation via DeepL/OpenAI
  → Quality scoring (parallel AI evaluation)
  → If score < threshold → flag for human review
  → Output: translated files + quality report
  → Auto-commit to localization branch
```

## Files
- `SKILL.md` — this file
- `deepl_translator.py` — DeepL API translation
- `quality_scorer.py` — translation quality evaluation
- `terminology_manager.py` — terminology lock system
- `batch_translator.py` — multi-file batch translation

## Setup
```bash
cd integrations/translation-automation
cp .env.example .env
# Fill in: DEEPL_API_KEY or OPENAI_API_KEY
# Import n8n workflow: n8n-translation-workflow.json
```

## Integration Points
- DeepL API / Google Cloud Translation
- OpenAI / Claude (context-aware translation)
- GitHub (commit to locale branches)
- Crowdin / Phrase (TMS integration)
- Notion / Contentful (CMS)
- Slack / Email (review notifications)

## Related
- `ai-prompt-engineering/` — prompt optimization
- `social-media-automation/` — multi-language social posts
- `docs-generator/` — multilingual documentation
