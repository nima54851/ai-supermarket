#!/usr/bin/env python3
"""
咒術回戰 動漫視頻生成器 — 靈犀
用法: python3 generate_episode.py <集數> [时长秒]
例: python3 generate_episode.py 01 60
"""
import sys, os, math, random, subprocess, argparse
from PIL import Image, ImageDraw, ImageFont

# 參數
EPISODE = sys.argv[1] if len(sys.argv) > 1 else "01"
DURATION = int(sys.argv[2]) if len(sys.argv) > 2 else 60
FPS = 60  # 高幀率
W, H = 1080, 1920  # 9:16 短視頻豎版

OUTPUT_DIR = "/tmp/frames"
OUTPUT_MP4 = f"/tmp/jujutsu_ep{EPISODE}.mp4"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ========== 工具函數 ==========
def ease(t): return t*t*(3-2*t)
def clamp(x,lo,hi): return max(lo,min(hi,x))
def lerp(a,b,t): return a+(b-a)*t

# ========== 渲染單幀 ==========
def render(frame_num):
    t = frame_num / FPS
    img = Image.new('RGBA',(W,H),(3,3,12,255))
    draw = ImageDraw.Draw(img)

    # 背景光暈
    for i in range(8):
        a = int(10*(8-i)//8)
        r = 150+i*120
        draw.ellipse([W//2-r, H//2-r, W//2+r, H//2+r], fill=(255,55+i*15,15,a))

    # 地面網格
    for x in range(0,W,60):
        draw.line([(x,0),(x,H)],fill=(15,0,30,12),width=1)
    for y in range(0,H,60):
        draw.line([(0,y),(W,y)],fill=(15,0,30,10),width=1)

    # 咒力圓環
    for ri in range(4):
        radius = 160+ri*100
        rot = t*(0.25+ri*0.08)*(1 if ri%2==0 else -1)
        a_ring = int(220*(1-ri*0.18))
        cx,cy = W//2,H//2-100
        # 畫圓（多邊形逼近）
        pts = [(cx+math.cos(math.radians(i)+rot)*radius,
                cy+math.sin(math.radians(i)+rot)*radius) for i in range(0,360,2)]
        for i in range(len(pts)-1):
            draw.line([pts[i],pts[i+1]],fill=(255,60+ri*15,20,a_ring),width=3-ri//2)
        # 符文光點
        for fi in range(8):
            angle = rot+fi*math.pi/4
            fx = cx+math.cos(angle)*radius
            fy = cy+math.sin(angle)*radius
            draw.ellipse([fx-5,fy-5,fx+5,fy+5],fill=(255,90,30,200))

    # 咒力粒子（1200個）
    random.seed(int(t*10))
    for p in range(1200):
        angle = p*0.41+t*0.4
        r = 120+(p%100)*9+math.sin(t*2.5+p)*35
        px = W//2+math.cos(angle)*r
        py = H//2-100+math.sin(angle)*r*1.4+math.sin(t+p*0.4)*50
        py = clamp(py,0,H)
        sz = max(1,2+math.sin(t*4+p)*1.5)
        c = (255,55+p%80,15,200)
        draw.ellipse([px-sz,py-sz,px+sz,py+sz],fill=c)

    # 閃電
    if frame_num%10<2:
        la = int(220*(1-(frame_num%10)/2))
        lx=W//2+math.sin(t*9)*180
        ly=H//2-380
        for seg in range(6):
            lx2=lx+random.uniform(-35,35)
            ly2=ly+70
            draw.line([(lx,ly),(lx2,ly2)],fill=(255,110,40,la),width=3)
            lx,ly=lx2,ly2

    # === UI 層 ===
    
    # 開場標題動畫 (0~7秒)
    title_phase = min(1,t/2)*ease(min(1,max(0,(2-t)/2)))
    fade_out = ease(min(1,max(0,(t-8)/1.5))) if t>8 else 0
    ta = max(0,min(1,title_phase-fade_out))
    ta_int = int(255*ta)
    if ta_int>0:
        draw.rectangle([0,H//2-240,W,H//2+240],fill=(3,3,12,210))
        f72 = lambda s: ImageFont.load_default()  # 避免字體問題
        draw.text((W//2,H//2-80),  "JUJUTSU KAISEN",  fill=(255,60,20,ta_int))
        draw.text((W//2,H//2-30),  "呪術廻戦",          fill=(255,255,255,ta_int))
        draw.text((W//2,H//2+20),  f"EP{EPISODE}  第{EPISODE}話", fill=(200,200,200,ta_int))

    # 傷害數字 (3.5~6秒)
    if 3.5<t<6.5:
        dt=(t-3.5)/3
        da=int(255*(1-dt**2))
        ds=1+(1-dt)*0.6
        size=int(100*ds)
        draw.text((W//2,H//2-180),f"×{EPISODE}",fill=(255,200,50,da))
        draw.text((W//2,H//2-100),"宿儺",fill=(255,80,20,da))

    # 彈幕 (4~DURATION秒)
    danmaku_pool = [
        (4.0,"呪術回戦！！！"),(4.8,"虎杖悠仁"),(5.5,"宿儺おいしい"),
        (6.2,"MAPPA 作画神"),(7.0,"第1話永遠の名作"),(7.8,"釘崎かわいい"),
        (8.5,"五条先生最强"),(9.2,"呪術回戦最高！！！"),(10.0,"このアニメ好き"),
        (10.8,"伏黒の影太强了"),(11.5,"野薔薇好颯"),(12.2,"呪術好き"),
    ]
    for dm_t,dm_txt in danmaku_pool:
        if dm_t<t<dm_t+7:
            xpos=W-(t-dm_t)/7*(W+400)+200
            if -200<xpos<W+100:
                da2=min(255,int(255*min((t-dm_t)*3,(dm_t+7-t)*3)))
                if da2>0:
                    draw.text((xpos,H*0.25),dm_txt,fill=(255,255,255,da2))
                    draw.text((xpos,H*0.25+2),dm_txt,fill=(0,0,0,da2))

    # 底部欄 (9秒後)
    if t>9:
        ba=int(200*ease(min(1,(t-9)/2)))
        draw.rectangle([0,H-80,W,H],fill=(0,0,0,ba))
        draw.text((30,H-45),"© 芥見下々/集英社",fill=(255,60,20,ba))
        draw.text((W-30,H-45),"MAPPA|朴性厚",fill=(150,150,150,ba),anchor='ra')

    # 裂紋 (15秒後)
    if t>15 and frame_num%30==0:
        ca=int(150*ease(min(1,(t-15)/3)))
        if ca>20:
            random.seed(frame_num//30)
            for _ in range(6):
                cx2=random.randint(0,W);cy2=random.randint(0,H)
                for _ in range(8):
                    nx=cx2+math.cos(random.uniform(0,6.28))*random.randint(25,65)
                    ny=cy2+math.sin(random.uniform(0,6.28))*random.randint(25,65)
                    draw.line([(cx2,cy2),(nx,ny)],fill=(255,60,20,ca),width=2)
                    cx2,cy2=nx,ny

    # 集數徽章 (2秒後)
    if t>2:
        draw.text((W-20,30),f"EP{EPISODE}",fill=(255,60,20,200))
        draw.text((W-20,55),"JUJUTSU KAISEN",fill=(180,180,180,150))

    return img

# ========== 主流程 ==========
print(f"生成 EP{EPISODE} — {DURATION}秒 @ {FPS}fps = {DURATION*FPS} 帧")
total = DURATION * FPS
for i in range(total):
    frame = render(i)
    frame.save(f"{OUTPUT_DIR}/frame_{i:06d}.png",'PNG',quality=95)
    if i%150==0: print(f"  {i}/{total} ({100*i//total}%)")

print("合成 MP4...")
FFMPEG = "/usr/local/lib/python3.12/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
subprocess.run([
    FFMPEG,"-y","-framerate",str(FPS),
    "-i",f"{OUTPUT_DIR}/frame_%06d.png",
    "-c:v","libx264","-preset","slow","-crf","18",
    "-pix_fmt","yuv420p","-movflags","+faststart",
    "-vf",f"scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
    OUTPUT_MP4
], capture_output=True)

size = os.path.getsize(OUTPUT_MP4)
print(f"✅ 完成! {OUTPUT_MP4} ({size//1024//1024}MB)")
