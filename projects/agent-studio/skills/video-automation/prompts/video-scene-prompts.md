# Video Scene Prompts

## 短片脚本分镜 Prompt

```
Create a video scene description for: {CONCEPT}

Scene details:
- Duration: {DURATION} seconds
- Camera: {CAMERA_TYPE} (static, pan, zoom, drone)
- Style: {STYLE} (cinematic, documentary, vlog, commercial)
- Mood: {MOOD} (dramatic, playful, serene, tense)
- Lighting: {LIGHTING} (golden hour, studio, neon, natural)
- Action: {ACTION_DESCRIPTION}
```

## 转场描述 Prompt

```
Describe a smooth video transition from:
"{SCENE_A}" → "{SCENE_B}"
Style: {STYLE} (fade, wipe, dissolve, match cut, cross blur)
Duration: {DURATION}ms
```

## B-Roll 自动生成 Prompt

```
Generate B-roll video concept for supporting:
Main topic: {TOPIC}
Context: {CONTEXT}
Style: {STYLE}
Duration: {DURATION} seconds
```

## AI 视频生成 Prompt (Runway / Kling)

```
Cinematic video: {DESCRIPTION}
- Shot type: {SHOT} (wide, medium, close-up, extreme close-up)
- Movement: {MOVEMENT} (static, tracking, dolly, handheld)
- Style: {STYLE} (film grain, sharp, dreamy, high contrast)
- Duration: {DURATION}s
```

## 缩略图场景 Prompt

```
Extract key visual frame from video concept: {CONCEPT}
Select the most visually striking moment,
frame: {FRAMING} (centered, rule of thirds, full bleed)
Add overlay text: "{TITLE}"
Style: {STYLE} (bright, dramatic, clean)
```
