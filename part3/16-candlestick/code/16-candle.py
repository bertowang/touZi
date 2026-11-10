#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 60 根带趋势与均线的合成 K 线，画 K 线+成交量+均线，并统计影线。

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
N = 60              # K 线根数
START = 50.0        # 起始价
DRIFT = 0.0015      # 日漂移
VOL = 0.014         # 日波动
MA_FAST, MA_SLOW = 5, 20

# ---- 计算与作图 ----
rng = random.Random(7)
ohlcv, px = [], START
for _ in range(N):
    o = px
    px = o * (1 + rng.gauss(DRIFT, VOL))
    c = px
    h = max(o, c) * (1 + abs(rng.gauss(0, 0.004)))
    l = min(o, c) * (1 - abs(rng.gauss(0, 0.004)))
    v = int(800000 * (1 + abs(rng.gauss(0, 0.35))))
    ohlcv.append((o, h, l, c, v))

bad = 0
for o, h, l, c, v in ohlcv:
    if not (l <= min(o, c) and max(o, c) <= h and v >= 0):
        bad += 1
closes = [r[3] for r in ohlcv]

def sma(series, w):
    return [None if i + 1 < w else statistics.fmean(series[i + 1 - w:i + 1])
            for i in range(len(series))]

fast, slow = sma(closes, MA_FAST), sma(closes, MA_SLOW)
candlestick(FIG / "16-candle.svg", ohlcv,
            title="合成 K 线（60 根）· MA5 / MA20 · 成交量",
            overlays=[(fast, BLUE, "MA5"), (slow, AMBER, "MA20")],
            xticks=[(i, "T%d" % i) for i in range(0, N, 10)])
print("K 线图:", str(FIG / "16-candle.svg"))

up = sum(1 for r in ohlcv if r[3] >= r[0])
bodies = [abs(r[3] - r[0]) / r[0] for r in ohlcv]
upper = [(r[1] - max(r[0], r[3])) / r[0] for r in ohlcv]
lower = [(min(r[0], r[3]) - r[2]) / r[0] for r in ohlcv]
doji = sum(1 for b in bodies if b < 0.002)
print("不变式违规=%d | 阳线=%d 阴线=%d 十字星=%d | 平均实体=%.2f%% 上影=%.2f%% 下影=%.2f%%" %
      (bad, up, N - up, doji, 100 * statistics.fmean(bodies),
       100 * statistics.fmean(upper), 100 * statistics.fmean(lower)))
