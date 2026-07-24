#!/usr/bin/env python3
"""测试 Telegram 代理连通性"""
import asyncio
import httpx

MTPROXY_URL = "socks5://ee29044830465c5171f152ab7d07ccfc89617a7572652e6d6963726f736f66742e636f6d@18.139.137.172:443"

async def test_proxy():
    print(f"测试代理: {MTPROXY_URL}")
    try:
        proxies = {"http://": MTPROXY_URL, "https://": MTPROXY_URL}
        async with httpx.AsyncClient(proxies=proxies, timeout=10.0) as client:
            resp = await client.get("https://api.telegram.org/bot8979991426:AAEtgWjhF1KV_pJZVwzjk-ZE2_Yf1-W4RDU/getMe")
            print("✅ Telegram API 响应:", resp.json())
    except Exception as e:
        print("❌ 连接失败:", type(e).__name__, str(e))

asyncio.run(test_proxy())
