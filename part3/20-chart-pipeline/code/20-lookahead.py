#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对比「全样本均值」与「滚动均值」两种信号，统一在下一根成交，量化差距。

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
N = 240
START, DRIFT, VOL = 50.0, 0.0006, 0.014
W = 20             # 合法滚动窗口
FEE = 0.0005       # 换仓成本

# ---- 计算与作图 ----
rng = random.Random(7)
px, prices = START, []
for _ in range(N):
    px *= (1 + rng.gauss(DRIFT, VOL))
    prices.append(px)

full_mean = statistics.fmean(prices)          # 非法：用到整段样本
rolling = [None] * N
for i in range(W - 1, N):
    rolling[i] = statistics.fmean(prices[i + 1 - W:i + 1])
sig_bad = [1 if prices[i] > full_mean else 0 for i in range(N)]
sig_ok = [1 if rolling[i] is not None and prices[i] > rolling[i] else 0 for i in range(N)]

def backtest(sig):
    v, path_, trades = 1.0, [1.0], 0
    for i in range(N - 1):
        r = prices[i + 1] / prices[i] - 1
        if i > 0 and sig[i] != sig[i - 1]:
            trades += 1
            v *= (1 - FEE)
        v *= (1 + sig[i] * r)
        path_.append(v)
    return path_, trades

bad_px, bad_trades = backtest(sig_bad)
ok_px, ok_trades = backtest(sig_ok)
buy_px, _ = backtest([1] * N)

c = Chart(FIG / "20-lookahead.svg", "未来函数策略 vs 合法滚动策略", xlabel="交易日", ylabel="净值")
c.line(range(N), bad_px, RED, label="全样本均值（含未来信息）")
c.line(range(N), ok_px, BLUE, label="滚动均值（合法）")
c.line(range(N), buy_px, GREEN, label="始终持有")
print("净值图:", c.save())

m = Chart(FIG / "20-mean.svg", "价格与两条基准线", xlabel="交易日", ylabel="价格")
m.line(range(N), prices, BLUE, label="价格")
m.hline(full_mean, RED, label="全样本均值（非法）")
xr = [i for i in range(N) if rolling[i] is not None]
m.line(xr, [rolling[i] for i in xr], AMBER, label="滚动均值（合法）")
print("基准图:", m.save())
print("终值 未来函数=%.3f 滚动=%.3f 持有=%.3f | 换仓 %d / %d 次 | 全样本均值=%.3f" %
      (bad_px[-1], ok_px[-1], buy_px[-1], bad_trades, ok_trades, full_mean))
