#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合成「追涨资金流 → 拥挤 → 后续收益受压」的数据生成过程，并做分箱对照。

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
N, FWD, BINS = 500, 20, 8
W = 20             # 拥挤度滚动窗口
GAMMA = 0.0009     # 拥挤对未来收益的压制系数
NOISE = 0.009      # 收益噪声

# ---- 计算与作图 ----
rng = random.Random(7)
rets, flow, crowd = [], [], []
for i in range(N):
    if i >= W:
        recent = flow[i - W:i]
        m = statistics.fmean(flow[:i])
        s = statistics.pstdev(flow[:i]) or 1.0
        c = (statistics.fmean(recent) - m) / s
    else:
        c = 0.0
    crowd.append(c)
    r = 0.0003 - GAMMA * c + rng.gauss(0, NOISE)
    rets.append(r)
    chase = 0.7 * (statistics.fmean(rets[-5:]) / NOISE) if rets else 0.0
    flow.append(chase + rng.gauss(0, 0.8))

prices, v = [], 1.0
for r in rets:
    v *= (1 + r)
    prices.append(v)
fwd = [prices[i + FWD] / prices[i] - 1 if i + FWD < N else None
       for i in range(N)]

lo, hi = min(crowd), max(crowd)
width = (hi - lo) / BINS
bucket = [[] for _ in range(BINS)]
for c, f in zip(crowd, fwd):
    if f is None:
        continue
    k = min(BINS - 1, int((c - lo) / width))
    bucket[k].append(f)
means = [statistics.fmean(b) if b else 0.0 for b in bucket]
counts = [len(b) for b in bucket]

c = Chart(FIG / "23-crowding.svg", "合成拥挤度时间序列", xlabel="交易日", ylabel="z 分数")
c.line(range(N), crowd, BLUE, label="拥挤度")
c.hline(2.0, RED, label="+2 高拥挤")
c.hline(-2.0, GREEN, label="−2 低拥挤")
print("拥挤图:", c.save())
b = Chart(FIG / "23-bins.svg", "拥挤度分箱后的 20 日前向平均收益", xlabel="拥挤度分箱", ylabel="平均收益 %",
          xticks=[(i, "Q%d" % (i + 1)) for i in range(BINS)])
b.bars(range(BINS), [100 * x for x in means], AMBER, label="前向收益")
b.hline(0.0, "#9aa6b2")
print("分箱图:", b.save())
valid = [(c, f) for c, f in zip(crowd, fwd) if f is not None]
mc = statistics.fmean(x for x, _y in valid); mf = statistics.fmean(y for _x, y in valid)
corr = sum((x - mc) * (y - mf) for x, y in valid) / math.sqrt(
    sum((x - mc) ** 2 for x, _y in valid) * sum((y - mf) ** 2 for _x, y in valid))
print("最低拥挤箱=%.3f%% 最高拥挤箱=%.3f%% 差=%+.3f%% | 相关系数=%.3f | 各箱样本 %s" %
      (100 * means[0], 100 * means[-1], 100 * (means[-1] - means[0]), corr, counts))
