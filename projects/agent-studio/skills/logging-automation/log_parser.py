#!/usr/bin/env python3
"""
log_parser.py — 结构化日志解析器
支持: JSON / CSV / 纯文本 / Nginx / Apache / Syslog 格式
"""

import json
import sys
import re
from datetime import datetime
from pathlib import Path

FORMATS = {
    "json": parse_json_line,
    "nginx": parse_nginx_line,
    "apache": parse_apache_line,
    "syslog": parse_syslog_line,
    "text": parse_text_line,
}


def parse_json_line(line: str) -> dict | None:
    try:
        obj = json.loads(line.strip())
        obj["_parsed_at"] = datetime.utcnow().isoformat()
        obj["_original"] = line.strip()
        return obj
    except json.JSONDecodeError:
        return None


NGINX_RE = re.compile(
    r'(?P<ip>[\d.]+) - (?P<user>[\w-]+) \[(?P<ts>[^\]]+)\] '
    r'"(?P<method>\w+) (?P<path>\S+) (?P<proto>\S+)" '
    r'(?P<status>\d+) (?P<size>\d+) "(?P<ref>[^"]*)" "(?P<ua>[^"]*)"'
)


def parse_nginx_line(line: str) -> dict | None:
    m = NGINX_RE.match(line.strip())
    if not m:
        return None
    g = m.groupdict()
    return {
        "ip": g["ip"],
        "user": g["user"],
        "timestamp": g["ts"],
        "method": g["method"],
        "path": g["path"],
        "status": int(g["status"]),
        "bytes": int(g["size"]),
        "referer": g["ref"],
        "user_agent": g["ua"],
        "_format": "nginx",
        "_parsed_at": datetime.utcnow().isoformat(),
    }


def parse_apache_line(line: str) -> dict | None:
    # Apache CLF — similar pattern to nginx
    return parse_nginx_line(line)


SYSLOG_RE = re.compile(
    r'(?P<month>\w+)\s+(?P<day>\d+)\s+(?P<ts>\S+)\s+(?P<host>\S+)\s+(?P<proc>\S+?)(?:\[(?P<pid>\d+)\])?:\s+(?P<msg>.*)'
)


def parse_syslog_line(line: str) -> dict | None:
    m = SYSLOG_RE.match(line.strip())
    if not m:
        return {"msg": line.strip(), "_format": "syslog_raw", "_parsed_at": datetime.utcnow().isoformat()}
    g = m.groupdict()
    return {
        "host": g["host"],
        "proc": g["proc"],
        "pid": g["pid"],
        "msg": g["msg"],
        "_format": "syslog",
        "_parsed_at": datetime.utcnow().isoformat(),
    }


def parse_text_line(line: str) -> dict:
    return {
        "line": line.strip(),
        "_format": "text",
        "_parsed_at": datetime.utcnow().isoformat(),
    }


def parse_args():
    import argparse
    p = argparse.ArgumentParser(description="结构化日志解析器")
    p.add_argument("--input", "-i", required=True, help="输入日志文件路径")
    p.add_argument("--output", "-o", default="parsed.jsonl", help="输出 JSONL 路径")
    p.add_argument("--format", "-f", choices=["auto", "json", "nginx", "apache", "syslog", "text"],
                   default="auto", help="日志格式，auto 自动检测")
    p.add_argument("--max-lines", "-n", type=int, default=0, help="最多处理行数（0=全部）")
    return p.parse_args()


def main():
    args = parse_args()
    fmt = args.format
    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "auto":
        # Detect from first non-empty line
        with open(input_path) as f:
            sample = ""
            for line in f:
                if line.strip():
                    sample = line.strip()
                    break
        if sample.startswith("{"):
            fmt = "json"
        elif " - " in sample and ("[" in sample):
            fmt = "nginx"
        else:
            fmt = "text"

    parser = FORMATS.get(fmt, parse_text_line)
    count = 0
    skipped = 0

    with open(input_path) as fin, open(output_path, "w") as fout:
        for line in fin:
            if not line.strip():
                continue
            result = parser(line)
            if result:
                fout.write(json.dumps(result, ensure_ascii=False) + "\n")
                count += 1
            else:
                skipped += 1
            if args.max_lines > 0 and count + skipped >= args.max_lines:
                break

    print(f"✅ Parsed {count} lines ({skipped} skipped), output → {output_path}")


if __name__ == "__main__":
    main()
