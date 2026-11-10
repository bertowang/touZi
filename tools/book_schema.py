#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全书分部、学习阶段与章节数据接口。

五个学习阶段把「产品 → 定价 → 盘面 → 证据 → 决策」串成一条主线：
    现金 → 产品 → 定价 → 组合 → 盘面 → 证据 → 执行 → 风险 → 复盘
"""
from __future__ import annotations

BOOK_TITLE = "投资理财：从产品到证据"
SUBTITLE = "本科到研究生 · 产品、定价、盘面、策略与风险的一条主线"
VERSION = "v0.1 · 2026-11"

S1 = "第一阶段 · 共同语言与产品地图"
S2 = "第二阶段 · 定价、组合与资产配置"
S3 = "第三阶段 · 盘面语言与看图识图"
S4 = "第四阶段 · 从直觉到可验证的证据"
S5 = "第五阶段 · 实盘、风险与长期主义"

PARTS = [
    dict(id="p0", title="卷首 · 共同语言", stage=S1, key="pre", folder="part0"),
    dict(id="p1", title="第一篇 · 产品地图与市场基础设施", stage=S1, key="products", folder="part1"),
    dict(id="p2", title="第二篇 · 估值定价与组合理论", stage=S2, key="pricing", folder="part2"),
    dict(id="p3", title="第三篇 · 盘面语言与看图识图", stage=S3, key="charts", folder="part3"),
    dict(id="p4", title="第四篇 · 因子、行为与市场证据", stage=S4, key="evidence", folder="part4"),
    dict(id="p5", title="第五篇 · 策略工程：从想法到证据", stage=S4, key="strategy", folder="part5"),
    dict(id="p6", title="第六篇 · 实盘、风险与长期主义", stage=S5, key="practice", folder="part6"),
    dict(id="pa", title="附录 · 速查与资源总表", stage=S5, key="appendix", folder="appendix"),
]
PART_BY_ID = {p["id"]: p for p in PARTS}


def C(cid, part, folder, title, lede, *, hours="2 学时", goals=(), points=(),
      sections=(), demos=(), highlights=(), analogy="", bridge="",
      pitfalls=(), exercises=(), further=(), status="done"):
    """一章的全部数据。

    bridge     : 本章在全书主线中的位置（承接什么、引出什么）
    analogy    : 把本章核心概念映射到程序员熟悉的计算概念
    sections   : [(编号, 标题, HTML 正文), ...]
    demos      : [demo(...), ...] 零依赖、自包含的 Python 分析脚本（含 SVG 图）
    highlights : [(资源 key, 推荐理由), ...] 本章必读参考资料卡片
    """
    return dict(id=cid, part=part, folder=folder, title=title, lede=lede,
                status=status, hours=hours, goals=list(goals), points=list(points),
                sections=list(sections), demos=list(demos), highlights=list(highlights),
                analogy=analogy, bridge=bridge, pitfalls=list(pitfalls),
                exercises=list(exercises), further=list(further))


def demo(file, title, code, steps, expect, params="", figs=()):
    """一段可独立运行的 Python 分析脚本。

    file 形如 code/04-products-map.py；figs 为 [(fig/xx.svg, 图注), ...]，
    由脚本运行时生成，生成器会把它们渲染成页面里的 <figure>。
    """
    return dict(file=file, title=title, code=code.strip("\n"), steps=steps,
                expect=expect, params=params, figs=list(figs))


def eq(text):
    """把一行公式排版成等宽公式块；text 里可以写 Unicode 数学符号。"""
    import html as html_mod
    return '<p class="eq">' + html_mod.escape(text, quote=False) + "</p>"


def table(headers, rows, widths=()):
    """生成一张对照表，headers 为字符串列表，rows 为二维字符串列表（已是 HTML）。"""
    w = [' style="width:%s"' % widths[i] if i < len(widths) else ""
         for i in range(len(headers))]
    out = ["<table><thead><tr>" + "".join("<th" + w[i] + ">" + h + "</th>"
                                        for i, h in enumerate(headers)) + "</tr></thead><tbody>"]
    for row in rows:
        out.append("<tr>" + "".join("<td>" + cell + "</td>" for cell in row) + "</tr>")
    out.append("</tbody></table>")
    return "\n".join(out)


DEMO_CONTRACT = """所有 Python 示例遵守同一契约：
  1. 只用 Python 3 标准库 + 仓库内 tools/chart.py（纯标准库 SVG 绘图），无第三方包；
  2. 自包含：行情/组合数据由代码里的模型合成，不联网、不读外部数据文件；
  3. random.seed(7) 固定随机数，所有可调量集中在「参数区」；
  4. 打印可手算核对的数值，并生成 fig/*.svg 矢量图（写入章节目录，可提交、可离线查看）；
  5. 页面代码块与 code/*.py 由 tools/extract_code.py 自动同步。"""

DISCLAIMER_HTML = (
    '<div class="disclaimer"><p><strong>风险提示与免责声明</strong>：本书为教学材料，'
    '所有行情、净值、回测与图表均为合成数据或模型示意，<strong>不构成任何投资建议、'
    '产品推荐或收益承诺</strong>。历史表现与回测结果不代表未来收益；杠杆、衍生品、'
    '跨境与场外产品可能导致本金全部损失。真实投资须遵守所在市场的法律法规、'
    '投资者适当性管理、券商与基金销售机构的风险揭示，并自行承担决策后果。</p></div>'
)

STAGE_CLASS = {"p0": "s1", "p1": "s1", "p2": "s2", "p3": "s3",
               "p4": "s4", "p5": "s4", "p6": "s5", "pa": "s5"}
STAGE_SHORT = {"p0": "共同语言", "p1": "产品 · 制度", "p2": "定价 · 组合",
               "p3": "盘面 · 识图", "p4": "因子 · 证据", "p5": "策略 · 工程",
               "p6": "实盘 · 风险", "pa": "速查 · 附录"}
