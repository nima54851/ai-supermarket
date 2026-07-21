# Voice AI Automation Integration

n8n workflow + 配置文件，用于构建完整的语音 AI 自动化管道。

## 文件说明

- `n8n-voice-pipeline.json` — 完整的语音 AI 工作流
- `whisper_config.json` — Whisper API 配置
- `tts_config.json` — ElevenLabs TTS 配置
- `voice_server.py` — 本地语音 HTTP 服务器

## 快速启动

```bash
# 1. 配置环境变量
cp whisper_config.json.example whisper_config.json
# 编辑 whisper_config.json 填入你的 API Key

# 2. 配置 TTS
cp tts_config.json.example tts_config.json
# 编辑 tts_config.json 填入 ElevenLabs API Key 和 Voice ID

# 3. 导入 n8n workflow
curl -X POST http://localhost:5678/webhook/voice-pipeline \
  -H "Content-Type: application/json" \
  -d @n8n-voice-pipeline.json

# 4. 启动语音服务器
python3 voice_server.py --port 8080

# 5. 测试
curl -X POST http://localhost:8080/transcribe \
  -F "audio=@test_audio.wav"
```

## 工作流节点说明

1. **Webhook** — 接收语音输入（wav/mp3/ogg）
2. **Whisper STT** — 调用 OpenAI Whisper 转文字
3. **Intent Classifier** — GPT-4o 意图分类
4. **Task Router** — 根据意图路由到不同处理节点
5. **Execute Action** — 执行对应任务（查询/操作/转人工）
6. **TTS Generator** — ElevenLabs 语音合成
7. **Response** — 返回音频流给用户

## 支持的意图类型

- `query` — 查询类问题（天气、百科、数据查询）
- `execute` — 操作类指令（开关灯、发消息、创建任务）
- `complaint` — 投诉建议 → 转工单系统
- `transfer_human` — 转人工客服
- `unknown` — 无法识别 → 礼貌引导

## 测试用例

```bash
# 测试语音转文字
python3 voice_server.py test --audio samples/test.wav

# 测试完整管道
curl -X POST http://localhost:5678/webhook/voice-pipeline \
  -F "audio=@samples/test.wav"
```

---

*此集成模块为 OpenClaw Agent Studio 的一部分*
