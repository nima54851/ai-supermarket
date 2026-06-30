---
name: coding-tutor
description: 编程学习助手，基于 freeCodeCamp 课程体系设计。用于：(1) 带学编程语言（Python / JavaScript / TypeScript / SQL 等），(2) 解释代码原理和概念，(3) 设计编程练习题和解答，(4) 代码 Debug 和优化建议，(5) 帮助搭建个人项目（从前端到后端）。当用户说"学 Python"、"教我写代码"、"这个报错什么意思"、"帮我做个 XX 小项目"、"刷算法题"时触发此技能。
---

# Coding Tutor

## 学习路径（基于 freeCodeCamp 体系）

```
HTML/CSS → JavaScript → React → Node.js → Python → SQL → 算法
```

## 核心教学原则

1. **先理解再写代码** — 不要让用户盲目复制，要解释为什么
2. **从例子出发** — 用具体代码讲解抽象概念
3. **动手优先** — 每讲一个概念，给一个可直接运行的练习
4. **即时反馈** — 用户给出代码，立刻指出问题和改进点

## 常用语言速查

### Python 入门模板
```python
# 变量与类型
name = "灵犀"        # str
age = 1             # int
is_active = True    # bool

# 函数
def greet(person_name):
    return f"你好，{person_name}！"

print(greet("万"))   # → 你好，万！

# 列表推导式
squares = [x**2 for x in range(10)]
```

### JavaScript 入门模板
```javascript
// 箭头函数
const greet = (name) => `你好，${name}！`;

// 异步
const fetchData = async (url) => {
  const res = await fetch(url);
  return await res.json();
};

// 解构
const { name, age } = { name: "灵犀", age: 1 };
```

## 学习路径详情

### Level 1：Web 基础
- HTML：标签、属性、结构
- CSS：选择器、盒模型、Flexbox、Grid
- 练习：做一个个人主页

### Level 2：JavaScript
- 变量、数据类型、条件、循环
- 函数、作用域、闭包
- DOM 操作、事件
- 练习：做一个 Todo App

### Level 3：React
- 组件、Props、State
- Hooks（useState、useEffect、useRef）
- 练习：做一个天气查询 App

### Level 4：后端
- Node.js + Express 基础
- RESTful API 设计
- 数据库：SQLite / PostgreSQL
- 练习：做一个小博客后端

### Level 5：Python + AI
- Python 基础语法
- 用 Ollama 本地跑大模型
- 构建 AI 增强的应用
- 练习：做一个本地 AI 助手

## 常见报错处理

| 报错信息 | 常见原因 | 解法 |
|---|---|---|
| `SyntaxError` | 语法错误 | 检查括号、引号、缩进 |
| `IndentationError` | 缩进不一致 | Python 用 4 空格或 Tab |
| `ModuleNotFoundError` | 没装依赖 | `pip install <pkg>` 或 `npm install` |
| `CORS error` | 跨域请求被拦截 | 后端加 CORS header |
| `Cannot read property 'xxx' of undefined` | 对象未定义 | 检查变量是否正确赋值 |

## 推荐练习资源

- freeCodeCamp：https://www.freecodecamp.org/learn
- LeetCode 简单题：两数之和、三数之和、反转链表
- 项目练手：Todo App、天气 App、Markdown 编辑器、短链接服务

## 教学流程

```
用户提问 → 判断水平（初/中/高）→ 解释原理 → 代码示例 → 练习题 → 反馈
```

遇到 Bug：贴代码 → 定位问题 → 给出修复方案 → 解释原因
