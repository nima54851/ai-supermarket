#!/bin/bash
echo "🚀 课程销售平台 GitHub 部署脚本"
echo "========================================="

# 检查项目文件
if [ ! -f "CoursePay_Project.tar.gz" ]; then
    echo "❌ 未找到项目文件"
    exit 1
fi

echo "✅ 项目文件已找到: $(ls -lh CoursePay_Project.tar.gz)"

echo ""
echo "📋 部署步骤："
echo "1. 前往 https://github.com/new"
echo "2. 创建新仓库：coursepay-sales"
echo "3. 仓库描述：CoursePay 课程销售平台"
echo "4. 选择公开(Public)"
echo "5. 添加 MIT 许可证"
echo "6. 点击创建仓库"

echo ""
echo "🔗 创建完成后，复制仓库URL："
echo "   https://github.com/YOUR_USERNAME/coursepay-sales.git"

echo ""
echo "📦 然后运行以下命令："
echo "----------------------------------------"
echo "git init"
echo "git add ."
echo "git commit -m '🎉 初始提交：CoursePay课程销售平台'"
echo "git branch -M main"
echo "git remote add origin https://github.com/YOUR_USERNAME/coursepay-sales.git"
echo "git push -u origin main"
echo "----------------------------------------"

echo ""
echo "🌐 最后启用 GitHub Pages："
echo "1. 进入仓库设置(Settings)"
echo "2. 左侧选择Pages"
echo "3. 分支选择main"
echo "4. 根目录选择/(root)"
echo "5. 点击保存"

echo ""
echo "🎉 完成！访问地址：https://YOUR_USERNAME.github.io/coursepay-sales"

echo ""
echo "💰 PayPal 收款账户：yinanzo@hotmail.com"
echo "🔥 技术支持：support@coursepay.com"