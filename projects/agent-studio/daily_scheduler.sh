#!/bin/bash
# agent-studio Daily Scheduler
# 每天 09:00 (北京时间) 自动执行运营任务
# 用法: ./daily_scheduler.sh &

PID_FILE="/tmp/agent_studio_scheduler.pid"
LOG_FILE="/root/.openclaw/workspace/projects/agent-studio/.scheduler_log"
LAST_RUN_FILE="/tmp/daily_ops_last_run.txt"
SCRIPT_DIR="/root/.openclaw/workspace/projects/agent-studio"

# 如果已在运行则退出
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat $PID_FILE)
    if kill -0 $OLD_PID 2>/dev/null; then
        echo "[$(date)] Scheduler already running as PID $OLD_PID"
        exit 0
    fi
fi

echo $$ > "$PID_FILE"
echo "[$(date '+%Y-%m-%d %H:%M')] Scheduler started (PID $$)" >> "$LOG_FILE"

TARGET_HOUR=9   # 北京时间 09:00
TARGET_MIN=0

while true; do
    NOW_HOUR=$(date '+%-H')    # -%H = 无前导零
    NOW_MIN=$(date '+%-M')
    TODAY=$(date '+%Y-%m-%d')
    LAST=$(cat "$LAST_RUN_FILE" 2>/dev/null | cut -d' ' -f1)

    # 目标时间到达且今天未运行
    if [ "$NOW_HOUR" = "$TARGET_HOUR" ] && [ "$NOW_MIN" -le 5 ] && [ "$LAST" != "$TODAY" ]; then
        echo "[$(date)] 🕘 Running daily ops..." >> "$LOG_FILE"
        cd "$SCRIPT_DIR"
        GITHUB_TOKEN="$GITHUB_TOKEN" \
            python3 daily_ops.py >> "$LOG_FILE" 2>&1
        echo "$TODAY $(date '+%H:%M')" > "$LAST_RUN_FILE"
        echo "[$(date)] ✅ Daily ops complete" >> "$LOG_FILE"
        # 等待下一分钟避免重复触发
        sleep 65
    fi

    sleep 55
done
