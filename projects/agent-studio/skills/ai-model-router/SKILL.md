# AI Model Router Skill

## 概述
智能路由多个 LLM（OpenAI / Anthropic / Google / Ollama / Cohere），根据任务类型、预算、延迟自动选择最优模型，构建成本最优的 AI Agent。

## 核心能力
- 🧭 **智能路由**：基于任务分类（代码/写作/分析/创意）自动路由到最适合的模型
- 💰 **成本优化**：令牌成本追踪、预算上限、模型切换阈值
- ⚡ **延迟控制**：根据用户设定的最大延迟自动选择快速模型
- 🔄 **Fallback 链**：主模型失败自动切换备用模型，保证可用性
- 📊 **使用分析**：Token 消耗、成本分布、成功率可视化

## 路由策略
| 任务类型 | 推荐模型 | 理由 |
|---------|---------|------|
| 代码生成 | Claude 4 / GPT-4o | 代码能力强 |
| 快速问答 | GPT-4o-mini / Gemini Flash | 成本低、速度快 |
| 长文本分析 | Claude 3.5 / Gemini Pro | 200K 上下文 |
| 创意写作 | GPT-4o / Claude 3.5 | 质量优先 |
| 函数调用 | GPT-4o / Claude 3.5 | 结构化输出好 |

## 快速开始
```python
from openai import OpenAI
import anthropic

class ModelRouter:
    def __init__(self, budget_limit=100.0):
        self.models = {
            'gpt-4o':      {'provider': 'openai',   'cost_per_1k': 0.015, 'speed': 'slow'},
            'gpt-4o-mini': {'provider': 'openai',   'cost_per_1k': 0.0004, 'speed': 'fast'},
            'claude-3-5':  {'provider': 'anthropic','cost_per_1k': 0.015, 'speed': 'medium'},
            'gemini-pro':  {'provider': 'google',   'cost_per_1k': 0.005, 'speed': 'medium'},
            'llama-3':     {'provider': 'ollama',   'cost_per_1k': 0, 'speed': 'fast'},
        }
        self.budget_limit = budget_limit
        self.spent = 0.0

    def route(self, task_type, max_latency=None):
        """根据任务类型和延迟约束选择最优模型"""
        candidates = [m for m, cfg in self.models.items()
                      if self._matches_task(m, task_type)]
        if max_latency:
            candidates = [m for m in candidates
                          if self.models[m]['speed'] in ['fast', 'medium']]
        return min(candidates, key=lambda m: self.models[m]['cost_per_1k'])

    def _matches_task(self, model, task):
        rules = {
            'code': ['claude-3-5', 'gpt-4o', 'gpt-4o-mini'],
            'writing': ['gpt-4o', 'claude-3-5'],
            'quick': ['gpt-4o-mini', 'gemini-pro', 'llama-3'],
            'long_context': ['claude-3-5', 'gemini-pro'],
        }
        return model in rules.get(task, [model])

# 使用示例
router = ModelRouter(budget_limit=50.0)
selected = router.route('code', max_latency=5.0)
print(f"路由到: {selected}")
```

## n8n 集成
- `integrations/ai-model-router/model-router-workflow.json`：多模型智能路由 n8n 工作流

## 脚本
- `scripts/model_cost_tracker.py`：Token 消耗追踪与报告
- `scripts/latency_benchmark.py`：模型延迟基准测试

## 参考资料
- OpenAI Router: https://github.com/anthropics/anthropic-cookbook
- LiteLLM: https://docs.litellm.ai/
- GPTRouter: https://github.com/ok/isomorphic-git
