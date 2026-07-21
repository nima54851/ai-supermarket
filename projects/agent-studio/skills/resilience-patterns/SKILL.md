# Resilience Patterns Skill

> AI Agent 技能：分布式系统韧性设计 — 容错、降级、熔断、重试、超时全链路方案

## 功能

让 AI Agent 系统在部分故障时依然可用。提供工程级韧性模式，适配 n8n、OpenClaw、自建服务。

## 核心模式

### 1. 熔断器（Circuit Breaker）
```
Closed（正常）→ 故障阈值触发 → Open（熔断）→ 超时后 → Half-Open（探测）
                                              ↓ OK
                                          Closed（恢复）
```
**状态阈值：** 失败5次 → Open → 60秒后 → Half-Open → 成功 → Closed

### 2. 重试策略（Retry with Backoff）
```
指数退避：100ms → 200ms → 400ms → 800ms → 1600ms
Jitter（随机抖动）防止惊群效应
最大重试：3次 | 超时：单次 5s
```

### 3. 限流（Rate Limiting）
```
滑动窗口限流：60 RPM
令牌桶：突发容量 10
来源识别：API Key / User ID / IP
```

### 4. 降级（Graceful Degradation）
```
主链路失败 → 降级到备用 LLM → 备用失败 → 返回缓存结果 → 缓存也没有 → 返回兜底回复
```

### 5. 超时控制（Timeout）
```
LLM 调用：30s
API 调用：10s
数据库查询：5s
```

## 目录结构

```
skills/resilience-patterns/
├── SKILL.md                          ← 本文件
├── circuit_breaker.py                ← Python 熔断器实现
├── retry_policy.py                   ← 重试策略（含指数退避 + Jitter）
├── rate_limiter.py                   ← 滑动窗口 + 令牌桶限流
├── graceful_degradation.py           ← 降级链路管理器
├── integration_test.py               ← 集成测试（模拟故障场景）
└── integrations/
    └── resilience-patterns/
        └── n8n-resilience-workflow.json ← 含熔断+重试+降级的 n8n workflow
```

## Python 熔断器示例

```python
from circuit_breaker import CircuitBreaker, CircuitOpen

cb = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

@cb
def call_llm(messages):
    response = openai.ChatCompletion.create(model="gpt-4o", messages=messages)
    return response
```

## n8n Resilience Workflow

```
[Request]
  → [Rate Limit Check]
      → [Pass] → [Try Primary LLM]
      → [Fail] → [Slack Alert] → [Return 429]
                    ↓ OK
              [Circuit Breaker Check]
                  → [Open] → [Fallback LLM]
                  → [Still Open] → [Cached Response]
                  → [Cache Miss] → [Graceful Error Response]
```

## 故障注入测试

```bash
# 模拟 API 延迟/故障
python3 integration_test.py \
  --scenarios latency,timeout,503 \
  --latency-ms 5000 \
  --failure-rate 0.3 \
  --runs 100
```

## 适用场景

- AI Agent 调用外部 API（OpenAI、Anthropic）
- n8n Workflow 调用外部服务
- 微服务间通信
- 数据库连接

## 适用工具

- n8n-workflow-automation
- llm-ops-automation
- monitoring-alerting-automation

---

*版本 1.0 | 2026-07-11*
