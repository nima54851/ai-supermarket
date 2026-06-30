# Skills Quick Guide

## 🚀 **快速开始**

### **1. 基础命令**
```bash
# 查看所有Skills
clawhub list

# 搜索Skills
clawhub search "skill-name"

# 安装Skill
clawhub install skill-name

# 更新Skill
clawhub update skill-name

# 更新所有Skills
clawhub update --all
```

### **2. 核心Skills使用**

#### **Skill开发**
```bash
# 开始新Skill开发
参考 skill-dev-guide

# 代码质量检查
参考 code-quality

# 架构设计
参考 software-architecture-design

# 测试验证
参考 test-master
```

#### **设计开发**
```bash
# UI/UX设计
参考 design
参考 ui-design
参考 ui-ux-design

# 前端实现
参考 anthropics-frontend-design
参考 web-development
```

#### **安全开发**
```bash
# 安全检查
参考 security

# 安全审计
参考 security-audit
参考 agentic-security-audit
```

#### **内存管理**
```bash
# 内存配置
参考 memory
参考 memory-management
参考 smart-memory-manager
```

### **3. 常用技能链**

#### **新Skill开发流程**
```
1. skill-dev-guide → 开发指南
2. software-architecture-design → 架构设计
3. code-quality → 代码标准
4. design + ui-design → 界面设计
5. test-master → 测试验证
6. security-audit → 安全审查
7. skill-quality-assurance → 质量保证
```

#### **现有Skill优化**
```
1. code-review → 代码审查
2. performance-testing-toolkit → 性能测试
3. security-audit → 安全检查
4. skill-quality-assurance → 质量改进
```

### **4. 分类快速参考**

#### **开发类**
- `agent-development` - 代理开发
- `api-development` - API开发
- `code-quality` - 代码质量
- `code-review` - 代码审查
- `software-architecture-design` - 架构设计
- `test-master` - 测试工具
- `web-development` - Web开发

#### **设计类**
- `design` - 综合设计
- `ui-design` - UI设计
- `ui-ux-design` - UI/UX设计
- `anthropics-frontend-design` - 前端设计
- `database-design` - 数据库设计

#### **安全类**
- `security` - 安全框架
- `security-audit` - 安全审计
- `agentic-security-audit` - 代理安全审计

#### **内存类**
- `memory` - 基础内存
- `memory-management` - 内存管理
- `smart-memory-manager` - 智能内存

#### **质量类**
- `performance-testing-toolkit` - 性能测试
- `skill-quality-assurance` - 质量保证
- `afrexai-observability-engine` - 观察性

### **5. 最佳实践**

#### **每次开发前**
```bash
# 检查相关Skills是否最新
clawhub update --all

# 参考开发指南
cat ~/.openclaw/workspace/skills/skill-dev-guide/SKILL.md

# 检查代码标准
cat ~/.openclaw/workspace/skills/code-quality/SKILL.md
```

#### **开发过程中**
```bash
# 定期进行代码审查
参考 code-review

# 进行安全审查
参考 security-audit

# 性能测试
参考 performance-testing-toolkit
```

#### **开发完成后**
```bash
# 最终质量检查
参考 skill-quality-assurance

# 安全审计
参考 agentic-security-audit

# 文档更新和发布
```

### **6. 故障排除**

#### **Skill安装失败**
```bash
# 检查网络连接
ping clawhub.com

# 清理缓存
rm -rf ~/.clawhub/cache/

# 重新安装
clawhub install skill-name --force
```

#### **Skill运行错误**
```bash
# 检查Skill文档
cat ~/.openclaw/workspace/skills/skill-name/SKILL.md

# 检查依赖
cat ~/.openclaw/workspace/skills/skill-name/_meta.json

# 查看日志
tail -f /tmp/openclaw/openclaw-*.log
```

#### **Skills不工作**
```bash
# 重启OpenClaw网关
openclaw gateway restart

# 检查服务状态
openclaw gateway status

# 查看技能扫描
journalctl --user -u openclaw-gateway.service | grep -i skill
```

### **7. 定期维护**

#### **每周维护**
```bash
# 更新所有Skills
clawhub update --all

# 清理过时Skills
# 备份重要配置
# 检查安全更新
```

#### **每月维护**
```bash
# 安全审计
参考 security-audit

# 性能优化
参考 performance-testing-toolkit

# 质量评估
参考 skill-quality-assurance

# 文档更新
```

### **8. 实用小贴士**

#### **快速搜索**
```bash
# 按类别搜索
clawhub search "development" --limit 10
clawhub search "design" --limit 10
clawhub search "security" --limit 10
clawhub search "memory" --limit 10
```

#### **评分参考**
- ⭐ **3.6+** - 高质量推荐使用
- ⭐ **3.0-3.5** - 可用，需注意维护状态
- ⭐ **2.5-3.0** - 实验性，谨慎使用
- ⭐ **<2.5** - 不推荐生产使用

#### **维护者检查**
```bash
# 查看Skill详细信息
clawhub search "skill-name" --verbose

# 检查最后更新时间
# 查看社区反馈
```

### **9. 开发模板**

#### **新Skill模板结构**
```
my-new-skill/
├── SKILL.md          # 技能描述
├── _meta.json        # 元数据
├── scripts/          # 脚本目录
├── references/       # 参考文档
└── assets/           # 资源文件
```

#### **质量检查清单**
- [ ] 代码质量符合标准 (code-quality)
- [ ] 安全审查通过 (security-audit)
- [ ] 性能测试合格 (performance-testing-toolkit)
- [ ] 文档完整清晰
- [ ] 错误处理完善
- [ ] 测试覆盖充分

### **10. 社区资源**

#### **官方资源**
- ClawHub官网: https://clawhub.com
- OpenClaw文档: https://docs.openclaw.ai
- GitHub仓库: https://github.com/openclaw

#### **社区支持**
- Discord社区
- GitHub Issues
- 开发者论坛

---

## 📞 **技术支持**

### **遇到问题**
1. 检查本指南
2. 查看Skill文档
3. 搜索社区讨论
4. 提交Issue报告

### **建议和反馈**
欢迎提出改进建议和反馈，帮助完善Skills生态系统！