---
name: architecture-diagram
version: 1.0.0
draft: true
description: 生成可在浏览器打开的 HTML 架构图。当用户要求画架构图、系统架构、模块关系图，或提到"画个图"、"架构图"、"系统图"、"模块图"时触发。输出为单个 .html 文件，暖色极简风格（Paper.design 风格），支持分层、分组卡片、箭头连接、用户角色、图例等常见架构图元素。
metadata:
  author: nexus-fe
  category: tools
  tags:
    - architecture
    - diagram
    - visualization
    - html
---

# 架构图生成

根据用户描述的系统架构，生成一个可在浏览器直接打开的 `.html` 架构图文件。

## 设计风格

基于 Paper.design 暖色极简风格，核心设计语言：

- **背景** `#edebe1` 暖奶油色
- **字体** Inter（正文 + 标题）、JetBrains Mono（代码/路径）
- **卡片** 浅色表面 `#f5f3eb`，细边框，顶部 3px 彩色指示条
- **交互** hover 轻微上浮 + 阴影加深
- **动画** fadeUp 错帧渐入，由上到下依次显现
- **色彩** 主色仅在标题和圆点指示使用，整体保持温暖中性

## 流程

1. 理解用户描述的架构：模块、层级、数据流向、用户角色
2. 规划图的结构：分几层、每层几个卡片、箭头方向、分组标签
3. 基于 [assets/template.html](assets/template.html) 的 CSS 变量和组件类名生成 HTML
4. 将文件写入用户指定位置（默认当前目录）

## 组件清单

以下 CSS 类名可直接使用，对照模板文件：

### 页面结构

| 类名 | 用途 |
|------|------|
| `.header` + `h1` + `.tagline` | 标题区域 |
| `.canvas` | 居中容器，max-width 1060px |

### 用户角色行

| 类名 | 用途 |
|------|------|
| `.users-row` | 用户卡片行，flex 居中 |
| `.user-card` | 单个用户 |
| `.user-avatar` + `.avatar-{theme}` | 圆形头像，theme 决定渐变色 |
| `.user-name` / `.user-desc` | 名称和描述 |

### 分组区块

| 类名 | 用途 |
|------|------|
| `.section` + `.section-N` | 分组区块（N 控制动画延迟） |
| `.section-tag` + `.tag-{theme}` | 悬浮标签（marketplace / pipeline 等） |

### 卡片

| 类名 | 用途 |
|------|------|
| `.cards-row` | 卡片行，flex 居中 |
| `.card` + `.card-{theme}` | 单张卡片，theme 控制顶部色条和标题色 |
| `.card-icon` | emoji 图标 |
| `.card-title` | 标题（自动跟随 theme 色） |
| `.card-route` | 路径/副标题（JetBrains Mono） |
| `.card-list` | 要点列表 |

可用 theme：`web`(蓝)、`api`(绿)、`db`(琥珀)、`git`(紫)、`cli`(靛蓝)、`feishu`(青)

### 连接线

| 类名 | 用途 |
|------|------|
| `.flow-arrow` + `.arrow-col` + `.line` + `.arrow-head` | 垂直箭头 |
| `.flow-arrow .label` | 箭头旁注释文字 |
| `.h-connector` + `.h-line` | 水平连接箭头（卡片之间） |

### 图例

| 类名 | 用途 |
|------|------|
| `.legend` | 图例行 |
| `.legend-item` + `.legend-dot` | 单个图例项 |

## 扩展规则

当架构复杂度超出模板时：

- **新增颜色**：在 `:root` 中添加 `--accent-{name}` 变量，新增 `.card-{name}::before` / `.card-title` / `.card-list li::before` 三行 CSS
- **新增标签样式**：添加 `.tag-{name}` 设置 background / color / border-color
- **新增用户头像**：添加 `.avatar-{name}` 设置 `linear-gradient(145deg, color1, color2)`
- **增加层级**：追加 `.section-N` 类并递增 `animation-delay`（每层 +0.2s）
- **双向箭头**：在 `.h-line` 上添加 `::before` 反向箭头
- **竖向布局**：在移动端 `@media` 中 `.cards-row` 已自动切换为纵向

## 输出要求

- 单个自包含 `.html` 文件，无外部依赖（仅引用 Google Fonts CDN）
- 文件名建议：`{project}-architecture.html`
- 确保响应式，768px 以下自动纵向排列
