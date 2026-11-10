#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合成五只成分股，计算三种加权指数，估计等权再平衡换手，并计算折溢价套利空间。

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
N = 120             # 交易日
N_ASSETS = 5
START_PRICES = [12.0, 28.0, 45.0, 8.0, 60.0]
SHARES = [9.0e8, 4.0e8, 2.5e8, 1.2e9, 1.5e8]
REBAL_EVERY = 20     # 等权指数再平衡周期
PREMIUM = 0.012      # 观察到的溢价
ARB_COST = 0.003     # 申赎 + 交易 + 冲击成本
CAP = 1000000.0      # 套利资金

# ---- 计算与作图 ----
rng = random.Random(7)
mu = [0.0006, 0.0004, 0.0003, 0.0008, 0.0002]
paths = []
for j in range(N_ASSETS):
    px, row = START_PRICES[j], []
    for _ in range(N):
        px *= (1 + rng.gauss(mu[j], 0.012))
        row.append(px)
    paths.append(row)

price_idx = [sum(paths[j][i] for j in range(N_ASSETS)) /
             sum(START_PRICES) for i in range(N)]
cap0 = sum(START_PRICES[j] * SHARES[j] for j in range(N_ASSETS))
cap_idx = [sum(paths[j][i] * SHARES[j] for j in range(N_ASSETS)) / cap0
           for i in range(N)]
eq_idx = [statistics.fmean(paths[j][i] / START_PRICES[j]
                           for j in range(N_ASSETS)) for i in range(N)]

turnover, w = 0.0, [1.0 / N_ASSETS] * N_ASSETS
for i in range(1, N):
    vals = [w[j] * paths[j][i] / paths[j][i - 1] for j in range(N_ASSETS)]
    tot = sum(vals)
    w = [v / tot for v in vals]
    if i % REBAL_EVERY == 0:
        turnover += sum(abs(x - 1.0 / N_ASSETS) for x in w) / 2
        w = [1.0 / N_ASSETS] * N_ASSETS

arb = CAP * (abs(PREMIUM) - ARB_COST)
c = Chart(FIG / "11-index.svg", "三种加权规则的归一化指数", xlabel="交易日", ylabel="点位")
c.line(range(N), price_idx, BLUE, label="价格加权")
c.line(range(N), cap_idx, RED, label="市值加权")
c.line(range(N), eq_idx, GREEN, label="等权")
c.hline(1.0, "#9aa6b2")
print("指数图:", c.save())

labels = ["价格加权", "市值加权", "等权"]
rets = [100 * (x[-1] - 1) for x in (price_idx, cap_idx, eq_idx)]
b = Chart(FIG / "11-weights.svg", "期末累计收益与等权再平衡换手", xlabel="规则", ylabel="%",
          xticks=[(i, n) for i, n in enumerate(labels)])
b.bars(range(3), rets, AMBER, label="累计收益 %")
print("对照图:", b.save())
print("期末收益 价格加权=%.2f%% 市值加权=%.2f%% 等权=%.2f%% | 等权累计单边换手=%.2f%%" %
      (rets[0], rets[1], rets[2], 100 * turnover))
print("溢价=%.2f%% 成本=%.2f%% → 单位资金套利空间=%.2f%%（%.0f 元）" %
      (100 * PREMIUM, 100 * ARB_COST, 100 * (abs(PREMIUM) - ARB_COST), arb))
