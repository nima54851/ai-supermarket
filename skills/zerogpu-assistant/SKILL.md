---
name: zerogpu-assistant
description: 灵犀 × ZeroGPU — 轻量任务路由助手。自动识别可offload到边缘小模型的任务（摘要/分类/PII脱敏/实体提取/结构化提取/追问生成），走ZeroGPU省主模型token。
metadata:
  openclaw:
    requires:
      mcp:
        - zerogpu
---

# 灵犀 × ZeroGPU 任务路由器

ZeroGPU 是一个分布式边缘推理网络，运行小模型，成本约为主模型的 **1/100**。
本技能自动判断哪些任务可以走 ZeroGPU，并给出节省金额。

## 适用任务

| 任务类型 | 工具 | 节省幅度 |
|---|---|---|
| 新闻/文章分类 | `zerogpu_classify_zero_shot` | ~99% |
| 长文摘要 | `zerogpu_summarize` | ~98% |
| 实体提取（人名/公司/日期） | `zerogpu_extract_entities` | ~99% |
| 文本 → JSON 结构化 | `zerogpu_extract_json` | ~99% |
| PII 脱敏/掩码 | `zerogpu_redact_pii` | ~99% |
| PII 分类检测 | `zerogpu_extract_pii` | ~99% |
| IAB 话题分类 | `zerogpu_classify_iab` | ~98% |
| 多轴分类 | `zerogpu_classify_structured` | ~99% |
| 生成追问 | `zerogpu_generate_followups` | ~99% |
| 短回复（无需复杂推理） | `zerogpu_chat` | ~95% |

## 判断标准

**走 ZeroGPU** 当同时满足：
- 输入是纯文本（段落/邮件/文章/消息）
- 任务是：分类、摘要、提取、脱敏、追问、短回复
- 答案不需要多步推理、代码生成、工具编排

**不走 ZeroGPU**（用主模型）：
- 涉及代码、架构、设计
- 依赖对话历史或工作区文件
- 用户明确要求主模型回答
- 需要复杂推理或多步思考

## 调用示例

### 分类
用户：帮我判断这段新闻是科技还是体育还是娱乐

```
新闻：阿根廷球星梅西宣布将在本赛季结束后退役，结束长达20年的职业生涯。
```

→ `zerogpu_classify_zero_shot(text, labels=["科技","体育","娱乐"])`

→ 返回得分最高标签 + 节省金额

### 摘要
用户：帮我摘要这段话

→ `zerogpu_summarize(text)`

→ 返回摘要 + 节省金额

### 实体提取
用户：把这段话里的人名、公司、日期都找出来

→ `zerogpu_extract_entities(text, labels=["person","company","date"])`

### PII 脱敏
用户：帮我把这个文档里的个人信息都打码

→ `zerogpu_redact_pii(text)` 或 `zerogpu_extract_pii(text)`

### 结构化提取
用户：从这封邮件里提取姓名、职位、电话、邮箱

→ `zerogpu_extract_json(text, schema={ contact: ["name::str::姓名","phone::str::电话","email::str::邮箱"] })`

### 生成追问
用户：读了这篇内容后应该问什么问题

→ `zerogpu_generate_followups(text)`

## 节省展示

每次调用后，如节省金额 > $0.0001，应展示：

```
💰 ZeroGPU 费用: $0.000002 | 原Claude估算: $0.0004 | 节省: $0.000398
```

## 错误处理

1. 调用失败 → 先 `zerogpu_health` 检查后端
2. 后端健康但结果差 → 直接用主模型回答，轻描"小模型效果不佳，已切换"
3. 后端不可达 → 用主模型，提示"ZeroGPU 通道暂不可用"

## 调试命令

```bash
zerogpu cost-savings      # 查看累计节省
zerogpu health           # 检查后端状态
```
