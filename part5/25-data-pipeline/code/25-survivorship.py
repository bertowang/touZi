#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合成 200 只基金，差的被清盘；比较「只看存活基金」与「含清盘全样本」的指数收益。

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
N_FUNDS, N_DAYS = 200, 500
ANN = 252
SIG = 0.012        # 日波动
KILL = 0.65        # 净值跌破该比例即清盘
LIQUID = -0.05     # 清盘时的额外损失

# ---- 计算与作图 ----
rng = random.Random(7)
funds, alive_by_day = [], [0] * N_DAYS
for _ in range(N_FUNDS):
    mu = rng.gauss(0.0002, 0.0004)      # 管理人能力异质
    v, row, alive = 1.0, [], True
    for t in range(N_DAYS):
        if alive:
            r = rng.gauss(mu, SIG)
            v *= (1 + r)
            if v < KILL:
                r += LIQUID
                alive = False
            else:
                alive_by_day[t] += 1
            row.append(r)
        else:
            row.append(0.0)             # 清盘后资金回到指数（简化）
    funds.append((row, alive))

survivors = [p for p, a in funds if a]
biased = [statistics.fmean(p[t] for p in survivors) for t in range(N_DAYS)]
unbiased = [statistics.fmean(p[t] for p, _a in funds) for t in range(N_DAYS)]

def curve(rets):
    v, out = 1.0, [1.0]
    for r in rets:
        v *= (1 + r)
        out.append(v)
    return out

cb, cu = curve(biased), curve(unbiased)
cagr_b = cb[-1] ** (ANN / N_DAYS) - 1
cagr_u = cu[-1] ** (ANN / N_DAYS) - 1

c = Chart(FIG / "25-survivorship.svg", "只看存活基金 vs 含清盘全样本", xlabel="交易日", ylabel="净值")
c.line(range(N_DAYS + 1), cb, RED, label="只看存活（有偏）")
c.line(range(N_DAYS + 1), cu, BLUE, label="全样本（无偏）")
print("净值图:", c.save())
f = Chart(FIG / "25-funnel.svg", "随时间存活的基金数量", xlabel="交易日", ylabel="只数")
f.line(range(N_DAYS), alive_by_day, GREEN, label="存活基金")
print("存活图:", f.save())
print("期初=%d 期末存活=%d | 有偏年化=%.2f%% 无偏年化=%.2f%% 偏差=%+.2f 个百分点" %
      (N_FUNDS, len(survivors), 100 * cagr_b, 100 * cagr_u, 100 * (cagr_b - cagr_u)))
