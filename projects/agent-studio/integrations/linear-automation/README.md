# Linear 自动化集成

> 将 Linear 项目管理与 AI Agent 工作流打通，实现自动化 issue 追踪、sprint规划和团队协作。

## 功能
- 🔄 Linear ↔ GitHub 双向同步（PR → Linear issue 自动关闭）
- 📋 Sprint 规划自动化（AI 分析 velocity，生成冲刺建议）
- 📊 团队看板统计（issue 分布、瓶颈检测）
- 🔔 自动化提醒（deadline 预警、状态变更通知）

## 目录结构
```
linear-automation/
├── README.md
├── n8n-linear-sync.json
├── scripts/
│   ├── linear_ai_triage.py
│   ├── sprint_planner.py
│   └── velocity_tracker.py
└── prompts/
    └── sprint-report-prompt.md
```

## n8n 工作流：Linear → GitHub 同步

```json
{
  "name": "Linear-GitHub Sync",
  "nodes": [
    {
      "name": "Linear Trigger",
      "type": "webhook",
      "parameters": {
        "path": "linear-webhook",
        "events": ["IssueData推", "CommentCreated"]
      }
    },
    {
      "name": "AI Triage",
      "type": "Code",
      "parameters": {
        "js": "
const labels = {
  'bug': 'bug',
  'feature': 'enhancement', 
  'docs': 'documentation'
};
const body = \`## Linear Issue\n\${$json.issue.title}\n\n\${$json.issue.description}\n\n**Priority:** \${$json.issue.priority}\n**Team:** \${$json.issue.team.name}\`;
return { body, labels: labels[$json.issue.label] || 'enhancement' };
        "
      }
    },
    {
      "name": "Create GitHub Issue",
      "type": "GitHub",
      "parameters": {
        "operation": "createIssue",
        "repository": "nima54851/agent-studio",
        "title": "{{ $json.issue.title }}",
        "body": "{{ $json.body }}",
        "labels": "{{ $json.labels }}"
      }
    },
    {
      "name": "Add Linear Comment",
      "type": "Linear",
      "parameters": {
        "operation": "comment",
        "issueId": "{{ $json.issue.id }}",
        "body": "✅ Synced to GitHub: {{ $json.github_issue_url }}"
      }
    }
  ]
}
```

## 核心脚本

### AI Issue 分流（linear_ai_triage.py）
```python
"""AI 自动分类 Linear Issue 并分配负责人"""
from linearSDK import LinearClient
from openai import OpenAI

LINEAR_API_KEY = os.getenv("LINEAR_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def triage_issue(issue_body: str) -> dict:
    """使用 AI 分析 issue 内容，返回优先级、类型和预估工时"""
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "system",
            "content": TRIAGE_PROMPT
        }, {
            "role": "user", 
            "content": issue_body
        }]
    )
    return json.loads(response.choices[0].message.content)

def auto_assign(issue_id: str, priority: int, issue_type: str):
    """根据 issue 类型自动分配给对应负责人"""
    assignees = {
        "bug": "dev-ops-team",
        "feature": "product-team", 
        "docs": "docs-team",
        "infra": "infra-team"
    }
    LinearClient(LINEAR_API_KEY).issues.update(
        issue_id,
        assigneeId=assignees.get(issue_type, "product-team"),
        priority=priority
    )
```

### Sprint 规划器（sprint_planner.py）
```python
"""AI 分析团队 velocity，自动生成下一个 Sprint 的 issue 分配建议"""
from datetime import datetime, timedelta

def analyze_velocity(team_id: str, weeks: int = 4) -> dict:
    """计算团队 velocity"""
    issues = LinearClient(LINEAR_API_KEY).issues.filter(
        team_id=team_id,
        completed_after=datetime.now() - timedelta(weeks=weeks)
    )
    return {
        "completed": len(issues),
        "total_points": sum(i.estimate or 0 for i in issues),
        "avg_per_week": sum(i.estimate or 0 for i in issues) / weeks,
        "bottlenecks": detect_bottlenecks(issues)
    }

def suggest_sprint(team_id: str) -> list:
    """AI 生成下一个 Sprint 建议"""
    velocity = analyze_velocity(team_id)
    backlog = get_backlog_issues(team_id)
    
    prompt = f"""
团队 velocity 分析：
- 过去4周完成：{velocity['completed']} issues
- 总 Story Points：{velocity['total_points']}
- 周均速度：{velocity['avg_per_week']} points

待办事项（按优先级）：
{format_issues(backlog)}

请按以下格式给出 Sprint 建议：
1. 建议纳入的 issues（总 points 不超过 velocity 的 80%）
2. 每个 issue 的完成顺序理由
3. 风险点提示
"""
    return ai_suggest(prompt)
```

### Velocity 追踪（velocity_tracker.py）
```python
"""每日追踪团队 velocity，检测是否有延迟风险"""
import schedule

def daily_velocity_report():
    teams = get_teams()
    report = []
    
    for team in teams:
        v = analyze_velocity(team.id, weeks=2)
        velocity_target = get_sprint_target(team.active_sprint_id)
        
        if v['avg_per_week'] < velocity_target * 0.7:
            report.append(f"⚠️ {team.name}: velocity 低于目标的 70%，可能无法按时完成 Sprint")
        else:
            report.append(f"✅ {team.name}: velocity 正常 ({v['avg_per_week']:.1f} pts/week)")
    
    send_to_slack("\n".join(report))

schedule.every().day.at("09:00").do(daily_velocity_report)
```

## 触发条件

| 事件 | 自动化动作 |
|---|---|
| Linear 新建 Issue | AI triage → 自动分配 → 通知负责人 |
| Issue 状态变更 | 更新相关 Slack/Discord 频道 |
| PR 合并到 main | 关闭对应 Linear Issue |
| Sprint 第一天 | AI 生成 Sprint plan |
| Sprint 最后2天 | 检测 velocity，预警延迟风险 |

## 环境变量
```bash
LINEAR_API_KEY=lin_api_xxxxx
LINEAR_TEAM_ID=team_xxxxx
GITHUB_TOKEN=ghp_xxxxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/xxxxx
```

## 安装
```bash
pip install linear-sdk openai schedule
cp .env.example .env
# 填写 LINEAR_API_KEY 等配置
```

## 在 OpenClaw Agent 中使用
```python
# 使用 Linear MCP 或直接调用 API
result = await agent.run("""
查看 Linear team {team_id} 的当前 Sprint 状态，
分析是否有延风险，并生成一份 5 条以内的行动建议
""")
```

---

*适用于 AI Agent 开发者的项目管理自动化工具*
