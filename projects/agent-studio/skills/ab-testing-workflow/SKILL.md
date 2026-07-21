# A/B Testing Workflow Skill

Create and run A/B tests for n8n workflows and OpenClaw agent prompts. Automatically measure which variant performs better.

## Concept
1. Define two variants of a workflow/prompt
2. Route traffic to each variant (50/50 or custom ratio)
3. Collect metrics (success rate, response time, user rating)
4. Statistical significance test
5. Auto-select winner

## Usage
```bash
python3 ab_tester.py --variants variant_a.json variant_b.json --metric success_rate --threshold 0.95
```
