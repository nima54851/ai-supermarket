# 🚀 Classroom.io 部署指南

## 📋 平台简介
Classroom.io 是一个开源的教育平台，替代Moodle，具有现代界面和完整功能。

## 🔧 技术栈
- Next.js 13 (React框架)
- Prisma (ORM)
- PostgreSQL (数据库)
- Tailwind CSS (样式)
- NextAuth.js (认证)

## 🎯 功能
- 课程创建和管理
- 学生注册和登录
- 作业和测验
- 支付集成 (Stripe/PayPal)
- 成绩管理
- 讨论区

## 📦 部署步骤

### 1. 环境准备
```bash
# 安装Node.js 18+
# 安装PostgreSQL 14+
# 安装Git
```

### 2. 项目设置
```bash
git clone https://github.com/classroomio/classroomio.git
cd classroomio
npm install
```

### 3. 环境配置
```env
# .env.local
DATABASE_URL="postgresql://username:password@localhost:5432/classroomio"
NEXTAUTH_SECRET="your-secret-key"
NEXTAUTH_URL="http://localhost:3000"
PAYPAL_CLIENT_ID="your-paypal-client-id"
PAYPAL_CLIENT_SECRET="your-paypal-secret"
```

### 4. 数据库设置
```bash
npx prisma db push
npx prisma generate
```

### 5. 启动服务
```bash
npm run dev
```

### 6. 访问
打开: http://localhost:3000

## 💰 PayPal配置
1. 登录PayPal开发者平台
2. 创建应用获取Client ID和Secret
3. 配置到环境变量
4. 在平台设置中启用PayPal支付

## 🚀 生产部署

### 使用Docker
```bash
docker-compose up -d
```

### 使用Vercel (推荐)
```bash
vercel --prod
```

### 使用Railway
```bash
railway up
```

## 📊 管理员设置
首次访问: http://localhost:3000/admin
默认管理员: admin@example.com / admin123

## 🔗 重要链接
- 项目主页: https://github.com/classroomio/classroomio
- 文档: https://docs.classroomio.com
- 演示: https://demo.classroomio.com

## ⚡ 快速启动
```bash
# 一键启动脚本
./scripts/setup.sh
```

## 🆘 常见问题
1. **数据库连接失败**: 检查PostgreSQL服务是否运行
2. **支付配置错误**: 确认PayPal沙盒账户
3. **编译错误**: 确保Node.js版本正确

## 🎉 完成部署后
1. 创建管理员账户
2. 添加课程内容
3. 配置支付方式
4. 邀请学生注册
5. 开始销售课程