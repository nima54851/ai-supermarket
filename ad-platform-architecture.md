# 高端广告服务平台 - 技术架构文档

## 项目概述
一个完整的高端广告服务平台，包含前端展示、会员管理、支付系统、广告投放、数据分析和管理员控制台。

## 技术栈选择

### 前端技术栈
- **框架**: React 18 + TypeScript
- **样式**: Tailwind CSS + Shadcn/ui
- **状态管理**: Zustand
- **路由**: React Router v6
- **数据获取**: React Query
- **表单**: React Hook Form + Zod
- **图标**: Lucide React

### 后端技术栈
- **框架**: Node.js + Express + TypeScript
- **数据库**: PostgreSQL + Prisma ORM
- **认证**: JWT + bcrypt
- **支付**: Stripe/PayPal API
- **实时**: WebSocket (Socket.io)
- **邮件**: Nodemailer
- **文件存储**: Cloudinary/AWS S3

### Telegram Bot
- **框架**: Telegraf.js
- **数据库**: PostgreSQL
- **Webhook**: Express endpoint

### DevOps
- **容器化**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **部署**: Vercel/Netlify (前端), Railway/Render (后端)
- **监控**: Sentry + LogRocket

## 数据库架构

### 核心数据表

```sql
-- 用户表
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(100) UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  avatar_url TEXT,
  role VARCHAR(50) DEFAULT 'user',
  telegram_id VARCHAR(100) UNIQUE,
  email_verified BOOLEAN DEFAULT FALSE,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 会员套餐表
CREATE TABLE membership_plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  price DECIMAL(10,2) NOT NULL,
  currency VARCHAR(10) DEFAULT 'USD',
  duration_days INTEGER NOT NULL,
  features JSONB DEFAULT '[]',
  is_active BOOLEAN DEFAULT TRUE,
  sort_order INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 订单表
CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  plan_id UUID REFERENCES membership_plans(id),
  amount DECIMAL(10,2) NOT NULL,
  currency VARCHAR(10) DEFAULT 'USD',
  status VARCHAR(50) DEFAULT 'pending',
  payment_method VARCHAR(50),
  payment_id VARCHAR(255),
  invoice_url TEXT,
  payment_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 广告表
CREATE TABLE ads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  content TEXT NOT NULL,
  media_urls JSONB DEFAULT '[]',
  category VARCHAR(100),
  target_url TEXT,
  budget DECIMAL(10,2) NOT NULL,
  spent DECIMAL(10,2) DEFAULT 0,
  status VARCHAR(50) DEFAULT 'draft',
  start_date TIMESTAMP,
  end_date TIMESTAMP,
  targeting JSONB DEFAULT '{}',
  impressions INTEGER DEFAULT 0,
  clicks INTEGER DEFAULT 0,
  ctr DECIMAL(5,2) DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 统计数据表
CREATE TABLE statistics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  date DATE NOT NULL,
  user_count INTEGER DEFAULT 0,
  order_count INTEGER DEFAULT 0,
  revenue DECIMAL(10,2) DEFAULT 0,
  ad_impressions INTEGER DEFAULT 0,
  ad_clicks INTEGER DEFAULT 0,
  ctr DECIMAL(5,2) DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## API 架构

### REST API 端点设计

```
/api/v1/
├── auth/
│   ├── POST /register
│   ├── POST /login
│   ├── POST /logout
│   ├── POST /refresh-token
│   └── POST /forgot-password
├── users/
│   ├── GET /profile
│   ├── PUT /profile
│   ├── GET /subscription
│   └── POST /subscribe
├── plans/
│   ├── GET / (所有套餐)
│   ├── GET /:id (套餐详情)
│   └── GET /features (功能列表)
├── ads/
│   ├── GET / (用户广告列表)
│   ├── POST / (创建广告)
│   ├── GET /:id (广告详情)
│   ├── PUT /:id (更新广告)
│   ├── DELETE /:id (删除广告)
│   └── GET /:id/stats (广告统计)
├── orders/
│   ├── GET / (用户订单)
│   ├── POST / (创建订单)
│   ├── GET /:id (订单详情)
│   └── POST /:id/pay (支付订单)
├── admin/
│   ├── GET /dashboard (管理员面板)
│   ├── GET /users (用户管理)
│   ├── GET /orders (订单管理)
│   ├── GET /ads (广告管理)
│   └── GET /stats (统计数据)
└── analytics/
    ├── GET /overview (概览数据)
    ├── GET /revenue (收入数据)
    ├── GET /users (用户分析)
    └── GET /ads (广告分析)
```

### WebSocket 实时功能
- 广告审批状态更新
- 支付成功通知
- 实时数据大屏更新
- 管理员通知

## 前端架构

### 页面结构

```
src/
├── components/           # 可复用组件
│   ├── ui/              # 基础UI组件
│   ├── layout/          # 布局组件
│   ├── forms/           # 表单组件
│   └── charts/          # 图表组件
├── pages/               # 页面组件
│   ├── Home/           # 首页
│   ├── Auth/           # 认证页面
│   ├── Dashboard/      # 用户面板
│   ├── Membership/     # 会员套餐
│   ├── Ads/           # 广告管理
│   ├── Analytics/     # 数据分析
│   └── Admin/         # 管理员面板
├── hooks/              # 自定义Hooks
├── lib/               # 工具函数
│   ├── api.ts         # API客户端
│   ├── auth.ts        # 认证工具
│   └── utils.ts       # 通用工具
├── store/             # 状态管理
├── types/             # TypeScript类型
└── styles/            # 全局样式
```

### 主要功能页面

1. **首页 (Landing Page)**
   - 项目展示
   - 广告案例展示
   - 会员套餐介绍
   - 用户中心入口

2. **用户面板 (User Dashboard)**
   - 个人资料管理
   - 订阅状态查看
   - 广告管理
   - 订单历史

3. **会员套餐页面 (Membership Plans)**
   - 套餐对比
   - 支付页面
   - 功能说明

4. **广告管理 (Ad Management)**
   - 广告创建表单
   - 广告列表
   - 实时统计
   - 预算控制

5. **数据大屏 (Data Dashboard)**
   - 实时数据可视化
   - 关键指标展示
   - 趋势分析
   - 导出功能

6. **管理员面板 (Admin Panel)**
   - 用户管理
   - 订单审核
   - 广告审批
   - 财务统计
   - 系统配置

## Telegram Bot 功能

### 主要命令
- `/start` - 欢迎消息和功能介绍
- `/register` - 用户注册
- `/plans` - 查看会员套餐
- `/ads` - 管理广告
- `/stats` - 查看统计
- `/support` - 联系客服

### Webhook 集成
- 支付通知
- 广告审批通知
- 用户状态更新
- 实时警报

## 支付系统集成

### 支持的支付方式
1. **信用卡/借记卡** (Stripe)
2. **PayPal**
3. **加密货币** (可选)
4. **银行转账**

### 支付流程
```
用户选择套餐 → 创建订单 → 支付页面 → 
支付网关处理 → Webhook回调 → 更新订单状态 →
激活会员权限 → 发送确认邮件
```

## 安全考虑

### 认证和授权
- JWT token 认证
- Role-based Access Control (RBAC)
- CSRF 保护
- CORS 配置

### 数据安全
- 密码加密存储 (bcrypt)
- HTTPS 强制
- SQL 注入防护
- XSS 防护

### 支付安全
- PCI DSS 合规
- 敏感数据加密
- 双重验证
- 交易日志记录

## 性能优化

### 前端优化
- 代码分割和懒加载
- 图片优化和WebP支持
- CDN 静态资源
- 缓存策略

### 后端优化
- 数据库索引优化
- Redis 缓存
- 连接池管理
- API 限流

### 监控和日志
- 错误跟踪 (Sentry)
- 性能监控 (New Relic)
- 业务日志
- 审计日志

## 部署架构

### 开发环境
- Docker Compose 本地运行
- 热重载支持
- 开发数据库

### 生产环境
```
前端 (Vercel/Netlify)
    ↓
负载均衡器 (Nginx)
    ↓
后端服务 (Railway/Render)
    ↓
数据库 (PostgreSQL)
    ↓
缓存 (Redis)
    ↓
文件存储 (S3/Cloudinary)
    ↓
消息队列 (RabbitMQ)
```

## 开发计划

### Phase 1: 基础架构 (1-2周)
- 数据库设计和搭建
- 基础API开发
- 用户认证系统
- 基本前端框架

### Phase 2: 核心功能 (2-3周)
- 会员系统
- 支付集成
- 广告管理基础
- 用户面板

### Phase 3: 高级功能 (2周)
- Telegram Bot
- 数据大屏
- 管理员面板
- 实时功能

### Phase 4: 优化和部署 (1周)
- 性能优化
- 安全加固
- 测试和QA
- 生产部署

## 总结

这个广告服务平台将提供一个完整的解决方案，包括用户管理、会员订阅、广告投放、数据分析和支付处理。采用现代化的技术栈和良好的架构设计，确保系统的可扩展性、安全性和用户体验。