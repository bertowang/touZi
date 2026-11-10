#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""模拟月度定投、阈值再平衡与决策日志，输出 TWR/MWR、费用与合规检查。

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
YEARS, ANN = 5, 12
MONTHS = YEARS * ANN
MONTHLY = 5000.0           # 每月投入
TARGET, BAND = 0.70, 0.03  # 股票目标权重与再平衡带
FEE = 0.001                # 调仓成本率

# ---- 计算与作图 ----
rng = random.Random(7)
rs, rb = [], []
for i in range(MONTHS):
    z, z2 = rng.gauss(0, 1), rng.gauss(0, 1)
    rs.append((0.012 if i < 30 else -0.004) + 0.045 * z)
    rb.append(0.0015 + 0.008 * (-0.15 * z + math.sqrt(1 - 0.0225) * z2))

cash_in, value, stock_part, bond_part = 0.0, 0.0, 0.0, 0.0
unit, w_prev = 1.0, TARGET
values, contributed, weights, log = [], [], [], []
for i in range(MONTHS):
    unit *= (1 + w_prev * rs[i] + (1 - w_prev) * rb[i])
    cash_in += MONTHLY
    stock_part += MONTHLY * TARGET
    bond_part += MONTHLY * (1 - TARGET)
    stock_part *= (1 + rs[i])
    bond_part *= (1 + rb[i])
    value = stock_part + bond_part
    w = stock_part / value
    if abs(w - TARGET) > BAND:
        trade = abs(TARGET - w) * value
        value -= trade * FEE
        stock_part, bond_part = value * TARGET, value * (1 - TARGET)
        w = TARGET
        log.append((i, "再平衡", round(trade, 0)))
    w_prev = w
    values.append(value)
    contributed.append(cash_in)
    weights.append(w)

twr = unit - 1
cf = [0.0] * (MONTHS + 1)
for i in range(MONTHS):
    cf[i] -= MONTHLY
cf[-1] += values[-1]

def npv(rate):
    return sum(c / (1 + rate) ** i for i, c in enumerate(cf))

lo, hi = -0.30, 0.30
for _ in range(120):
    mid = (lo + hi) / 2
    if npv(mid) > 0:
        lo = mid
    else:
        hi = mid
mwr = (1 + (lo + hi) / 2) ** ANN - 1

c = Chart(FIG / "31-plan.svg", "账户价值与累计投入", xlabel="月", ylabel="金额")
c.line(range(MONTHS), values, BLUE, label="账户价值")
c.line(range(MONTHS), contributed, GREEN, label="累计投入")
print("计划图:", c.save())
d = Chart(FIG / "31-drift.svg", "股票权重与 IPS 再平衡带", xlabel="月", ylabel="权重")
d.line(range(MONTHS), weights, AMBER, label="实际权重")
d.hline(TARGET, BLUE, label="目标 70%")
d.hline(TARGET + BAND, RED, label="上界")
d.hline(TARGET - BAND, RED, label="下界")
print("权重图:", d.save())
max_drift = max(abs(w - TARGET) for w in weights)
print("期末账户=%.0f 累计投入=%.0f TWR(单位净值)=%.2f%% MWR年化=%.2f%%" %
      (values[-1], cash_in, 100 * twr, 100 * mwr))
print("决策日志 %d 条 | 最大偏离=%.2f%% 带宽=%.1f%% | 合规=%s" %
      (len(log), 100 * max_drift, 100 * BAND, "是" if max_drift <= BAND + 0.02 else "需复核"))
