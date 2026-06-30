#!/usr/bin/env python3
"""
product_launch.py - AI 产品发布助手
自动生成发布材料包：README 更新、宣传文案、邮件模板等
"""

import os
import sys
import argparse
import json
from datetime import datetime

PRODUCT_TEMPLATES = {
    "ai-agent": {
        "name": "AI Agent / Skill",
        "tagline": "你的下一个 AI 员工",
        "platforms": ["OpenClaw", "Coze", "Gumroad"],
        "readme_sections": ["概述", "功能特性", "安装", "使用示例", "配置", "FAQ"]
    },
    "saas-tool": {
        "name": "SaaS 工具 / Workflow",
        "tagline": "自动化你的工作流",
        "platforms": ["n8n", "Make", "Gumroad"],
        "readme_sections": ["概述", "功能", "快速开始", "工作流配置", "截图", "更新日志"]
    },
    "course": {
        "name": "教程 / 课程",
        "tagline": "从入门到精通",
        "platforms": ["Notion", "Gmail", "Gumroad"],
        "readme_sections": ["概述", "课程大纲", "试听", "购买", "学员评价"]
    }
}

TWITTER_TEMPLATES = [
    "🚀 刚发布了 {name}！\n\n{tagline}\n\n✨ {feature1}\n✨ {feature2}\n✨ {feature3}\n\n→ {url}\n\n#AI #Agent #自动化",
    "我花了 {days} 天做了 {name}，解决 {problem}\n\n用起来是这样的：\n{feature1}\n{feature2}\n\n免费试用 → {url}\n\n求 Star 🙏",
    "{name} 正式上线！\n\n为什么做这个？\n{reason}\n\n上手只需要 {time}，快来试试：\n{url}"
]

EMAIL_TEMPLATE = """主题: 🎉 {name} 正式上线 - {tagline}

你好！

今天正式发布 {name}。

{name} 是一个 {product_type}，帮你 {benefit}。

✨ 核心功能
{features}

📖 快速开始
{quickstart}

💰 定价
{pricing}

👉 点击试用: {url}

有任何问题，回复这封邮件即可。

---
{name} by {author}
"""

def generate_launch_pack(product_id: str, product_type: str = "ai-agent", 
                         name: str = "", tagline: str = "", 
                         features: list = None,
                         benefit: str = "", reason: str = "",
                         url: str = "", author: str = "开发者"):
    
    if features is None:
        features = ["功能1", "功能2", "功能3"]
    
    template = PRODUCT_TEMPLATES.get(product_type, PRODUCT_TEMPLATES["ai-agent"])
    
    if not name:
        name = f"My {template['name']}"
    if not tagline:
        tagline = template['tagline']
    if not url:
        url = "https://github.com/your-repo"
    
    output = {
        "product_id": product_id,
        "generated_at": datetime.now().isoformat(),
        "product": {
            "name": name,
            "tagline": tagline,
            "type": template['name'],
            "platforms": template['platforms']
        },
        "twitter_posts": [
            t.format(
                name=name, tagline=tagline, 
                feature1=features[0] if len(features) > 0 else "",
                feature2=features[1] if len(features) > 1 else "",
                feature3=features[2] if len(features) > 2 else "",
                url=url, days="7", problem="重复工作", time="5分钟"
            ) for t in TWITTER_TEMPLATES
        ],
        "email_template": EMAIL_TEMPLATE.format(
            name=name, tagline=tagline,
            product_type=template['name'],
            benefit=benefit or "自动化工作流",
            features="\n".join([f"- {f}" for f in features]),
            quickstart=f"1. 访问 {url}\n2. 按照 README 指引配置\n3. 开始使用",
            pricing="免费版 / Pro ¥99/月",
            url=url, author=author
        ),
        "readme_checklist": template['readme_sections']
    }
    
    return output

def main():
    parser = argparse.ArgumentParser(description="AI 产品发布材料生成器")
    parser.add_argument("--product-id", required=True, help="产品 ID")
    parser.add_argument("--name", default="", help="产品名称")
    parser.add_argument("--type", default="ai-agent", 
                        choices=["ai-agent", "saas-tool", "course"],
                        help="产品类型")
    parser.add_argument("--tagline", default="", help="产品标语")
    parser.add_argument("--output", default="launch_pack.json", help="输出文件")
    args = parser.parse_args()
    
    result = generate_launch_pack(
        product_id=args.product_id,
        product_type=args.type,
        name=args.name,
        tagline=args.tagline
    )
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 发布材料包已生成: {args.output}")
    print(f"\n📣 Twitter 文案预览:")
    print("-" * 40)
    print(result['twitter_posts'][0])
    print("-" * 40)
    print(f"\n💾 完整数据: {args.output}")

if __name__ == "__main__":
    main()
