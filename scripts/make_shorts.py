#!/usr/bin/env python3
"""
YouTube Shorts Generator v2 — 适配 MoviePy 2.x
从游戏素材自动生成 9:16 竖屏 Shorts 视频
"""
import os
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, concatenate_videoclips
from moviepy.video.fx import FadeIn, FadeOut
import random

# 素材路径
GAME_DIR = "/root/.openclaw/workspace/game-platform/thumbs"
OUT_DIR  = "/root/.openclaw/workspace/shorts"
os.makedirs(OUT_DIR, exist_ok=True)

SHORTS_W, SHORTS_H = 1080, 1920  # 9:16 竖屏

# 游戏封面列表
GAME_PREVIEWS = [
    (f"{GAME_DIR}/dino.png",       "🦖 恐龙跑酷",     "Three.js 3D 重制版"),
    (f"{GAME_DIR}/survivor.png",   "⚔️ 深渊幸存者",   "俯视角生存射击"),
    (f"{GAME_DIR}/pinball.png",    "🎱 弹珠台",       "经典弹珠 物理真实"),
    (f"{GAME_DIR}/fruitninja.png", "🍉 水果忍者",     "一刀切 快感十足"),
    (f"{GAME_DIR}/jewel.png",      "💎 宝石消消乐",   "100+ 关卡 益智消消乐"),
    (f"{GAME_DIR}/blob-io.png",    "🫧 Blob.io",      "多人球球大作战"),
    (f"{GAME_DIR}/basketball.png", "🏀 篮球投篮",     "轨迹预测 物理模拟"),
    (f"{GAME_DIR}/space-shooter.png", "🚀 太空射击",  "街机风格 弹幕游戏"),
]

BG_COLOR  = (15, 15, 25)
ACCENT    = (255, 100, 50)
WHITE     = (255, 255, 255)
GRAY      = (160, 160, 190)

def load_font(size):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def make_gradient(w, h):
    """垂直渐变背景"""
    img = Image.new("RGB", (w, h))
    for y in range(h):
        r = int(15 + 15 * (y/h))
        g = int(10 + 5  * (y/h))
        b = int(25 + 20 * (y/h))
        for x in range(w):
            img.putpixel((x, y), (r, g, b))
    return img

def make_frame(title, subtitle, game_img_path=None):
    """生成一张完整的展示帧"""
    bg = make_gradient(SHORTS_W, SHORTS_H)
    draw = ImageDraw.Draw(bg)

    # 游戏封面（如果存在）
    if game_img_path and os.path.exists(game_img_path):
        try:
            gi = Image.open(game_img_path).convert("RGBA")
            scale = min(880/gi.width, 720/gi.height)
            nw, nh = int(gi.width*scale), int(gi.height*scale)
            gi = gi.resize((nw, nh), Image.LANCZOS)
            # 圆角
            mask = Image.new("L", (nw, nh), 0)
            md = ImageDraw.Draw(mask)
            md.rounded_rectangle([(0,0),(nw-1,nh-1)], 20, fill=255)
            gi.putalpha(mask)
            x, y = (SHORTS_W-nw)//2, 140
            bg.paste(gi, (x, y), gi)
        except Exception as e:
            print(f"  ⚠️ {game_img_path}: {e}")

    # 底部暗角
    overlay = Image.new("RGBA", (SHORTS_W, 420), (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([(0,0),(SHORTS_W,420)], fill=(0,0,0,200))
    bg.paste(overlay, (0, SHORTS_H-420), overlay)

    # 文字
    draw = ImageDraw.Draw(bg)
    ft = load_font(78)
    fs = load_font(42)

    # 标题（居中）
    tw = draw.textbbox((0,0), "在线游戏合集", font=ft)[2]
    tx = (SHORTS_W - tw)//2
    ty = SHORTS_H - 330
    # 黑色描边
    for dx,dy in [(-2,-2),(2,-2),(-2,2),(2,2)]:
        draw.text((tx+dx, ty+dy), title, font=ft, fill=(0,0,0))
    draw.text((tx, ty), title, font=ft, fill=WHITE)

    # 副标题
    sw = draw.textbbox((0,0), subtitle, font=fs)[2]
    sx = (SHORTS_W - sw)//2
    sy = SHORTS_H - 230
    draw.text((sx, sy), subtitle, font=fs, fill=GRAY)

    return bg

def make_intro():
    bg = make_gradient(SHORTS_W, SHORTS_H)
    draw = ImageDraw.Draw(bg)

    ft = load_font(96)
    fs = load_font(46)
    ft2 = load_font(38)

    # 左上角标签
    draw.rounded_rectangle([30, 50, 330, 115], 18, fill=ACCENT)
    draw.text((180, 82), "🔥 精选游戏", font=ft2, fill=WHITE, anchor="mm")

    # 主标题
    tw = draw.textbbox((0,0), "在线游戏合集", font=ft)[2]
    tx = (SHORTS_W - tw)//2
    for dx,dy in [(-3,-3),(3,-3),(-3,3),(3,3)]:
        draw.text((tx+dx, SHORTS_H//2-80+dy), "在线游戏合集", font=ft, fill=(0,0,0))
    draw.text((tx, SHORTS_H//2-80), "在线游戏合集", font=ft, fill=WHITE)

    # 副标题
    draw.text((SHORTS_W//2, SHORTS_H//2-10), "免费玩 · 无需下载 · 浏览器直接开",
              font=fs, fill=GRAY, anchor="mm")

    # 底部行动号召
    draw.text((SHORTS_W//2, SHORTS_H-100),
              "👆 点击游戏开始玩",
              font=ft2, fill=ACCENT, anchor="mm")

    return bg

def make_outro():
    bg = make_gradient(SHORTS_W, SHORTS_H)
    draw = ImageDraw.Draw(bg)
    ft = load_font(80)
    fs = load_font(46)
    ft2 = load_font(36)

    draw.text((SHORTS_W//2, SHORTS_H//2-100), "👍 喜欢就点赞",
              font=ft, fill=WHITE, anchor="mm")
    draw.text((SHORTS_W//2, SHORTS_H//2-20), "🔔 订阅获取更多",
              font=fs, fill=GRAY, anchor="mm")
    draw.text((SHORTS_W//2, SHORTS_H//2+50),
              "🌐 github.com/nima54851",
              font=ft2, fill=ACCENT, anchor="mm")
    return bg

def img_to_clip(img, duration, fade_in=0.3, fade_out=0.4):
    """PIL Image → MoviePy ImageClip，加淡入淡出"""
    import numpy as np
    arr = np.array(img.convert("RGB"))
    clip = (ImageClip(arr)
            .with_duration(duration)
            .with_fps(30)
            .with_effects([FadeIn(fade_in), FadeOut(fade_out)]))
    return clip

def build_video(clips_data, output_path):
    """合成最终视频"""
    segments = []

    # 开场
    segments.append(img_to_clip(make_intro(), 2.0, 0.5, 0.3))

    # 游戏帧
    for img_path, title, subtitle in clips_data:
        frame = make_frame(title, subtitle, img_path)
        segments.append(img_to_clip(frame, 4.5, 0.3, 0.5))

    # 结尾
    segments.append(img_to_clip(make_outro(), 2.0, 0.3, 0.8))

    video = concatenate_videoclips(segments, method="compose")
    video.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio=False,
        preset="ultrafast",
        bitrate="5000k",
        logger=None
    )
    return output_path

def generate(n_games=4):
    """生成每日 Shorts"""
    date_str = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
    output = f"{OUT_DIR}/shorts-{date_str}.mp4"

    selected = random.sample(GAME_PREVIEWS, min(n_games, len(GAME_PREVIEWS)))
    print(f"🎬 生成 Shorts，选用: {[t for _,t,_ in selected]}")
    build_video(selected, output)
    print(f"✅ 已保存: {output}")

    # 同步到 reports 目录（方便查看）
    import shutil
    rdir = "/root/.openclaw/workspace/reports"
    os.makedirs(rdir, exist_ok=True)
    shutil.copy(output, f"{rdir}/shorts-{date_str}.mp4")
    return output

if __name__ == "__main__":
    print("🎬 YouTube Shorts 生成器 v2")
    print(f"   素材: {GAME_DIR}")
    print(f"   输出: {OUT_DIR}")
    print()
    generate()
