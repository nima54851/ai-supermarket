# 🚀 CoursePay GitHub 部署指南
# ✅ 5分钟完成部署

## 🎯 当前状态
- ✅ 项目代码已准备完成
- ✅ 服务器访问已修复 (端口:3003)
- ✅ PayPal直接收款功能已实现
- ✅ 零跳转支付方案已配置

## 📁 部署文件说明
```
CoursePay_Deploy/ 部署文件夹
├── index.html        主页面 (重命名自CoursePay_SimplePay.html)
├── success.html      部署成功提示页
├── README.md         此文档
├── DEPLOY_TO_GITHUB.md  部署指南
└── CoursePay_SimplePay.html  原始页面
```

## 🔗 本地测试地址
```
http://localhost:3003/CoursePay_SimplePay.html
```

## 📋 部署步骤

### **第1步：创建GitHub仓库**
```
1. 访问 https://github.com/new
2. 仓库名: coursepay-sales-platform (或 coursepay)
3. 描述: "CoursePay 课程销售平台"
4. 公开访问
5. 点击创建仓库
```

### **第2步：上传文件**
**方法A：Git命令行**
```bash
# 下载项目文件
wget https://[你的服务器]/coursepay_deploy.tar.gz

# 解压并上传
tar -xzf coursepay_deploy.tar.gz
cd coursepay_deploy

# 初始化和推送
git init
git add .
git commit -m "🚀 部署CoursePay课程销售平台"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/coursepay-sales-platform.git
git push -u origin main
```

**方法B：Web上传**
1. 点击 "Upload files"
2. 上传整个 coursepay_deploy 文件夹
3. 提交到 main 分支

### **第3步：启用GitHub Pages**
```
1. 进入仓库 Settings
2. 左侧选择 Pages
3. Source: Deploy from branch
4. Branch: main
5. Folder: / (root)
6. 点击 Save
```

### **第4步：等待生效**
- 等待1-2分钟
- 访问: https://YOUR_USERNAME.github.io/coursepay-sales-platform
- 如果显示成功页面，部署完成

## 💰 收款账户配置
**PayPal收款账户:**
```
yinanzo@hotmail.com
```

**学生支付流程:**
1. 选择课程
2. 点击"立即付款"
3. 显示收款账户
4. 点击"复制地址"
5. 学生在PayPal中直接转账
6. 完成支付

## 🔧 访问地址
- **GitHub Pages**: https://YOUR_USERNAME.github.io/coursepay-sales-platform
- **直接链接**: https://YOUR_USERNAME.github.io/coursepay-sales-platform/index.html

## 🛠️ 快速测试
```bash
# 直接访问测试
curl https://YOUR_USERNAME.github.io/coursepay-sales-platform

# 如果返回HTML，说明部署成功
```

## 📞 技术支持
- **技术问题**: support@coursepay.com
- **收款问题**: yinanzo@hotmail.com
- **紧急联系**: +86 [你的手机号]

## 🎯 立即开始
**只需完成第一步：创建GitHub仓库**，后续步骤我会帮你完成！

---

© 2026 CoursePay. All rights reserved.