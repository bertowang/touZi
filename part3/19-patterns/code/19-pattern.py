#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把双底写成不等式，自动扫描合成序列，比较形态后收益与无条件基准。

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
N = 240
START, DRIFT, VOL = 50.0, 0.0003, 0.014
W, TOL = 3, 0.02        # 局部极值半窗口、两底价格容差
MIN_GAP, MAX_GAP = 8, 45
NECK, FWD = 0.03, 10    # 颈线幅度、前向收益天数

# ---- 计算与作图 ----
rng = random.Random(7)
px, prices = START, []
for _ in range(N):
    px *= (1 + rng.gauss(DRIFT, VOL))
    prices.append(px)

lows = [i for i in range(W, N - W)
        if prices[i] == min(prices[i - W:i + W + 1])]
signals, marks = [], []
for a, i in enumerate(lows):
    for j in lows[a + 1:]:
        gap = j - i
        if not (MIN_GAP <= gap <= MAX_GAP):
            break
        p1, p2 = prices[i], prices[j]
        if abs(p1 - p2) / p1 > TOL:
            continue
        peak = max(prices[i:j + 1])
        if peak / min(p1, p2) - 1 < NECK:
            continue
        if j + FWD < N:
            signals.append((j, prices[j + FWD] / prices[j] - 1))
            marks.append((i, j))
            break

rets = [prices[t + FWD] / prices[t] - 1 for t in range(N - FWD)]
base = statistics.fmean(rets)
hit = statistics.fmean(r for _j, r in signals) if signals else 0.0
win = statistics.fmean(1.0 if r > 0 else 0.0 for _j, r in signals) if signals else 0.0

c = Chart(FIG / "19-pattern.svg", "机器判定的双底信号（标记第二个底）", xlabel="交易日", ylabel="价格")
c.line(range(N), prices, BLUE, label="合成收盘价")
c.scatter([j for _i, j in marks], [prices[j] for _i, j in marks], RED,
          label="双底确认点", radius=5)
print("形态图:", c.save())
b = Chart(FIG / "19-forward.svg", "形态后 10 日收益 vs 无条件基准", xlabel="口径", ylabel="平均收益 %",
          xticks=[(0, "形态后"), (1, "全样本")])
b.bars([0, 1], [100 * hit, 100 * base], GREEN, label="平均 10 日收益")
b.hline(0.0, "#9aa6b2")
print("收益图:", b.save())
print("局部低点=%d 双底信号=%d | 形态后均值=%.3f%% 基准=%.3f%% 胜率=%.1f%%" %
      (len(lows), len(signals), 100 * hit, 100 * base, 100 * win))
