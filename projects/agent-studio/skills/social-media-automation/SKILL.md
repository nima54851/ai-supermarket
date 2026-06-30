# Social Media Automation Skill

**Skill Name:** social-media-automation  
**Category:** Marketing & Growth  
**Tags:** twitter, x, linkedin, auto-post, social-media, content-calendar, growth-hacking  
**Last Updated:** 2026-06-30

## What This Skill Does

Automates social media workflows: scheduled posting, content repurposing, engagement automation, and cross-platform publishing via n8n and AI agents.

## Supported Platforms

| Platform | Capabilities |
|---|---|
| Twitter/X | Post, reply, retweet, like, follow-back, thread creation |
| LinkedIn | Post articles, comment, connect, message |
| Discord | Post to channels, schedule announcements |
| Telegram | Broadcasts, auto-reply to keywords |

## Core Workflows

### 1. Auto-Posting Pipeline
```
RSS Feed / Notion DB / CSV
    ↓
AI Content Rewriter (platform-specific tone)
    ↓
Schedule via n8n (Cron)
    ↓
Post to Twitter + LinkedIn + Discord
```

### 2. Content Repurposing
- Blog post → Twitter thread → LinkedIn article → Discord summary
- AI generates platform-native versions (length, tone, hashtags)

### 3. Engagement Automation
- Auto-like/retweet posts with target keywords
- Auto-reply with AI-generated contextual responses
- Follow/unfollow for growth (with safety limits)

### 4. Content Calendar
- Notion → n8n → scheduled posts
- Weekly batch scheduling
- A/B headline testing

## Setup

### Twitter/X API Setup
```bash
# 1. Create Twitter Developer App
# https://developer.twitter.com/en/portal/dashboard

# 2. Get credentials
# API Key, API Secret, Access Token, Access Token Secret

# 3. Configure in n8n
# Credentials → Twitter API v2
```

### LinkedIn OAuth Setup
```bash
# 1. Create LinkedIn Developer App
# https://www.linkedin.com/developers/apps

# 2. Set up OAuth 2.0
# Scopes: w_member_social, r_liteprofile, w_organization_social

# 3. Add credentials to n8n
```

## n8n Workflow Structure

```
Cron (schedule)
    ↓
Notion DB (get scheduled posts)
    ↓
AI Rewriter (Twitter version)
    ↓
[Tweet] → Twitter node
    ↓
AI Rewriter (LinkedIn version)
    ↓
[Post] → LinkedIn node
    ↓
Log results → Notion
```

## Configuration

| Variable | Description | Default |
|---|---|---|
| `POST_INTERVAL_MIN` | Minutes between posts | `60` |
| `MAX_DAILY_POSTS` | Safety cap per platform | `10` |
| `CONTENT_SOURCES` | Comma-separated source URLs | RSS feeds |
| `TIMEZONE` | Posting timezone | `Asia/Shanghai` |

## Safety & Rate Limits

| Platform | Daily Limit | Notes |
|---|---|---|
| Twitter | 50 tweets/day (free) | Use v2 API |
| LinkedIn | 5 posts/day | Organic only |
| Discord | N/A | No rate limit |

**Never exceed platform limits.** This skill includes automatic rate limiting.

## Example: AI Twitter Thread Generator

```javascript
// n8n Function: Generate Twitter Thread from Blog Post
const blogPost = $json; // from RSS or webhook
const threadCount = 5; // tweets per thread

// Call AI to break content into tweets
const thread = await fetch('http://localhost:5678/webhook/ai-thread-generator', {
  method: 'POST',
  body: JSON.stringify({
    content: blogPost.content,
    count: threadCount,
    platform: 'twitter',
    style: 'educational'
  }),
  headers: { 'Content-Type': 'application/json' }
}).then(r => r.json());

// Return array of tweets for sequential posting
return thread.tweets.map((text, i) => ({
  tweet_number: i + 1,
  text: text,
  is_thread: true
}));
```

## Files in This Skill

```
skills/social-media-automation/
├── SKILL.md                      ← This file
└── README.md                     ← Detailed guide

integrations/social-media-automation/
├── n8n-twitter-auto-post.json   ← Twitter automation workflow
├── n8n-linkedin-poster.json      ← LinkedIn posting workflow
├── n8n-content-rewriter.json     ← AI content repurposing
├── content-calendar.notion.json  ← Notion DB template
└── twitter-growth-script.py       ← Follow/unfollow automation
```

---

*Part of agent-studio by nima54851 | CC-BY-4.0*
