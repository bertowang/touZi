#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在带转折的合成价格上计算均线，检测交叉，量化窗口—滞后权衡。

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
N = 160
TURN = 80           # 真实趋势转折点
START = 50.0
UP, DOWN = 0.004, -0.003
NOISE = 0.010
FAST, SLOW = 5, 20
LOOKBACK = 20

# ---- 计算与作图 ----
rng = random.Random(7)
px, prices = START, []
for i in range(N):
    drift = UP if i < TURN else DOWN
    px *= (1 + drift + rng.gauss(0, NOISE))
    prices.append(px)

def sma(series, w):
    return [None if i + 1 < w else statistics.fmean(series[i + 1 - w:i + 1])
            for i in range(len(series))]

def ema(series, w):
    a, out, prev = 2.0 / (w + 1), [], series[0]
    for v in series:
        prev = a * v + (1 - a) * prev
        out.append(prev)
    return out

fast, slow, ema_fast = sma(prices, FAST), sma(prices, SLOW), ema(prices, FAST)
crosses = []
for i in range(1, N):
    if None in (fast[i - 1], slow[i - 1], fast[i], slow[i]):
        continue
    if fast[i - 1] <= slow[i - 1] and fast[i] > slow[i]:
        crosses.append((i, "金叉"))
    if fast[i - 1] >= slow[i - 1] and fast[i] < slow[i]:
        crosses.append((i, "死叉"))

support = [min(prices[max(0, i + 1 - LOOKBACK):i + 1]) for i in range(N)]
resist = [max(prices[max(0, i + 1 - LOOKBACK):i + 1]) for i in range(N)]

def clean(series):
    xs = [i for i, v in enumerate(series) if v is not None]
    return xs, [series[i] for i in xs]

xf, yf = clean(fast)
x_slow, y_slow = clean(slow)
c = Chart(FIG / "17-trend.svg", "价格、SMA/EMA 与滚动支撑阻力", xlabel="交易日", ylabel="价格")
c.line(range(N), prices, "#9aa6b2", label="价格", opacity=0.8)
c.line(xf, yf, BLUE, label="SMA5")
c.line(x_slow, y_slow, AMBER, label="SMA20")
c.line(range(N), ema_fast, GREEN, label="EMA5")
c.line(range(N), support, RED, label="滚动支撑", dash="3 3")
c.line(range(N), resist, RED, label="滚动阻力", dash="6 3")
c.vline(TURN, "#8a6316", label="真实转折点")
print("趋势图:", c.save())

windows = [3, 5, 10, 20, 40]
lags = []
for w in windows:
    f, s = sma(prices, w), sma(prices, w * 2)
    first = next((i for i in range(TURN, N)
                  if f[i] and s[i] and f[i - 1] and s[i - 1]
                  and f[i - 1] >= s[i - 1] and f[i] < s[i]), N)
    lags.append(first - TURN)
l = Chart(FIG / "17-lag.svg", "均线窗口与转折信号滞后", xlabel="快线窗口", ylabel="滞后（根）",
          xticks=[(i, "n=%d" % w) for i, w in enumerate(windows)])
l.bars(range(len(windows)), lags, BLUE, label="死叉滞后")
print("滞后图:", l.save())
post_death = [x for x in crosses if x[0] >= TURN and x[1] == "死叉"]
print("交叉总数=%d 转折前噪声交叉=%d | 转折后首个死叉=%s | 窗口 %s 对应滞后 %s | 真实转折 T%d" %
      (len(crosses), len([x for x in crosses if x[0] < TURN]),
       post_death[0] if post_death else "无", windows, lags, TURN))
