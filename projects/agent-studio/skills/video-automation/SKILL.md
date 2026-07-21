# Video Automation

**分类:** Creative AI / Media Automation
**标签:** video-generation, AI-video, runway, kling, pika, ffmpeg, automation
**适用场景:** AI Agent 自动生成视频、剪辑、加字幕、生成缩略图

---

## Overview

Video Automation 让 AI Agent 能够端到端处理视频创作：从 AI 生成视频片段，到自动剪辑、加字幕、配音，再到多平台发布，实现零人工介入的视频内容生产流水线。

## 核心功能

- 🎬 **Text-to-Video**: 文字描述 → AI 生成视频片段（DALL·E 视频 / Runway / Kling / Pika）
- ✂️ **Auto Editing**: 自动剪辑、转场、裁剪（FFmpeg + AI scene detection）
- 📝 **Auto Subtitles**: 自动生成字幕（Whisper → SRT → 烧录）
- 🖼️ **Thumbnail Generation**: 自动生成多尺寸缩略图
- 🎙️ **Voiceover**: 文字转语音自动配音（ElevenLabs / Azure TTS）
- 📡 **Multi-Platform Publish**: 自动适配格式并发布（YouTube / TikTok / Bilibili）
- 📊 **Video Analytics**: 自动生成视频数据报告
- 🔗 **Pipeline Integration**: 与图片生成、文案创作skill无缝串联

## 支持的视频生成模型

| 模型 | 类型 | 适用场景 | API |
|------|------|---------|-----|
| Runway Gen-3 | 文生视频 | 高质量短片 | Replicate / API |
| Kling AI | 文生视频 | 快手国产，质量优秀 | 官方 API |
| Pika 2.0 | 文生视频 | 动画风格 | Pika API |
| Luma Dream Machine | 文生视频 | 场景扩展 | Luma API |
| Haiper | 文生视频 | 多镜头叙事 | Haiper API |
| Stable Video Diffusion | 文生视频 | 开源自部署 | Replicate |
| DALL·E Video (Sora-like) | 文生视频 | OpenAI 官方 | 限内测 |
| CogVideoX | 文生视频 | 开源中文 | HuggingFace |

## 工作流 Pipeline

### Pipeline A: AI 视频内容全自动生产

```
[Article / Script] 
→ [Scene split by GPT] 
→ [Loop: Image Gen per scene] 
→ [Video Gen (Kling/Runway)] 
→ [Merge clips (FFmpeg)] 
→ [Auto subtitle (Whisper + ffmpeg)] 
→ [Add BGM] 
→ [Export multi-format] 
→ [Upload to YouTube/TikTok]
```

### Pipeline B: 产品展示视频自动生成

```
[Product images from database]
→ [Auto slideshow (FFmpeg)] 
→ [Add voiceover (ElevenLabs)] 
→ [Generate subtitle]
→ [Export 16:9 + 9:16]
→ [Notify via Slack/Email]
```

## n8n Workflow 示例

### 1. 文章转视频（AI Video from Script）
**文件:** `integrations/video-automation/script-to-video.json`

```
[Webhook trigger] 
→ [Parse script] 
→ [GPT scene planning] 
→ [Image Gen per scene] 
→ [Video Gen API call] 
→ [Merge + Subtitle] 
→ [Upload YouTube]
```

### 2. 批量视频剪辑自动化
**文件:** `integrations/video-automation/auto-editor.json`

### 3. 视频缩略图批量生成
**文件:** `integrations/video-automation/thumbnail-generator.json`

## 核心脚本

### 视频合并 + 字幕烧录
```python
# integrations/video-automation/scripts/video_merge.py
import subprocess
import whisper

def process_video(input_clips: list, output_path: str, srt_path: str = None):
    """合并视频片段 + 烧录字幕"""
    # Step 1: 拼接片段
    concat_list = "concat_list.txt"
    with open(concat_list, "w") as f:
        for clip in input_clips:
            f.write(f"file '{clip}'\n")
    
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", concat_list, "-c", "copy", "merged.mp4"
    ])
    
    # Step 2: 生成字幕（如无SRT则用 Whisper 自动识别）
    if not srt_path:
        srt_path = whisper_transcribe("merged.mp4")
    
    # Step 3: 烧录字幕
    subprocess.run([
        "ffmpeg", "-i", "merged.mp4", "-vf",
        f"subtitles={srt_path}", output_path
    ])
    
    return output_path
```

### 自动生成缩略图
```python
# integrations/video-automation/scripts/thumbnail_generator.py
from PIL import Image, ImageDraw, ImageFont

def generate_thumbnail(video_path: str, title: str, styles: list):
    """从视频提取帧 + 添加标题生成多尺寸缩略图"""
    # 提取中间帧
    frame = extract_middle_frame(video_path)
    
    sizes = {"youtube": (1280, 720), "tiktok": (1080, 1920), "twitter": (1200, 675)}
    
    thumbnails = {}
    for platform, (w, h) in sizes.items():
        thumb = resize_with_padding(frame, w, h)
        draw_thumb = add_title_overlay(thumb, title)
        path = f"thumb_{platform}.jpg"
        draw_thumb.save(path, quality=95)
        thumbnails[platform] = path
    
    return thumbnails
```

### 多平台视频格式转换
```python
# integrations/video-automation/scripts/multi_format_export.py
def export_multi_format(input_path: str, platforms: list):
    """自动导出多平台适配格式"""
    configs = {
        "youtube": {"codec": "libx264", "crf": 18, "res": "1920x1080", "fps": 30},
        "tiktok":  {"codec": "libx264", "crf": 20, "res": "1080x1920", "fps": 30},
        "twitter": {"codec": "libx264", "crf": 23, "res": "1280x720",  "fps": 30, "maxdur": 140},
        "bilibili": {"codec": "libx264", "crf": 18, "res": "1920x1080", "fps": 30, "maxdur": 600},
    }
    
    results = {}
    for platform in platforms:
        cfg = configs[platform]
        output = f"output_{platform}.mp4"
        run_ffmpeg_export(input_path, output, cfg)
        results[platform] = output
    
    return results
```

## 与其他 Skill 联动

- `image-generation-automation`: 图片 → 视频的素材来源
- `voice-ai-automation`: 语音旁白配音
- `social-media-automation`: 视频 → 多平台自动发布
- `docs-generator`: 文章 → 视频的文案来源
- `analytics-dashboard`: 发布后自动记录视频数据

## 最佳实践

1. **视频长度控制**: YouTube 建议 >8min 有利于算法推荐；TikTok 建议 15-60s
2. **场景拆分**: 复杂脚本拆成多个 5-10s 片段分别生成，再合并质量更稳定
3. **字幕优先**: 所有平台必须烧录字幕，SEO 和无障碍都有帮助
4. **分辨率策略**: 1080p 是基准，4K 仅 YouTube 长视频值得生成
5. **水印添加**: 统一添加片头水印/右下角 logo
6. **成本控制**: AI 视频生成成本高，先用图片生成低预算版测试，再生成视频

## 文件列表

```
skills/video-automation/
├── SKILL.md                          # 本文件
├── prompts/
│   ├── video-scene-prompts.md        # 视频分镜 prompt 模板
│   └── thumbnail-prompts.md          # 缩略图设计 prompt
└── scripts/
    ├── video_merge.py                # 合并 + 字幕烧录
    ├── thumbnail_generator.py        # 多尺寸缩略图
    └── multi_format_export.py        # 多平台格式导出

integrations/video-automation/
├── script-to-video.json              # n8n: 文章→视频工作流
├── auto-editor.json                  # n8n: 自动剪辑工作流
└── thumbnail-generator.json           # n8n: 缩略图批量生成
```

---

*v1.0 | 2026-07-06 | AI Agent Studio*
