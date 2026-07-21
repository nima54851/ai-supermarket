#!/usr/bin/env python3
"""
DeepL Translator
Batch and context-aware translation using DeepL API.
"""
import os
import json
import httpx
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

DEEPL_KEY = os.environ.get("DEEPL_API_KEY")
DEEPL_URL = "https://api-free.deepl.com/v2/translate" if os.environ.get("DEEPL_FREE") else "https://api.deepl.com/v2/translate"

def translate_text(text: str, target_lang: str, source_lang: str = None, context: str = None) -> dict:
    """Translate text using DeepL with optional context."""
    headers = {"Authorization": f"DeepL-Auth-Key {DEEPL_KEY}"}
    payload = {
        "text": [text],
        "target_lang": target_lang.upper(),
    }
    if source_lang:
        payload["source_lang"] = source_lang.upper()
    if context:
        payload["context"] = context

    with httpx.Client(timeout=30) as c:
        r = httpx.post(DEEPL_URL, headers=headers, data=payload)
    result = r.json()
    return {
        "translated_text": result["translations"][0]["text"],
        "detected_source_lang": result["translations"][0].get("detected_source_language"),
        "usage": result.get("usage", {}),
    }

def batch_translate(items: list, target_lang: str, source_lang: str = None) -> list:
    """Batch translate a list of strings."""
    results = []
    for item in items:
        try:
            res = translate_text(item["text"], target_lang, source_lang)
            results.append({**item, "translation": res["translated_text"]})
        except Exception as e:
            results.append({**item, "error": str(e)})
    return results

def context_aware_translate(text: str, target_lang: str, domain: str) -> str:
    """Use LLM for context-aware translation with domain expertise."""
    domain_context = {
        "legal": "This is a legal document. Preserve exact legal meaning, not just literal translation.",
        "marketing": "This is marketing copy. Make it culturally appropriate and engaging for the target audience.",
        "technical": "This is technical documentation. Preserve technical terms and precision.",
        "support": "This is customer support content. Be polite, clear, and helpful.",
    }
    instruction = domain_context.get(domain, "Translate naturally.")
    prompt = f"""{instruction}

Original text ({os.environ.get("SOURCE_LANG", "EN")}):
{text}

Translate to {target_lang}:"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    print("DeepL Translator — import and use as a module")
