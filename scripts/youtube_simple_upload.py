#!/usr/bin/env python3
"""
YouTube 简易上传脚本（无需 Google Cloud！）
使用 YouTube 内部 API + 浏览器 Cookie 上传
只需要你的电脑上有 Chrome 并登录了 YouTube

使用方法：
1. 确保本机 Chrome 已登录 YouTube
2. pip install browser_cookie3 requests
3. python3 youtube_simple_upload.py 视频.mp4
"""
import sys
import os
import requests
import browser_cookie3
import json
from datetime import datetime

# YouTube 内部上传 API（无需 OAuth）
UPLOAD_URL = "https://www.youtube.com/upload/video"

def get_youtube_cookies():
    """从 Chrome 读取 YouTube 登录 Cookie"""
    print("🔑 读取 Chrome YouTube Cookie...")
    try:
        cookies = browser_cookie3.chrome(domain_name='youtube.com')
        cookie_dict = {}
        for c in cookies:
            cookie_dict[c.name] = c.value
        required = ['SID', 'HSID', 'SSID', 'APISID', 'SAPISID', '__Secure-1PSID']
        missing = [k for k in required if k not in cookie_dict]
        if missing:
            print(f"⚠️ 缺少 Cookie: {missing}，请确保 Chrome 已登录 YouTube")
            return None
        return cookie_dict
    except Exception as e:
        print(f"❌ 读取 Cookie 失败: {e}")
        return None

def get_upload_token(cookies):
    """获取上传页面 token"""
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "*/*",
    }
    r = session.get("https://www.youtube.com/upload", headers=headers, cookies=cookies)
    # 从页面提取 token
    token = None
    for line in r.text.split('\n'):
        if 'XSRF_TOKEN' in line or 'token' in line.lower():
            if 'value=' in line:
                try:
                    token = line.split('value=')[1].split('"')[1]
                    break
                except:
                    pass
    return session, token, cookies

def upload_video(video_path, title, description, tags):
    """上传视频到 YouTube"""
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        return

    print(f"📤 开始上传: {video_path}")
    print(f"   标题: {title}")
    print(f"   大小: {os.path.getsize(video_path)/1024/1024:.1f}MB")

    cookies = get_youtube_cookies()
    if not cookies:
        print("\n💡 如果 Chrome Cookie 读取失败，请尝试：")
        print("   1. 确认 Chrome 已登录 YouTube")
        print("   2. 或安装 EditThisCookie 扩展，导出 JSON 后改名为 youtube_cookies.json")
        return

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.youtube.com/upload",
    })
    # 设置 Cookie
    for name, value in cookies.items():
        session.cookies.set(name, value, domain='.youtube.com')

    # 获取上传页面
    print("🔄 获取上传页面...")
    r = session.get("https://www.youtube.com/upload")
    if "Sign in" in r.text or r.status_code == 403:
        print("❌ Cookie 已过期，请重新在 Chrome 登录 YouTube")
        return

    # 从页面提取 xsrf token
    xsrf = ""
    for c in session.cookies:
        if c.name == 'XSRF_TOKEN':
            xsrf = c.value
            break

    # 上传视频文件
    print("📤 上传中（请耐心等待）...")
    filename = os.path.basename(video_path)

    # 第一步：初始化上传
    init_url = "https://www.youtube.com/upload/internalupload/ViVaBetterThanStandard"
    files_meta = {
        "filename": (None, filename, "application/x-www-form-urlencoded"),
    }

    data = {
        "token": xsrf,
        "title": title,
        "description": description,
        "category": "20",  # Gaming
        "keywords": ",".join(tags),
        "privacyStatus": "public",
    }

    with open(video_path, 'rb') as f:
        files = {
            "file": (filename, f, "video/*"),
        }
        files.update(files_meta)
        r = session.post(init_url, data=data, files=files, timeout=300)

    if r.status_code in [200, 201, 204]:
        video_id = r.json().get('videoId', 'unknown')
        print(f"✅ 上传成功！")
        print(f"   视频ID: {video_id}")
        print(f"   链接: https://www.youtube.com/watch?v={video_id}")
    else:
        print(f"⚠️ 响应状态: {r.status_code}")
        print(f"   响应: {r.text[:500]}")
        print("\n💡 YouTube 内部 API 可能已更新，建议使用 Google Colab 方式上传")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 youtube_simple_upload.py <视频文件路径>")
        print("示例: python3 youtube_simple_upload.py shorts-2026-07-19.mp4")
        sys.exit(1)

    video_path = sys.argv[1]
    title = f"🔥 在线游戏合集 {datetime.now().strftime('%Y年%m月%d日')} | 免费玩"
    description = """🎮 免费在线游戏合集，无需下载，浏览器直接玩！

恐龙跑酷 · 宝石消消乐 · 水果忍者 · 弹珠台 · 篮球投篮 · 深渊幸存者

🌐 完整游戏列表: https://nima54851.github.io/game-platform/

#游戏 #HTML5 #在线游戏 #益智游戏 #休闲游戏 #Gaming"""
    tags = ["在线游戏", "HTML5游戏", "益智游戏", "休闲游戏", "免费游戏", "浏览器游戏"]

    upload_video(video_path, title, description, tags)
