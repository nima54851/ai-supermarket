# Logging Automation Skill

> AI Agent 技能：自动化日志收集、结构化、分析与告警

## 功能

将散乱的日志流变成可操作的情报。覆盖日志采集、结构化解析、AI 异常检测、告警路由全链路。

## 核心场景

- **日志采集：** 从服务器、Kubernetes、容器收集日志 → 结构化存储
- **AI 分析：** LLM 自动识别异常模式、根因分析、日志摘要
- **告警路由：** 异常 → n8n → Slack/PagerDuty/钉钉/飞书
- **可观测性：** 日志 + 指标 + 链路追踪 三合一

## 包含内容

```
skills/logging-automation/
├── SKILL.md                        ← 本文件
├── log_parser.py                   ← 结构化日志解析器（JSON/CSV/纯文本）
├── log_analyzer.py                 ← AI 日志异常检测（基于 LLM）
├── log_enricher.py                 ← 日志字段富化（IP→地理/服务→团队）
├── prompts/
│   ├── log-summary-prompt.md        ← 日志摘要 prompt
│   └── log-root-cause-prompt.md    ← 根因分析 prompt
└── integrations/
    └── logging-automation/
        └── n8n-log-collector.json ← 日志采集 + AI 分析 + 告警 n8n workflow
```

## n8n 工作流

```
[Log Sources] → [Webhook In] → [Parse JSON] → [AI Log Analyzer]
                                                           ↓
                                              [Anomaly Score > 0.8?]
                                              ↓ Yes                    ↓ No
                                        [Route Alert]           [Store ElasticSearch]
                                              ↓                         ↓
                                    [Slack / PagerDuty]          [Kibana Dashboard]
```

## 使用方法

### 1. 收集日志

```bash
# 采集本地日志
python3 log_parser.py --input /var/log/syslog --format text --output parsed.jsonl

# 采集 JSON 日志
python3 log_parser.py --input app.log --format json --output parsed.jsonl
```

### 2. AI 分析异常

```bash
# 分析日志异常
python3 log_analyzer.py --input parsed.jsonl \
  --prompt prompts/log-root-cause-prompt.md \
  --api openai \
  --model gpt-4o-mini
```

### 3. 富化日志

```bash
# IP → 地理位置 / 服务名 → 团队
python3 log_enricher.py --input parsed.jsonl --output enriched.jsonl
```

## AI Prompt 示例

```markdown
## log-summary-prompt.md

你是一个 SRE 工程师。请分析以下日志片段：

1. 识别 ERROR/WARN 条目
2. 归类问题类型（数据库/网络/认证/超时/内存）
3. 给出 3 条最可能的根因
4. 给出修复建议（1-2句）

输出格式：JSON
```

## 技术栈

- 日志采集：Filebeat / Fluentd / Vector
- 存储：Elasticsearch / Loki / ClickHouse
- 可视化：Kibana / Grafana / Datadog
- 告警：PagerDuty / OpsGenie / 自建 n8n

## 适用工具

- n8n-workflow-automation
- monitoring-alerting-automation
- webhook-automation

---

*版本 1.0 | 2026-07-11*
