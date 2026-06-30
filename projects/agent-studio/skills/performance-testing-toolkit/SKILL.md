# SKILL.md — Performance Testing Toolkit

> 让 AI Agent 具备对 Web API、WebSocket、微服务进行性能压测的能力。

## 技能说明

本技能帮助开发者快速构建性能测试脚本：
- HTTP 压测（wrk 风格 + Python 版）
- WebSocket 并发连接测试
- n8n 工作流执行时间监控
- OpenClaw MCP 响应时间基准测试
- 生成压测报告（latency/p99/QPS）

## 核心脚本

| 脚本 | 功能 |
|------|------|
| `scripts/http_stress.py` | Python HTTP 压测，支持并发 + 延迟分布 |
| `scripts/websocket_stress.py` | WebSocket 并发连接测试 |
| `scripts/workflow_benchmark.py` | n8n workflow 执行耗时基准 |
| `scripts/report_generator.py` | 生成 Markdown 压测报告 |

## 使用方法

### 1. HTTP 压测
```bash
python3 scripts/http_stress.py \
  --url https://api.example.com/health \
  --concurrency 50 \
  --duration 30s \
  --method GET
```

### 2. WebSocket 压测
```bash
python3 scripts/websocket_stress.py \
  --url wss://api.example.com/ws \
  --connections 100 \
  --duration 60s
```

### 3. n8n Workflow 基准测试
```bash
python3 scripts/workflow_benchmark.py \
  --webhook http://localhost:5678/webhook-test/my-workflow \
  --iterations 50 \
  --concurrency 5
```

## 输出示例

```
=== HTTP Stress Test ===
Target: https://api.example.com/health
Duration: 30s | Concurrency: 50

Total requests:  12,450
Success rate:     99.8%
Avg latency:      45ms
p50 latency:      38ms
p90 latency:      72ms
p99 latency:     143ms
Max latency:     891ms
QPS:              415 req/s
```

## 集成 OpenClaw

在 OpenClaw 中使用此技能：
```
性能测试 Agent → 分析需求 → 生成压测脚本 → 执行 → 汇报结果
```

## 依赖

```bash
pip install httpx websockets aiohttp
```

## 注意事项

- 压测前确保目标服务有足够的容错能力
- 并发数不宜超过服务器承受上限（建议从低并发开始）
- 生产环境压测请使用专门的压测工具（k6、locust）
