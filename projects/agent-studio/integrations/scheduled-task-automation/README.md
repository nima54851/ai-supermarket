# Scheduled Task Automation Integration

n8n workflow + Python 脚本，用于跨平台的定时任务自动化。

## 文件说明

- `n8n-scheduled-workflow.json` — n8n 定时任务工作流
- `scheduler_runner.py` — Python 调度器入口脚本
- `distributed_lock.py` — Redis 分布式锁实现
- `health_monitor.py` — 定时健康检查脚本

## 快速启动

```bash
# 1. 导入 n8n workflow
curl -X POST http://localhost:5678/webhook/scheduled-task \
  -H "Content-Type: application/json" \
  -d @n8n-scheduled-workflow.json

# 2. 运行 Python 调度器（独立于 n8n）
python3 scheduler_runner.py

# 3. 运行健康检查（每小时执行）
python3 health_monitor.py &
```

## 预置调度任务

| 任务 | 频率 | 说明 |
|------|------|------|
| GitHub 运营报告 | 每天 09:00 | Star/Fork/Issue 统计上报 |
| 健康检查 | 每 30 分钟 | n8n/OpenClaw 服务状态 |
| 数据库备份 | 每天 03:00 | PostgreSQL 增量备份 |
| 日志清理 | 每周一 00:00 | 清理 7 天前日志 |
| 依赖检查 | 每周三 09:00 | 检查 pip/npm 更新的 |

## n8n Workflow 定时触发配置

```json
{
  "trigger": {
    "type": "cron",
    "config": {
      "hour": 9,
      "minute": 0
    }
  }
}
```

修改 `n8n-scheduled-workflow.json` 中的 cron 配置可自定义触发时间。

## 健康检查配置（health_monitor.py）

```python
# 配置检查项
HEALTH_CHECKS = {
    "n8n": "http://localhost:5678",
    "openclaw": "http://localhost:18432",
    "github_api": "https://api.github.com",
    "postgres": "localhost:5432"
}

# 告警阈值
ALERT_THRESHOLDS = {
    "response_time_ms": 3000,
    "failed_checks": 3
}
```

## 日志输出

```
[2026-07-03 09:00:00] Scheduler started
[2026-07-03 09:00:01] Task: daily_report — acquired lock
[2026-07-03 09:00:05] Task: daily_report — SUCCESS
[2026-07-03 09:00:05] Task: daily_report — released lock
[2026-07-03 09:30:00] Task: health_check — acquired lock
[2026-07-03 09:30:02] Task: health_check — SUCCESS (all services OK)
```

---

*此集成模块为 OpenClaw Agent Studio 的一部分*
