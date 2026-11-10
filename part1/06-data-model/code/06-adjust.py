#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构造含一次 1 拆 2 的合成 OHLCV，比较不复权与前复权收益，并画出价格与收益对照。

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
N = 60              # 交易日数
SPLIT_DAY = 30      # 拆股发生日
FACTOR = 2.0        # 1 股拆为 2 股
BASE = 20.0         # 起始价格
VOL = 0.015         # 日波动

# ---- 计算与作图 ----
rng = random.Random(7)
raw, px = [], BASE
for i in range(N):
    px *= (1 + rng.gauss(0.001, VOL))
    if i == SPLIT_DAY:
        px /= FACTOR
    raw.append(px)

adjusted = [v / FACTOR if i < SPLIT_DAY else v for i, v in enumerate(raw)]

ohlcv = []
for c in raw:
    o = c / (1 + rng.gauss(0, 0.004))
    h = max(o, c) * (1 + abs(rng.gauss(0, 0.003)))
    l = min(o, c) * (1 - abs(rng.gauss(0, 0.003)))
    v = int(1e6 * (1 + abs(rng.gauss(0, 0.3))))
    ohlcv.append((round(o, 3), round(h, 3), round(l, 3), round(c, 3), v))

raw_ret = [raw[i] / raw[i - 1] - 1 for i in range(1, N)]
adj_ret = [adjusted[i] / adjusted[i - 1] - 1 for i in range(1, N)]

c = Chart(FIG / "06-adjusted.svg", "拆股日前后：不复权价 vs 前复权价", xlabel="交易日", ylabel="价格")
c.line(range(N), raw, RED, label="不复权收盘价")
c.line(range(N), adjusted, BLUE, label="前复权收盘价")
c.vline(SPLIT_DAY, "#9aa6b2", label="拆股日")
print("价格图:", c.save())

r = Chart(FIG / "06-returns.svg", "同一个拆股日的日收益率", xlabel="交易日", ylabel="日收益")
r.line(range(1, N), raw_ret, RED, label="未复权（含假暴跌）")
r.line(range(1, N), adj_ret, GREEN, label="前复权（真实收益）")
r.hline(0.0, "#9aa6b2")
print("收益图:", r.save())
print("OHLCV 首行=%s" % (ohlcv[0],))
print("拆股日 未复权收益=%.2f%% 前复权收益=%.2f%% | 全期 未复权=%.2f%% 前复权=%.2f%%" %
      (100 * raw_ret[SPLIT_DAY - 1], 100 * adj_ret[SPLIT_DAY - 1],
       100 * (raw[-1] / raw[0] - 1), 100 * (adjusted[-1] / adjusted[0] - 1)))
