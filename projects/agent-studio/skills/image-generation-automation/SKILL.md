# Image Generation Automation

**分类:** Creative AI / Media Automation
**标签:** image-generation, dall-e, stable-diffusion, flux, n8n, openai, automation
**适用场景:** AI Agent 自动生成配图、封面、素材

---

## Overview

Image Generation Automation 让 AI Agent 能够根据文字描述自动生成高质量图片，支持 DALL·E、Stable Diffusion、Flux 等主流图像生成模型，并通过 n8n 工作流实现批量处理、按需生成、图片优化等自动化场景。

## 核心功能

- 🖼️ **Text-to-Image**: 纯文字描述 → 高质量图片
- 🔄 **批量生成**: 支持一次性生成多组变体（variants）
- 🎨 **风格控制**: 支持指定艺术风格（写实、动漫、水彩、赛博朋克等）
- 📐 **尺寸适配**: 自由设置输出尺寸（1:1、16:9、9:16 等）
- 🖌️ **图片变体 (Inpainting/Outpainting)**: 局部修改、扩展图片
- 🏷️ **自动打标签**: 生成后自动添加 prompt 标签、描述 metadata
- 📦 **存储分发**: 自动上传至 OSS/GCS/S3，支持 CDN 加速访问
- 🔁 **Pipeline**: 与其他 skill 串联（语音→文案→图片→发布）

## 支持的模型

| 模型 | 提供方 | 优势 |
|------|--------|------|
| DALL·E 3 | OpenAI | 文字理解强，细节丰富 |
| Stable Diffusion XL | Replicate / Stability AI | 开源可自部署 |
| Flux.1 | Replicate / Black Forest Labs | 写实风格极佳 |
| Midjourney | Via API | 艺术感强 |
| Imagen 3 | Google Vertex AI | 高保真照片级 |
| Playground v2.5 | Playground AI | 色彩表现突出 |

## n8n Workflow 示例

### 1. 内容配图自动生成

```
[Notion Article] → [Extract keywords] → [Generate prompt] 
→ [DALL·E 3 / SDXL] → [Upload to OSS] → [Save URL to Notion]
```

**文件:** `integrations/image-generation-automation/content-cover-gen.json`

### 2. 批量产品图生成

```
[CSV (product list)] → [n8n Loop] → [Prompt engineer] 
→ [Image Gen API] → [Upload to S3] → [Send email report]
```

### 3. AI 漫画/配图 Pipeline

```
[Article content] → [GPT-4o summary] → [Prompt generation] 
→ [Flux.1 real] → [GIMP crop/resize] → [Publish]
```

## Prompt 模板库

### 封面图 Prompt
```
[Style] cover image for article: [TOPIC]
- Aspect ratio: 16:9
- Colors: [COLOR_PALETTE or "vibrant and professional"]
- Text overlay: [TITLE] (add only if explicitly requested)
- Style: [realistic | illustration | 3d render | flat design | cinematic]
```

### 产品图 Prompt
```
Professional product photography of [PRODUCT],
[BACKGROUND], studio lighting, high detail,
8k resolution, commercial photography style
```

### 配图 Prompt
```
Editorial illustration for: [CONCEPT]
- Style: [watercolor | digital art | minimalist | tech infographic]
- Mood: [SERIOUS | PLAYFUL | INSPIRING]
- Color scheme: [COLOR]
```

## 自动化场景

### 场景 1: 博客文章自动配图
```python
# skills/image-generation-automation/scripts/auto_cover.py
import openai
import requests
import oss2

def generate_article_cover(article_title: str, style: str = "cinematic"):
    """根据文章标题自动生成封面图"""
    prompt = build_cover_prompt(article_title, style)
    
    # 调用图像生成 API
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1792x1024",
        quality="hd"
    )
    
    image_url = response.data[0].url
    
    # 下载并上传 OSS
    image_bytes = download_image(image_url)
    oss_path = upload_to_oss(image_bytes, f"covers/{slugify(article_title)}.png")
    
    return oss_path

def build_cover_prompt(title: str, style: str) -> str:
    return f"""{style} style cover image for article: {title}
    High quality, 16:9 aspect ratio, vibrant professional,
    digital art, cinematic lighting, ultra detailed"""
```

### 场景 2: 批量生成社交媒体素材
```python
# skills/image-generation-automation/scripts/batch_social_images.py
def generate_social_batch(topics: list, platform: str = "twitter"):
    sizes = {
        "twitter": (1200, 675),
        "instagram": (1080, 1080),
        "linkedin": (1200, 627),
        "youtube": (1280, 720),
    }
    
    for topic in topics:
        prompt = f"Professional social media image about: {topic}, {platform} format"
        size = sizes.get(platform, (1200, 675))
        image = generate_image(prompt, size)
        upload_and_tag(image, topic, platform)
```

## API 工具

### OpenAI DALL·E
```python
openai.images.generate(
    model="dall-e-3",
    prompt="...",
    n=1,
    size="1024x1024" | "1792x1024" | "1024x1792",
    quality="standard" | "hd",
    response_format="url" | "b64_json"
)
```

### Replicate (SDXL / Flux)
```python
import replicate
output = replicate.run(
    "stability-ai/sdxl:...",
    input={"prompt": "...", "num_inference_steps": 50}
)
```

### Stability AI API
```python
requests.post(
    "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
    headers={"Authorization": f"Bearer {STABILITY_KEY}"},
    json={"text_prompts": [{"text": "..."}]}
)
```

## 最佳实践

1. **Prompt 工程**: 使用结构化 prompt（主体 + 风格 + 光照 + 构图）效果最佳
2. **版权注意**: 避免生成带版权人物、品牌 logo 的图片
3. **尺寸规划**: 提前规划多平台尺寸，用 Pillow 做 resize 而非重复生成
4. **缓存策略**: 相同 prompt 的图片做好 hash 缓存，避免重复调用
5. **质量分级**: DALL·E 3 适合精图，SDXL 适合批量草图
6. **成本控制**: 使用 `quality=standard` 降成本，用 `n=1` 避免浪费

## 与其他 Skill 联动

- `voice-ai-automation`: 语音转文字 → AI 生成配图 → 发布
- `social-media-automation`: 配图 → 自动发布 Twitter/LinkedIn
- `docs-generator`: 文档生成时自动配图
- `n8n-workflow-automation`: 所有图像工作流的核心调度

## 文件列表

```
skills/image-generation-automation/
├── SKILL.md                          # 本文件
├── prompts/
│   ├── cover-image-prompts.md        # 封面图 prompt 模板
│   └── product-photography-prompts.md
└── scripts/
    ├── auto_cover.py                # 自动封面生成
    └── batch_social_images.py        # 批量社媒图

integrations/image-generation-automation/
├── content-cover-gen.json            # n8n: 博客配图工作流
├── batch-product-images.json          # n8n: 批量产品图
└── social-media-pipeline.json         # n8n: 社媒配图发布流
```

---

*v1.0 | 2026-07-06 | AI Agent Studio*
