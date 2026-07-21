# Voice AI Automation Skill

**分类:** 语音 AI · 自动化
**功能:** 将语音输入转为 AI 处理的端到端自动化管道，支持电话、语音助手、实时转录场景
**适用场景:** 客服电话自动化、AI 语音播报、语音指令执行、电话机器人

---

## 工作原理

```
用户语音 → Whisper ASR → LLM 理解意图 → 工具执行 → TTS 播报 → 用户
```

---

## 核心流程

### 1. 语音识别（Whisper）
- 实时语音转文字
- 支持中文/英文/多语言
- 噪音过滤、回声消除

### 2. 意图分类（LLM）
- Zero-shot 意图识别
- 多轮对话状态管理
- 上下文窗口保留

### 3. 任务执行
- 查数据库 / 调用 API
- n8n workflow 触发
- 多工具协调

### 4. 语音播报（TTS）
- ElevenLabs / Azure TTS
- 流式输出，逐句播报
- 支持情感语音

---

## n8n Workflow（voice-ai-pipeline.json）

```json
{
  "name": "Voice AI Pipeline",
  "nodes": [
    {
      "name": "Webhook (Voice Input)",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "voice-input",
        "rawBody": false
      }
    },
    {
      "name": "Whisper STT",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.openai.com/v1/audio/transcriptions",
        "method": "POST",
        "body": {
          "model": "whisper-1"
        }
      }
    },
    {
      "name": "LLM Intent Classifier",
      "type": "@n8n/n8n-nodes-langchain.chatOpenAi",
      "parameters": {
        "model": "gpt-4o",
        "prompt": "识别用户意图，分类为：查询、执行、投诉、转人工"
      }
    },
    {
      "name": "Execute Task",
      "type": "n8n-nodes-base.switch",
      "parameters": {
        "dataType": "string",
        "valueComparison": "{{ $json.intent }}"
      }
    },
    {
      "name": "TTS Response",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.elevenlabs.io/v1/text-to-speech/{{ $json.voice_id }}",
        "method": "POST"
      }
    }
  ]
}
```

---

## 快速开始

### 步骤 1：配置 Whisper API
```bash
# 环境变量
export OPENAI_API_KEY="sk-..."
```

### 步骤 2：配置 ElevenLabs TTS
```bash
export ELEVENLABS_API_KEY="..."
export VOICE_ID="rachel"  # 选择音色
```

### 步骤 3：导入 n8n Workflow
```bash
curl -X POST http://localhost:5678/webhook/voice-input \
  -H "Content-Type: application/json" \
  -d @integrations/voice-ai-automation/n8n-voice-pipeline.json
```

### 步骤 4：启动语音服务
```bash
python3 scripts/voice_server.py --port 8080
```

---

## 适用场景示例

| 场景 | 输入 | 输出 |
|------|------|------|
| 电话客服 | 客户语音 | AI 语音回答 + 工单创建 |
| 语音助手 | 语音指令 | 执行任务 + TTS 反馈 |
| 语音播报 | 文本内容 | ElevenLabs 语音流 |
| 会议记录 | 会议音频 | 文字记录 + 要点摘要 |

---

## 相关工具

- **Whisper API:** 语音转文字（OpenAI）
- **ElevenLabs:** 高质量 TTS
- **n8n:** 工作流编排
- **OpenClaw:** 意图理解 & 任务执行

---

*此技能为 OpenClaw Agent Studio 的一部分*
