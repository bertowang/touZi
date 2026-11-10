#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""模拟含厚尾的日收益，扫描杠杆，估计强平概率、终值分位数与 CVaR。

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
N_PATHS, N_DAYS = 2000, 250
LEVERAGES = (0.5, 1.0, 1.5, 2.0, 3.0)
MU, SIG = 0.0004, 0.012
P_STRESS, STRESS_MULT = 0.02, 4.0
RUIN_BARRIER = 0.25     # 净值低于初始的 25% 视为触发强平
ANN = 252

# ---- 计算与作图 ----
rng = random.Random(7)
kelly = MU / (SIG ** 2)
rows = []
for lev in LEVERAGES:
    finals, ruins = [], 0
    for _ in range(N_PATHS):
        eq = 1.0
        ruined = False
        for _d in range(N_DAYS):
            sig = SIG * STRESS_MULT if rng.random() < P_STRESS else SIG
            r = rng.gauss(MU, sig)
            eq *= (1 + lev * r)
            if eq <= RUIN_BARRIER:
                ruined = True
                break
        finals.append(eq)
        ruins += 1 if ruined else 0
    finals.sort()
    k = max(1, int(0.05 * len(finals)))
    cvar = statistics.fmean(finals[:k])
    rows.append((lev, ruins / N_PATHS, statistics.median(finals), finals[k - 1], cvar))

c = Chart(FIG / "30-ruin.svg", "杠杆与强平概率（合成厚尾收益）", xlabel="杠杆 L", ylabel="概率")
c.bars([x[0] for x in rows], [100 * x[1] for x in rows], RED, label="强平概率 %")
print("强平图:", c.save())
t = Chart(FIG / "30-terminal.svg", "终值中位数与 5% 分位数", xlabel="杠杆 L", ylabel="期末净值")
t.line([x[0] for x in rows], [x[2] for x in rows], BLUE, label="中位数")
t.line([x[0] for x in rows], [x[3] for x in rows], AMBER, label="5% 分位")
t.hline(1.0, "#9aa6b2", label="本金")
print("终值图:", t.save())
print("凯利 f*=%.2f（上界）| 强平概率 L=1: %.1f%% L=3: %.1f%%" %
      (kelly, 100 * rows[1][1], 100 * rows[-1][1]))
print("L=3 终值中位=%.3f 5%%分位=%.3f CVaR95=%.3f | 年化波动=%.1f%%" %
      (rows[-1][2], rows[-1][3], rows[-1][4], 100 * SIG * math.sqrt(ANN)))
