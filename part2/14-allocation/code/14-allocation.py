#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合成 20 年月度股债收益，比较三种规则的风险、收益、回撤与权重漂移。

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
YEARS = 20
MONTHS = YEARS * 12
TARGET = (0.60, 0.40)   # 股 / 债目标权重
REBAL_EVERY = 12        # 每 12 个月再平衡
V0 = 100000.0
COST = 0.001            # 单次调仓成本率

# ---- 计算与作图 ----
rng = random.Random(7)
rs, rb = [], []
for _ in range(MONTHS):
    z, z2 = rng.gauss(0, 1), rng.gauss(0, 1)
    rs.append(0.007 + 0.045 * z)
    rb.append(0.002 + 0.012 * (-0.2 * z + math.sqrt(1 - 0.04) * z2))

all_stock = [V0]
bh_series, rb_series = [V0], [V0]
bh_s, bh_b = V0 * TARGET[0], V0 * TARGET[1]   # 买入持有：份额固定
rb_s, rb_b = V0 * TARGET[0], V0 * TARGET[1]   # 再平衡：份额可调
turnover, w_bh, w_rb = 0.0, [], []
for i in range(MONTHS):
    all_stock.append(all_stock[-1] * (1 + rs[i]))
    bh_s *= (1 + rs[i]); bh_b *= (1 + rb[i])
    bh_value = bh_s + bh_b
    bh_series.append(bh_value)
    w_bh.append(bh_s / bh_value)

    if (i + 1) % REBAL_EVERY == 0:
        rb_value = rb_s + rb_b
        trade = abs(TARGET[0] - rb_s / rb_value) * rb_value
        turnover += trade
        rb_value -= trade * COST
        rb_s, rb_b = rb_value * TARGET[0], rb_value * TARGET[1]
    rb_s *= (1 + rs[i]); rb_b *= (1 + rb[i])
    rb_value = rb_s + rb_b
    rb_series.append(rb_value)
    w_rb.append(rb_s / rb_value)

def metrics(xs):
    rr = [xs[i] / xs[i - 1] - 1 for i in range(1, len(xs))]
    peak, mdd = xs[0], 0.0
    for v in xs:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1)
    cagr = (xs[-1] / xs[0]) ** (1 / YEARS) - 1
    return cagr, statistics.pstdev(rr) * math.sqrt(12), mdd

c = Chart(FIG / "14-equity.svg", "三种配置规则的账户净值", xlabel="月", ylabel="账户价值")
c.line(range(MONTHS + 1), all_stock, RED, label="100% 股票")
c.line(range(MONTHS + 1), bh_series, AMBER, label="60/40 买入持有")
c.line(range(MONTHS + 1), rb_series, BLUE, label="60/40 年度再平衡")
print("净值图:", c.save())
w = Chart(FIG / "14-weights.svg", "股票权重的漂移与拉回", xlabel="月", ylabel="股票权重")
w.line(range(MONTHS), w_bh, AMBER, label="买入持有（漂移）")
w.line(range(MONTHS), w_rb, BLUE, label="年度再平衡")
w.hline(TARGET[0], "#9aa6b2", label="目标 60%")
print("权重图:", w.save())
m1, m2, m3 = metrics(all_stock), metrics(bh_series), metrics(rb_series)
print("再平衡累计调仓金额=%.0f 元 | 期末权重 买入持有=%.1f%% 再平衡=%.1f%%" %
      (turnover, 100 * w_bh[-1], 100 * w_rb[-1]))
print("全股 CAGR=%.2f%% σ=%.2f%% MDD=%.1f%% | 买入持有 %.2f%% / %.2f%% / %.1f%% | 再平衡 %.2f%% / %.2f%% / %.1f%%" %
      (100 * m1[0], 100 * m1[1], 100 * m1[2], 100 * m2[0], 100 * m2[1], 100 * m2[2],
       100 * m3[0], 100 * m3[1], 100 * m3[2]))
