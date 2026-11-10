#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从章节 HTML 的 <pre class="code" data-file="code/xx.py"> 同步生成 .py 文件。

用法:
  python3 tools/extract_code.py            # 同步（新建/更新）
  python3 tools/extract_code.py --check   # 只检查是否一致
  python3 tools/extract_code.py --clean   # 同步并删除无对应代码块的旧脚本
"""
from __future__ import annotations

import argparse
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
BLOCK = re.compile(
    r'<pre\s+class="code"\s+data-file="([^"]+)"[^>]*><code>(.*?)</code></pre>',
    re.DOTALL,
)


def collect():
    """返回 {目标文件路径: 代码文本}，跳过 data-file="inline" 的命令片段。"""
    found = {}
    for page in sorted(ROOT.rglob("index.html")):
        if page.parent == ROOT:
            continue
        text = page.read_text(encoding="utf-8")
        for m in BLOCK.finditer(text):
            name, code = m.group(1), html.unescape(m.group(2))
            if name == "inline" or not name.endswith(".py"):
                continue
            target = (page.parent / name).resolve()
            if target in found:
                raise SystemExit("代码块 data-file 重复: " + str(target))
            found[target] = code.strip("\n") + "\n"
    return found


def main():
    ap = argparse.ArgumentParser(description="从 HTML 代码块同步 Python 分析脚本")
    ap.add_argument("--check", action="store_true", help="只检查，不写入")
    ap.add_argument("--clean", action="store_true", help="删除无对应代码块的旧 .py 文件")
    args = ap.parse_args()

    found = collect()
    new = updated = same = 0
    for target, code in sorted(found.items()):
        if not target.exists():
            if not args.check:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(code, encoding="utf-8")
            new += 1
        elif target.read_text(encoding="utf-8") != code:
            if not args.check:
                target.write_text(code, encoding="utf-8")
            updated += 1
        else:
            same += 1

    removed = []
    if args.clean:
        for old in sorted(ROOT.rglob("code/*.py")):
            if old.resolve() not in found:
                if not args.check:
                    old.unlink()
                removed.append(str(old.relative_to(ROOT)))

    print("同步完成：共 %d 个脚本，新建 %d，更新 %d，未变 %d，清理 %d" %
          (len(found), new, updated, same, len(removed)))
    if args.check and (new or updated or removed):
        print("检查未通过：HTML 代码块与 code/*.py 不一致，请运行 python3 tools/extract_code.py")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
