# SKILL.md — Video Processing Automation

## 概述
AI 驱动的视频处理自动化：将原始视频素材转换为带字幕、转场、特效的成品视频。支持 FFmpeg、AI 自动剪辑、视频压缩、格式转换。

## 核心能力
- **AI 剪辑**：自动识别精彩片段（B-roll 检测、静音片段跳过）
- **字幕生成**：Whisper/STT 提取字幕 → 翻译 → 烧录 SRT/ASS
- **转场特效**：自动添加 B-roll、转场动画、Logo 水印
- **多格式输出**：横版(16:9)、竖版(9:16)、方形(1:1)，适配各平台
- **AI 配音**：TTS 生成配音轨道，自动音画对齐
- **视频压缩**：H.264/H.265 编码，保持质量的同时压缩体积

## 典型场景
- 视频号/B站内容批量处理
- 直播录屏自动剪辑
- 产品宣传片批量生成
- 课程视频自动化后期

## 工具依赖
- FFmpeg（核心视频处理）
- Whisper（字幕提取）
- OpenAI / Claude（脚本/解说词生成）
- ElevenLabs / Azure TTS（配音）

## n8n 集成
→ `integrations/video-processing-automation/video-processing-pipeline.json`

## 使用方法
1. 上传原始视频到指定目录
2. 配置处理参数（分辨率、转场、字幕语言）
3. 触发 n8n workflow，自动执行完整 pipeline
4. 成品视频输出至指定存储

## 示例命令
```bash
# 提取字幕
ffmpeg -i input.mp4 -ac 1 audio.wav && whisper audio.wav --model medium --language zh

# 竖版裁剪+加水印
ffmpeg -i input.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920,drawtext=text='AI生成':fontsize=48" output_vertical.mp4

# 压缩并转码
ffmpeg -i input.mp4 -c:v libx265 -crf 23 -c:a aac -b:a 128k output_compressed.mp4
```
