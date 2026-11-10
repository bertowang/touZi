#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用限价单簿求最大成交量开盘价，再模拟受涨跌停约束的 240 分钟分时价格。

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
BIDS = [(10.02, 300), (10.01, 200), (10.00, 500), (9.99, 400), (9.98, 600)]
ASKS = [(9.98, 200), (9.99, 300), (10.00, 400), (10.01, 200), (10.02, 500)]
PREV_CLOSE = 10.00
LIMIT = 0.10        # ±10% 涨跌停
MINUTES = 240
VOL_MIN = 0.0012    # 每分钟价格波动尺度

# ---- 计算与作图 ----
prices = sorted({p for p, _q in BIDS} | {p for p, _q in ASKS})
best_px, best_vol = None, -1
for p in prices:
    demand = sum(q for pb, q in BIDS if pb >= p)
    supply = sum(q for pa, q in ASKS if pa <= p)
    vol = min(demand, supply)
    if vol > best_vol or (vol == best_vol and best_px is not None and abs(p - PREV_CLOSE) < abs(best_px - PREV_CLOSE)):
        best_px, best_vol = p, vol

rng = random.Random(7)
up, down = PREV_CLOSE * (1 + LIMIT), PREV_CLOSE * (1 - LIMIT)
px, path_ = best_px, []
touches = 0
for _ in range(MINUTES):
    raw = px * (1 + rng.gauss(0, VOL_MIN))
    new = min(up, max(down, raw))
    if new == up or new == down:
        touches += 1
    px = new
    path_.append(px)

c = Chart(FIG / "04-intraday.svg", "涨跌停约束下的合成分时价格", xlabel="分钟", ylabel="价格")
c.line(range(MINUTES), path_, BLUE, label="分时价")
c.hline(up, RED, label="涨停")
c.hline(down, GREEN, label="跌停")
c.hline(PREV_CLOSE, "#9aa6b2", label="昨收")
print("图:", c.save())
print("集合竞价开盘价=%.2f 成交量=%d | 收盘=%.2f 涨跌幅=%.2f%% | 触及涨跌停分钟数=%d" %
      (best_px, best_vol, px, 100 * (px / PREV_CLOSE - 1), touches))
