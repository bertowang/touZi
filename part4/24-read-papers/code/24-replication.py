#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""量化「选择性剔除 + 零成本 + 样本内」对夏普的抬升，并与净额/样本外对照。

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
N, SPLIT = 600, 300
MU, SIG = 0.0004, 0.010   # 合成策略的日均毛收益与波动
COST = 0.0003             # 每日双边成本
TRIM = 0.10               # 论文口径「剔除最差 10% 交易日」
ANN = 252

# ---- 计算与作图 ----
rng = random.Random(7)
raw = [rng.gauss(MU, SIG) for _ in range(N)]

def sharpe(series):
    s = statistics.pstdev(series)
    return statistics.fmean(series) / s * math.sqrt(ANN) if s else 0.0

def equity(series):
    v, out = 1.0, [1.0]
    for r in series:
        v *= (1 + r)
        out.append(v)
    return out

paper = sorted(raw)[int(N * TRIM):]           # 非法：用全样本挑掉最差的日子
net = [r - COST for r in raw]
oos = [r - COST for r in raw[SPLIT:]]
is_net = [r - COST for r in raw[:SPLIT]]
s_paper, s_net, s_is, s_oos = sharpe(paper), sharpe(net), sharpe(is_net), sharpe(oos)

labels = ["论文口径", "全样本净额", "样本内净额", "样本外净额"]
vals = [s_paper, s_net, s_is, s_oos]
c = Chart(FIG / "24-sharpe.svg", "同一策略在四种报告口径下的夏普比率", xlabel="口径", ylabel="年化夏普",
          xticks=[(i, n) for i, n in enumerate(labels)])
c.bars(range(4), vals, BLUE, label="夏普")
c.hline(0.0, "#9aa6b2")
print("夏普图:", c.save())
e = Chart(FIG / "24-equity.svg", "论文口径 vs 净额净值的账户曲线", xlabel="交易日", ylabel="净值")
e.line(range(len(paper) + 1), equity(paper), RED, label="选择性剔除 + 零成本")
e.line(range(N + 1), equity(net), BLUE, label="全样本 + 成本")
e.hline(1.0, "#9aa6b2")
print("净值图:", e.save())
print("论文口径=%.3f 全样本净额=%.3f 样本内=%.3f 样本外=%.3f | 成本使夏普下降 %.3f" %
      (s_paper, s_net, s_is, s_oos, s_paper - s_net))
