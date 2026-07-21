# Ollama Self-Hosted LLM Skill

Deploy and operate Ollama for self-hosted AI inference — local LLMs, model management, API integration, and cost optimization.

## Overview

Ollama runs open-source LLMs locally (Llama 3, Mistral, Phi, Gemma, Qwen, DeepSeek, etc.). This skill covers deployment, API setup, n8n integration, and production-grade patterns.

## Quick Setup

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.2
ollama pull mistral
ollama pull qwen2.5

# Run API server
ollama serve

# Test
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Hello, world!"
}'
```

## Use Cases

### Local AI Agent (no API costs)
OpenClaw AI Agent → Ollama API (localhost) → local LLM inference

### Document Q&A
RAG pipeline: load PDF → embed → query with Ollama

### Code Generation
DeepSeek-Coder via Ollama → code generation for automation scripts

### Multimodal
Ollama with vision models (llava, moondream) for image understanding

## n8n Integration

```json
{
  "name": "ollama-workflow",
  "nodes": [
    {"type": "n8n-nodes-base.httpRequest"},
    {"parameters": {
      "url": "http://localhost:11434/api/generate",
      "method": "POST",
      "body": {
        "model": "{{ $json.model }}",
        "prompt": "{{ $json.prompt }}",
        "stream": false
      }
    }}
  ]
}
```

## Production Patterns
1. **Model pooling** — warm up frequently-used models
2. **Cache prompts** — reuse similar embeddings
3. **Batch inference** — queue requests for throughput
4. **Health monitoring** — check model availability via API
