# Fine-Tuning Automation Skill

## 概述
自动化 LLM 微调流程：数据准备 → 训练 → 评估 → 部署，覆盖 OpenAI、Anthropic、Ollama 及开源模型（Llama、Qwen、Mistral）。

## 核心能力
- 📊 **数据集准备**：CSV/JSON/JSONL 自动清洗、去重、分词，构建高质量微调数据集
- ⚙️ **多平台训练**：OpenAI Fine-tuning API / Axolotl / LLaMA-Factory / Ollama LoRA
- 📈 **训练监控**：Loss 曲线、过拟合检测、早停（Early Stopping）
- 🧪 **自动化评估**：BLEU / ROUGE / 自定义 eval prompt 与参考答案对比
- 🚀 **一键部署**：微调后模型自动注册、版本管理、API 暴露

## 工作流编排（n8n）
- 自动触发训练任务（GitHub PR / Slack / 定时）
- 训练完成后自动跑 eval，结果推送到 Slack/Discord
- 训练失败告警 + 自动重试机制

## 适用场景
- 企业私有知识库适配
- 垂直领域 AI 助手（法律、医疗、金融）
- 特定写作风格迁移
- 特定格式输出微调（JSON/TABLE/MARKDOWN）

## 快速开始
```bash
# 1. 准备数据集
python3 scripts/prepare_dataset.py --input data/raw.jsonl --output data/train.jsonl

# 2. 上传 OpenAI 微调
openai fine-tuning.jobs.create \
  --training_file=data/train.jsonl \
  --model=gpt-4o-mini

# 3. 监控训练状态
openai fine-tuning.jobs.list

# 4. 测试微调模型
openai chat.completions.create \
  --model=ft:gpt-4o-mini:your-org:your-suffix \
  --messages=[{"role":"user","content":"Hello"}]
```

## 脚本
- `scripts/prepare_dataset.py`：数据清洗、分词、格式转换
- `scripts/eval_model.py`：自动化评估脚本
- `scripts/deploy_model.py`：模型注册 + API 部署脚本

## n8n 集成
- `integrations/fine-tuning-automation/n8n-fine-tuning-workflow.json`

## 参考资料
- OpenAI Fine-tuning: https://platform.openai.com/docs/guides/fine-tuning
- Axolotl: https://github.com/axolotl-54/axolotl
- LLaMA-Factory: https://github.com/hiyouga/LLaMA-Factory
