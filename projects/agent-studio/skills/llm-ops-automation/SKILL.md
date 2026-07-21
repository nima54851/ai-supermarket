# LLM Ops Automation Skill

> AI Agent 技能：LLM（大语言模型）运维全流程自动化

## 功能

覆盖 LLM 从部署、调用、监控、调优到成本控制的完整运维链路。适用于 OpenAI、Azure OpenAI、Anthropic、Ollama、Hugging Face 等主流 LLM 提供商。

## 核心场景

- **模型部署：** Ollama / vLLM / Hugging Face TGI 自动部署脚本
- **调用网关：** 统一 API 网关，支持模型路由、负载均衡、熔断降级
- **成本监控：** Token 消耗追踪、预算告警、成本分摊报告
- **Prompt 管理：** 版本控制、A/B 测试、性能评估
- **自动化调优：** 基于反馈的 Prompt 优化循环

## 目录结构

```
skills/llm-ops-automation/
├── SKILL.md                         ← 本文件
├── model_gateway.py                 ← 统一 LLM 网关（路由 + 熔断）
├── cost_tracker.py                 ← Token 消耗追踪 & 成本报告
├── prompt_versioner.py              ← Prompt 版本控制 & A/B 测试
├── prompts/
│   ├── llm-ops-role-prompt.md       ← LLM Ops Agent Role
│   └── cost-alert-prompt.md         ← 成本告警生成 Prompt
└── integrations/
    └── llm-ops-automation/
        └── n8n-llm-ops-workflow.json ← LLM Ops 完整 n8n workflow
```

## 模型网关架构

```
[Client] → [Model Gateway] → [Router]
                              ├─ OpenAI (GPT-4o)
                              ├─ Anthropic (Claude 3.5)
                              ├─ Ollama (Llama 3)
                              └─ Azure OpenAI (GPT-4)
```

## 使用方法

### 1. 启动统一网关

```bash
python3 model_gateway.py \
  --port 8080 \
  --routes openai,anthropic,ollama \
  --fallback ollama \
  --rate-limit 60
```

### 2. Token 成本追踪

```bash
# 追踪 API 调用成本
python3 cost_tracker.py \
  --api-key $OPENAI_API_KEY \
  --report daily \
  --alert-threshold 50.0  # $50 告警阈值
```

### 3. Prompt A/B 测试

```bash
# 启动 Prompt 版本对比
python3 prompt_versioner.py \
  --test "Is this a positive review?" \
  --variant-a prompts/v1-sentiment.md \
  --variant-b prompts/v2-sentiment.md \
  --model gpt-4o-mini \
  --runs 10
```

## n8n 工作流

```
[Webhook: LLM Request]
  → [Route by model/tag] 
  → [LLM: Cost Estimator]
  → [Log to DB]
  → [Token Budget Check] 
      → [Budget OK] → [Call LLM] → [Return Response]
      → [Budget Exceeded] → [Slack Alert] → [Reject Request]
```

## 成本对比参考

| 模型 | $1M input tokens | $1M output tokens | 适用场景 |
|------|-----------------|-------------------|---------|
| GPT-4o | $2.50 | $10.00 | 通用对话 |
| GPT-4o-mini | $0.15 | $0.60 | 高频轻量任务 |
| Claude 3.5 Sonnet | $3.00 | $15.00 | 长上下文分析 |
| Claude 3 Haiku | $0.25 | $1.25 | 快速分类 |
| Llama 3 70B (self-hosted) | ~$0 (GPU成本) | ~$0 | 成本敏感场景 |

## 适用工具

- n8n-workflow-automation
- ai-model-router
- monitoring-alerting-automation
- logging-automation

---

*版本 1.0 | 2026-07-11*
