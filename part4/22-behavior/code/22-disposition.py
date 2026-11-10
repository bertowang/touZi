#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""模拟带损失厌恶的卖出概率，计算实现盈利比例与实现亏损比例。

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
N_DAYS, N_POS = 250, 1200
START, DRIFT, VOL = 50.0, 0.0004, 0.012
BASE_SELL = 0.03     # 基准卖出概率
GAIN_EXTRA = 0.12    # 盈利时的额外卖出倾向
STEEP = 60.0         # 概率函数陡峭程度

# ---- 计算与作图 ----
def sell_prob(pnl):
    return BASE_SELL + GAIN_EXTRA / (1 + math.exp(-STEEP * pnl))

rng = random.Random(7)
px, prices = START, []
for _ in range(N_DAYS):
    px *= (1 + rng.gauss(DRIFT, VOL))
    prices.append(px)

sell_g = hold_g = sell_l = hold_l = 0
win_days, lose_days = [], []
for _ in range(N_POS):
    entry = rng.randrange(0, N_DAYS - 20)
    ep = prices[entry]
    for t in range(entry + 1, N_DAYS):
        pnl = prices[t] / ep - 1
        if rng.random() < sell_prob(pnl):
            if pnl > 0:
                sell_g += 1; win_days.append(t - entry)
            else:
                sell_l += 1; lose_days.append(t - entry)
            break
        if pnl > 0:
            hold_g += 1
        else:
            hold_l += 1

pgr = sell_g / (sell_g + hold_g) if sell_g + hold_g else 0.0
plr = sell_l / (sell_l + hold_l) if sell_l + hold_l else 0.0

pnl_bins = [-0.10 + i * 0.01 for i in range(21)]
probs = [100 * sell_prob(x + 0.005) for x in pnl_bins]
c = Chart(FIG / "22-disposition.svg", "卖出概率 vs 未实现盈亏（行为假设）",
          xlabel="未实现盈亏", ylabel="卖出概率 %")
c.bars(pnl_bins, probs, BLUE, label="卖出概率")
print("概率图:", c.save())
b = Chart(FIG / "22-pgr.svg", "PGR 与 PLR：处置效应的度量", xlabel="口径", ylabel="比例",
          xticks=[(0, "PGR 实现盈利"), (1, "PLR 实现亏损")])
b.bars([0, 1], [pgr, plr], RED, label="实现比例")
print("度量图:", b.save())
print("PGR=%.4f PLR=%.4f 差值=%+.4f | 盈利持仓平均持有=%.1f 天 亏损=%.1f 天" %
      (pgr, plr, pgr - plr,
       statistics.fmean(win_days) if win_days else 0,
       statistics.fmean(lose_days) if lose_days else 0))
