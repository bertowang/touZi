#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合成指数与 ETF 净值，加入均值回复的折溢价与套利阻尼，计算跟踪误差与套利触发次数。

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
FEE_DAILY = 0.00002  # 管理费与现金拖累（按日）
TRACK_NOISE = 0.0004 # 抽样复制噪声
ARB_COST = 0.003     # 申赎 + 冲击成本边界
PREM_VOL = 0.002     # 折溢价冲击
PREM_AR = 0.85       # 折溢价自相关
ARB_DAMP = 0.55      # 套利发生后的收敛系数

# ---- 计算与作图 ----
rng = random.Random(7)
idx_ret = [rng.gauss(0.0004, 0.009) for _ in range(N)]
noise = [rng.gauss(0, TRACK_NOISE) for _ in range(N)]
noise_mean = statistics.fmean(noise)
noise = [e - noise_mean for e in noise]   # 去均值：让复制噪声只影响误差、不污染偏离
nav_ret = [r - FEE_DAILY + e for r, e in zip(idx_ret, noise)]

idx, nav, idx_v, nav_v = [], [], 1.0, 1.0
for ri, rn in zip(idx_ret, nav_ret):
    idx_v *= (1 + ri)
    nav_v *= (1 + rn)
    idx.append(idx_v)
    nav.append(nav_v)

prem, prem_series, arb_hits = 0.0, [], 0
for _ in range(N):
    if abs(prem) > ARB_COST:
        prem *= ARB_DAMP
        arb_hits += 1
    prem = PREM_AR * prem + rng.gauss(0, PREM_VOL)
    prem_series.append(prem)
price = [v * (1 + p) for v, p in zip(nav, prem_series)]

dev = [rn - ri for ri, rn in zip(idx_ret, nav_ret)]
tracking_error = statistics.pstdev(dev)
tracking_diff = statistics.fmean(dev)

c = Chart(FIG / "07-premium.svg", "ETF 折溢价率与套利成本边界", xlabel="交易日", ylabel="折溢价率")
c.line(range(N), prem_series, BLUE, label="折溢价率")
c.hline(ARB_COST, RED, label="套利上界")
c.hline(-ARB_COST, GREEN, label="套利下界")
c.hline(0.0, "#9aa6b2")
print("折溢价图:", c.save())
t = Chart(FIG / "07-tracking.svg", "指数与 ETF 净值（归一化）", xlabel="交易日", ylabel="净值")
t.line(range(N), idx, BLUE, label="标的指数")
t.line(range(N), nav, GREEN, label="ETF 净值")
print("跟踪图:", t.save())
print("年化跟踪误差=%.3f%% 日均跟踪偏离=%.5f%% | 平均|溢价|=%.3f%% 套利触发=%d 次" %
      (100 * tracking_error * math.sqrt(252), 100 * tracking_diff,
       100 * statistics.fmean(abs(x) for x in prem_series), arb_hits))
