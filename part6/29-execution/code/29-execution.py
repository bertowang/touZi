#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 U 形成交量曲线与临时/永久冲击模型，比较四种执行方式的成交均价。

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
Q = 100000         # 总订单量（股）
SLICES = 20        # 日内切片数
ARRIVAL = 10.00    # 决策到达价
ETA = 0.002        # 临时冲击系数
PERM = 0.0015      # 永久冲击系数
LIMIT_PX = 10.01   # 限价单价格上限

# ---- 计算与作图 ----
rng = random.Random(7)
base = [ARRIVAL]
for _ in range(SLICES):
    base.append(base[-1] * (1 + rng.gauss(0, 0.0008)))
vol_curve = [1.2 - 0.8 * math.sin(math.pi * t / (SLICES - 1)) for t in range(SLICES)]
tot_vol = sum(vol_curve)
vwap_q = [Q * v / tot_vol for v in vol_curve]
twap_q = [Q / SLICES] * SLICES
market_q = [Q] + [0.0] * (SLICES - 1)

def execute(qtys, limit=None):
    cum, cost, filled, marks = 0.0, 0.0, 0.0, []
    for t, q in enumerate(qtys):
        if q <= 0:
            marks.append(None)
            continue
        px = base[t] * (1 + PERM * cum / Q)
        temp = ETA * (q / (Q / SLICES))
        fill_px = px + temp
        if limit is not None and fill_px > limit:
            marks.append(None)
            continue
        cost += q * fill_px
        filled += q
        cum += q
        marks.append(fill_px)
    return (cost / filled if filled else 0.0), filled / Q, marks

results = {
    "市价一次性": execute(market_q),
    "TWAP": execute(twap_q),
    "VWAP": execute(vwap_q),
    "限价单": execute(twap_q, limit=LIMIT_PX),
}

c = Chart(FIG / "29-execution.svg", "基准价格与两类执行点", xlabel="日内切片", ylabel="价格")
c.line(range(SLICES), base[:SLICES], BLUE, label="无冲击基准价")
marks = results["TWAP"][2]
c.scatter([t for t, m in enumerate(marks) if m], [m for m in marks if m], GREEN,
          label="TWAP 成交价", radius=4)
mm = results["市价一次性"][2]
c.scatter([0], [mm[0]], RED, label="市价一次性", radius=6)
print("执行图:", c.save())

names = list(results)
slips = [10000 * (v[0] / ARRIVAL - 1) if v[0] else 0.0 for v in results.values()]
b = Chart(FIG / "29-slippage.svg", "四种执行方式的滑点（基点）", xlabel="方式", ylabel="bp",
          xticks=[(i, n) for i, n in enumerate(names)])
b.bars(range(len(names)), slips, AMBER, label="滑点 bp")
print("滑点图:", b.save())
print("到达价=%.3f | 滑点(bp) 市价=%.1f TWAP=%.1f VWAP=%.1f 限价=%.1f | 成交率 限价=%.0f%%" %
      (ARRIVAL, *slips, 100 * results["限价单"][1]))
