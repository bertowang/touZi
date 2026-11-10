#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""四条不同费率的终值曲线，并把换手成本折算成年化拖累。

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
YEARS = 30
R_GROSS = 0.07          # 毛年化收益
FEES = (0.000, 0.001, 0.005, 0.015)
V0 = 100000.0
TURNOVER = 1.5          # 年换手率（双边口径见下）
SPREAD = 0.0010         # 单边价差成本
COMMISSION = 0.0003     # 单边佣金与税费

# ---- 计算与作图 ----
one_way = SPREAD + COMMISSION
annual_drag = TURNOVER * 2 * one_way
xs = list(range(YEARS + 1))
curves = [(f, [V0 * (1 + R_GROSS - f) ** t for t in xs]) for f in FEES]

c = Chart(FIG / "05-fee.svg", "不同年费率下的 30 年终值", xlabel="年", ylabel="金额（元）")
cols = (BLUE, GREEN, AMBER, RED)
for (f, ys), col in zip(curves, cols):
    c.line(xs, ys, col, label="费率 %.1f%%" % (100 * f))
net = [V0 * (1 + R_GROSS - FEES[1] - annual_drag) ** t for t in xs]
c.line(xs, net, "#6b4f8a", label="0.1% 费率 + 换手成本")
print("图:", c.save())
print("双边单次成本=%.2f%% | 年换手 %.1f → 年化拖累=%.2f%%" %
      (100 * one_way, TURNOVER, 100 * annual_drag))
print("30年终值 零费率=%.0f 0.1%%费率=%.0f 1.5%%费率=%.0f 叠加换手=%.0f | 成本合计吞掉 %.1f%%" %
      (curves[0][1][-1], curves[1][1][-1], curves[3][1][-1], net[-1],
       100 * (1 - net[-1] / curves[0][1][-1])))
