# SKILL.md — Sentiment Analysis Automation

## 概述
AI 驱动的情感分析自动化：对评论/反馈/聊天记录进行实时情感分析，自动分类情感倾向、提取关键话题、生成报告。支持多语言、多平台数据源集成。

## 核心能力
- **实时情感分类**：正面/负面/中性，自动打分（-1.0 ~ +1.0）
- **话题提取**：从文本中自动识别讨论主题/关键词
- **意图识别**：投诉、咨询、反馈、购买意向自动分类
- **趋势分析**：情感随时间变化的趋势图
- **告警触发**：负面情感超过阈值时自动通知
- **多语言支持**：中、英、日、韩等主流语言

## 典型场景
- 客服聊天实时情感监控
- 产品评论自动分析
- 社交媒体舆情监测
- NPS 分数自动预测

## 工具依赖
- OpenAI / Claude（情感分析 LLM）
- ZeroGPU（低成本批量分析）
- n8n（workflow 编排）
- Slack/Discord/Email（告警通知）

## n8n 集成
→ `integrations/sentiment-analysis-automation/n8n-sentiment-workflow.json`

## 分析维度
| 维度 | 描述 |
|---|---|
| 整体情感 | positive / negative / neutral |
| 情感强度 | -1.0（极度负面）~ +1.0（极度正面）|
| 关键话题 | 自动提取 3-5 个核心话题 |
| 意图标签 | complaint / inquiry / feedback / purchase_intent |
| 紧急程度 | low / medium / high / critical |

## 示例 API 调用
```python
import openai
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": f"Analyze sentiment: '{text}'. Return JSON with sentiment (positive/negative/neutral), score (-1 to 1), topics[], and urgency (low/medium/high)."
    }]
)
```
