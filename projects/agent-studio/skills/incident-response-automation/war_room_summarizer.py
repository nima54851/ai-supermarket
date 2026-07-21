#!/usr/bin/env python3
"""
War Room Summarizer
Summarizes incident war-room messages every N minutes.
Supports Slack channels, Teams, and custom webhooks.
"""
import os
import json
import httpx
from datetime import datetime, timedelta
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_slack_messages(channel_id: str, oldest: str, latest: str) -> list:
    """Fetch messages from a Slack channel."""
    token = os.environ.get("SLACK_BOT_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "channel": channel_id,
        "oldest": oldest,
        "latest": latest,
        "limit": 200,
    }
    with httpx.Client() as c:
        r = httpx.get(
            "https://slack.com/api/conversations.history",
            headers=headers,
            params=params,
        )
    data = r.json()
    return data.get("messages", []) if data.get("ok") else []

def summarize_messages(messages: list) -> str:
    """Summarize war-room messages using LLM."""
    if not messages:
        return "No messages in the last interval."
    text = "\n".join([
        f"[{m.get('ts','')}] {m.get('user','')}: {m.get('text','')}"
        for m in messages
    ])
    prompt = f"Summarize this incident war-room chat. Focus on: what's been tried, what's the current status, what's next.\n\n{text}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    return response.choices[0].message.content

def post_to_slack(channel_id: str, text: str):
    """Post a summary message to Slack."""
    token = os.environ.get("SLACK_BOT_TOKEN")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"channel": channel_id, "text": text}
    with httpx.Client() as c:
        httpx.post(
            "https://slack.com/api/chat.postMessage",
            headers=headers,
            json=payload,
        )

if __name__ == "__main__":
    print("War Room Summarizer — use with cron every 5 minutes")
