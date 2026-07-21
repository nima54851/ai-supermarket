#!/usr/bin/env python3
"""
YouTube Cookie 上传器（无需 Google Cloud！）

使用步骤：
1. 在 Chrome 安装插件 "EditThisCookie"
2. 打开 youtube.com，登录你的账号
3. 点击 EditThisCookie 图标 → 导出为 JSON → 保存为 youtube_cookies.json
4. 把 youtube_cookies.json 放到这个脚本同目录
5. 运行: python3 youtube_cookie_upload.py

或者直接运行，上传今天生成的 Shorts：
  python3 youtube_cookie_upload.py
"""
import os
import json
import requests
import sys
from datetime import datetime

# ============ 配置区 ============
COOKIE_FILE = "/root/.openclaw/workspace/scripts/youtube_cookies.json"
VIDEO_FILE  = "/root/.openclaw/workspace/shorts/shorts-2026-07-19.mp4"  # 今天生成的
TITLE       = "🔥 在线游戏合集 | 免费玩 浏览器直接开"
DESCRIPTION = """🎮 免费在线游戏合集，无需下载，浏览器直接玩！

恐龙跑酷 / 宝石消消乐 / 水果忍者 / 弹珠台 / 篮球投篮 / 深渊幸存者

🌐 完整游戏列表: https://nima54851.github.io/game-platform/

#游戏 #HTML5 #在线游戏 #益智游戏 #休闲游戏 #Gaming"""
TAGS        = "在线游戏,HTML5游戏,益智游戏,休闲游戏,免费游戏,浏览器游戏,Gaming"
# =================================

YOUTUBE_URL = "https://www.youtube.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.youtube.com/upload",
}


def load_cookies():
    """加载 cookies JSON 文件"""
    if not os.path.exists(COOKIE_FILE):
        print(f"❌ Cookie 文件不存在: {COOKIE_FILE}")
        print("\n📋 请按以下步骤获取 Cookie：")
        print("   1. Chrome 安装插件 EditThisCookie")
        print("   2. 打开 youtube.com 并登录")
        print("   3. 点击 EditThisCookie 图标 → 导出为 JSON")
        print(f"   4. 保存为: {COOKIE_FILE}")
        print("\n💡 或者直接把 Cookie 内容粘贴到脚本里（见脚本底部的 COOKIE_DATA）")
        return None

    with open(COOKIE_FILE, "r") as f:
        cookies_list = json.load(f)

    # requests 的 RequestsCookieJar 格式
    jar = requests.cookies.RequestsCookieJar()
    for c in cookies_list:
        jar.set(
            name=c.get("name", ""),
            value=c.get("value", ""),
            domain=c.get("domain", ".youtube.com"),
            path=c.get("path", "/"),
            secure=c.get("secure", True),
            expires=c.get("expirationDate"),
        )
    return jar


def get_upload_page(session):
    """访问上传页面，获取必要的 session cookies 和 token"""
    print("🔄 访问上传页面...")
    r = session.get(f"{YOUTUBE_URL}/upload", headers=HEADERS, timeout=15)
    if r.status_code != 200:
        print(f"❌ 访问失败: {r.status_code}")
        return None

    # 检查是否已登录
    if "yt-navigate-start" not in r.text and "SignIn" in r.text:
        print("⚠️ 可能未登录，请检查 Cookie 是否包含登录态")
        return session

    print(f"✅ 上传页面访问成功 (状态码 {r.status_code})")
    return session


def extract_token(session, resp_text):
    """从上传页面提取 CSRF token"""
    import re
    # 尝试多种 token 提取方式
    patterns = [
        r'"XSRF_TOKEN"\s*:\s*"([^"]+)"',
        r'xsrf_token\s*[=:]\s*["\']([^"\']+)["\']',
        r'&token=([^&]+)',
        r'name="csrf"\s+value="([^"]+)"',
    ]
    for pat in patterns:
        m = re.search(pat, resp_text)
        if m:
            token = m.group(1)
            session.headers.update({"X-CSRF-Token": token})
            print(f"✅ CSRF Token 获取成功")
            return token
    print("⚠️ 未找到 CSRF Token，将尝试直接上传")
    return ""


def upload_video(session, video_path):
    """上传视频到 YouTube"""
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        return None

    file_size = os.path.getsize(video_path)
    filename = os.path.basename(video_path)
    print(f"\n📤 开始上传: {filename}")
    print(f"   大小: {file_size/1024/1024:.1f} MB")

    # 第一步：获取上传 session
    upload_url = f"{YOUTUBE_URL}/upload_ajax"

    with open(video_path, "rb") as f:
        files = {
            "file": (filename, f, "video/*"),
        }
        data = {
            "name": filename,
            "title": TITLE,
            "description": DESCRIPTION,
            "keywords": TAGS,
            "category": "20",  # Gaming
            "privacyStatus": "public",
            "publishType": "YOUTUBE",
        }

        # 带上所有 session cookies
        session.headers.update({
            "X-YouTube-Videos-Checksum-Algorithm": "crc32",
            "X-YouTube-Package-Snapshot-Id": "",
        })

        print("📤 上传中（这可能需要几分钟）...")
        r = session.post(
            upload_url,
            files=files,
            data=data,
            timeout=600,
            allow_redirects=True
        )

    print(f"   响应状态: {r.status_code}")

    # 尝试从响应中提取 video ID
    try:
        resp = r.json()
        video_id = resp.get("video_id") or resp.get("id")
        if video_id:
            return video_id
        # 尝试其他格式
        for key in ["videoId", "video_id", "id"]:
            if key in resp:
                return resp[key]
    except:
        pass

    # 检查响应中是否包含 video ID
    text = r.text
    if "video_id" in text:
        import re
        m = re.search(r'"video_id"\s*:\s*"([^"]+)"', text)
        if m:
            return m.group(1)

    print(f"⚠️ 响应内容（前500字）: {r.text[:500]}")
    return None


def main():
    print("🎬 YouTube Cookie 上传器")
    print("=" * 40)

    # 加载 cookies
    jar = load_cookies()
    if not jar:
        print("\n💡 备选方案：直接粘贴 Cookie 内容到脚本底部 COOKIE_DATA 变量中")
        return

    # 创建 session
    session = requests.Session()
    session.cookies = jar
    session.headers.update(HEADERS)

    # 获取上传页面
    r = session.get(f"{YOUTUBE_URL}/upload", headers=HEADERS, timeout=15)
    if r.status_code == 403 or "SignIn" in r.text or "signin" in r.url:
        print("❌ Cookie 已过期或无效，请重新导出最新 Cookie")
        return

    # 提取 token
    extract_token(session, r.text)

    # 上传视频
    video_id = upload_video(session, VIDEO_FILE)

    if video_id:
        url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"\n🎉 上传成功！")
        print(f"   视频ID: {video_id}")
        print(f"   链接: {url}")
    else:
        print("\n❌ 上传未能获取到视频ID，可能需要换一种方式")
        print("   建议：视频文件可以手动上传到 https://studio.youtube.com")


# ---- 手动粘贴 Cookie 数据的备选方案 ----
# 如果无法导出 JSON，可以在这里直接粘贴 Cookie 字符串
COOKIE_DATA = None  # 示例: "LOGIN_INFO=xxx; SID=xxx; ..."
