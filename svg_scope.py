#!/usr/bin/env python3
"""Find common active-content and resource-reference patterns in an SVG."""

import argparse
import re
import sys
from pathlib import Path


MAX_BYTES = 32 * 1024 * 1024
SVG_TAG = re.compile(r"<\s*(?:[A-Za-z_][\w.-]*:)?svg\b", re.IGNORECASE)
SCRIPT_TAG = re.compile(r"<\s*(?:[A-Za-z_][\w.-]*:)?script\b", re.IGNORECASE)
FOREIGN_OBJECT = re.compile(
    r"<\s*(?:[A-Za-z_][\w.-]*:)?foreignObject\b", re.IGNORECASE
)
EVENT_ATTRIBUTE = re.compile(r"\son[a-z][a-z0-9:_-]*\s*=", re.IGNORECASE)
JAVASCRIPT_URI = re.compile(r"javascript\s*:", re.IGNORECASE)
HREF = re.compile(
    r'''\bhref\s*=\s*(?:"([^"]*)"|'([^']*)')''', re.IGNORECASE
)
CSS_URL = re.compile(r"\burl\(\s*([^)]*)\)", re.IGNORECASE)
CSS_IMPORT = re.compile(r"@import\b", re.IGNORECASE)


def inspect(path):
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("SVG 文件超过 32 MiB 扫描上限")
    content = data.decode("utf-8-sig")
    if not SVG_TAG.search(content):
        raise ValueError("未找到 SVG 根元素标记")

    counts = {
        "script 元素标记": len(SCRIPT_TAG.findall(content)),
        "foreignObject 标记": len(FOREIGN_OBJECT.findall(content)),
        "事件处理器属性": len(EVENT_ATTRIBUTE.findall(content)),
        "javascript: URI": len(JAVASCRIPT_URI.findall(content)),
        "非片段 href 引用": sum(
            not value.strip().startswith("#")
            for values in HREF.findall(content)
            for value in values
            if value
        ),
        "CSS 外部 url() 引用": sum(
            bool(value.strip().strip("\"'").strip())
            and not value.strip().strip("\"'").strip().startswith("#")
            for value in CSS_URL.findall(content)
        ),
        "CSS @import": len(CSS_IMPORT.findall(content)),
    }
    print("扫描 SVG 文本中的常见风险标记；没有解析 XML 或访问外部资源。")
    findings = sum(counts.values())
    for label, count in counts.items():
        if count:
            print(f"需留意：{label} {count} 处")
    if not findings:
        print("未发现已识别标记；文本扫描不能证明文件安全。")
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="扫描 SVG 文本中的常见活动内容与资源引用，不解析、不执行、不改写文件。"
    )
    parser.add_argument("svg", help="UTF-8 编码且不超过 32 MiB 的 SVG 文件")
    args = parser.parse_args(argv)
    path = Path(args.svg).expanduser()
    try:
        return 1 if inspect(path) else 0
    except (OSError, UnicodeError, ValueError) as error:
        message = "".join(
            char if char.isprintable() else char.encode("unicode_escape").decode("ascii")
            for char in str(error)
        )
        print(f"svg-scope: 无法扫描 SVG：{message}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
