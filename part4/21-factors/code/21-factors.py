#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用已知真值的合成数据生成个股收益，估计 CAPM 与 FF3，比较 alpha。

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
N = 600
TRUE_ALPHA = 0.0002
TRUE_B = (0.90, 0.30, -0.20)   # MKT / SMB / HML 的真实暴露
NOISE = 0.006
ANN = 252                       # 年化天数

# ---- 计算与作图 ----
rng = random.Random(7)
mkt = [rng.gauss(0.0003, 0.010) for _ in range(N)]
smb = [rng.gauss(0.0001, 0.005) for _ in range(N)]
hml = [rng.gauss(0.0001, 0.006) for _ in range(N)]
rets = [TRUE_ALPHA + TRUE_B[0] * mkt[i] + TRUE_B[1] * smb[i]
        + TRUE_B[2] * hml[i] + rng.gauss(0, NOISE) for i in range(N)]

def inv(A):
    k = len(A)
    M = [row[:] + [1.0 if i == j else 0.0 for j in range(k)]
         for i, row in enumerate(A)]
    for col in range(k):
        piv = max(range(col, k), key=lambda r: abs(M[r][col]))
        M[col], M[piv] = M[piv], M[col]
        d = M[col][col]
        M[col] = [v / d for v in M[col]]
        for r in range(k):
            if r != col:
                f = M[r][col]
                M[r] = [M[r][j] - f * M[col][j] for j in range(2 * k)]
    return [row[k:] for row in M]

def ols(X, y):
    n, k = len(y), len(X[0])
    xtx = [[sum(X[t][i] * X[t][j] for t in range(n)) for j in range(k)]
           for i in range(k)]
    xty = [sum(X[t][i] * y[t] for t in range(n)) for i in range(k)]
    inv_xtx = inv(xtx)
    coef = [sum(inv_xtx[i][j] * xty[j] for j in range(k)) for i in range(k)]
    resid = [y[t] - sum(coef[i] * X[t][i] for i in range(k)) for t in range(n)]
    s2 = sum(e * e for e in resid) / (n - k)
    se = [math.sqrt(s2 * inv_xtx[i][i]) for i in range(k)]
    ybar = statistics.fmean(y)
    r2 = 1 - sum(e * e for e in resid) / sum((v - ybar) ** 2 for v in y)
    return coef, [coef[i] / se[i] for i in range(k)], r2, resid

X1 = [[1.0, mkt[i]] for i in range(N)]
X3 = [[1.0, mkt[i], smb[i], hml[i]] for i in range(N)]
c1, t1, r21, _e1 = ols(X1, rets)
c3, t3, r23, e3 = ols(X3, rets)

def cum(series):
    v, out = 0.0, []
    for x in series:
        v += x
        out.append(v)
    return out

c = Chart(FIG / "21-factors.svg", "三个合成因子的累计收益", xlabel="交易日", ylabel="累计收益")
c.line(range(N), cum(mkt), BLUE, label="MKT")
c.line(range(N), cum(smb), GREEN, label="SMB")
c.line(range(N), cum(hml), AMBER, label="HML")
print("因子图:", c.save())
a = Chart(FIG / "21-alpha.svg", "FF3 残差累计（alpha 的稳定性）", xlabel="交易日", ylabel="累计残差")
a.line(range(N), cum(e3), RED, label="残差")
a.hline(0.0, "#9aa6b2")
print("残差图:", a.save())
print("真值 α=%.5f β=(%.2f,%.2f,%.2f) | CAPM α=%.5f β=%.3f R²=%.3f" %
      (TRUE_ALPHA, *TRUE_B, c1[0], c1[1], r21))
print("FF3 α=%.5f(t=%.2f) β=(%.3f,%.3f,%.3f) t=(%.1f,%.1f,%.1f) R²=%.3f | 年化 α=%.2f%%" %
      (c3[0], t3[0], c3[1], c3[2], c3[3], t3[1], t3[2], t3[3], r23, 100 * ANN * c3[0]))
