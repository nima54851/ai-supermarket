# 🚀 CoursePay 完整平台架构

## 📁 项目结构
```
coursepay-real/
├── client/                 # 前端
│   ├── public/            # 静态资源
│   ├── src/
│   │   ├── components/    # React组件
│   │   ├── pages/        # 页面
│   │   ├── api/          # API调用
│   │   └── styles/       # 样式
│   └── package.json
│
├── server/                 # 后端
│   ├── models/           # 数据库模型
│   ├── routes/          # API路由
│   ├── controllers/     # 控制器
│   ├── middleware/      # 中间件
│   └── server.js        # 主文件
│
├── admin/                 # 管理后台
│   ├── dashboard/       # 仪表板
│   ├── users/          # 用户管理
│   ├── courses/        # 课程管理
│   └── orders/         # 订单管理
│
├── database/             # 数据库
│   ├── migrations/      # 迁移文件
│   └── seeds/          # 种子数据
│
├── docker-compose.yml    # Docker配置
├── README.md            # 文档
└── .env.example         # 环境变量
```

## 🔧 技术栈
### 前端
- React 18 + TypeScript
- Vite (构建工具)
- Tailwind CSS (样式)
- React Router (路由)
- Axios (HTTP客户端)

### 后端
- Node.js + Express
- MongoDB + Mongoose
- JWT认证
- Nodemailer (邮件)
- Multer (文件上传)

### 部署
- Docker + Docker Compose
- Nginx (反向代理)
- PM2 (进程管理)
- GitHub Actions (CI/CD)

## 🎯 功能模块
### 1. 用户系统
- 注册/登录
- 个人资料
- 购买历史
- 权限管理

### 2. 课程管理
- 课程创建/编辑
- 分类/标签
- 价格管理
- 内容上传

### 3. 支付系统
- PayPal集成
- 订单管理
- 发票生成
- 退款处理

### 4. 管理后台
- 用户管理
- 订单统计
- 销售报表
- 系统设置

## 📦 立即创建
现在开始创建完整的项目！