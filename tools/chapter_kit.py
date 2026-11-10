#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""章节撰写套件：把常见 HTML 片段与 Python 示例样板收敛成小函数。

所有 Python 示例都由 mk_demo() 拼装同一份「零依赖样板」：
    shebang → 标准库导入 → 引入 tools/chart.py → 固定 seed(7)
    → 参数区 → 计算与作图 → print 可核对数值 + 写出 fig/*.svg
因此 33 个脚本的契约完全一致，读者只需关注「参数区」和「计算与作图」两段。
"""
from __future__ import annotations

from book_schema import demo

PREAMBLE = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""@DOC@

数据为合成数据或模型示意，仅用于教学，不构成投资建议。
"""
from __future__ import annotations

import math
import pathlib
import random
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "tools"))
from chart import Chart, candlestick, heatmap, BLUE, RED, GREEN, AMBER

FIG = pathlib.Path(__file__).resolve().parents[1] / "fig"
FIG.mkdir(exist_ok=True)

random.seed(7)

# ---- 参数区 ----
'''


def mk_demo(file, title, doc, params, body, figs, steps, expect, tweak):
    """组装一个示例。

    params : 参数区源码（纯文本，可含中文注释）
    body   : 计算与作图源码（须含 print 与 .save()/candlestick()/heatmap()）
    figs   : [(fig/xx.svg, 图注), ...]，与 body 写出的文件一一对应
    """
    code = (PREAMBLE.replace("@DOC@", doc.strip())
            + params.strip("\n") + "\n\n"
            + "# ---- 计算与作图 ----\n" + body.strip("\n") + "\n")
    return demo(file, title, code, steps, expect, tweak, figs)


# ---------------------------------------------------------------- HTML 片段
def p(s):
    return "<p>" + s + "</p>"


def ul(items):
    return "<ul>\n" + "\n".join("<li>" + x + "</li>" for x in items) + "\n</ul>"


def ol(items):
    return "<ol>\n" + "\n".join("<li>" + x + "</li>" for x in items) + "\n</ol>"


def note(label, body):
    return ('<div class="card note"><span class="card-label">' + label + "</span>"
            '<p style="margin-bottom:0">' + body + "</p></div>")


def warn(label, body):
    return ('<div class="card warn"><span class="card-label">' + label + "</span>"
            '<p style="margin-bottom:0">' + body + "</p></div>")


def sec(*parts):
    return "\n".join(parts)
