# Cross-Platform Notification Automation

> 统一推送通知到 Email / Slack / Discord / Telegram / SMS — AI 驱动的智能告警路由

## 核心功能

- **多通道路由** — 同时发送至 5+ 通知平台
- **智能告警聚合** — 去重 + 压缩 + 优先级合并
- **A/B 测试通知文案** — 测试哪个版本打开率更高
- **时区感知** — 非工作时间静默，DND 期间延迟
- **升级策略** — 未确认自动升级（P3→P2→P1→电话）

## 通知通道

| 通道 | 用途 | 成本 |
|------|------|------|
| Email | 正式告警、报告 | 低 |
| Slack | 团队实时协作 | 免费 |
| Discord | 开发者社区 | 免费 |
| Telegram | 个人即时通知 | 免费 |
| SMS | 紧急 P1 告警 | 高 |
| Webhook | 自定义集成 | 免费 |

## 目录结构

```
cross-platform-notification/
├── SKILL.md
└── workflows/
    ├── n8n-notification-router.json    ← 核心路由 workflow
    ├── n8n-alert-aggregator.json        ← 告警聚合 workflow
    └── n8n-oncall-escalation.json      ← 升级策略 workflow
```

## 快速开始

### 1. 配置通道凭证（n8n Credentials）

在 n8n 中配置以下凭证：

```
slack-webhook:  Slack Incoming Webhook URL
discord-webhook: Discord Webhook URL
telegram-bot:  Bot Token + Chat ID
smtp:           Email SMTP 配置
twilio:         SMS（Twilio Account SID + Auth Token）
```

### 2. 发送告警

```bash
curl -X POST https://your-n8n.com/webhook/notify \
  -H "Content-Type: application/json" \
  -d '{
    "severity": "p2",
    "title": "数据库 CPU > 80%",
    "body": "prod-db-01 CPU 使用率已达 85%，持续 5 分钟",
    "channels": ["slack", "telegram", "email"],
    "source": "prometheus",
    "runbook_url": "https://wiki.example.com/runbooks/high-cpu",
    "tags": ["database", "production"]
  }'
```

### 3. 升级策略示例

```
P3 告警 → Slack（15min无响应）→ Telegram
P2 告警 → Slack + Telegram（30min无响应）→ Email + SMS
P1 告警 → 全通道立即发送（同时）→ 30min无响应→ 电话
```

### 4. 告警聚合配置

```javascript
// n8n Function Node — 聚合规则
const AGGREGATION_RULES = {
  windowMs: 5 * 60 * 1000,        // 5分钟内合并
  maxCount: 10,                     // 最多10条合并为1条
  groupBy: ["tags.service"],        // 按服务分组
  dedupBy: "fingerprint",           // 按指纹去重
};
```

## 通知模板

### Slack Block Kit

```json
{
  "blocks": [
    {
      "type": "header",
      "text": {"type": "plain_text", "text": "⚠️ [P2] 数据库 CPU 高"}
    },
    {
      "type": "section",
      "fields": [
        {"type": "mrkdwn", "text": "*服务:*\nprod-db-01"},
        {"type": "mrkdwn", "text": "*指标:*\nCPU 85%"},
        {"type": "mrkdwn", "text": "*持续:*\n5 分钟"},
        {"type": "mrkdwn", "text": "*来源:*\nPrometheus"}
      ]
    },
    {
      "type": "actions",
      "elements": [
        {"type": "button", "text": {"type": "plain_text", "text": "✅ Acknowledge"}, "action_id": "ack"},
        {"type": "button", "text": {"type": "plain_text", "text": "📖 Runbook"}, "url": "https://..."}
      ]
    }
  ]
}
```

## 相关 Skills

- `monitoring-alerting-automation/` — Prometheus + Grafana 监控告警
- `incident-response-automation/` — 事故响应与升级
- `slack-bot/` / `discord-ai-bot/` / `telegram-bot/` — 各平台 Bot 集成

---

*Version 1.0 | 2026-07-20*
