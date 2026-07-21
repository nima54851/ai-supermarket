#!/usr/bin/env python3
"""
Prompt Builder — structured prompt composer with templates
"""
import argparse, json, os, sys
from pathlib import Path
from datetime import datetime

PROMPT_TEMPLATES = {
    "code-review": {
        "system": "You are an expert {language} code reviewer. Analyze the provided code for security vulnerabilities, bugs, performance issues, and style violations. Respond in structured JSON format.",
        "user": "Review this {language} code:\n\n```{language}\n{code}\n```\n\nFocus areas: {focus_areas}"
    },
    "customer-support": {
        "system": "You are a helpful customer support agent. Classify the issue, draft a response, and suggest next steps. Be empathetic and clear.",
        "user": "Customer message:\n{message}\n\nCustomer history: {history}\nProduct context: {context}"
    },
    "data-extraction": {
        "system": "Extract structured entities from the text. Return valid JSON matching the schema. If a field is not present, use null.",
        "user": "Text:\n{text}\n\nSchema:\n{schema}"
    },
    "reasoning": {
        "system": "Think step by step. Show your reasoning process clearly, then provide the final answer. Verify your answer before responding.",
        "user": "Question: {question}\n\nContext: {context}"
    },
    "summarization": {
        "system": "Provide an abstractive summary followed by 3-5 key points. Be concise but capture the essential information.",
        "user": "Document:\n{text}\n\nMax summary length: {max_words} words"
    }
}

def build_prompt(template_name, **kwargs):
    if template_name not in PROMPT_TEMPLATES:
        print(f"Unknown template: {template_name}. Available: {list(PROMPT_TEMPLATES.keys())}")
        sys.exit(1)
    t = PROMPT_TEMPLATES[template_name]
    system = t["system"].format(**kwargs)
    user = t["user"].format(**kwargs)
    return f"---\ntype: {template_name}\ncreated: {datetime.now().isoformat()}\n---\n\n# System Prompt\n{system}\n\n# User Prompt Template\n{user}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", default="reasoning")
    parser.add_argument("--lang", default="python")
    parser.add_argument("--focus-areas", default="security, bugs, performance")
    parser.add_argument("--code", default="")
    parser.add_argument("--output", default="stdout")
    parser.add_argument("--json", action="store_true")
    # Additional template args
    args = parser.parse_args()
    
    prompt = build_prompt(
        args.task,
        language=args.lang,
        focus_areas=args.focus_areas,
        code=args.code,
        message="(customer message here)",
        history="(customer history here)",
        context="(product context here)",
        text="(text to process)",
        schema='{"field": "type // description"}',
        question="(question here)",
        context="(context here)",
        max_words=150
    )
    
    if args.output == "stdout":
        print(prompt)
    else:
        with open(args.output, "w") as f:
            f.write(prompt)
        print(f"Prompt written to {args.output}")

if __name__ == "__main__":
    main()
