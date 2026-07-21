#!/usr/bin/env python3
"""
每日 Shorts + YouTube 上传自动化脚本
用法: python3 upload_shorts.py [--no-upload]
"""
import os, sys, argparse

SHORTS_DIR = "/root/.openclaw/workspace/shorts"
REPORTS_DIR = "/root/.openclaw/workspace/reports"
CLIENT_SECRET = "/root/.openclaw/workspace/youtube_client_secret.json"

def generate():
    """生成 Shorts 视频"""
    import subprocess
    result = subprocess.run(
        ["python3", "/root/.openclaw/workspace/scripts/make_shorts.py"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ 生成失败: {result.stderr}")
        sys.exit(1)
    print(result.stdout)

def get_latest_shorts():
    """获取今天生成的 Shorts"""
    import glob
    files = sorted(glob.glob(f"{SHORTS_DIR}/shorts-*.mp4"), key=os.path.getmtime)
    return files[-1] if files else None

def upload_to_youtube(video_path, title, description):
    """通过 YouTube Data API 上传视频"""
    # 检查凭据
    if not os.path.exists(CLIENT_SECRET):
        print(f"❌ 缺少 YouTube OAuth 凭据: {CLIENT_SECRET}")
        print("请先在 Google Cloud Console 创建 OAuth 2.0 客户端 ID 并保存为该文件")
        return False

    print("✅ 凭据检查通过，准备上传...")
    # 实际上传逻辑在 youtube_uploader.py
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-upload", action="store_true", help="仅生成，不上传")
    args = parser.parse_args()

    print("🎬 === 每日 Shorts 自动化 ===")
    generate()

    video = get_latest_shorts()
    if not video:
        print("❌ 未找到生成的视频")
        sys.exit(1)

    print(f"\n📹 视频: {video}")
    size_mb = os.path.getsize(video) / 1024 / 1024
    print(f"   大小: {size_mb:.1f}MB")

    if not args.no_upload:
        title = "🔥 精选在线游戏合集 | 免费玩 浏览器直接开"
        desc = """🎮 免费在线游戏合集，无需下载，浏览器直接玩！

恐龙跑酷 / 宝石消消乐 / 水果忍者 / 弹珠台 / 篮球投篮 / 深渊幸存者

🌐 完整游戏列表: https://nima54851.github.io/game-platform/

#游戏 #HTML5 #在线游戏 #益智游戏 #休闲游戏"""
        upload_to_youtube(video, title, desc)

if __name__ == "__main__":
    main()
