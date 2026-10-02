#!/usr/bin/env python3
"""Report potentially active or external content in an SVG without changing it."""

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


CSS_URL = re.compile(r"url\(\s*([^)]*)\)", re.IGNORECASE)
CSS_IMPORT = re.compile(r"@import\b", re.IGNORECASE)


def local_name(value):
    return value.rsplit("}", 1)[-1].lower()


def inspect(path):
    counts = {
        "script 元素": 0,
        "foreignObject 元素": 0,
        "事件处理器属性": 0,
        "javascript: 属性值": 0,
        "非片段 href 引用": 0,
        "CSS 外部 url() 引用": 0,
        "CSS @import": 0,
    }
    elements = 0
    root_seen = False

    for event, element in ET.iterparse(path, events=("start", "end")):
        tag = local_name(element.tag)
        if event == "start":
            elements += 1
            if not root_seen:
                root_seen = True
                if tag != "svg":
                    raise ValueError("根 XML 元素不是 SVG")
            if tag == "script":
                counts["script 元素"] += 1
            elif tag == "foreignobject":
                counts["foreignObject 元素"] += 1

            for name, value in element.attrib.items():
                attribute = local_name(name)
                lowered = value.strip().lower()
                if attribute.startswith("on") and len(attribute) > 2:
                    counts["事件处理器属性"] += 1
                if "javascript:" in lowered:
                    counts["javascript: 属性值"] += 1
                if attribute == "href" and lowered and not lowered.startswith("#"):
                    counts["非片段 href 引用"] += 1
                if attribute == "style":
                    count_css_references(value, counts)
        elif tag == "style" and element.text:
            count_css_references(element.text, counts)
        if event == "end":
            element.clear()

    if not root_seen:
        raise ValueError("SVG 文件为空")
    print(f"已扫描 {elements} 个 XML 元素。")
    findings = sum(counts.values())
    for label, count in counts.items():
        if count:
            print(f"需留意：{label} {count} 处")
    if not findings:
        print("未发现已识别的活动内容或外部引用；静态扫描不能证明文件安全。")
    return findings


def count_css_references(value, counts):
    for match in CSS_URL.finditer(value):
        reference = match.group(1).strip().strip("\"'").lower()
        if reference and not reference.startswith("#"):
            counts["CSS 外部 url() 引用"] += 1
    counts["CSS @import"] += len(CSS_IMPORT.findall(value))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="扫描 SVG 中可能执行脚本或加载外部资源的标记，不执行、不改写文件。"
    )
    parser.add_argument("svg", help="SVG 文件路径")
    args = parser.parse_args(argv)
    path = Path(args.svg).expanduser()
    try:
        return 1 if inspect(path) else 0
    except (OSError, UnicodeError, ET.ParseError, ValueError) as error:
        message = "".join(
            char if char.isprintable() else char.encode("unicode_escape").decode("ascii")
            for char in str(error)
        )
        print(f"svg-scope: 无法读取 SVG：{message}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
