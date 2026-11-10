#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""三资产、给定 μ/Σ，穷举权重网格，画风险—收益散点与有效前沿。

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
MU = (0.08, 0.05, 0.12)      # 年化期望收益
SIG = (0.18, 0.08, 0.25)     # 年化波动
CORR = ((1.0, 0.20, 0.60),
        (0.20, 1.0, 0.10),
        (0.60, 0.10, 1.0))
RF = 0.02                    # 无风险利率
STEP = 0.02                  # 权重网格步长

# ---- 计算与作图 ----
COV = [[SIG[i] * SIG[j] * CORR[i][j] for j in range(3)] for i in range(3)]

def stats(w):
    er = sum(w[i] * MU[i] for i in range(3))
    var = sum(w[i] * w[j] * COV[i][j] for i in range(3) for j in range(3))
    return er, math.sqrt(max(var, 0.0))

points, grid = [], int(round(1.0 / STEP))
for a in range(grid + 1):
    for b in range(grid + 1 - a):
        w = (a * STEP, b * STEP, 1.0 - (a + b) * STEP)
        er, vol = stats(w)
        points.append((vol, er, w, (er - RF) / vol if vol > 0 else 0.0))

best = max(points, key=lambda x: x[3])
gmv = min(points, key=lambda x: x[0])
lo = min(er for _v, er, _w, _s in points)
hi = max(er for _v, er, _w, _s in points)
frontier = []
for k in range(41):
    target = lo + (hi - lo) * k / 40
    near = [x for x in points if target - 0.002 <= x[1] <= target + 0.002]
    if near:
        frontier.append(min(near, key=lambda x: x[0]))

c = Chart(FIG / "13-frontier.svg", "三资产组合的风险—收益可行集", xlabel="年化波动", ylabel="年化期望收益")
c.scatter([x[0] for x in points], [x[1] for x in points], "#9aa6b2", label="可行组合", radius=1.8)
c.line([x[0] for x in frontier], [x[1] for x in frontier], BLUE, label="有效前沿", width=2.6)
c.scatter([best[0]], [best[1]], RED, label="切点组合", radius=6)
c.scatter([gmv[0]], [gmv[1]], GREEN, label="最小方差", radius=6)
c.line([0.0, best[0] * 1.6], [RF, RF + (best[1] - RF) * 1.6], AMBER,
       label="资本市场线", dash="5 4")
print("前沿图:", c.save())

heatmap(FIG / "13-corr.svg", CORR, ["股票A", "债券B", "成长C"], ["A", "B", "C"],
        title="三资产相关系数矩阵")
print("相关图:", str(FIG / "13-corr.svg"))
print("最小方差 w=(%.2f,%.2f,%.2f) σ=%.2f%% | 切点 w=(%.2f,%.2f,%.2f) E=%.2f%% σ=%.2f%% Sharpe=%.3f" %
      (*gmv[2], 100 * gmv[0], *best[2], 100 * best[1], 100 * best[0], best[3]))
