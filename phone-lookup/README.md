# 手机号归属地精准查询 Bot

基于工信部公开号段数据库开发的 Telegram Bot，支持 11 位手机号精准查询（省+城市级别）。

## 功能特性

- 📱 **11位精准查询** → 精确到省份 + 城市
- 🏢 **运营商识别** → 移动 / 联通 / 电信 / 广电 / 虚拟运营商
- 📡 **号段类型** → 识别 2G / 3G / 4G / 5G / 物联网号段
- 🌐 **国际格式支持** → 自动识别 +86 格式
- 📊 **数据库统计** → 实时查看覆盖范围
- 🔗 **一键分享** → 内置分享给好友功能

## 快速部署

### 1. 创建 Telegram Bot

1. Telegram 搜索 **@BotFather**
2. 发送 `/newbot`
3. 设置机器人名称和用户名
4. 复制获得的 **Bot Token**

### 2. 部署

```bash
# 克隆（私有仓库，需 SSH Key）
git clone git@github.com:nima54851/phone-lookup.git
cd phone-lookup

# 安装依赖
pip install -r requirements.txt

# 设置 Bot Token
export BOT_TOKEN="你的BotToken"

# 启动
python3 bot.py
```

### 3. 使用 Railway 部署（推荐）

```bash
railway login
cd phone-lookup
railway init
railway variables set BOT_TOKEN=你的BotToken
railway up --detach
```

### 4. 使用 Docker 部署

```bash
docker build -t phone-lookup-bot .
docker run -d --name phone-lookup \
  -e BOT_TOKEN=你的BotToken \
  phone-lookup-bot
```

## Bot 命令

| 命令 | 说明 |
|------|------|
| `/start` | 开始使用 |
| `/help` | 帮助信息 |
| `/stats` | 数据库统计 |
| `/version` | 版本信息 |
| 直接发手机号 | 查询归属地 |

## 查询示例

支持多种格式：

```
13800138000        → 11位完整号码
+8613800138000     → 国际格式
1380013           → 7位号段
138               → 3位运营商号段
```

## 数据库覆盖

- **4位号段**：三大运营商全号段覆盖
- **7位精细号段**：覆盖全国 300+ 城市
- **精度**：省/自治区级别（部分城市级）

## 项目结构

```
phone-lookup/
├── bot.py           # Telegram Bot 主程序
├── phone_data.py    # 号段数据库（7位精细 + 4位基础）
├── requirements.txt # Python 依赖
├── Dockerfile       # Docker 部署
├── railway.toml     # Railway 部署配置
└── README.md
```

## 安全说明

- ✅ 查询基于公开号段数据，不涉及个人隐私
- ✅ Bot Token 仅用于 Telegram API 认证
- ✅ 无日志记录敏感个人信息
- ✅ 数据库完全本地化，无外部 API 依赖

## 版本

- **v1.0.0** - 初始版本，支持 11 位手机号查询
- **数据库版本** - v2026.1
