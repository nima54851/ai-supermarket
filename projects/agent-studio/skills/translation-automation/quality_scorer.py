#!/usr/bin/env python3
"""
Translation Quality Scorer
Scores translations for accuracy, fluency, and terminology consistency.
"""
import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def score_translation(original: str, translation: str, target_lang: str) -> dict:
    """Score a translation on accuracy, fluency, and terminology."""
    prompt = f"""Evaluate this translation from English to {target_lang}.

Original: {original}

Translation: {translation}

Score it on:
1. Accuracy (0-100): Does it convey the same meaning?
2. Fluency (0-100): Is it natural, grammatically correct {target_lang}?
3. Terminology (0-100): Are domain terms used correctly?
4. Overall (0-100): Overall quality.

Return JSON:
{{"accuracy": N, "fluency": N, "terminology": N, "overall": N, "issues": [...], "suggestions": [...], "pass": true|false}}"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)

def batch_score(translations: list, target_lang: str, threshold: int = 70) -> list:
    """Score a batch of translations, flagging low-confidence ones."""
    scored = []
    for item in translations:
        score = score_translation(item["original"], item["translation"], target_lang)
        scored.append({
            **item,
            **score,
            "needs_review": score["overall"] < threshold,
        })
    return scored

if __name__ == "__main__":
    import sys
    data = json.loads(sys.stdin.read())
    results = batch_score(data["translations"], data.get("target_lang", "ES"))
    print(json.dumps(results, indent=2, ensure_ascii=False))
