#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把八类产品按五个维度归一化，用线性打分给出教学建议顺序，并画属性热力图。

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
PRODUCTS = ["货币基金", "国债/债券ETF", "宽基ETF", "主动股票基金",
           "个股", "可转债", "REIT", "期权/期货"]
DIMS = ["收益潜力", "风险", "流动性", "门槛", "复杂度"]
# 每行 0~1 的归一化评分；数据为教学示意打分，非真实测评
M = [
    [0.10, 0.05, 0.95, 0.95, 0.05],
    [0.30, 0.25, 0.85, 0.85, 0.25],
    [0.60, 0.55, 0.95, 0.90, 0.30],
    [0.65, 0.60, 0.60, 0.90, 0.40],
    [0.90, 0.90, 0.85, 0.70, 0.60],
    [0.55, 0.55, 0.60, 0.60, 0.75],
    [0.50, 0.60, 0.65, 0.70, 0.55],
    [0.95, 1.00, 0.70, 0.30, 1.00],
]
W = (0.30, -0.30, 0.20, 0.10, -0.10)  # 收益/风险/流动性/易得性/复杂度

# ---- 计算与作图 ----
scored = []
for name, row in zip(PRODUCTS, M):
    s = sum(w * x for w, x in zip(W, row))
    scored.append((s, name))
scored.sort(reverse=True)

heatmap(FIG / "03-product-map.svg", M, PRODUCTS, DIMS,
        title="八类可交易产品的属性矩阵（0~1，教学打分）", vmin=0.0, vmax=1.0)
print("热力图:", str(FIG / "03-product-map.svg"))
c = Chart(FIG / "03-ranking.svg", "按「收益−风险+流动性−复杂度」的教学建议顺序",
          xlabel="产品", ylabel="综合得分",
          xticks=[(i, n) for i, (_s, n) in enumerate(scored)])
c.bars(range(len(PRODUCTS)), [s for s, _ in scored], BLUE, label="综合得分")
c.hline(0.0, "#9aa6b2")
print("排序图:", c.save())
print("建议顺序: " + " > ".join(n for _s, n in scored))
print("最高=%.3f 最低=%.3f | 打分仅用于演示「先定维度再排序」的方法" %
      (scored[0][0], scored[-1][0]))
