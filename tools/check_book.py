#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全书静态自检：目录、内链、HTML 标签、代码块/插图同步、脚本契约与实跑。

用法: python3 tools/check_book.py [--run] [--urls]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from book_schema import PARTS, PART_BY_ID, STAGE_CLASS  # noqa: E402
from book_data import CHAPTERS, BY_ID, problems, fig_count  # noqa: E402
from book_resources import R  # noqa: E402
from extract_code import collect  # noqa: E402

VOID_TAGS = {"meta", "link", "br", "hr", "img", "input", "source", "area",
             "base", "col", "embed", "param", "track", "wbr"}
SKIP = ("http://", "https://", "mailto:", "data:", "#")
STATUS_LABEL = {"done": "已完稿", "skeleton": "框架待补", "todo": "待建"}
BANNED = re.compile(r"^\s*(import|from)\s+(numpy|pandas|scipy|statsmodels|matplotlib)\b", re.M)
REQUIRED = ("#!/usr/bin/env python3", "random.seed(7)", "参数区", "print(")
errors, warnings = [], []


def err(m):
    errors.append(m)


def warn(m):
    warnings.append(m)


def all_pages():
    return sorted(ROOT.rglob("*.html"))


class TagBalance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.problems = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID_TAGS:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            self.problems.append("标签交叉：期望 </%s>，实际 </%s>" % (self.stack[-1], tag))
            while self.stack and self.stack[-1] != tag:
                self.stack.pop()
            if self.stack:
                self.stack.pop()
        else:
            self.problems.append("多余的 </%s>" % tag)


for p in problems():
    err("章节数据: " + p)

toc_text = (ROOT / "assets/toc.js").read_text(encoding="utf-8")
try:
    a = toc_text.index("window.BOOK_TOC = ") + len("window.BOOK_TOC = ")
    toc = json.loads(toc_text[a:toc_text.index(";\n\nwindow.BOOK_FLAT")])
except (ValueError, json.JSONDecodeError) as e:
    err("无法解析 assets/toc.js: " + str(e))
    toc = {"parts": []}
part_key = {p["id"]: p["key"] for p in PARTS}
toc_items = [(c["path"], c["status"], c["id"], part.get("stage", ""),
              part_key.get(part["id"], ""))
             for part in toc.get("parts", []) for c in part["chapters"]]
toc_paths = [x[0] for x in toc_items]
if len(toc_paths) != len(CHAPTERS) or len(set(toc_paths)) != len(toc_paths):
    err("toc.js 章节数或 path 唯一性与 book_data 不一致")
for path in toc_paths:
    if not (ROOT / path).is_file():
        err("toc.js 指向的页面不存在: " + path)
for part in toc.get("parts", []):
    if not part.get("stage"):
        err("toc.js 分部缺少 stage: " + part.get("id", "?"))

index_text = (ROOT / "index.html").read_text(encoding="utf-8")
index_links = re.findall(r'class="toc-title"\s+href="([^"]+)"', index_text)
for p in toc_paths:
    if p not in index_links:
        err("总目录缺少章节链接: " + p)
if index_text.count('class="toc-extra"') < len(toc_paths):
    err("总目录中有章节缺少「扩展阅读」入口")
if index_text.count('<span class="badge done">已完稿</span>') < len(toc_paths):
    err("总目录中有章节状态徽章未更新为已完稿")
if index_text.count('class="stage-banner') < 5:
    err("总目录缺少五个学习阶段的分区标识")
for path, status, cid, stage, key in toc_items:
    page = ROOT / path
    if not page.is_file():
        continue
    text = page.read_text(encoding="utf-8")
    if '<span class="badge ' + status + '">' + STATUS_LABEL.get(status, "") + "</span>" not in text:
        err("章节页状态徽章与 toc.js 不一致: " + path)
    ch = BY_ID.get(cid)
    if ch and 'class="badge ' + STAGE_CLASS[ch["part"]] + '"' not in text:
        err("章节页阶段徽章不一致: " + path)

# ---------- 2. 逐页检查 ----------
declared_figs = set()
for ch in CHAPTERS:
    for d in ch["demos"]:
        for fname, _cap in d["figs"]:
            declared_figs.add(ch["folder"] + "/" + fname)

for page in all_pages():
    text = page.read_text(encoding="utf-8")
    rel = str(page.relative_to(ROOT))
    if 'class="site-foot"' not in text:
        err("缺少页脚: " + rel)
    for token in ("汪亮", "bertonwang", "47608843@qq.com", "AI 使用说明"):
        if token not in text:
            err("页脚缺少署名信息 [%s]: %s" % (token, rel))
    if "{{" in text or "}}" in text:
        err("存在未解析的占位符: " + rel)
    if page.parent != ROOT:
        for need in ('id="extra-links"', "扩展学习</th>", "data-chapter=",
                     'class="bridge"', 'class="analogy"', 'id="highlights"'):
            if need not in text:
                err("章节页缺少 %s: %s" % (need, rel))
        if text.count('class="repo-card"') < 2:
            err("章节页参考资料卡片不足: " + rel)
        cid = re.search(r'data-chapter="([^"]+)"', text)
        ch = BY_ID.get(cid.group(1) if cid else "")
        if ch and ch["id"] != "A" and ('id="lab"' not in text or 'data-file="code/' not in text):
            err("章节缺少 Python 实例栏目: " + rel)
    if "</html>" not in text:
        err("HTML 未闭合: " + rel)
    for attr in re.findall(r'(?:href|src)\s*=\s*(["\'])([^"\']+)\1', text):
        target = attr[1]
        if target.startswith(SKIP):
            continue
        part = target.split("#", 1)[0]
        if part and not (page.parent / part).resolve().exists():
            err("失效链接 %s -> %s" % (rel, target))
    parser = TagBalance()
    parser.feed(text)
    parser.close()
    for problem in parser.problems[:5]:
        err("HTML 标签 %s: %s" % (rel, problem))
    if parser.stack:
        err("HTML 标签未闭合 %s: %s" % (rel, ", ".join(parser.stack[:5])))

for rel_fig in sorted(declared_figs):
    f = ROOT / rel_fig
    if not f.is_file():
        err("插图未生成（请运行 ./tools/run_python.sh）: " + rel_fig)
        continue
    try:
        ET.parse(f)
    except ET.ParseError as e:
        err("SVG 不是合法 XML %s: %s" % (rel_fig, e))
    if not f.read_text(encoding="utf-8").lstrip().startswith("<svg"):
        err("SVG 缺少根元素: " + rel_fig)
if len(declared_figs) != fig_count():
    err("插图声明数不一致")
for page in all_pages():
    if page.parent == ROOT:
        continue
    for src in re.findall(r'<img\s+src="(fig/[^"]+)"', page.read_text(encoding="utf-8")):
        if str(page.parent.relative_to(ROOT)) + "/" + src not in declared_figs:
            err("页面引用了未声明的插图: %s -> %s" % (page.name, src))

# ---------- 3. 代码块与 .py 同步 ----------
found = collect()
if not found:
    err("没有抽取到任何 Python 代码块")
for target, code in sorted(found.items()):
    rel = str(target.relative_to(ROOT))
    if not target.exists():
        err("缺少脚本文件（请运行 extract_code.py）: " + rel)
        continue
    if target.read_text(encoding="utf-8") != code:
        err("脚本与 HTML 代码块不一致: " + rel)

# ---------- 4. Python 脚本契约与实跑 ----------
ap = argparse.ArgumentParser(description="投资理财教材静态自检")
ap.add_argument("--run", action="store_true", help="实跑全部 Python 分析脚本")
ap.add_argument("--urls", action="store_true", help="联网探测全部外部链接")
args = ap.parse_args()

for target in sorted(found):
    if not target.exists():
        continue
    rel = str(target.relative_to(ROOT))
    code = target.read_text(encoding="utf-8")
    if not code.splitlines() or not code.splitlines()[0].startswith("#!"):
        err("脚本首行应为 shebang: " + rel)
    for needed in REQUIRED:
        if needed not in code:
            err("Python 脚本缺少 %s: %s" % (needed, rel))
    if BANNED.search(code):
        err("Python 脚本使用了第三方依赖（破坏零依赖）: " + rel)
    try:
        compile(code, rel, "exec")
    except SyntaxError as e:
        err("Python 脚本语法错误 %s: %s" % (rel, e))

if args.run:
    ok = 0
    for target in sorted(found):
        if not target.exists():
            continue
        rel = str(target.relative_to(ROOT))
        try:
            proc = subprocess.run([sys.executable, rel], cwd=ROOT,
                                  capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            err("脚本运行超时: " + rel)
            continue
        if proc.returncode != 0:
            err("脚本运行失败 %s: %s" % (rel, proc.stderr.strip()[:200]))
        elif not proc.stdout.strip():
            err("脚本没有打印任何数值: " + rel)
        else:
            ok += 1
    print("实跑：%d / %d 个脚本通过" % (ok, len(found)))


# ---------- 5. 资源链接（可选联网探测） ----------
def probe(item):
    key, (name, url, _desc, _cat) = item
    last = "unknown"
    for _attempt in range(2):
        for method in ("HEAD", "GET"):
            try:
                req = urllib.request.Request(url, method=method,
                                             headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=6) as r:
                    return key, r.status, "", "ok"
            except urllib.error.HTTPError as e:
                if e.code in (404, 410):
                    return key, e.code, str(e)[:60], "bad"
                return key, e.code, "HTTP %d" % e.code, "blocked"
            except Exception as e:  # noqa: BLE001
                last = str(e)[:70]
    return key, 0, last, "unreachable"


if args.urls:
    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(probe, R.items()))
    bad = [r for r in results if r[3] == "bad"]
    blocked = [r for r in results if r[3] == "blocked"]
    unreachable = [r for r in results if r[3] == "unreachable"]
    wiki = [r for r in unreachable if "wikipedia.org" in R[r[0]][1]]
    for k, _s, e, _ in bad:
        warn("疑似失效链接 [%s] %s (%s)" % (k, R[k][1], e))
    for k, _s, e, _ in unreachable:
        if "wikipedia.org" not in R[k][1]:
            warn("本环境不可达，需人工确认 [%s] %s (%s)" % (k, R[k][1], e))
    print("链接探测：%d 条，可达 %d，反爬拦截 %d，本环境不可达 %d（wikipedia.org %d），疑似失效 %d" %
          (len(results), len(results) - len(bad) - len(blocked) - len(unreachable),
           len(blocked), len(unreachable), len(wiki), len(bad)))


# ---------- 6. 报告 ----------
for w in warnings:
    print("提示:", w)
for e in errors:
    print("错误:", e)
print("自检：%d 个 HTML 页面，%d 个章节，%d 个 Python 脚本，%d 张 SVG 图，%d 条错误，%d 条提示" %
      (len(all_pages()), len(CHAPTERS), len(found), len(declared_figs), len(errors), len(warnings)))
sys.exit(1 if errors else 0)
