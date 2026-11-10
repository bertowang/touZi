#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用标准库实现 DCF，扫描折现率与增长率，并用二分法反推市价隐含的增长。

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
FCF0 = 10.0        # 起始自由现金流
STAGE1 = 5         # 高增长阶段年数
G_TERM = 0.025     # 永续增长率
R0 = 0.10          # 基准折现率
G0 = 0.10          # 基准高增长阶段增长率
MARKET = 180.0     # 观察到的市值（合成示意）
R_LIST = [0.08, 0.09, 0.10, 0.11, 0.12]
G_LIST = [0.02, 0.06, 0.10, 0.14, 0.18]

# ---- 计算与作图 ----
def dcf(r, g1):
    fcf, pv = FCF0, 0.0
    for t in range(1, STAGE1 + 1):
        fcf *= (1 + g1)
        pv += fcf / (1 + r) ** t
    tv = fcf * (1 + G_TERM) / (r - G_TERM)
    return pv + tv / (1 + r) ** STAGE1

base = dcf(R0, G0)
matrix = [[dcf(r, g) for g in G_LIST] for r in R_LIST]
heatmap(FIG / "10-sensitivity.svg", matrix,
        ["r=%.0f%%" % (100 * r) for r in R_LIST],
        ["g=%.0f%%" % (100 * g) for g in G_LIST],
        title="两阶段 DCF 敏感性：折现率 × 高增长率",
        vmin=min(min(row) for row in matrix), vmax=max(max(row) for row in matrix))
print("敏感性图:", str(FIG / "10-sensitivity.svg"))

fcf_path, pv_path, fcf = [], [], FCF0
for t in range(1, STAGE1 + 1):
    fcf *= (1 + G0)
    fcf_path.append(fcf)
    pv_path.append(fcf / (1 + R0) ** t)
c = Chart(FIG / "10-dcf.svg", "高增长期现金流与其现值", xlabel="年", ylabel="金额")
c.bars(range(1, STAGE1 + 1), fcf_path, BLUE, label="FCF")
c.bars(range(1, STAGE1 + 1), pv_path, GREEN, label="折现后现值")
print("现金流图:", c.save())

lo, hi = -0.10, 0.60
for _ in range(80):
    mid = (lo + hi) / 2
    if dcf(R0, mid) < MARKET:
        lo = mid
    else:
        hi = mid
implied = (lo + hi) / 2
print("基准DCF=%.2f 终值占比=%.1f%% | 敏感性区间 %.1f ~ %.1f | 市价隐含 g=%.2f%%" %
      (base, 100 * (1 - sum(pv_path) / base),
       min(min(row) for row in matrix), max(max(row) for row in matrix), 100 * implied))
