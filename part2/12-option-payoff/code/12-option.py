#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用标准库实现 CRR 二叉树，验证平价关系，并用中心差分求 delta。

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
S0, K = 100.0, 100.0
R, SIGMA, T = 0.03, 0.20, 1.0
STEPS = 60          # 二叉树步数

# ---- 计算与作图 ----
def crr(S, kind):
    dt = T / STEPS
    u, d = math.exp(SIGMA * math.sqrt(dt)), math.exp(-SIGMA * math.sqrt(dt))
    p = (math.exp(R * dt) - d) / (u - d)
    disc = math.exp(-R * dt)
    total = 0.0
    for j in range(STEPS + 1):
        st = S * u ** j * d ** (STEPS - j)
        prob = math.comb(STEPS, j) * p ** j * (1 - p) ** (STEPS - j)
        val = max(st - K, 0.0) if kind == "call" else max(K - st, 0.0)
        total += prob * val
    return (disc ** STEPS) * total

call, put = crr(S0, "call"), crr(S0, "put")
parity = (call - put) - (S0 - K * math.exp(-R * T))
eps = S0 * 0.01
delta = (crr(S0 + eps, "call") - crr(S0 - eps, "call")) / (2 * eps)
gamma = (crr(S0 + eps, "call") - 2 * call + crr(S0 - eps, "call")) / (eps * eps)

s_grid = [60.0 + i * 1.0 for i in range(81)]
call_pl = [max(s - K, 0.0) - call for s in s_grid]
put_pl = [max(K - s, 0.0) - put for s in s_grid]
stock_pl = [s - S0 for s in s_grid]
c = Chart(FIG / "12-payoff.svg", "到期损益图（含权利金）", xlabel="标的到期价 S_T", ylabel="损益")
c.line(s_grid, call_pl, RED, label="买入看涨")
c.line(s_grid, put_pl, GREEN, label="买入看跌")
c.line(s_grid, stock_pl, BLUE, label="持有现货")
c.hline(0.0, "#9aa6b2", label="盈亏平衡基准")
c.vline(K, AMBER, label="行权价 K")
print("损益图:", c.save())

s_delta = [70.0 + i * 1.0 for i in range(61)]
d_values = [(crr(s + eps, "call") - crr(s - eps, "call")) / (2 * eps) for s in s_delta]
d = Chart(FIG / "12-delta.svg", "看涨期权 delta 随标的价格变化", xlabel="标的价格", ylabel="delta")
d.line(s_delta, d_values, BLUE, label="delta（数值差分）")
d.hline(0.5, RED, label="平值附近 ≈ 0.5")
print("delta 图:", d.save())
print("CRR 看涨=%.4f 看跌=%.4f | 平价残差=%.6f | delta=%.4f gamma=%.6f" %
      (call, put, parity, delta, gamma))
