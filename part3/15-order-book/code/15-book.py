#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构造订单簿快照，逐档吃单计算 VWAP，并画出订单量与冲击成本曲线。

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
MID = 10.00
TICK = 0.01
LEVELS = 5
BASE_SIZE = 2000     # 每档基准挂单量
ORDER_QTY = 6000     # 待执行的市价买单
MAX_QTY = 20000      # 冲击曲线扫描上限

# ---- 计算与作图 ----
rng = random.Random(7)
bid_px = [round(MID - TICK / 2 - i * TICK, 2) for i in range(LEVELS)]
ask_px = [round(MID + TICK / 2 + i * TICK, 2) for i in range(LEVELS)]
bid_sz = [int(BASE_SIZE * (1 + abs(rng.gauss(0, 0.4)))) for _ in range(LEVELS)]
ask_sz = [int(BASE_SIZE * (1 + abs(rng.gauss(0, 0.4)))) for _ in range(LEVELS)]
spread = ask_px[0] - bid_px[0]
mid = (ask_px[0] + bid_px[0]) / 2
imbalance = (sum(bid_sz) - sum(ask_sz)) / (sum(bid_sz) + sum(ask_sz))

def execute(qty):
    left, cost, used = qty, 0.0, []
    for px, sz in zip(ask_px, ask_sz):
        take = min(left, sz)
        cost += take * px
        used.append((px, take))
        left -= take
        if left <= 0:
            break
    filled = qty - left
    return cost / filled if filled else mid, filled, used

vwap, filled, used = execute(ORDER_QTY)
impact = vwap / mid - 1

c = Chart(FIG / "15-depth.svg", "五档订单簿深度（买负 / 卖正）", xlabel="价格", ylabel="挂单量")
c.bars(ask_px, ask_sz, RED, label="卖盘")
c.bars(bid_px, [-s for s in bid_sz], GREEN, label="买盘")
c.hline(0.0, "#9aa6b2")
print("深度图:", c.save())

qs = list(range(1000, MAX_QTY + 1, 1000))
impacts = [(execute(q)[0] / mid - 1) * 100 for q in qs]
i = Chart(FIG / "15-impact.svg", "市价买单规模与价格冲击", xlabel="订单量（股）", ylabel="冲击 %")
i.line(qs, impacts, BLUE, label="冲击成本")
i.hline(0.0, "#9aa6b2")
print("冲击图:", i.save())
print("最优买=%.2f 最优卖=%.2f 价差=%.4f (%.3f%%) | 深度失衡=%+.3f" %
      (bid_px[0], ask_px[0], spread, 100 * spread / mid, imbalance))
print("市价买 %d 股 成交 %d 股 VWAP=%.4f 冲击=%.3f%% | 吃到第 %d 档" %
      (ORDER_QTY, filled, vwap, 100 * impact, len(used)))
