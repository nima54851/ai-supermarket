# Ollama Self-Hosted LLM Guide

## Model Catalog (Recommended)

| Model | Size | Best For | RAM Required |
|-------|------|----------|-------------|
| llama3.2 | 2GB | General chat, reasoning | 4GB |
| mistral | 4GB | Code, instructions | 8GB |
| qwen2.5 | 4GB | Multilingual, long context | 8GB |
| deepseek-coder | 4GB | Code generation | 8GB |
| llava | 4GB | Vision + text | 8GB |
| phi3 | 2GB | Lightweight tasks | 4GB |

## GPU Acceleration

```bash
# NVIDIA GPU
ollama pull llama3.2
# Automatically uses CUDA if available

# AMD ROCm
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

## Environment Variables
```
OLLAMA_HOST=0.0.0.0:11434
OLLAMA_MODELS=/data/ollama/models
OLLAMA_NUM_PARALLEL=4
OLLAMA_MAX_LOADED_MODELS=2
```

## Monitoring
```bash
# List running models
curl http://localhost:11434/api/tags

# Check model info
ollama show llama3.2

# GPU usage
nvidia-smi
```
