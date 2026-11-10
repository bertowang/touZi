#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""固定一条合成月度收益路径，比较一次性持有、定额投入与滞后追涨三种流程。

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
N = 120                 # 月数
MU, SIGMA = 0.006, 0.045 # 合成月度收益的均值与波动
INVEST = 1000.0           # 每月可投入现金
CAPITAL = INVEST * N      # 三种流程的总投入相同

# ---- 计算与作图 ----
rng = random.Random(7)
rets = [rng.gauss(MU, SIGMA) for _ in range(N)]

def path(returns, exposure):
    v, out = 1.0, []
    for r, e in zip(returns, exposure):
        v *= (1 + e * r)
        out.append(v)
    return out

def mdd(xs):
    peak, worst = xs[0], 0.0
    for x in xs:
        peak = max(peak, x)
        worst = min(worst, x / peak - 1.0)
    return worst

hold_f = path(rets, [1.0] * N)
chase_f = path(rets, [0.0] + [1.0 if rets[i - 1] > 0 else 0.0 for i in range(1, N)])
hold = [CAPITAL * v for v in hold_f]
chase = [CAPITAL * v for v in chase_f]

cash, shares, dca = CAPITAL, 0.0, []
for i in range(N):
    buy = min(INVEST, cash)
    cash -= buy
    shares += buy / hold_f[i]
    dca.append(shares * hold_f[i] + cash)

c = Chart(FIG / "00-decision.svg", "同一收益路径下的账户价值（总投入相同）",
          xlabel="月", ylabel="账户价值")
c.line(range(N), hold, BLUE, label="一次性买入并持有")
c.line(range(N), dca, GREEN, label="每月定额投入")
c.line(range(N), chase, RED, label="追涨杀跌（滞后信号）")
print("图:", c.save())
print("终值 持有=%.0f 定投=%.0f 追涨=%.0f | 最大回撤 持有=%.1f%% 定投=%.1f%% 追涨=%.1f%%" %
      (hold[-1], dca[-1], chase[-1], 100 * mdd(hold), 100 * mdd(dca), 100 * mdd(chase)))
