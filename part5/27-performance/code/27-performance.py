#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合成 36 个月组合与基准收益，计算指标族、IRR 与两部门归因。

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
N_MONTHS = 36
ANN = 12
RF_M = 0.02 / 12          # 月度无风险利率
CONTRIB = (12, 10.0)      # 第 12 个月追加投入
WP, WB = (0.60, 0.40), (0.50, 0.50)
RP, RB = (0.012, 0.004), (0.010, 0.005)

# ---- 计算与作图 ----
rng = random.Random(7)
port = [rng.gauss(0.008, 0.035) for _ in range(N_MONTHS)]
bench = [0.6 * p + rng.gauss(0.001, 0.020) for p in port]

def curve(rets):
    v, out = 1.0, [1.0]
    for r in rets:
        v *= (1 + r)
        out.append(v)
    return out

cp, cb = curve(port), curve(bench)
excess = [p - RF_M for p in port]
down = [min(0.0, x) for x in excess]
down_sd = math.sqrt(statistics.fmean(x * x for x in down))
sharpe = statistics.fmean(excess) / statistics.pstdev(port) * math.sqrt(ANN)
sortino = statistics.fmean(excess) / down_sd * math.sqrt(ANN) if down_sd else 0.0
peak, mdd = cp[0], 0.0
for v in cp:
    peak = max(peak, v)
    mdd = min(mdd, v / peak - 1)
cagr = cp[-1] ** (ANN / N_MONTHS) - 1
calmar = cagr / abs(mdd) if mdd else 0.0
active = [p - b for p, b in zip(port, bench)]
te = statistics.pstdev(active) * math.sqrt(ANN)
ir = statistics.fmean(active) * ANN / te if te else 0.0

acct = 100.0
for i, r in enumerate(port):
    if i == CONTRIB[0]:
        acct += CONTRIB[1]
    acct *= (1 + r)
cf = [-100.0] + [0.0] * N_MONTHS
cf[CONTRIB[0]] -= CONTRIB[1]
cf[-1] += acct

def npv(rate):
    return sum(c / (1 + rate) ** i for i, c in enumerate(cf))

lo, hi = -0.50, 0.50
for _ in range(120):
    mid = (lo + hi) / 2
    if npv(mid) > 0:
        lo = mid
    else:
        hi = mid
mwr_m = (lo + hi) / 2

alloc = sum((WP[i] - WB[i]) * RB[i] for i in range(2))
select = sum(WB[i] * (RP[i] - RB[i]) for i in range(2))
inter = sum((WP[i] - WB[i]) * (RP[i] - RB[i]) for i in range(2))
r_p, r_b = sum(WP[i] * RP[i] for i in range(2)), sum(WB[i] * RB[i] for i in range(2))

c = Chart(FIG / "27-equity.svg", "组合与基准的累计净值", xlabel="月", ylabel="净值")
c.line(range(N_MONTHS + 1), cp, BLUE, label="组合")
c.line(range(N_MONTHS + 1), cb, GREEN, label="基准")
print("净值图:", c.save())
matrix = [[100 * port[y * 12 + m] for m in range(12)] for y in range(3)]
heatmap(FIG / "27-monthly.svg", matrix, ["第1年", "第2年", "第3年"],
        ["M%d" % (m + 1) for m in range(12)], title="组合月度收益热力图（%）",
        vmin=-8, vmax=8)
print("月度图:", str(FIG / "27-monthly.svg"))
print("CAGR=%.2f%% Sharpe=%.3f Sortino=%.3f MDD=%.1f%% Calmar=%.3f TE=%.2f%% IR=%.3f" %
      (100 * cagr, sharpe, sortino, 100 * mdd, calmar, 100 * te, ir))
print("TWR=%.2f%% MWR年化=%.2f%% | Brinson 配置=%.3f%% 选股=%.3f%% 交互=%.3f%% 合计=%.3f%% (实际 %.3f%%)" %
      (100 * (cp[-1] - 1), 100 * ((1 + mwr_m) ** ANN - 1),
       100 * alloc, 100 * select, 100 * inter,
       100 * (alloc + select + inter), 100 * (r_p - r_b)))
