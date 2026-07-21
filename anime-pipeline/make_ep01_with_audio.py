#!/usr/bin/env python3
"""
咒術回戦 EP01 有声完整版
用法: python3 make_ep01_with_audio.py
"""
import asyncio, os, math, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
import edge_tts

# ========== 参数 ==========
EP = "01"
TITLE_CN = "咒术回战"
TITLE_JP = "呪術廻戦"
FPS = 30
W, H = 1080, 1920
FFMPEG = "/usr/local/lib/python3.12/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
TMP = "/tmp/jujutsu_ep01"
os.makedirs(TMP, exist_ok=True)
os.makedirs(f"{TMP}/frames", exist_ok=True)
os.makedirs(f"{TMP}/audio", exist_ok=True)

# ========== 助手 ==========
def ease(t): return t*t*(3-2*t)
def clamp(x,lo,hi): return max(lo,min(hi,x))

# ========== 对白剧本 ==========
SCENES = [
    # (开始秒, 结束秒, 角色, 语言, 文本)
    (0.0, 2.5,  None,    "narration_zh", "东京——这座表面繁华的城市，隐藏着无数诅咒的角落。"),
    (2.5, 5.0,  None,    "narration_zh", "人类产生的负面情绪，凝聚成咒灵，潜伏在黑暗之中。"),
    (5.0, 7.5,  "虎杖",  "male_zh",     "我叫虎杖悠仁，速度快，体力好，最适合当咒术师了！"),
    (7.5, 10.0, "虎杖",  "male_zh",     "爷爷说，要为一个群人努力到死。我一直记着这句话。"),
    (10.0, 12.5,"伏黒",  "male_zh",     "虎杖，你吃下去了。那个是宿儺的手指。"),
    (12.5, 15.0,"虎杖",  "male_zh",     "什么？！宿儺？那个千年诅咒之王？"),
    (15.0, 17.5,"伏黒",  "male_zh",     "现在你体内有20根手指中的1根。宿儺暂时无法完全觉醒。"),
    (17.5, 20.0,"五条",  "male_zh",     "我就知道你会吃下去，虎杖。"),
    (20.0, 22.5,"五条",  "male_zh",     "从今天起，你就是咒术师了。欢迎来到咒术高专。"),
    (22.5, 25.0,"野薔薇", "female_zh",  "哇，新人耶！我叫釘崎野薔薇，请多关照！"),
    (25.0, 27.5,"虎杖",  "male_zh",     "我叫虎杖悠仁，请多指教！"),
    (27.5, 30.0,"伏黒",  "male_zh",     "接下来，我们要对你进行咒力控制训练。"),
    (30.0, 32.5,None,   "narration_zh", "虎杖悠仁的咒术之路，从这一刻正式开始。"),
    (32.5, 35.0,None,   "narration_zh", "然而，宿儺的意识，已经在他的体内悄然苏醒……"),
    (35.0, 37.5,"宿儺", "male_zh",     "有趣的人类……你的身体，我就收下了。"),
    (37.5, 40.0,"虎杖", "male_zh",     "你是什么东西？！给我滚出去！"),
    (40.0, 42.5,"宿儺", "male_zh",     "哈哈哈！在这具身体里，你才是外来者。"),
    (42.5, 45.0,None,   "narration_zh", "第壱話「头来」——完"),
    (45.0, 47.0,None,   "narration_zh", "下集预告：宿儺的契约者……十种影术的秘密……"),
]

# 语音映射
VOICE_MAP = {
    "male_zh":    "zh-CN-YunxiNeural",
    "female_zh":  "zh-CN-XiaoxiaoNeural",
    "narration_zh": "zh-CN-YunyangNeural",
    "male_jp":    "ja-JP-KeitaNeural",
    "female_jp":  "ja-JP-NanamiNeural",
    "narration_jp": "ja-JP-KeitaNeural",
}

DURATION = 47.0

# ========== 生成 TTS 音频 ==========
async def generate_tts():
    print("🎙️  生成TTS音频...")
    tasks = []
    for i, (start, end, char, lang, text) in enumerate(SCENES):
        voice = VOICE_MAP.get(lang, "zh-CN-YunxiNeural")
        out_file = f"{TMP}/audio/scene_{i:02d}.mp3"
        if os.path.exists(out_file) and os.path.getsize(out_file) > 100:
            print(f"  跳过 scene_{i:02d} (已存在)")
            continue
        async def make_audio(txt, v, fn):
            try:
                comm = edge_tts.Communicate(txt, v)
                await comm.save(fn)
                return True
            except Exception as e:
                print(f"  ❌ {fn}: {e}")
                return False
        tasks.append(make_audio(text, voice, out_file))
        print(f"  排队: scene_{i:02d} [{char or '旁白'}] {text[:20]}...")
    # 并发生成
    await asyncio.gather(*tasks)
    print("  ✅ TTS 生成完成")

# ========== 生成背景音乐 ==========
def generate_bgm():
    print("🎵  生成背景音乐...")
    BGM = f"{TMP}/bgm.mp3"
    # 用 ffmpeg 生成简单的氛围音（低频嗡鸣 + 节奏鼓点）
    # 先生成一个正弦波环境音
    subprocess.run([
        FFMPEG, "-y",
        "-f", "lavfi", "-i", f"sine=frequency=80:duration={DURATION+2}",
        "-af", f"volume=0.08,lowpass=f=200,aecho=0.8:0.9:100|200:0.4|300:0.3",
        f"{TMP}/ambient.mp3"
    ], capture_output=True)
    # 节奏鼓点
    subprocess.run([
        FFMPEG, "-y",
        "-f", "lavfi", "-i", f"anoisesrc=d=1:c=pink:r=44100:a=0.1",
        "-af", f"lowpass=f=150,volume=0.05,tremolo=f=2:d=0.4",
        "-t", str(DURATION+2),
        f"{TMP}/drums.mp3"
    ], capture_output=True)
    # 合并混音
    subprocess.run([
        FFMPEG, "-y",
        "-i", f"{TMP}/ambient.mp3",
        "-i", f"{TMP}/drums.mp3",
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=longest,volume=1.5",
        "-t", str(DURATION+2),
        BGM
    ], capture_output=True)
    print(f"  ✅ BGM 生成完成 ({os.path.getsize(BGM)//1024}KB)")

# ========== 渲染单帧 ==========
def render_frame(frame_num):
    t = frame_num / FPS
    img = Image.new('RGBA', (W,H), (3,3,12,255))
    d = ImageDraw.Draw(img)

    # 背景光晕动画
    pulse = 0.8 + math.sin(t*1.5)*0.2
    for k in range(8):
        a = int(15*(8-k)//8*pulse)
        r = 120+k*110
        img_r = int(255*(0.9+0.1*math.sin(t+k)))
        d.ellipse([W//2-r, H//2-r, W//2+r, H//2+r], fill=(img_r,55+k*12,15,a))

    # 网格地面
    for x in range(0,W,50):
        d.line([(x,0),(x,H)],fill=(15,0,30,12),width=1)
    for y in range(0,H,50):
        d.line([(0,y),(W,y)],fill=(15,0,30,10),width=1)

    # 咒力圆环
    for ri in range(4):
        radius = 150+ri*100
        rot = t*(0.3+ri*0.08)*(1 if ri%2==0 else -1)
        a_ring = int(220*(1-ri*0.18))
        cx,cy = W//2, H//2-100
        pts = [(cx+math.cos(math.radians(a)+rot)*radius,
                cy+math.sin(math.radians(a)+rot)*radius) for a in range(0,360,2)]
        for j in range(len(pts)-1):
            d.line([pts[j],pts[j+1]],fill=(255,60+ri*15,20,a_ring),width=3-ri//2)
        for fi in range(8):
            angle = rot+fi*math.pi/4
            fx=cx+math.cos(angle)*radius; fy=cy+math.sin(angle)*radius
            d.ellipse([fx-5,fy-5,fx+5,fy+5],fill=(255,90,30,220))

    # 咒力粒子
    random.seed(int(t*12))
    for p in range(1500):
        angle = p*0.42+t*0.4
        r = 100+(p%110)*10+math.sin(t*3+p)*40
        px=W//2+math.cos(angle)*r
        py=H//2-100+math.sin(angle)*r*1.4+math.sin(t+p*0.5)*60
        py=clamp(py,0,H)
        sz=max(1,2+math.sin(t*5+p)*2)
        bright=170+int(85*math.sin(t*2+p))
        d.ellipse([px-sz,py-sz,px+sz,py+sz],fill=(bright,50+p%50,15,200))

    # 闪电
    if frame_num%12<2:
        la=int(220*(1-(frame_num%12)/2))
        lx=W//2+math.sin(t*10)*200
        ly=H//2-400
        for _ in range(7):
            lx2=lx+random.uniform(-40,40); ly2=ly+75
            d.line([(lx,ly),(lx2,ly2)],fill=(255,120,45,la),width=4)
            lx,ly=lx2,ly2

    # 当前场景对话框
    current_scene = None
    for start, end, char, lang, text in SCENES:
        if start <= t < end:
            current_scene = (start, end, char, lang, text)
            break

    scene_progress = 0
    if current_scene:
        start, end, char, lang, text = current_scene
        scene_progress = (t - start) / (end - start)
        scene_a = int(255 * ease(min(1, (t-start)*4)))
        fade_out_a = int(255 * ease(min(1, max(0, (end-t)*4))))
        alpha = min(scene_a, fade_out_a)

        if alpha > 20:
            # 对话框背景
            box_h = 180
            box_y = H - box_h - 30
            d.rectangle([30, box_y, W-30, H-30], fill=(0,0,0,180))
            d.rectangle([30, box_y, W-30, H-30], outline=(255,60,20,alpha), width=2)

            # 角色名
            char_name = char or "旁白"
            d.text((50, box_y+15), char_name, fill=(255,60,20,alpha))

            # 对话文字（分行）
            words = text
            d.text((50, box_y+55), words, fill=(255,255,255,alpha))

            # 进度条
            bar_w = W-80
            prog = scene_progress
            d.rectangle([40, H-20, W-40, H-10], fill=(30,0,0,150))
            d.rectangle([40, H-20, 40+bar_w*prog, H-10], fill=(255,60,20,200))

    # 顶部集数标题（开场）
    title_a = max(0, int(255*ease(min(1,t/1.5))*(1-ease(max(0,(t-4)/2)))))
    if title_a > 20:
        d.rectangle([0, H//2-180, W, H//2+180], fill=(3,3,12,180))
        d.text((W//2, H//2-60), "JUJUTSU KAISEN", fill=(255,60,20,title_a))
        d.text((W//2, H//2),    "呪術廻戦", fill=(255,255,255,title_a))
        d.text((W//2, H//2+50), f"EP{EP} 第{EP}話「头来」", fill=(200,200,200,title_a))

    # 弹幕
    danmaku_list = [
        (2.0,"呪術回戦！！！"),(3.0,"虎杖悠仁"),(4.5,"宿儺おいしい"),
        (6.0,"MAPPA 作画神"),(8.0,"五条先生最强"),(10.0,"伏黒好帅"),
        (12.0,"野薔薇我婆"),(14.0,"第1話永远的名作"),(16.0,"呪術最高！！！"),
        (20.0,"钉崎野蔷薇登场"),(22.0,"咒术高专好酷"),(25.0,"新人三人组"),
        (28.0,"宿儺开始觉醒了"),(30.0,"好热血"),(33.0,"下集预告！！"),
        (36.0,"宿儺的声音好帅"),(38.0,"虎杖加油"),(40.0,"第1話永远的神"),
        (43.0,"五条老师教教我"),(45.0,"第2話期待"),(46.0,"完结撒花🎉"),
    ]
    for dm_t, dm_txt in danmaku_list:
        if dm_t < t < dm_t+6:
            xpos = W - (t-dm_t)/6*(W+400)+200
            if -200 < xpos < W+100:
                da = min(255, int(255*min((t-dm_t)*4,(dm_t+6-t)*3)))
                if da > 0:
                    d.text((xpos, H*0.18+math.sin(t+dm_t)*10), dm_txt, fill=(255,255,255,da))
                    d.text((xpos+1, H*0.18+math.sin(t+dm_t)*10+1), dm_txt, fill=(0,0,0,da))

    # 底部版权栏
    if t > 2:
        d.rectangle([0,H-60,W,H],fill=(0,0,0,150))
        d.text((30,H-35), "© 芥見下々/集英社", fill=(255,60,20,150))
        d.text((W-30,H-35), "MAPPA|朴性厚", fill=(150,150,150,120), anchor="ra")

    # 集数徽章
    if t > 1:
        d.text((W-20,30), f"EP{EP}", fill=(255,60,20,180))
        d.text((W-20,55), "JUJUTSU KAISEN", fill=(180,180,180,130))

    return img

# ========== 生成视频帧 ==========
def generate_frames():
    print(f"🖼️  生成 {DURATION*FPS} 帧 ({FPS}fps)...")
    total = int(DURATION * FPS)
    for i in range(total):
        frame = render_frame(i)
        frame.save(f"{TMP}/frames/frame_{i:06d}.png", "PNG", quality=95)
        if i % 150 == 0:
            print(f"  {i}/{total} ({100*i//total}%)")
    print("  ✅ 帧生成完成")

# ========== 合并音频 ==========
def combine_audio():
    print("🎧  合并音频...")
    # 先拼接所有场景音频成一个长音频
    concat_list = f"{TMP}/concat.txt"
    with open(concat_list, "w") as f:
        for i in range(len(SCENES)):
            f.write(f"file 'audio/scene_{i:02d}.mp3'\n")
            f.write(f"file 'silence_0.3.mp3'\n")
    
    # 生成0.3秒静音
    subprocess.run([
        FFMPEG, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
        "-t", "0.3", f"{TMP}/silence_0.3.mp3"
    ], capture_output=True)
    
    # 合并场景音频
    subprocess.run([
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c:a", "aac", "-b:a", "128k",
        f"{TMP}/dialogue.aac"
    ], capture_output=True)
    
    # 混音：对话 + BGM
    subprocess.run([
        FFMPEG, "-y",
        "-i", f"{TMP}/dialogue.aac",
        "-i", f"{TMP}/bgm.mp3",
        "-filter_complex", "[0:a]volume=1.4[dlg];[1:a]volume=0.35[bgm];[dlg][bgm]amix=inputs=2:duration=longest[out]",
        "-map", "[out]",
        "-t", str(DURATION+2),
        f"{TMP}/final_audio.aac"
    ], capture_output=True)
    print("  ✅ 音频混音完成")

# ========== 合成最终视频 ==========
def make_video():
    print("🎬  合成最终视频...")
    subprocess.run([
        FFMPEG, "-y",
        "-framerate", str(FPS),
        "-i", f"{TMP}/frames/frame_%06d.png",
        "-i", f"{TMP}/final_audio.aac",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        "-shortest",
        f"/root/.openclaw/workspace/jujutsu_ep{EP}_full.mp4"
    ], capture_output=True)
    size = os.path.getsize(f"/root/.openclaw/workspace/jujutsu_ep{EP}_full.mp4")
    print(f"  ✅ 完成: jujutsu_ep{EP}_full.mp4 ({size//1024//1024}MB)")

# ========== 主流程 ==========
async def main():
    print(f"=== 咒術回戦 EP{EP} 有声完整版生成 ===")
    await generate_tts()
    generate_bgm()
    generate_frames()
    combine_audio()
    make_video()
    print("\n🎉 全部完成！")

asyncio.run(main())
