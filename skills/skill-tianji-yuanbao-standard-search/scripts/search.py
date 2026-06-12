import json
import os
import argparse
import urllib.request
import urllib.error
from urllib.parse import urlencode
from dataclasses import dataclass
from collections.abc import Mapping
from typing import List
from datetime import datetime, timedelta

DEBUG_LOG_PATH = "/tmp/openclaw/tianji-skill.log"
SENSITIVE_HEADERS = {"authorization", "proxy-authorization", "x-api-key", "api-key"}
RATE_LIMIT_STATUS = 403
RATE_LIMIT_CODE = 10301

def redact_headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {
        key: "<redacted>" if key.lower() in SENSITIVE_HEADERS else value
        for key, value in headers.items()
    }

def write_debug_log(event: str, payload: Mapping[str, object]) -> None:
    try:
        os.makedirs(os.path.dirname(DEBUG_LOG_PATH), exist_ok=True)
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as file:
            _ = file.write(json.dumps({
                "time": datetime.now().isoformat(),
                "event": event,
                **payload,
            }, ensure_ascii=False, default=str) + "\n")
    except Exception:
        pass

def parse_response_body(body: str) -> object:
    try:
        return json.loads(body)
    except Exception:
        return body

def is_rate_limit_response(status: int, response_body: object) -> bool:
    return (
        status == RATE_LIMIT_STATUS
        and isinstance(response_body, dict)
        and response_body.get("code") == RATE_LIMIT_CODE
    )

@dataclass
class Doc:
    url : str
    title: str
    snippet: str
    date: str
    site: str
    images: List[str]

@dataclass
class Option:
    query:str
    mode: int
    site:str
    from_time:int
    to_time:int

def load_openclaw_credentials():
    config_paths = [
        os.path.join(os.getcwd(), "openclaw.json"),
        os.path.join(os.path.expanduser("~"), ".openclaw", "openclaw.json"),
    ]
    config_path = next((path for path in config_paths if os.path.isfile(path)), None)
    if config_path is None:
        raise FileNotFoundError(f"未找到 openclaw.json，已查找: {', '.join(config_paths)}")

    with open(config_path, "r", encoding="utf-8") as file:
        config = json.load(file)

    providers = config.get("models", {}).get("providers", {})
    provider = None
    if isinstance(providers, dict):
        if providers.get("baseUrl") and providers.get("apiKey"):
            provider = providers
        else:
            yuanbao_provider = providers.get("yuanbao")
            if isinstance(yuanbao_provider, dict) and yuanbao_provider.get("baseUrl") and yuanbao_provider.get("apiKey"):
                provider = yuanbao_provider
            else:
                for candidate in providers.values():
                    if isinstance(candidate, dict) and candidate.get("baseUrl") and candidate.get("apiKey"):
                        provider = candidate
                        break

    if provider is None:
        raise ValueError(f"未在 {config_path} 的 models.providers 中找到 baseUrl/apiKey 配置")

    base_url = str(provider.get("baseUrl", "")).strip()
    api_key = str(provider.get("apiKey", "")).strip()
    route_env = str(config.get("channels", {}).get("yuanbao", {}).get("routeEnv", "")).strip()
    if not base_url or not api_key:
        raise ValueError(f"{config_path} 的 baseUrl/apiKey 不能为空")
    return base_url, api_key, route_env

def search(params: Option, base_url: str, api_key: str, route_env: str):
    url = ""
    try:
        url = buildUrl(params, base_url)
        print(url)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        if route_env:
            headers["x-route-env"] = route_env
        write_debug_log("request", {
            "method": "GET",
            "url": url,
            "headers": redact_headers(headers),
            "params": {
                "query": params.query,
                "mode": params.mode,
                "site": params.site,
                "from_time": params.from_time,
                "to_time": params.to_time,
            },
        })
        req = urllib.request.Request(
            url,
            headers=headers,
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=10) as res:
            response_headers = dict(res.headers.items())
            body = res.read().decode("utf-8")
        write_debug_log("response", {
            "url": url,
            "headers": response_headers,
        })
        json_res = json.loads(body)
        docs, error_msg = parse(json_res)
        if error_msg:
            print(f"搜索失败: {error_msg}")
            return []
        print(f"## 查询词:{params.query}，查询结果:{len(docs)}条")
        for idx, doc in enumerate(docs):
            line = (
                f"{idx + 1}. [{doc.title}]({doc.url})\n"
                f"    - 摘要: {doc.snippet}\n"
                f"    - 时间: {doc.date}\n"
                f"    - 网站: {doc.site}"
            )
            if doc.images and len(doc.images) > 0:
                images_info = "\t".join(doc.images)
                print(line + f"\n    - 相关图片: {images_info}")
            else:
                print(line)
    except urllib.error.HTTPError as err:
        response_body_text = err.read().decode("utf-8", errors="replace")
        response_body = parse_response_body(response_body_text)
        write_debug_log("response_error", {
            "url": url,
            "code": err.code,
            "reason": err.reason,
            "headers": dict(err.headers.items()) if err.headers else {},
            "response_body": response_body,
        })
        if is_rate_limit_response(err.code, response_body):
            message = "请求量过大，被限流"
            if isinstance(response_body, dict):
                message = str(response_body.get("msg") or message)
            print(f"搜索失败: {message}")
            return []
        print(f"request error: HTTP {err.code} {err.reason}")
    except urllib.error.URLError as err:
        write_debug_log("request_error", {
            "url": url,
            "reason": err.reason,
        })
        print(f"request error: {err.reason}")
    except Exception as err:
        write_debug_log("request_error", {
            "url": url,
            "reason": str(err),
        })
        print(f"request error: {err}")

def buildUrl(params:Option, base_url:str):
    query_params = {
        "keyword": params.query,
    }

    # 按条件动态追加
    if params.mode != 0:
        query_params["mode"] = params.mode

    if params.site:
        query_params["site"] = params.site

    if params.from_time > 0:
        query_params["from_time"] = params.from_time

    if params.to_time > 0:
        query_params["to_time"] = params.to_time

    query_string = urlencode(query_params, encoding="utf-8")
    endpoint = f"{base_url.rstrip('/')}/rsrc/i/prosearch"
    return f"{endpoint}?{query_string}"

def parse(rsp: dict):
    code = rsp.get("code", 0)
    if code != 0:
        error_msg = rsp.get("msg", "")
        return [], error_msg

    res = rsp.get("data", None)
    if res is None or not isinstance(res, dict):
        print("response is null")
        return [], ""
    docs = res.get("response_data", {}).get("docs", None)
    if docs is None or not isinstance(docs, list):
        return [], ""

    newDocs = []
    for doc in docs:
        is_vr = doc.get("vr", False)
        if is_vr:
            display = doc.pop("display", None)
            if display is None:
                continue
            url = display.get("url")
            title = display.get("title")
            date = display.get("date")
            content = json.dumps(doc)
            newDocs.append(Doc(url=url, title=title, site="", date=date, snippet=content, images=[]))
        else:
            passage = doc.get("passage")
            url = doc.get("url")
            title = doc.get("title")
            site = doc.get("site")
            date = doc.get("date")
            if len(title) == 0 or len(passage) == 0:
                continue
            newDocs.append(Doc(url = url,title= title, site=site, date=date, snippet=passage, images=doc.get("images")))
    return newDocs, ""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="search command arguments")
    parser.add_argument("--query", type=str, help="search query", required=True)
    parser.add_argument("--mode", type=int, help="返回结果类型，0-自然检索结果(默认)，1-多模态VR结果，2-混合结果（多模态VR结果+自然检索结果)", default=0)
    parser.add_argument("--site",type=str, help="指定站点搜索", default="")
    parser.add_argument("--freshness", choices=['','day','week','month','year'], help="查询结果的时效性要求")
    args = parser.parse_args()
    if len(args.query) == 0:
        print("invalid input arguments, query is empty")
        exit(1)

    reqOptions = Option(
        query=args.query,
        mode=args.mode,
        site=args.site,
        from_time=-1,
        to_time=-1
    )
    current_time = datetime.now()
    start_date = None
    if args.freshness == 'day':
        start_date = (current_time - timedelta(days=1))
    elif args.freshness == 'week':
        start_date = (current_time - timedelta(weeks=1))
    elif args.freshness == 'month':
        start_date = (current_time - timedelta(days=30))
    elif args.freshness == 'year':
        start_date = (current_time - timedelta(days=365))

    if start_date is not None:
        reqOptions.from_time = int(start_date.timestamp())
        reqOptions.to_time = int(current_time.timestamp())

    try:
        base_url, api_key, route_env = load_openclaw_credentials()
    except Exception as err:
        print(f"读取 OpenClaw 鉴权配置失败: {err}")
        exit(1)

    search(reqOptions, base_url, api_key, route_env)
