# GitHub 认证指南

## 方法 1：浏览器认证（推荐）

### 步骤：
1. **打开终端**（在你的电脑上）
2. **运行命令**：
   ```bash
   gh auth login --web
   ```
3. **浏览器打开**：按提示在浏览器中完成认证
4. **授权访问**：授权 GitHub CLI 访问你的账号

### 生成个人访问令牌：
1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token"
3. 选择权限：至少需要 `repo` 权限
4. 生成并复制令牌

## 方法 2：使用令牌认证

### 如果你已有令牌：
```bash
# 方法 A：直接使用令牌
echo "你的GitHub令牌" | gh auth login --with-token

# 方法 B：设置环境变量
export GH_TOKEN=你的GitHub令牌
gh auth status  # 验证认证状态
```

## 方法 3：手动配置

### 创建配置文件：
```bash
# 创建 GitHub 配置文件
mkdir -p ~/.config/gh
cat > ~/.config/gh/config.yml << EOF
github.com:
  oauth_token: 你的GitHub令牌
  git_protocol: https
EOF
```

## 验证认证

认证后验证：
```bash
# 检查认证状态
gh auth status

# 测试 API 访问
gh api user

# 创建仓库测试
gh repo create test-repo --public --description "测试仓库"
```

## 安全提示

⚠️ **重要安全提醒**：
1. **不要分享令牌**：GitHub 令牌相当于密码
2. **使用环境变量**：不要在脚本中硬编码令牌
3. **限制权限**：只授予必要的权限
4. **定期轮换**：定期更新令牌

## 问题排查

### 常见问题：
1. **认证失败**：检查令牌是否过期或权限不足
2. **网络问题**：检查是否能访问 GitHub
3. **代理设置**：如果有代理需要配置

### 测试连接：
```bash
# 测试 GitHub API
curl -H "Authorization: token 你的令牌" https://api.github.com/user

# 测试 GitHub CLI
gh --version
```

## 下一步

认证成功后，你可以：
1. 创建 GitHub 仓库
2. 推送 NewAPI 项目
3. 配置 CI/CD
4. 部署到 GitHub Pages 或服务器