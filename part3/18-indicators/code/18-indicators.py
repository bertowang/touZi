#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用标准库计算 MACD、RSI、布林带、KDJ，并统计超买超卖与交叉次数。

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
N = 180
START = 50.0
DRIFT, VOL = 0.0008, 0.012
FAST, SLOW, SIGNAL = 12, 26, 9
RSI_N, BOLL_N, KDJ_N = 14, 20, 9

# ---- 计算与作图 ----
rng = random.Random(7)
px, prices = START, []
for _ in range(N):
    px *= (1 + rng.gauss(DRIFT, VOL))
    prices.append(px)

def ema(series, w):
    a, out, prev = 2.0 / (w + 1), [], series[0]
    for v in series:
        prev = a * v + (1 - a) * prev
        out.append(prev)
    return out

dif = [a - b for a, b in zip(ema(prices, FAST), ema(prices, SLOW))]
dea = ema(dif, SIGNAL)
hist = [2 * (a - b) for a, b in zip(dif, dea)]
changes = [prices[i] - prices[i - 1] for i in range(1, N)]
gains = [max(c, 0.0) for c in changes]
losses = [max(-c, 0.0) for c in changes]
ag, al = statistics.fmean(gains[:RSI_N]), statistics.fmean(losses[:RSI_N])
rsi = [None] * N
for i in range(RSI_N, N):
    ag = (ag * (RSI_N - 1) + gains[i - 1]) / RSI_N
    al = (al * (RSI_N - 1) + losses[i - 1]) / RSI_N
    rsi[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)

upper, lower, pct_b = [None] * N, [None] * N, [None] * N
for i in range(BOLL_N - 1, N):
    win = prices[i + 1 - BOLL_N:i + 1]
    m, s = statistics.fmean(win), statistics.pstdev(win)
    upper[i], lower[i] = m + 2 * s, m - 2 * s
    pct_b[i] = (prices[i] - lower[i]) / (upper[i] - lower[i]) if upper[i] > lower[i] else 0.5

k, d, j = [None] * N, [None] * N, [None] * N
kp, dp = 50.0, 50.0
for i in range(KDJ_N - 1, N):
    win = prices[i + 1 - KDJ_N:i + 1]
    hi, lo = max(win), min(win)
    rsv = 100 * (prices[i] - lo) / (hi - lo) if hi > lo else 50.0
    kp, dp = (2 * kp + rsv) / 3, (2 * dp + kp) / 3
    k[i], d[i], j[i] = kp, dp, 3 * kp - 2 * dp

def clean(series):
    xs = [i for i, v in enumerate(series) if v is not None]
    return xs, [series[i] for i in xs]

xu, yu = clean(upper); xl, yl = clean(lower)
c = Chart(FIG / "18-indicators.svg", "布林带与价格（%B 提示价格在通道中的位置）",
          xlabel="交易日", ylabel="价格")
c.line(range(N), prices, BLUE, label="收盘价")
c.line(xu, yu, RED, label="上轨 SMA+2σ", dash="5 4")
c.line(xl, yl, GREEN, label="下轨 SMA−2σ", dash="5 4")
print("布林图:", c.save())
m = Chart(FIG / "18-macd.svg", "MACD：DIF / DEA / 柱状能量", xlabel="交易日", ylabel="数值")
m.bars(range(N), hist, "#9aa6b2", label="MACD 柱")
m.line(range(N), dif, BLUE, label="DIF")
m.line(range(N), dea, AMBER, label="DEA")
m.hline(0.0, "#8a909b")
print("MACD 图:", m.save())

cross = sum(1 for i in range(1, N) if (hist[i - 1] <= 0 < hist[i]) or (hist[i - 1] >= 0 > hist[i]))
over = sum(1 for v in rsi if v is not None and v > 70)
under = sum(1 for v in rsi if v is not None and v < 30)
print("RSI=%.2f K=%.2f D=%.2f J=%.2f %%B=%.3f | RSI>70 共%d 天 <30 共%d 天 柱变号%d 次" %
      (rsi[-1], k[-1], d[-1], j[-1], pct_b[-1], over, under, cross))
