# AI Document Intelligence

> Extract, understand, and act on structured data from PDFs, scanned documents, contracts, and forms using LLM-powered document understanding.

## What This Does

Automates the extraction of structured data from unstructured documents:
- PDF parsing and text extraction (including scanned images via OCR)
- Contract clause extraction and risk analysis
- Invoice/receipt data extraction
- Form field auto-fill from documents
- Multi-document comparison and summarization
- Legal document analysis

## When to Use

- Processing incoming invoices or receipts automatically
- Extracting key clauses from NDAs or contracts
- Auto-filling CRM/database from paper forms
- Analyzing research papers or technical documentation
- Archiving documents with searchable metadata

## Core Capabilities

### PDF Text Extraction
```python
import pymupdf  # formerly PyMuPDF

doc = pymupdf.open("contract.pdf")
for page in doc:
    text = page.get_text()
    # Process with LLM for structure
```

### LLM Document Analysis Prompt
```
Extract the following structured data from this document:
- Parties involved (names, roles)
- Key dates (start, end, renewal dates)
- Financial terms (amounts, payment schedules)
- Termination clauses
- Special conditions or obligations
- Risk flags (unusual terms, missing sections)

Return as JSON.
```

### Invoice Extraction
```json
{
  "invoice_number": "INV-2024-001",
  "date": "2024-01-15",
  "vendor": {
    "name": "Acme Corp",
    "address": "123 Main St",
    "tax_id": "US123456789"
  },
  "line_items": [
    { "description": "AI Agent API calls", "qty": 1000, "unit_price": 0.002, "total": 2.00 }
  ],
  "subtotal": 2.00,
  "tax": 0.20,
  "total": 2.20,
  "currency": "USD"
}
```

### Contract Risk Analysis
```
Analyze this contract for:
1. Unusual liability clauses (unlimited liability, auto-renewal)
2. Missing protections (no SLA, no data portability)
3. Termination traps (long notice periods, penalties)
4. Data rights issues (broad IP assignment, unrestricted sharing)
5. Compliance risks (missing GDPR/CCPA clauses)

Output: Risk score (0-10), flagged clauses, recommended negotiations
```

## Architecture

```
Document → PDF Parser → Text Chunker → LLM Analysis → Structured JSON
                                     ↓
                              Action Router → CRM / Database / Email
```

## Tech Stack

- **PDF Parsing:** pymupdf (PyMuPDF), pdfplumber, OCRmyPDF
- **LLM Analysis:** GPT-4o, Claude 3, or local Ollama
- **Storage:** PostgreSQL (structured data), S3 (raw docs)
- **Pipeline:** n8n workflow orchestrator
- **UI:** Streamlit or Gradio for human review

## Quick Start

```python
# Basic PDF extraction
import pymupdf
import openai

def extract_contract_data(pdf_path: str) -> dict:
    doc = pymupdf.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "system",
            "content": "You are a legal document analyst. Extract structured data as JSON."
        }, {
            "role": "user", 
            "content": f"Extract structured data from this document:\n\n{text[:8000]}"
        }]
    )
    return json.loads(response.choices[0].message.content)
```

## n8n Integration

See `integrations/ai-document-intelligence/` for the complete pipeline:
1. Email attachment → Gmail trigger
2. PDF → Text extraction node
3. LLM → Structured data extraction
4. Validation → Database insert / human review queue
5. Notification → Slack / email confirmation

## Best Practices

- **OCR first:** Always run OCR on scanned documents before LLM analysis
- **Chunking:** Large documents → chunk by page or section (8K context limit)
- **Validation:** Always validate LLM output against schema before DB insert
- **Human review:** Flag low-confidence extractions for manual review
- **Audit trail:** Store raw PDF + extraction results + confidence scores

---

*Part of agent-studio | AI Agent Automation Toolkit*
