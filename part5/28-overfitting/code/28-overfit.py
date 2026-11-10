#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在同一条合成价格上扫描均线参数，比较 IS 最优组合的 OOS 排名与中位数。

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
N, SPLIT = 800, 400
START, DRIFT, VOL = 50.0, 0.0003, 0.014
FAST_GRID = (3, 5, 10, 20)
SLOW_GRID = (20, 40, 60, 80)
FEE, ANN = 0.0005, 252
ALPHA = 0.05

# ---- 计算与作图 ----
rng = random.Random(7)
px, prices = START, []
for _ in range(N):
    px *= (1 + rng.gauss(DRIFT, VOL))
    prices.append(px)
rets = [prices[t] / prices[t - 1] - 1 for t in range(1, N)]

def sma(series, w):
    return [None if i + 1 < w else statistics.fmean(series[i + 1 - w:i + 1])
            for i in range(len(series))]

def sharpe(xs):
    s = statistics.pstdev(xs)
    return statistics.fmean(xs) / s * math.sqrt(ANN) if s else 0.0

def strategy(fast, slow):
    f, s = sma(prices, fast), sma(prices, slow)
    sig = [0] * N
    for t in range(N):
        if f[t] is not None and s[t] is not None:
            sig[t] = 1 if f[t] > s[t] else 0
    out = []
    for t in range(1, N):
        cost = FEE if t > 1 and sig[t - 1] != sig[t - 2] else 0.0
        out.append(sig[t - 1] * rets[t - 1] - cost)
    return out

rows, records = [], []
for fi, fast in enumerate(FAST_GRID):
    row = []
    for slow in SLOW_GRID:
        rr = strategy(fast, slow)
        is_s, oos_s = sharpe(rr[:SPLIT]), sharpe(rr[SPLIT:])
        row.append(is_s)
        records.append((fast, slow, is_s, oos_s))
    rows.append(row)

best = max(records, key=lambda x: x[2])
oos_sorted = sorted(x[3] for x in records)
rank = sum(1 for x in oos_sorted if x > best[3]) + 1
median_oos = statistics.median(oos_sorted)
bh_oos = sharpe(rets[SPLIT:])
m_tests = len(records)
fam_rate = 1 - (1 - ALPHA) ** m_tests

heatmap(FIG / "28-heatmap.svg", rows,
        ["fast=%d" % f for f in FAST_GRID], ["slow=%d" % s for s in SLOW_GRID],
        title="样本内夏普（%d 组参数）" % m_tests,
        vmin=min(min(r) for r in rows), vmax=max(max(r) for r in rows))
print("热力图:", str(FIG / "28-heatmap.svg"))
c = Chart(FIG / "28-isoos.svg", "样本内 vs 样本外夏普（每点一组参数）",
          xlabel="样本内夏普", ylabel="样本外夏普")
c.scatter([x[2] for x in records], [x[3] for x in records], BLUE,
          label="参数组合", radius=4)
c.scatter([best[2]], [best[3]], RED, label="IS 最优", radius=6)
c.hline(0.0, "#9aa6b2")
print("散点图:", c.save())
print("M=%d 至少一次假阳性概率=%.1f%% Bonferroni 单次阈值=%.4f" %
      (m_tests, 100 * fam_rate, ALPHA / m_tests))
print("IS 最优 fast=%d slow=%d IS=%.3f OOS=%.3f | OOS 排名=%d/%d 中位=%.3f 持有基准=%.3f" %
      (best[0], best[1], best[2], best[3], rank, m_tests, median_oos, bh_oos))
