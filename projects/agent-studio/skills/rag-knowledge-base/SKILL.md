# RAG Knowledge Base Automation

> Build intelligent knowledge retrieval systems powered by your documents.

## Overview

RAG (Retrieval-Augmented Generation) connects your AI agents to real-world knowledge bases. This skill automates the full pipeline: document ingestion → chunking → embedding → vector storage → retrieval → generation.

## What's Included

- `SKILL.md` — this file
- `n8n-rag-pipeline.json` — complete RAG pipeline n8n workflow
- `rag-qa-bot.py` — Python RAG QA bot script
- `embed_and_index.py` — document embedding & indexing script

## Architecture

```
Documents (PDF/HTML/MD/TXT)
       ↓
  Text Splitter (chunk=512, overlap=64)
       ↓
  Embedding Model (OpenAI / Ollama / Cohere)
       ↓
  Vector Store (Chroma / Qdrant / Pinecone / FAISS)
       ↓
  Semantic Search (top-k retrieval)
       ↓
  LLM Generation (context-injected answer)
```

## n8n Workflow: RAG Pipeline

Import `n8n-rag-pipeline.json` into your n8n instance:

```json
{
  "nodes": [
    {
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "rag-query",
        "method": "POST"
      }
    },
    {
      "name": "Embed Query",
      "type": "@n8n/n8n-nodes-langchain.embeddingsOpenAi",
      "parameters": {
        "modelName": "text-embedding-3-small"
      }
    },
    {
      "name": "Vector Search",
      "type": "@n8n/n8n-nodes-langchain.vectorStoreChroma",
      "parameters": {
        "operation": "similaritySearch",
        "topK": 5
      }
    },
    {
      "name": "Build Context",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "const docs = $input.all(); const context = docs.map(d => d.json.text).join('\\n\\n'); return [{ json: { context } }];"
      }
    },
    {
      "name": "LLM Answer",
      "type": "@n8n/n8n-nodes-langchain.chatOpenAi",
      "parameters": {
        "modelName": "gpt-4o",
        "messages": [
          {"role": "system", "content": "Answer based ONLY on the provided context. If unsure, say you don't know."},
          {"role": "user", "content": "Context:\n{{ $json.context }}\n\nQuestion: {{ $json.query }}"}
        ]
      }
    }
  ]
}
```

## Usage in OpenClaw

```python
# rag-qa-bot.py usage
from rag_qa_bot import RAGBot

bot = RAGBot(
    vector_store="chroma",
    collection="agent-docs",
    embedding_model="text-embedding-3-small"
)

# Index documents
bot.index_folder("./docs/")

# Query
answer = bot.ask("How do I set up OpenClaw?")
print(answer)
```

## Document Support

| Format | Parser | Notes |
|--------|--------|-------|
| PDF | pdfplumber / PyMuPDF | tables + text |
| HTML | BeautifulSoup | link preservation |
| Markdown | regex / mistral | header hierarchy |
| TXT | raw | line-by-line |
| CSV | pandas | row-level chunks |
| DOCX | python-docx | paragraph chunks |

## Prompt Templates

**System Prompt (RAG Agent):**
```
You are a helpful AI assistant with access to a knowledge base.
Use ONLY the information provided in the context below to answer questions.
Cite the source document in your response when applicable.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
```

**Fallback Prompt (no results):**
```
I couldn't find relevant information in the knowledge base for your question.
Try rephrasing or ask about a different topic.
```

## Embedding Providers

| Provider | Model | Pros |
|----------|-------|------|
| OpenAI | text-embedding-3-small | Best quality, paid |
| Ollama | nomic-embed-text | Free, local |
| Cohere | embed-english-v3.0 | Fast, good for non-English |
| Google | text-embedding-004 | Free tier available |

## Vector Stores

| Store | Best For | Deployment |
|-------|----------|------------|
| Chroma | Dev/small scale | Local pip install |
| Qdrant | Production | Docker + cloud |
| Pinecone | Enterprise scale | Cloud managed |
| FAISS | Single-machine | Local, no server |

## Automations

### Auto-sync Notion → Knowledge Base
- Trigger: Notion page updated
- Action: Re-embed + update vector store
- Tool: `integrations/notion-sync/` (see that skill)

### Auto-sync GitHub Docs
- Trigger: GitHub file changed
- Action: Fetch markdown → chunk → embed
- Tool: `integrations/github-actions-automation/`

## See Also

- `skills/self-hosted-ai/` — deploy Ollama for local embeddings
- `skills/database-automation/` — structured data retrieval patterns
- `integrations/notion-sync/` — Notion as content source
