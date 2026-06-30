#!/bin/bash
LOGFILE="/tmp/trending.log"
SCRIPT="/root/.openclaw/workspace/projects/github-trending/scraper.py"
LAST_RUN_FILE="/tmp/trending_last_run.txt"

echo "[$(date)] 🚀 调度器启动" >> $LOGFILE

while true; do
    NOW=$(date +%H)
    LAST=$(cat $LAST_RUN_FILE 2>/dev/null)
    TODAY=$(date +%Y-%m-%d)
    
    # 每天 9:00 运行
    if [ "$NOW" = "09" ] && [ "$LAST" != "$TODAY" ]; then
        echo "[$(date)] 📡 开始抓取 GitHub Trending..." >> $LOGFILE
        cd /root/.openclaw/workspace/projects/github-trending
        python3 $SCRIPT >> $LOGFILE 2>&1
        echo $TODAY > $LAST_RUN_FILE
        echo "[$(date)] ✅ 完成" >> $LOGFILE
    fi
    
    sleep 300  # 每5分钟检查一次
done
