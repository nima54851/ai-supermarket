#!/usr/bin/env python3
"""
Batch Translator
Translates entire files or repositories in batch mode.
"""
import os
import json
import glob
from pathlib import Path
from deepl_translator import translate_text, context_aware_translate, batch_translate
from quality_scorer import score_translation

def translate_file(input_path: str, output_path: str, target_lang: str, domain: str = "technical") -> dict:
    """Translate a single file and write output."""
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Split into chunks (500 chars each for API limits)
    chunks = [content[i:i+500] for i in range(0, len(content), 500)]
    translated = []
    for chunk in chunks:
        t = context_aware_translate(chunk, target_lang, domain)
        translated.append(t)
    result = "\n".join(translated)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)
    return {"input": input_path, "output": output_path, "lang": target_lang, "chunks": len(chunks)}

def translate_directory(input_dir: str, output_dir: str, target_lang: str, pattern: str = "*.md") -> list:
    """Translate all matching files in a directory."""
    results = []
    for path in glob.glob(f"{input_dir}/{pattern}"):
        rel = Path(path).relative_to(input_dir)
        out_path = Path(output_dir) / target_lang.upper() / rel
        result = translate_file(path, str(out_path), target_lang)
        results.append(result)
    return results

if __name__ == "__main__":
    import sys
    args = json.loads(sys.stdin.read())
    results = translate_directory(args["input_dir"], args["output_dir"], args["target_lang"])
    print(json.dumps(results, indent=2))
