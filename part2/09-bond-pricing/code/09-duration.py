#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用中心差分求一阶/二阶导数，比较三种价格估计，并画收益率曲线。

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
FACE = 100.0
COUPON = 0.04      # 年票息率
MATURITY = 8       # 年
Y0 = 0.035         # 当前 YTM
H = 0.0001         # 数值微分步长
SHOCKS = (-0.020, -0.010, 0.0, 0.010, 0.020)
CURVE = [(1, 0.021), (2, 0.023), (3, 0.025), (5, 0.028),
         (10, 0.032), (20, 0.035)]

# ---- 计算与作图 ----
def bond_price(y):
    cf = [COUPON * FACE] * MATURITY
    cf[-1] += FACE
    return sum(c / (1 + y) ** t for t, c in enumerate(cf, 1))

p0 = bond_price(Y0)
d1 = (bond_price(Y0 + H) - bond_price(Y0 - H)) / (2 * H)
d2 = (bond_price(Y0 + H) - 2 * p0 + bond_price(Y0 - H)) / (H * H)
mod_dur, convexity = -d1 / p0, d2 / p0
macaulay = mod_dur * (1 + Y0)

ys = [0.005 + i * 0.0025 for i in range(25)]
actual = [bond_price(Y0 + dy) for dy in ys]
linear = [p0 + d1 * dy for dy in ys]
quad = [p0 + d1 * dy + 0.5 * d2 * dy * dy for dy in ys]
dys = [Y0 + dy for dy in ys]

c = Chart(FIG / "09-convexity.svg", "价格—收益率曲线与一阶/二阶近似", xlabel="YTM", ylabel="价格")
c.line(dys, actual, BLUE, label="精确价格")
c.line(dys, linear, RED, label="久期（切线）近似", dash="5 4")
c.line(dys, quad, GREEN, label="久期+凸性近似", dash="2 3")
c.vline(Y0, "#9aa6b2", label="当前 YTM")
print("近似图:", c.save())
cu = Chart(FIG / "09-curve.svg", "合成收益率曲线（期限结构）", xlabel="期限（年）", ylabel="YTM")
cu.line([t for t, _y in CURVE], [y for _t, y in CURVE], AMBER, label="收益率曲线")
print("曲线图:", cu.save())

rows = []
for dy in SHOCKS:
    px = bond_price(Y0 + dy) - p0
    e1 = d1 * dy - px
    e2 = d1 * dy + 0.5 * d2 * dy * dy - px
    rows.append((dy, px, e1, e2))
print("麦考利久期=%.3f 年 修正久期=%.3f 凸性=%.2f | 当前价格=%.3f" %
      (macaulay, mod_dur, convexity, p0))
print("期限利差 10Y-1Y=%.2f%% | Δy=+2%% 时 实际=%.3f 一阶误差=%.3f 二阶误差=%.3f" %
      (100 * (CURVE[4][1] - CURVE[0][1]), rows[-1][1], rows[-1][2], rows[-1][3]))
