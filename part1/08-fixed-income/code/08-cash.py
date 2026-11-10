#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""计算 5 年期债券在不同 YTM 下的价格，并把逆回购与货币基金换算到同一口径。

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
FACE = 100.0       # 面值
COUPON = 0.03      # 年票息率
MATURITY = 5       # 年数
REPO_CAP = 100000.0
REPO_RATE = 0.018  # 逆回购年化报价
REPO_DAYS = 7      # 名义期限
REAL_DAYS = 9      # 跨周末的实际占款天数
REPO_FEE = 0.00001 # 手续费率
MM_DAILY = (0.000048, 0.000051, 0.000049, 0.000050, 0.000052, 0.000047, 0.000050)

# ---- 计算与作图 ----
def bond_price(y):
    cf = [COUPON * FACE] * MATURITY
    cf[-1] += FACE
    return sum(c / (1 + y) ** t for t, c in enumerate(cf, 1))

ys = [0.01 + i * 0.0025 for i in range(21)]
ps = [bond_price(y) for y in ys]

c = Chart(FIG / "08-bond-curve.svg", "5 年期 3% 票息债券：价格—到期收益率", xlabel="YTM", ylabel="价格")
c.line(ys, ps, BLUE, label="债券价格")
c.hline(FACE, RED, label="面值 100")
c.vline(COUPON, "#9aa6b2", label="票息率 3%")
print("债券图:", c.save())

repo_interest = REPO_CAP * REPO_RATE * REPO_DAYS / 365 - REPO_CAP * REPO_FEE
repo_effective = repo_interest / REPO_CAP * 365 / REAL_DAYS
mm_annual = statistics.fmean(MM_DAILY) * 365
mm_7d = (1 + statistics.fmean(MM_DAILY)) ** 7 - 1

labels = ["逆回购报价", "逆回购实际", "货币基金7日年化"]
vals = [100 * REPO_RATE, 100 * repo_effective, 100 * mm_annual]
b = Chart(FIG / "08-cash.svg", "现金工具收益口径对照（年化 %，合成示意）",
          xlabel="口径", ylabel="年化 %", xticks=[(i, n) for i, n in enumerate(labels)])
b.bars(range(3), vals, GREEN, label="年化收益")
print("现金图:", b.save())
print("YTM=票息时价格=%.3f | YTM 5%% 时价格=%.3f（跌 %.2f%%）" %
      (bond_price(COUPON), bond_price(0.05), 100 * (bond_price(0.05) / FACE - 1)))
print("逆回购利息=%.2f 元 报价=%.2f%% 按实际占款折算=%.2f%% | 货基7日累计=%.4f%% 年化=%.2f%%" %
      (repo_interest, 100 * REPO_RATE, 100 * repo_effective, 100 * mm_7d, 100 * mm_annual))
