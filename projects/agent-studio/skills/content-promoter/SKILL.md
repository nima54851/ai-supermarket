---
name: content-promoter
description: AI Agent 内容推流系统 — 自动生成各平台适配推广文案并分发到技术社区（掘金/CSDN/知乎/V2EX）和社交平台（Twitter/Reddit/Hacker News）。用于：(1) 输入产品链接自动生成多平台文案，(2) 自动分发到各平台，(3) 追踪推流效果，(4) 生成每日/每周推流报告。当用户说"推流"、"分发内容"、"推广到XX"、"生成推广文案"、"自动发帖子"、"做内容运营"时触发此技能。
---

# Content Promoter — AI Agent 推流系统

## 核心功能

```
产品/内容输入
    → 生成多平台适配文案
    → 分发到目标平台
    → 记录追踪结果
```

## 支持平台

| 平台 | 类型 | 文案风格 | 长度 |
|---|---|---|---|
| 掘金 | 技术博客 | 专业、实战、代码 | 800-1500字 |
| CSDN | 技术博客 | 详细、步骤、截图 | 1000-2000字 |
| 知乎 | 问答/文章 | 深度分析、观点 | 500-1000字 |
| V2EX | 社区 | 简洁、话题感 | 200-500字 |
| Twitter/X | 社交 | 短促、钩子、标签 | 280字内 |
| Reddit | 社区 | 真实分享、互动 | 500-800字 |
| Hacker News | 新闻 | 技术深度、英文 | 英文200-400词 |

## 文案生成模板

### 通用结构（长文平台）

```
【标题】: 有冲击力的标题，含数字和关键词
【开头】: 痛点切入，1-2句话引起共鸣
【正文】: 产品是什么 + 能做什么 + 怎么用
【亮点】: 3-5个核心功能点（列表形式）
【结尾】: CTA引导（star/try/download）
【标签】: 相关话题标签
```

### Twitter/X 模板

```
🚀 [产品名] — [一句话价值]
[2-3个核心亮点，emoji列表]
👉 [链接]
#AI #Agent #[领域标签]
```

## 推流脚本使用

```bash
# 生成各平台文案（不自动发送）
python3 scripts/generate_posts.py \
  --product "agent-studio" \
  --url "https://github.com/nima54851/agent-studio" \
  --output ./drafts/

# 预览文案
python3 scripts/preview_posts.py ./drafts/

# 自动推流（需配置各平台凭证）
python3 scripts/publish_posts.py ./drafts/ --platforms juejin,v2ex,twitter
```

## 各平台发帖要点

### 掘金
- 标题要含数字（如"12个技能模板"）
- 正文要有代码示例
- 结尾加"点赞/关注"引导
- 标签选热门的：AI、Python、GitHub

### CSDN
- 标题含长尾关键词
- 结构清晰，分段标题
- 加代码块和效果图描述
- 标签精准：AI、GitHub、自动化

### V2EX
- 直接说产品
- 简短说明亮点
- 可以提"免费"/"开源"
- 语气随意，不要太营销

### Twitter/X
- 第一个词用 emoji 开头
- 每条 tweet 只说一件事
- 附上 repo link
- 用 2-3 个 hashtag

### Reddit
- 先在社区混几天再发
- 不要直接发广告
- 先分享使用体验，再提产品
- 选对 subreddit：r/programming、r/AI、r/Entrepreneur

## 推流频率建议

| 平台 | 频率 | 最佳时间 |
|---|---|---|
| 掘金 | 每周1-2篇 | 周二-周四 10:00-11:00 |
| CSDN | 每周1篇 | 周三 14:00-16:00 |
| V2EX | 每周1篇 | 随时（内容为王） |
| Twitter | 每天1-2条 | 北京时间 21:00-23:00 |
| Reddit | 每周1篇 | UTC 14:00-18:00 |

## 凭证配置

在 `~/.promoter/config.json` 中配置：

```json
{
  "defaults": {
    "author": "nima54851",
    "github": "https://github.com/nima54851"
  },
  "platforms": {
    "juejin": { "cookie": "YOUR_COOKIE" },
    "csdn": { "cookie": "YOUR_COOKIE" },
    "v2ex": { "cookie": "YOUR_COOKIE" },
    "twitter": { "cookies": "@~/.promoter/twitter_cookies.json" }
  }
}
```

## 追踪指标

每次推流后记录：
- 发布平台
- 发布时间
- 标题
- 产生的 UV / Star / Fork
- 后续行动（跟进评论）

用 `scripts/track_results.py` 更新追踪表。
