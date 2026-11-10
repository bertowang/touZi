#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""名义复利、扣通胀、扣费率、波动拖累四条曲线的对照，全部可手算核对。

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
YEARS = 30          # 投资年限
R_NOM = 0.07        # 名义年收益
INFL = 0.025        # 年通胀
FEE = 0.010         # 年管理费
SIGMA = 0.18        # 年化波动，用于波动拖累近似
V0 = 100000.0       # 初始本金

# ---- 计算与作图 ----
xs = list(range(YEARS + 1))
nominal = [V0 * (1 + R_NOM) ** t for t in xs]
real = [V0 * ((1 + R_NOM) / (1 + INFL)) ** t for t in xs]
after_fee = [V0 * (1 + R_NOM - FEE) ** t for t in xs]
drag = [V0 * (1 + R_NOM - SIGMA ** 2 / 2) ** t for t in xs]

r_real = (1 + R_NOM) / (1 + INFL) - 1
fee_loss = 1 - after_fee[-1] / nominal[-1]

c = Chart(FIG / "01-compound.svg", "10 万元在 30 年里的四种终值口径",
          xlabel="年", ylabel="金额（元）")
c.line(xs, nominal, BLUE, label="名义复利 7%")
c.line(xs, real, GREEN, label="扣通胀后的购买力")
c.line(xs, after_fee, AMBER, label="再扣 1% 管理费")
c.line(xs, drag, RED, label="含波动拖累近似")
print("图:", c.save())
print("实际年收益=%.3f%% | 30年名义=%.0f 实际=%.0f 扣费=%.0f | 费率吞掉=%.1f%% | 波动拖累=%.2f%%/年" %
      (100 * r_real, nominal[-1], real[-1], after_fee[-1],
       100 * fee_loss, 100 * SIGMA ** 2 / 2))
