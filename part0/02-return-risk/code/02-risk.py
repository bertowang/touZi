#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""混合正态生成 2000 个日收益，计算全套风险指标并画净值与收益直方图。

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
N = 2000          # 交易日数
MU = 0.0004        # 日均值
SIG_LOW = 0.008    # 常态日波动
SIG_HIGH = 0.035   # 尾部日波动
P_STRESS = 0.05    # 尾部状态概率
ALPHA = 0.95       # VaR 置信水平

# ---- 计算与作图 ----
rng = random.Random(7)
rets = []
for _ in range(N):
    sig = SIG_HIGH if rng.random() < P_STRESS else SIG_LOW
    rets.append(rng.gauss(MU, sig))

mean = statistics.fmean(rets)
sd = statistics.pstdev(rets)
skew = sum(((x - mean) / sd) ** 3 for x in rets) / N
kurt = sum(((x - mean) / sd) ** 4 for x in rets) / N - 3

equity, v, peak, worst = [], 1.0, 1.0, 0.0
for r in rets:
    v *= (1 + r)
    equity.append(v)
    peak = max(peak, v)
    worst = min(worst, v / peak - 1.0)

ordered = sorted(rets)
k = max(1, int((1 - ALPHA) * N))
var95 = ordered[k - 1]
cvar95 = statistics.fmean(ordered[:k])
normal_var = mean - 1.645 * sd

c = Chart(FIG / "02-path.svg", "厚尾收益序列的净值路径", xlabel="交易日", ylabel="净值")
c.line(range(N), equity, BLUE, label="账户净值")
c.hline(1.0, "#9aa6b2", label="初始净值")
print("净值图:", c.save())

bins = [-0.10 + i * 0.005 for i in range(40)]
counts = [0] * (len(bins) - 1)
for r in rets:
    for i in range(len(bins) - 1):
        if bins[i] <= r < bins[i + 1]:
            counts[i] += 1
            break
h = Chart(FIG / "02-tail.svg", "日收益分布与 95% VaR", xlabel="日收益", ylabel="频数")
h.bars(bins[:-1], counts, GREEN, label="收益直方图")
h.vline(var95, RED, label="历史 VaR95")
print("分布图:", h.save())
print("均值=%.5f 标准差=%.5f 偏度=%.2f 超额峰度=%.2f | MDD=%.1f%% | VaR95=%.2f%% CVaR95=%.2f%% 正态VaR=%.2f%%" %
      (mean, sd, skew, kurt, 100 * worst, 100 * var95, 100 * cvar95, 100 * normal_var))
