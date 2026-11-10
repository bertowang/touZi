#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""实现信号→下一根成交→计费的状态链，并与错误版、零成本版、持有基准对照。

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
N, W = 400, 10
START, DRIFT, VOL = 50.0, 0.0004, 0.014
FEE = 0.0005       # 换仓费率
SLIP = 0.0003      # 换仓滑点

# ---- 计算与作图 ----
rng = random.Random(7)
px, prices = START, []
for _ in range(N):
    px *= (1 + rng.gauss(DRIFT, VOL))
    prices.append(px)
rets = [prices[t] / prices[t - 1] - 1 for t in range(1, N)]
sig = [0] * N
for t in range(W, N):
    sig[t] = 1 if prices[t] > statistics.fmean(prices[t + 1 - W:t + 1]) else 0

def run(mode, with_cost=True):
    v, eq_curve, prev, trades, cost = 1.0, [1.0], 0, 0, 0.0
    for t in range(1, N):
        exposure = sig[t] if mode == "same_bar" else sig[t - 1]
        r = rets[t - 1]
        if exposure != prev:
            trades += 1
            if with_cost:
                slip = SLIP
                v *= (1 - FEE)
                cost += FEE + slip
            else:
                slip = 0.0
        else:
            slip = 0.0
        v *= (1 + exposure * (r - slip))
        prev = exposure
        eq_curve.append(v)
    return eq_curve, trades, cost

naive, naive_trades, _ = run("same_bar", False)
legal_nc, trades, _ = run("next_bar", False)
legal, _t2, total_cost = run("next_bar", True)
hold, v = [1.0], 1.0
for r in rets:
    v *= (1 + r)
    hold.append(v)

c = Chart(FIG / "26-backtest.svg", "四种口径的账户净值", xlabel="交易日", ylabel="净值")
c.line(range(N), naive, RED, label="同根成交（含前视偏差）")
c.line(range(N), legal_nc, AMBER, label="下一根成交 · 零成本")
c.line(range(N), legal, BLUE, label="下一根成交 · 扣费")
c.line(range(N), hold, GREEN, label="始终持有")
print("净值图:", c.save())
b = Chart(FIG / "26-cost.svg", "终值对照", xlabel="口径", ylabel="净值",
          xticks=[(i, n) for i, n in enumerate(["同根成交", "零成本", "扣费", "持有"])])
b.bars(range(4), [naive[-1], legal_nc[-1], legal[-1], hold[-1]], BLUE, label="期末净值")
b.hline(1.0, "#9aa6b2")
print("对照图:", b.save())
print("同根成交=%.3f 零成本=%.3f 扣费=%.3f 持有=%.3f | 换仓 %d 次 累计成本=%.4f | 泄漏=%.3f" %
      (naive[-1], legal_nc[-1], legal[-1], hold[-1], trades, total_cost,
       naive[-1] - legal_nc[-1]))
