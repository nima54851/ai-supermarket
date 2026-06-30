# 🚀 CoursePay GitHub Pages 部署指南

## **✅ 已完成**
1. ✅ GitHub仓库: https://github.com/nima54851/coursepay-sales
2. ✅ CoursePay页面: coursepay-site/index.html
3. ✅ PayPal收款账户: yinanzo@hotmail.com
4. ✅ GitHub Actions工作流: .github/workflows/deploy.yml

## **🚀 最后一步：启用GitHub Pages**

### **步骤1：打开仓库**
访问: https://github.com/nima54851/coursepay-sales

### **步骤2：点击Settings**
![settings](https://user-images.githubusercontent.com/...)

### **步骤3：选择Pages**
左侧菜单 → **Pages**

### **步骤4：配置部署**
```
Source: Deploy from branch
Branch: main
Folder: /coursepay-site
```

### **步骤5：保存**
点击 **Save**

### **步骤6：等待**
等待1-2分钟构建

### **步骤7：访问**
打开: https://nima54851.github.io/coursepay-sales/

## **🎯 立即开始收款**

### **学生支付流程：**
1. **访问**: https://nima54851.github.io/coursepay-sales/
2. **选择课程**: 基础编程入门课程等
3. **点击**: "💰 立即付款"
4. **复制地址**: yinanzo@hotmail.com
5. **转账**: 在PayPal中直接转账

### **收款流程：**
1. 学生在PayPal转账到 `yinanzo@hotmail.com`
2. 备注课程名称
3. 你手动/自动发送课程链接
4. 完成交易

## **📊 功能说明**

### **CoursePay功能：**
- ✅ 课程选择系统
- ✅ PayPal直接收款
- ✅ 地址复制功能
- ✅ 响应式设计
- ✅ 移动端适配
- ✅ 无跳转支付

### **技术特性：**
- GitHub Pages托管
- 免费HTTPS证书
- CDN加速
- 自动部署
- 版本控制

## **🔧 自定义修改**

### **修改收款账户：**
编辑 `coursepay-site/index.html`:
```html
<div id="paypal-address">yinanzo@hotmail.com</div>
```

### **添加课程：**
```html
<div class="course-item" onclick="selectCourse(this)">
    <div class="course-title">新课程名称</div>
    <div class="course-price">¥价格</div>
</div>
```

### **修改价格：**
修改相应元素的innerText即可

## **📞 技术支持**
- **问题解决**: GitHub Issues
- **PayPal支持**: contact@paypal.com
- **业务咨询**: support@coursepay.com
- **收款账户**: yinanzo@hotmail.com

## **🎉 成功标准**
- ✅ 页面正常显示
- ✅ 课程选择正常
- ✅ PayPal地址显示正常
- ✅ 复制功能正常
- ✅ GitHub Pages正常访问

---

**🔥 现在立即启用GitHub Pages，开始销售课程！**

**完成最后一步，即可公网访问：https://nima54851.github.io/coursepay-sales/**

© 2026 CoursePay. All rights reserved.