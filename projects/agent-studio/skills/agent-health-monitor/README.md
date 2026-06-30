# agent-health-monitor

> GitHub Actions + Webhook → AI 自动健康检查 · 监控 agent 服务状态

## 📦 包含

```
agent-health-monitor/
├── SKILL.md           ← OpenClaw skill 定义
├── health_check.py    ← 健康检查脚本
└── alert_workflow.json ← n8n 告警 workflow
```

## ⚡ 快速使用

```bash
# 手动触发健康检查
python3 health_check.py --service your-agent-url --threshold 500

# Webhook 模式（GitHub Actions 回调）
python3 health_check.py --webhook-url https://your-n8n.io/webhook/health
```

## 🔧 配置环境变量

```bash
export HEALTH_ENDPOINT=http://localhost:5678/api/v1/health
export ALERT_WEBHOOK=https://hooks.slack.com/xxx
export ALERT_THRESHOLD_MS=1000
```

## 📊 支持的检查项

| 检查项 | 说明 | 默认阈值 |
|--------|------|---------|
| HTTP 响应码 | 服务是否可达 | 2xx |
| 响应时间 | API 延迟 | 1000ms |
| n8n 活跃工作流数 | 自动化健康 | ≥1 |
| 错误率 | 最近 5 分钟错误 | <5% |
| 磁盘使用率 | 本地存储 | <90% |

## 🚨 告警触发时

1. 发送 Slack/Discord/Telegram 通知
2. 记录到 `/tmp/health_log.jsonl`
3. 自动尝试重启服务（可选）

---

*Powered by [agent-studio](https://github.com/nima54851/agent-studio)*
