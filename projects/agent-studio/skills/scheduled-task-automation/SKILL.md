# Scheduled Task Automation Skill

**分类:** 自动化 · 调度
**功能:** 跨平台的定时任务自动化框架，支持 cron、事件触发、延迟队列、分布式调度
**适用场景:** 每日运营报告、定时爬取、定时推送、定时检查、周期性清理

---

## 工作原理

```
定时触发 → 任务执行器 → 条件判断 → 动作执行 → 结果记录 → 通知
```

---

## 核心功能

### 1. Cron 调度
- 标准 cron 表达式（分/时/日/月/周）
- 支持时区配置
- 秒级精度调度

### 2. 事件触发
- 文件变化触发（watch）
- HTTP webhook 触发
- 队列消息触发

### 3. 分布式调度
- 多节点竞争锁
- 避免重复执行
- 故障转移

### 4. 执行日志 & 告警
- 每次执行记录状态
- 失败自动重试（指数退避）
- 失败时发送通知

---

## 快速开始

### Python 调度器（scheduler.py）

```python
import schedule
import time
from datetime import datetime

def daily_report():
    """每日 09:00 执行 GitHub 运营报告"""
    print(f"[{datetime.now()}] 生成每日报告...")
    # 调用 n8n webhook 或执行脚本
    pass

def hourly_check():
    """每小时检查服务健康状态"""
    print(f"[{datetime.now()}] 健康检查...")
    pass

# 定时调度
schedule.every().day.at("09:00").do(daily_report)
schedule.every().hour.do(hourly_check)
schedule.every(30).minutes.do(lambda: print("每30分钟任务"))

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Cron 表达式参考

```
┌───────────── 分钟 (0-59)
│ ┌─────────── 小时 (0-23)
│ │ ┌───────── 日 (1-31)
│ │ │ ┌─────── 月 (1-12)
│ │ │ │ ┌───── 周几 (0-7, 0和7都是周日)
│ │ │ │ │
* * * * *  command
```

| 示例 | 含义 |
|------|------|
| `0 9 * * *` | 每天 09:00 |
| `*/15 * * * *` | 每 15 分钟 |
| `0 9 * * 1-5` | 工作日 09:00 |
| `0 */2 * * *` | 每 2 小时 |
| `30 23 * * *` | 每天 23:30 |

---

## n8n Workflow（scheduled-task-automation.json）

```json
{
  "name": "Scheduled Task Automation",
  "nodes": [
    {
      "name": "Cron Trigger",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "rule": {
          "interval": [
            { "field": "cron", "hours": 9, "minutes": 0 }
          ]
        }
      }
    },
    {
      "name": "Fetch Data",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.github.com/repos/nima54851/agent-studio"
      }
    },
    {
      "name": "Process & Format",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "const data = $input.first().json;\nreturn [{json: {\n  stars: data.stargazers_count,\n  forks: data.forks_count,\n  issues: data.open_issues_count,\n  timestamp: new Date().toISOString()\n}}];"
      }
    },
    {
      "name": "GitHub API Push",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.github.com/repos/nima54851/agent-studio/contents/.github/stats.json",
        "method": "PUT",
        "body": {
          "message": "Update stats",
          "content": "{{ $json.encoded }}"
        }
      }
    },
    {
      "name": "Notify (if failed)",
      "type": "n8n-nodes-base.errorTrigger",
      "parameters": {}
    }
  ]
}
```

---

## Linux Crontab 集成

```bash
# 编辑 crontab
crontab -e

# 添加任务
0 9 * * * /root/.openclaw/workspace/projects/agent-studio/scripts/daily_operations.sh >> /var/log/daily_ops.log 2>&1
*/30 * * * * /root/.openclaw/workspace/projects/agent-studio/scripts/health_check.sh
0 */6 * * * /root/.openclaw/workspace/projects/agent-studio/scripts/backup.sh

# 查看 crontab
crontab -l

# 查看执行日志
grep CRON /var/log/syslog
```

---

## 分布式调度（Redis + Python）

```python
import redis
import hashlib
import time

r = redis.Redis(host='localhost', port=6379, db=0)
LOCK_TTL = 300  # 5分钟锁

def acquire_lock(task_name):
    """竞争分布式锁"""
    lock_key = f"scheduler:lock:{task_name}"
    lock_value = hashlib.md5(str(time.time()).encode()).hexdigest()
    return r.set(lock_key, lock_value, nx=True, ex=LOCK_TTL)

def run_task(task_name, func):
    """带锁的任务执行"""
    if acquire_lock(task_name):
        print(f"[{task_name}] 获得锁，开始执行")
        func()
        r.delete(f"scheduler:lock:{task_name}")
        print(f"[{task_name}] 执行完成，释放锁")
    else:
        print(f"[{task_name}] 未获得锁，跳过执行（其他节点正在运行）")
```

---

## 告警配置

```bash
# 监控失败任务
tail -f /var/log/daily_ops.log | grep -i error

# 邮件告警（sendmail）
echo "任务执行失败" | mail -s "[Agent Studio] 任务失败告警" admin@example.com

# Telegram 告警
curl -s "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
  -d "chat_id=$CHAT_ID" \
  -d "text=⚠️ agent-studio 每日任务执行失败"
```

---

*此技能为 OpenClaw Agent Studio 的一部分*
