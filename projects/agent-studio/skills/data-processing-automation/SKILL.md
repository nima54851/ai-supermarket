# Data Processing Automation

> Automated data pipelines for CSV, Excel, JSON, PDF, and API data — ETL, transformations, and analytics.

## Overview

Process, transform, and route data from any source to any destination. Perfect for AI agents that need to work with structured data, generate reports, or automate data workflows.

## What's Included

- `SKILL.md` — this file
- `n8n-etl-pipeline.json` — generic ETL pipeline workflow
- `csv_processor.py` — CSV/Excel processing with AI enrichment
- `pdf_extractor.py` — PDF text/table extraction
- `json_transform.py` — JSON transformation & mapping

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│  Sources    │────▶│  Transform   │────▶│  Destinations  │
│  CSV/Excel  │     │  AI Enrich   │     │  DB/API/Email  │
│  PDF/JSON   │     │  Aggregate   │     │  Dashboard     │
│  APIs       │     │  Validate    │     │  Slack/Notion  │
└─────────────┘     └──────────────┘     └────────────────┘
```

## CSV / Excel Processing

```python
# csv_processor.py
import pandas as pd
import json
from pathlib import Path
from typing import Callable, Optional


class DataProcessor:
    """Process CSV/Excel with AI enrichment."""

    def __init__(self):
        self.df: Optional[pd.DataFrame] = None

    def load_csv(self, path: str, encoding: str = "utf-8") -> "DataProcessor":
        self.df = pd.read_csv(path, encoding=encoding)
        return self

    def load_excel(self, path: str, sheet: str = 0) -> "DataProcessor":
        self.df = pd.read_excel(path, sheet_name=sheet)
        return self

    def load_json(self, path: str) -> "DataProcessor":
        """Load JSON as flat records."""
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, list):
            self.df = pd.DataFrame(data)
        else:
            self.df = pd.DataFrame([data])
        return self

    def clean(self) -> "DataProcessor":
        """Basic data cleaning."""
        self.df = self.df.dropna(how="all")
        self.df = self.df.fillna("")
        self.df = self.df.drop_duplicates()
        self.df.columns = self.df.columns.str.strip().str.lower().str.replace(" ", "_")
        return self

    def transform(self, fn: Callable) -> "DataProcessor":
        """Apply a transformation function."""
        self.df = self.df.apply(fn, axis=1)
        return self

    def add_column(self, name: str, fn: Callable) -> "DataProcessor":
        """Add a computed column."""
        self.df[name] = self.df.apply(fn, axis=1)
        return self

    def filter_rows(self, condition: str) -> "DataProcessor":
        """Filter rows using a query string."""
        self.df = self.df.query(condition)
        return self

    def enrich_with_ai(self, prompt: str, column: str, output_col: str) -> "DataProcessor":
        """Enrich a column using an AI model (via OpenClaw or Ollama)."""
        import os, json as _json, urllib.request

        def call_ai(row):
            text = str(row.get(column, ""))
            try:
                # Ollama local
                req = urllib.request.Request(
                    "http://localhost:11434/api/generate",
                    data=_json.dumps({"model": "llama3.2", "prompt": f"{prompt}: {text}", "stream": False}).encode(),
                    headers={"Content-Type": "application/json"}
                )
                resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
                return resp.get("response", "")[:500]
            except Exception:
                return f"[AI: {text[:50]}...]"

        self.df[output_col] = self.df.apply(call_ai, axis=1)
        return self

    def to_csv(self, path: str) -> None:
        self.df.to_csv(path, index=False)

    def to_excel(self, path: str) -> None:
        self.df.to_excel(path, index=False)

    def to_json(self, path: str) -> None:
        self.df.to_json(path, orient="records", indent=2)

    def summary(self) -> dict:
        return {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "column_names": list(self.df.columns),
            "memory_mb": self.df.memory_usage(deep=True).sum() / 1024 / 1024
        }


# Usage
if __name__ == "__main__":
    proc = DataProcessor()
    proc.load_csv("sales_data.csv") \
        .clean() \
        .add_column("revenue_per_item", lambda row: row["price"] * row["quantity"]) \
        .filter_rows("revenue_per_item > 50") \
        .to_excel("processed_sales.xlsx")
    print(proc.summary())
```

## PDF Extraction

```python
# pdf_extractor.py
import pdfplumber
from pathlib import Path
from typing import Literal


def extract_pdf(
    pdf_path: str,
    extract_tables: bool = True,
    extract_pages: list = None
) -> dict:
    """Extract text and tables from a PDF."""

    result = {"pages": [], "tables": [], "total_text": ""}

    with pdfplumber.open(pdf_path) as pdf:
        pages = extract_pages or list(range(len(pdf.pages)))

        for i in pages:
            page = pdf.pages[i]
            text = page.extract_text() or ""
            result["pages"].append({"page": i + 1, "text": text})
            result["total_text"] += text + "\n\n"

            if extract_tables:
                tables = page.extract_tables()
                for t in tables:
                    result["tables"].append({
                        "page": i + 1,
                        "data": t
                    })

    return result


def extract_key_value_pairs(text: str, keywords: list = None) -> dict:
    """Extract key-value pairs from text (e.g., invoices, receipts)."""
    import re
    keywords = keywords or ["date", "amount", "total", "invoice", "customer", "address"]
    pairs = {}

    for kw in keywords:
        pattern = rf"{kw}[:\s]+(.+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            pairs[kw] = match.group(1).strip()

    return pairs
```

## JSON Transformation

```python
# json_transform.py
import json
from typing import Any, Callable


class JSONTransformer:
    """Transform, map, and reshape JSON data."""

    def __init__(self, data: Any):
        self.data = data

    def flatten(self, separator: str = ".") -> dict:
        """Flatten nested JSON to dot-notation keys."""
        def _flatten(obj, prefix=""):
            items = {}
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{prefix}{separator}{k}" if prefix else k
                    items.update(_flatten(v, new_key))
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    items.update(_flatten(v, f"{prefix}[{i}]"))
            else:
                items[prefix] = obj
            return items
        return _flatten(self.data)

    def map_fields(self, mapping: dict) -> dict:
        """Rename/map fields in a dict or list of dicts."""
        if isinstance(self.data, list):
            return [{mapping.get(k, k): v for k, v in item.items()} for item in self.data]
        elif isinstance(self.data, dict):
            return {mapping.get(k, k): v for k, v in self.data.items()}

    def filter_fields(self, keep: list) -> dict:
        """Keep only specified fields."""
        if isinstance(self.data, list):
            return [{k: v for k, v in item.items() if k in keep} for item in self.data]
        elif isinstance(self.data, dict):
            return {k: v for k, v in self.data.items() if k in keep}

    def add_computed(self, field: str, fn: Callable) -> dict:
        """Add a computed field."""
        data = json.loads(json.dumps(self.data))
        if isinstance(data, list):
            for item in data:
                item[field] = fn(item)
        elif isinstance(data, dict):
            data[field] = fn(data)
        return data
```

## n8n ETL Pipeline

Import `n8n-etl-pipeline.json` — features:
- File trigger (CSV, Excel, JSON, PDF)
- AI enrichment node
- Deduplication + validation
- Output to: PostgreSQL, Slack, email, Notion, file

## Automations

### Daily Sales Report
- Trigger: schedule (daily 08:00)
- Source: CSV exports from CRM
- Transform: aggregate by product/region
- Output: email with Excel attachment + Slack notification

### Invoice Processing
- Trigger: email attachment (PDF)
- Extract: date, amount, vendor, line items
- Classify: AI categorize expense
- Output: add to Notion DB + send Slack alert

### API Data Sync
- Trigger: schedule (every 15 min)
- Source: REST API (paginated)
- Transform: normalize + deduplicate
- Output: PostgreSQL upsert

## See Also

- `skills/database-automation/` — write processed data to DB
- `skills/email-automation/` — send reports via email
- `skills/analytics-dashboard/` — visualize processed data
- `skills/docs-generator/` — generate reports from data
