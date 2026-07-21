#!/usr/bin/env python3
"""
Terminology Manager
Maintains consistent domain-specific terminology across translations.
"""
import os
import json
import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(REDIS_URL)
TERM_PREFIX = "term:lang:"

def add_term(source_term: str, translations: dict, definition: str = "", domain: str = "general"):
    """Add a terminology entry."""
    key = f"{TERM_PREFIX}{source_term.lower()}:{domain}"
    entry = {"source": source_term, "translations": translations, "definition": definition, "domain": domain}
    r.set(key, json.dumps(entry))
    return entry

def get_term(source_term: str, domain: str = "general") -> dict:
    """Get a terminology entry."""
    key = f"{TERM_PREFIX}{source_term.lower()}:{domain}"
    raw = r.get(key)
    return json.loads(raw) if raw else None

def get_all_terms(domain: str = None) -> list:
    """Get all terminology entries."""
    pattern = f"{TERM_PREFIX}*"
    if domain:
        pattern = f"{TERM_PREFIX}*:{domain}"
    keys = r.keys(pattern)
    return [json.loads(r.get(k)) for k in keys]

def export_glossary(format: str = "json") -> str:
    """Export glossary in JSON or CSV format."""
    terms = get_all_terms()
    if format == "json":
        return json.dumps(terms, indent=2, ensure_ascii=False)
    elif format == "csv":
        lines = ["source_term,target_lang,translation,definition,domain"]
        for t in terms:
            for lang, trans in t["translations"].items():
                lines.append(f'{t["source"]},{lang},{trans},{t["definition"]},{t["domain"]}')
        return "\n".join(lines)
    return json.dumps(terms)

if __name__ == "__main__":
    print("Terminology Manager — use add_term() and get_term() functions")
