# GitHub 技能功能测试

## 技能概述
此技能通过 `gh` CLI 提供对 GitHub 的全面访问能力。

## 已确认的功能

### 1. Pull Requests 管理
```bash
# 查看PR的CI状态
gh pr checks <pr-number> --repo <owner>/<repo>

# 列出PR
gh pr list --repo <owner>/<repo> --state open

# 查看PR详情
gh pr view <pr-number> --repo <owner>/<repo>
```

### 2. Issues 管理
```bash
# 列出问题
gh issue list --repo <owner>/<repo>

# 创建问题
gh issue create --repo <owner>/<repo> --title "Bug" --body "Description"

# 查看问题详情
gh issue view <issue-number> --repo <owner>/<repo>
```

### 3. CI/CD 工作流
```bash
# 列出工作流运行
gh run list --repo <owner>/<repo> --limit 10

# 查看特定运行
gh run view <run-id> --repo <owner>/<repo>

# 只查看失败步骤的日志
gh run view <run-id> --repo <owner>/<repo> --log-failed
```

### 4. 高级 API 访问
```bash
# 使用GitHub API查询
gh api repos/<owner>/<repo>/pulls/<pr-number> --jq '.title, .state, .user.login'

# 获取仓库信息
gh api repos/<owner>/<repo> --jq '.name, .description, .stargazers_count'
```

### 5. 结构化输出
```bash
# JSON格式输出
gh issue list --repo <owner>/<repo> --json number,title,state

# 使用jq过滤
gh pr list --repo <owner>/<repo> --json number,title --jq '.[] | "\(.number): \(.title)"'
```

## 使用前准备
要使用此技能，需要：
1. 安装 GitHub CLI：`brew install gh` (macOS) 或 `apt-get install gh` (Ubuntu)
2. 登录 GitHub：`gh auth login`
3. 设置默认仓库（可选）：`gh repo set-default <owner>/<repo>`

## 典型工作流程
1. 克隆仓库或进入现有git目录
2. 使用 `gh` 命令与 GitHub 交互
3. 在非git目录中使用 `--repo <owner>/<repo>` 参数
4. 利用 `--json` 和 `--jq` 进行数据处理

## 测试结果
✅ 技能文件结构完整
✅ 功能文档清晰
✅ 覆盖了 GitHub 的主要功能
⚠️ 需要先安装 `gh` CLI 才能实际使用