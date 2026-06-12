# 元宝搜索标准版skill - OpenClaw 配置指南

## 配置来源

执行时会读取 `$HOME/.openclaw/openclaw.json` 中 `models.providers` 下的 `baseUrl` 和 `apiKey`。

脚本会将请求 URL 拼接为：

```text
<baseUrl>/rsrc/i/prosearch
```

鉴权方式使用 OpenAI 兼容的 Bearer 格式：

```text
Authorization: Bearer <apiKey>
```

## 配置 OpenClaw

OpenClaw 配置文件位置：

- Linux/MacOS: `~/.openclaw/openclaw.json`
- Windows: `%USERPROFILE%/.openclaw/openclaw.json`

添加或修改以下部分：

```json
{
  "models": {
    "providers": {
      "yuanbao": {
        "baseUrl": "https://bot-test.yuanbao.tencent.com/api/bot",
        "apiKey": "<your_api_key_here>",
        "api": "openai-completions"
      }
    }
  }
}
```

以上示例最终请求 URL 为：

```text
https://bot-test.yuanbao.tencent.com/api/bot/rsrc/i/prosearch
```

确认 `<your_api_key_here>` 为你的实际 API Key，否则警告用户当前未初始化元宝派机器人模型。

## 故障排除

### 找不到配置

- 确认配置文件路径是 `$HOME/.openclaw/openclaw.json`
- 确认 `models.providers` 中存在包含 `baseUrl` 和 `apiKey` 的 provider（优先读取 `yuanbao`）

### API 密钥无效

- 确认 `apiKey` 正确复制，没有多余空格
- 确认请求使用的是 `Authorization: Bearer <apiKey>` 格式

### URL 不正确

- 确认 `baseUrl` 不包含 `/rsrc/i/prosearch`
- 脚本会自动在 `baseUrl` 后追加 `/rsrc/i/prosearch`
