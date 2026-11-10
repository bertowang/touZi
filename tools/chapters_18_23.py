#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 18～23 章：指标、形态、画图工程，以及因子与行为证据。"""
from __future__ import annotations

from book_schema import C, eq, table
from chapter_kit import mk_demo, p, ul, note, warn, sec

CH = [

# ==================================================================== 18
C("18", "p3", "part3/18-indicators", "MACD、RSI、布林带与 KDJ 的数学定义",
  "每个指标都是价格序列上的一个确定性变换；先写公式，再谈用法。",
  hours="3 学时",
  goals=["能写出 MACD、RSI、布林带、KDJ 的计算式与初始化方式。",
         "能说明指标的参数、滞后与自相关来源。",
         "能识别指标共用同一价格序列导致的信号相关性。",
         "能用标准库实现四个指标并核对数值。"],
  points=["EMA 与 MACD", "DIF / DEA / 柱状图", "RSI 与 Wilder 平滑", "布林带与 %B",
          "KDJ 与 RSV", "指标滞后", "参数与自相关", "指标不是独立证据"],
  sections=[
      ("18.1", "MACD：两条 EMA 之差", sec(
          eq("DIF = EMA_12(P) − EMA_26(P)　|　DEA = EMA_9(DIF)　|　MACD 柱 = 2 × (DIF − DEA)"),
          p("MACD 是<strong>趋势的二阶差分</strong>：DIF 衡量快慢均线距离，DEA 再平滑一次，"
            "柱状图是两者之差。它继承了均线的滞后，柱的符号变化比金叉更早，但假信号也更多。"
            "初始化方式（前 n 期用 SMA 还是首值递推）会造成数值差异，"
            "对照交易 App 时必须<strong>先对齐初始化口径</strong>。"))),
      ("18.2", "RSI、布林带与 KDJ", sec(
          eq("RSI = 100 − 100/(1 + RS)　，RS = 平均涨幅 / 平均跌幅（Wilder 平滑）"),
          eq("布林: 上/下轨 = SMA_20 ± 2σ_20　|　%B = (P − 下轨)/(上轨 − 下轨)"),
          eq("RSV = (C − L_n)/(H_n − L_n) × 100　，K = (2/3)K' + (1/3)RSV"),
          table(["指标", "回答的问题", "隐含假设", "典型失效"], [
              ["MACD", "趋势动量是增强还是衰减", "趋势有延续性", "震荡市反复交叉"],
              ["RSI", "涨跌幅度是否失衡", "均值回复", "单边趋势中长期超买"],
              ["布林带", "波动是否异常扩张/收缩", "波动有聚集性", "突破后波动状态切换"],
              ["KDJ", "收盘价在近期区间的位置", "区间震荡", "强趋势中高位钝化"],
          ], ["14%", "30%", "26%", "30%"]),
          p("四个指标都是<strong>同一条价格序列的函数</strong>，因此它们高度相关，"
            "「三指标共振」不是三个独立证据，而是同一份信息被数了三遍。"))),
      ("18.3", "从指标到证据还差什么", sec(
          p("指标给出的是<strong>描述统计量</strong>，不是收益预测。要变成策略，至少还需要："
            "明确的信号定义、无未来函数的执行时点、成本、样本外检验与多重检验修正。"
            "第 20 章先解决未来函数，第 26～28 章补齐回测与统计检验。"))),
  ],
  demos=[mk_demo(
      "code/18-indicators.py", "实验 18-1 · 四个指标的手写实现与共振检查",
      "用标准库计算 MACD、RSI、布林带、KDJ，并统计超买超卖与交叉次数。",
      """N = 180
START = 50.0
DRIFT, VOL = 0.0008, 0.012
FAST, SLOW, SIGNAL = 12, 26, 9
RSI_N, BOLL_N, KDJ_N = 14, 20, 9""",
      """rng = random.Random(7)
px, prices = START, []
for _ in range(N):
    px *= (1 + rng.gauss(DRIFT, VOL))
    prices.append(px)

def ema(series, w):
    a, out, prev = 2.0 / (w + 1), [], series[0]
    for v in series:
        prev = a * v + (1 - a) * prev
        out.append(prev)
    return out

dif = [a - b for a, b in zip(ema(prices, FAST), ema(prices, SLOW))]
dea = ema(dif, SIGNAL)
hist = [2 * (a - b) for a, b in zip(dif, dea)]
changes = [prices[i] - prices[i - 1] for i in range(1, N)]
gains = [max(c, 0.0) for c in changes]
losses = [max(-c, 0.0) for c in changes]
ag, al = statistics.fmean(gains[:RSI_N]), statistics.fmean(losses[:RSI_N])
rsi = [None] * N
for i in range(RSI_N, N):
    ag = (ag * (RSI_N - 1) + gains[i - 1]) / RSI_N
    al = (al * (RSI_N - 1) + losses[i - 1]) / RSI_N
    rsi[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)

upper, lower, pct_b = [None] * N, [None] * N, [None] * N
for i in range(BOLL_N - 1, N):
    win = prices[i + 1 - BOLL_N:i + 1]
    m, s = statistics.fmean(win), statistics.pstdev(win)
    upper[i], lower[i] = m + 2 * s, m - 2 * s
    pct_b[i] = (prices[i] - lower[i]) / (upper[i] - lower[i]) if upper[i] > lower[i] else 0.5

k, d, j = [None] * N, [None] * N, [None] * N
kp, dp = 50.0, 50.0
for i in range(KDJ_N - 1, N):
    win = prices[i + 1 - KDJ_N:i + 1]
    hi, lo = max(win), min(win)
    rsv = 100 * (prices[i] - lo) / (hi - lo) if hi > lo else 50.0
    kp, dp = (2 * kp + rsv) / 3, (2 * dp + kp) / 3
    k[i], d[i], j[i] = kp, dp, 3 * kp - 2 * dp

def clean(series):
    xs = [i for i, v in enumerate(series) if v is not None]
    return xs, [series[i] for i in xs]

xu, yu = clean(upper); xl, yl = clean(lower)
c = Chart(FIG / "18-indicators.svg", "布林带与价格（%B 提示价格在通道中的位置）",
          xlabel="交易日", ylabel="价格")
c.line(range(N), prices, BLUE, label="收盘价")
c.line(xu, yu, RED, label="上轨 SMA+2σ", dash="5 4")
c.line(xl, yl, GREEN, label="下轨 SMA−2σ", dash="5 4")
print("布林图:", c.save())
m = Chart(FIG / "18-macd.svg", "MACD：DIF / DEA / 柱状能量", xlabel="交易日", ylabel="数值")
m.bars(range(N), hist, "#9aa6b2", label="MACD 柱")
m.line(range(N), dif, BLUE, label="DIF")
m.line(range(N), dea, AMBER, label="DEA")
m.hline(0.0, "#8a909b")
print("MACD 图:", m.save())

cross = sum(1 for i in range(1, N) if (hist[i - 1] <= 0 < hist[i]) or (hist[i - 1] >= 0 > hist[i]))
over = sum(1 for v in rsi if v is not None and v > 70)
under = sum(1 for v in rsi if v is not None and v < 30)
print("RSI=%.2f K=%.2f D=%.2f J=%.2f %%B=%.3f | RSI>70 共%d 天 <30 共%d 天 柱变号%d 次" %
      (rsi[-1], k[-1], d[-1], j[-1], pct_b[-1], over, under, cross))""",
      [("fig/18-indicators.svg", "布林带上下轨与收盘价"),
       ("fig/18-macd.svg", "DIF、DEA 与 MACD 柱状能量")],
      "把 <code>RSI_N</code> 从 14 改成 5，观察超买超卖天数；注意所有指标都来自同一条 <code>prices</code>。",
      "四个指标都是价格序列的确定性变换，彼此高度相关。参数一变信号计数就变，"
      "所以「共振」必须先声明参数并做样本外检验。",
      "把 <code>DRIFT</code> 提高，观察 RSI 在单边趋势里长期停留在超买区（指标钝化）。")],
  highlights=[("macd", "双指数均线差与柱状能量的定义"),
              ("rsi", "相对强弱指标的原始公式"),
              ("bollinger", "均值 ± k 倍标准差通道"),
              ("ta-lib", "工业实现，用来核对手写公式的初始化口径")],
  analogy="指标是有状态的流式算子：<code>ema</code> 是递归滤波，<code>RSI</code> 是带衰减的涨跌比，"
          "布林带是滑动窗口的 z-score。<strong>它们共享同一个输入流，因此不是独立投票。</strong>",
  bridge="第 17 章的单条均线在这里扩展成指标族；{{ch:19}} 把多根 K 线组合写成形态判定，"
         "{{ch:20}} 则检查这些计算有没有偷看未来。",
  pitfalls=["指标初始化口径不同，导致与 App 显示值不一致。",
            "把 RSI 超买直接当卖出信号，忽略趋势市中的钝化。",
            "把三个相关指标当成三份独立证据。",
            "用未来数据计算「当前」的滚动分位数。"],
  exercises=["推导 EMA 的等效窗口长度，与同长度 SMA 比较滞后。",
             "在示例里统计 RSI 与 %B 同日向超买/超卖方向变动的比例，验证相关性。",
             "把四个指标的信号做或运算，说明为什么这不是四次独立试验。"],
  further=["{{ch:20}} 未来函数与画图陷阱；{{ch:28}} 参数扫描与过拟合。"]),

# ==================================================================== 19
C("19", "p3", "part3/19-patterns", "形态识别：从主观描述到可判定规则",
  "「双底」不是一个图形，而是一组带容差、带参数的不等式；写下它们才谈得上检验。",
  hours="3 学时",
  goals=["能把头肩、双底、三角、缺口写成可判定条件。",
         "能识别形态定义里隐含的自由参数。",
         "能计算形态后的前向收益并与无条件基准比较。",
         "能解释「看图很准」为何常来自选择性记忆。"],
  points=["头肩顶与颈线", "双底与双顶", "三角形与突破", "缺口与回补",
          "局部极值判定", "容差与自由参数", "前向收益检验", "选择性记忆"],
  sections=[
      ("19.1", "把形态翻译成谓词", sec(
          p("形态识别的第一步不是找图，而是写 "
            "<code>is_double_bottom(prices, params) -&gt; bool</code>：存在两个局部低点 "
            "<code>i &lt; j</code>，间隔在给定区间内，两底价格相差小于容差，"
            "且中间存在一个明显高于低点的高点（颈线）。"),
          table(["要素", "自由参数", "参数变大时"], [
              ["局部低点", "左右窗口 w", "信号变少、更「显著」"],
              ["两底相近", "价格容差 ε", "信号变多、更宽松"],
              ["间隔合理", "最小/最大间隔", "决定形态的时间尺度"],
              ["中间有颈线", "颈线高度阈值", "决定形态是否「像」"],
              ["确认突破", "突破幅度与量能", "更晚确认、更少假信号"],
          ], ["24%", "32%", "44%"]),
          warn("关键", "五个参数全是人定的。只要允许事后调整，任何一段历史行情里都能找到「完美形态」——"
               "这就是第 28 章要处理的数据挖掘问题。"))),
      ("19.2", "形态必须配一个可证伪的命题", sec(
          eq("H0: E[r_前向 | 形态出现] = E[r_前向]"),
          p("只有把「形态有用」写成关于<strong>前向收益</strong>的命题，才能用样本外数据、"
            "成本扣除与显著性检验去否定它。只看图形画得多标准，不构成证据。"))),
  ],
  demos=[mk_demo(
      "code/19-pattern.py", "实验 19-1 · 双底的机器判定与前向收益对照",
      "把双底写成不等式，自动扫描合成序列，比较形态后收益与无条件基准。",
      """N = 240
START, DRIFT, VOL = 50.0, 0.0003, 0.014
W, TOL = 3, 0.02        # 局部极值半窗口、两底价格容差
MIN_GAP, MAX_GAP = 8, 45
NECK, FWD = 0.03, 10    # 颈线幅度、前向收益天数""",
      """rng = random.Random(7)
px, prices = START, []
for _ in range(N):
    px *= (1 + rng.gauss(DRIFT, VOL))
    prices.append(px)

lows = [i for i in range(W, N - W)
        if prices[i] == min(prices[i - W:i + W + 1])]
signals, marks = [], []
for a, i in enumerate(lows):
    for j in lows[a + 1:]:
        gap = j - i
        if not (MIN_GAP <= gap <= MAX_GAP):
            break
        p1, p2 = prices[i], prices[j]
        if abs(p1 - p2) / p1 > TOL:
            continue
        peak = max(prices[i:j + 1])
        if peak / min(p1, p2) - 1 < NECK:
            continue
        if j + FWD < N:
            signals.append((j, prices[j + FWD] / prices[j] - 1))
            marks.append((i, j))
            break

rets = [prices[t + FWD] / prices[t] - 1 for t in range(N - FWD)]
base = statistics.fmean(rets)
hit = statistics.fmean(r for _j, r in signals) if signals else 0.0
win = statistics.fmean(1.0 if r > 0 else 0.0 for _j, r in signals) if signals else 0.0

c = Chart(FIG / "19-pattern.svg", "机器判定的双底信号（标记第二个底）", xlabel="交易日", ylabel="价格")
c.line(range(N), prices, BLUE, label="合成收盘价")
c.scatter([j for _i, j in marks], [prices[j] for _i, j in marks], RED,
          label="双底确认点", radius=5)
print("形态图:", c.save())
b = Chart(FIG / "19-forward.svg", "形态后 10 日收益 vs 无条件基准", xlabel="口径", ylabel="平均收益 %",
          xticks=[(0, "形态后"), (1, "全样本")])
b.bars([0, 1], [100 * hit, 100 * base], GREEN, label="平均 10 日收益")
b.hline(0.0, "#9aa6b2")
print("收益图:", b.save())
print("局部低点=%d 双底信号=%d | 形态后均值=%.3f%% 基准=%.3f%% 胜率=%.1f%%" %
      (len(lows), len(signals), 100 * hit, 100 * base, 100 * win))""",
      [("fig/19-pattern.svg", "按不等式自动识别出的双底确认点"),
       ("fig/19-forward.svg", "形态后收益与无条件平均收益的对照")],
      "把 <code>TOL</code> 从 0.02 放宽到 0.08，观察信号数量与形态后收益如何变化。",
      "本例的价格是<strong>纯随机游走</strong>，不含任何形态效应，所以形态后收益与基准的差异只是抽样噪声"
      "（本例恰好偏高，换一个种子就可能偏低）。但放宽容差后总能找到更多「标准双底」——"
      "这就是选择性记忆的算法版本。",
      "把 <code>NECK</code> 调到 0.01，形态变松、信号变多，说明结论对参数极敏感。")],
  highlights=[("chart-pattern", "常见形态的流派与争议"),
              ("support", "成交密集区与自我实现价位"),
              ("technical-analysis", "价量研究的假设与检验现状"),
              ("emh", "价格是否已反映图形信息")],
  analogy="形态识别是一段带超参的模式匹配；<code>TOL</code>、<code>W</code>、<code>NECK</code> "
          "是它的正则项。<strong>在纯噪声上也能匹配出一堆「信号」</strong>，"
          "所以必须配一个独立的前向收益检验。",
  bridge="第 18 章是单根 K 线的变换，本章是多根 K 线的组合规则；"
         "{{ch:20}} 检查这类规则是否偷看了未来数据。",
  pitfalls=["事后在图上画颈线，把任意两个低点解释成双底。",
            "只展示成功的形态样本，不报告全部信号的前向收益。",
            "把「形态确认」画在最低点当天，而实际只能在其后才判定。",
            "忽略突破失败的样本与交易成本。"],
  exercises=["给示例补上「突破颈线才确认」的条件，比较信号数量。",
             "把 <code>FWD</code> 改成 1、10、30，观察结论是否稳定。",
             "设计一个能自动统计「头肩顶」的谓词，并列出它比双底多几个自由参数。"],
  further=["{{ch:20}} 未来函数；{{ch:24}} 读论文时的样本外意识；{{ch:28}} 多重检验。"]),

# ==================================================================== 20
C("20", "p3", "part3/20-chart-pipeline", "用代码画图：SVG 图与看图陷阱",
  "把「一张图」变成可复现的产物，同时堵住最常见的数据泄漏。",
  hours="3 学时",
  goals=["能用纯标准库生成可提交、可离线查看的 SVG 图表。",
         "能识别并复现未来函数（look-ahead bias）造成的虚假超额收益。",
         "能说明全样本统计量与滚动统计量的差别。",
         "能把坐标、复权、周期三项设置写进实验记录。"],
  points=["SVG 与文本矢量图", "零依赖绘图", "图层与坐标", "全样本均值泄漏",
          "滚动窗口与因果性", "信号与下一根成交", "未来函数", "可复现的实验记录"],
  sections=[
      ("20.1", "为什么用 SVG 而不是截图", sec(
          p("本书所有插图由 <code>tools/chart.py</code> 生成：输出是<strong>文本 SVG</strong>，"
            "不弹窗、不依赖 GUI、不需要第三方包，能进 Git、能 diff、能在浏览器里缩放不失真。"
            "对教材而言，图与代码同源意味着<strong>改一个参数就能重画一遍</strong>，"
            "而不是留下一张无法复核的截图。"),
          ul(["<strong>数据层</strong>：合成行情 → 计算指标 → 得到数值结论（打印）。",
              "<strong>图层</strong>：折线 / 柱 / 散点 / 参考线 / 图例统一渲染。",
              "<strong>校验层</strong>：XML 解析检查 SVG 合法、脚本批量运行检查数值。",
              "<strong>文档层</strong>：参数区、随机种子、生成命令都写在页面上。"]),
      )),
      ("20.2", "未来函数：最容易被忽略的 bug", sec(
          p("一段看起来无害的归一化，就足以毁掉回测："),
          eq("错误: z_t = (P_t − mean(P_1 … P_T)) / std(P_1 … P_T)　← 用到了 T 时刻才知道的量"),
          eq("正确: z_t = (P_t − mean(P_(t−w+1) … P_t)) / std(P_(t−w+1) … P_t)"),
          p("全样本均值、全样本分位数、全样本最大值、以及「在最低点画买入箭头」都属于同一类错误："
            "<strong>把未来信息编码进了 t 时刻的特征</strong>。真实交易中你只有 <code>prices[:t+1]</code>。"),
      )),
      ("20.3", "三道防线", sec(
          table(["防线", "做法", "检查方式"], [
              ["时间切分", "特征只用 <code>prices[:t+1]</code>", "把 t 之后的数据全删掉，结论应不变"],
              ["执行延迟", "t 时刻信号在 t+1 成交", "统计信号与成交的时间戳差"],
              ["样本外隔离", "调参与评估用不同数据段", "比较样本内/外夏普（第 28 章）"],
          ], ["22%", "44%", "34%"]),
          note("工程习惯", "把「数据可用时刻」作为每个字段的元数据。任何特征函数签名写成 "
               "<code>f(history_up_to_t)</code>，就能从类型上阻止大部分未来函数。"),
      )),
  ],
  demos=[mk_demo(
      "code/20-lookahead.py", "实验 20-1 · 全样本均值泄漏如何制造虚假超额收益",
      "对比「全样本均值」与「滚动均值」两种信号，统一在下一根成交，量化差距。",
      """N = 240
START, DRIFT, VOL = 50.0, 0.0006, 0.014
W = 20             # 合法滚动窗口
FEE = 0.0005       # 换仓成本""",
      """rng = random.Random(7)
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
      (bad_px[-1], ok_px[-1], buy_px[-1], bad_trades, ok_trades, full_mean))""",
      [("fig/20-lookahead.svg", "含未来函数的策略与合法策略的净值差距"),
       ("fig/20-mean.svg", "全样本均值与滚动均值的因果性差异")],
      "先跑一遍记录三条终值；再把 <code>DRIFT</code> 改成 0，观察「未来函数优势」是否依然显著。",
      "全样本均值把<strong>整段行情的中心位置</strong>提前告诉了策略，"
      "所以非法信号的净值明显高于合法的滚动信号（本例约 1.23 对 1.03），差距来自信息泄漏而非技能。"
      "注意它仍可能低于「始终持有」：择时本身不必然占优，这正说明回测必须同时给多个基准。"
      "合法信号只能用 <code>prices[:t+1]</code>。",
      "把 <code>W</code> 从 20 调到 60，合法策略的信号变少、更平滑，但绝不会因此获得未来信息。")],
  highlights=[("mdn-svg", "本书自绘图表所用矢量格式参考"),
              ("lookahead", "前视偏差的定义与常见来源"),
              ("matplotlib", "成熟绘图库，可与本书 SVG 自绘方案对照"),
              ("python-docs", "标准库文档，脚本语言与工具链的权威参考")],
  analogy="未来函数就是<strong>训练集里混进了测试集标签</strong>。"
          "<code>f(history_up_to_t)</code> 是类型级约束，"
          "t+1 成交是时间级约束，样本外切分是评估级约束——三层都得有。",
  bridge="第三阶段以「如何可靠地画图与看图」收尾；"
         "{{ch:21}} 起进入第四阶段，把「规律」升级为可检验的因子假设。",
  pitfalls=["用全样本均值/分位数/最大值做归一化或阈值。",
            "在信号产生的同一根 K 线收盘价成交。",
            "把「事后标出的最低点」写进策略条件。",
            "图上标注了参数却没写数据复权与坐标设置，换设备无法复现。"],
  exercises=["列举三种「看起来无害」的全样本统计量，并说明如何改成滚动版本。",
             "在示例里加入 t+2 成交，观察合法策略与未来函数策略的差距变化。",
             "给 SVG 生成脚本补一个 XML 解析校验，说明它能挡住哪类错误。"],
  further=["{{ch:26}} 回测引擎的时间链；{{ch:28}} 样本外与多重检验；{{ch:25}} point-in-time 数据。"]),

# ==================================================================== 21
C("21", "p4", "part4/21-factors", "因子、CAPM 与 Fama-French",
  "把「为什么这只股票涨得多」拆成可估计的暴露与不可解释的残差。",
  hours="3 学时",
  goals=["能写出 CAPM 与 Fama-French 三因子回归式。",
         "能用手写 OLS 估计 beta、alpha 与 t 值。",
         "能解释遗漏变量如何把因子收益错记成 alpha。",
         "能说明因子溢价、数据挖掘与交易成本三者之间的关系。"],
  points=["CAPM 与 beta", "市场因子", "规模与价值因子 SMB/HML", "三因子回归",
          "alpha 与 t 值", "R² 与残差", "遗漏变量偏差", "因子与 Smart Beta"],
  sections=[
      ("21.1", "收益的线性分解", sec(
          eq("r_i − r_f = α_i + β_m MKT + β_s SMB + β_h HML + ε_i"),
          p("α 是<strong>模型无法解释的平均残差</strong>，β 是对共同因子的暴露。"
            "第 13 章末尾留下的问题「分散不掉的那部分风险」在这里有了名字：市场因子。"
            "SMB（小市值减大市值）与 HML（高账面市值比减低）是后续加入的横截面维度。"),
          table(["模型", "解释变量", "α 的含义", "主要风险"], [
              ["CAPM", "MKT", "相对市场的超额收益", "遗漏其他系统性因子"],
              ["FF3", "MKT + SMB + HML", "相对三因子的残差均值", "样本期与构造口径依赖"],
              ["FF5 / 动量", "再加 RMW/CMA/UMD", "更严格的残差", "因子越来越多，过拟合风险上升"],
          ], ["18%", "30%", "28%", "24%"]),
      )),
      ("21.2", "alpha 是最容易被偷换的概念", sec(
          p("若真实收益由三因子生成，却只用 CAPM 回归，β_s、β_h 的贡献会被挤进 α，"
            "于是「选股能力」其实是<strong>规模/价值暴露</strong>。"
            "这在工程上就是遗漏变量偏差：模型少了一列，系数就会去吸收它的影响。"
            "评估基金时，先问「对什么基准、加了哪些因子」。"),
      )),
      ("21.3", "从因子到可交易策略还差四步", sec(
          ul(["因子必须在<strong>样本外</strong>与不同市场重复出现（第 24、28 章）。",
              "构建组合要处理停牌、退市与成分股历史（第 25 章）。",
              "换手、冲击与税费会吞掉大部分毛溢价（第 26、29 章）。",
              "拥挤与结构性变化会让历史上有效的因子失效（第 23 章）。"]),
      )),
  ],
  demos=[mk_demo(
      "code/21-factors.py", "实验 21-1 · 手写 OLS 估计三因子模型与遗漏变量偏差",
      "用已知真值的合成数据生成个股收益，估计 CAPM 与 FF3，比较 alpha。",
      """N = 600
TRUE_ALPHA = 0.0002
TRUE_B = (0.90, 0.30, -0.20)   # MKT / SMB / HML 的真实暴露
NOISE = 0.006
ANN = 252                       # 年化天数""",
      """rng = random.Random(7)
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
      (c3[0], t3[0], c3[1], c3[2], c3[3], t3[1], t3[2], t3[3], r23, 100 * ANN * c3[0]))""",
      [("fig/21-factors.svg", "三个合成因子的累计收益路径"),
       ("fig/21-alpha.svg", "三因子模型残差的累计轨迹")],
      "把 <code>TRUE_B[1]</code> 设为 0，观察 CAPM 与 FF3 的 alpha 是否趋于一致；"
      "再把它调大，看遗漏变量如何被错记成选股能力。",
      "FF3 的估计 β 应接近真值，α 的 t 值通常不显著；而 CAPM 的 α 会吸收 SMB/HML 的贡献。"
      "这说明<strong>「超额收益」永远依赖于你声明了哪些因子</strong>。",
      "把 <code>N</code> 改成 60，t 值会明显变小——小样本下几乎无法区分 α 与噪声。")],
  highlights=[("fama-french", "三因子模型的标准表述"),
              ("french", "Ken French Data Library 的原始因子序列"),
              ("smart-beta", "规则化因子指数与对应 ETF"),
              ("spiva", "主动基金相对基准的长期统计")],
  analogy="因子回归是一次多元线性回归：<code>X</code> 是因子暴露矩阵，<code>α</code> 是截距，"
          "<code>t 值</code> 是信噪比。漏掉一列特征，截距就会替它背锅。",
  bridge="第四阶段从「可验证的收益分解」开始；{{ch:22}} 讨论模型之外的人，"
         "{{ch:23}} 讨论资金拥挤，{{ch:24}} 讨论怎样读一篇因子论文。",
  pitfalls=["把 CAPM alpha 当成选股能力。",
            "用同一段数据既挑因子又评估显著性。",
            "忽略因子构建口径（市值加权、分组断点、换仓频率）。",
            "把因子 ETF 的历史回测当成因子溢价的未来承诺。"],
  exercises=["推导遗漏变量偏差公式，说明 α 的偏移方向由 β 与因子均值决定。",
             "在示例中加入第四个与 MKT 高度相关的因子，观察 t 值如何下降（共线性）。",
             "查一份指数编制方案，列出至少三个会影响因子暴露的实现细节。"],
  further=["{{ch:24}} 论文复现清单；{{ch:27}} 信息比率与归因；{{ch:28}} 多重检验。"]),

# ==================================================================== 22
C("22", "p4", "part4/22-behavior", "有效市场、行为偏差与处置效应",
  "价格不一定「正确」，但想稳定套利，你得先证明错误是可重复、可执行的。",
  hours="3 学时",
  goals=["能说明有效市场三种形式与对应的可检验命题。",
         "能解释损失厌恶、参照点、锚定与羊群效应。",
         "能用 PGR/PLR 度量处置效应并复现它。",
         "能区分「市场不理性」与「存在可交易的错误定价」。"],
  points=["有效市场假说", "弱式/半强式/强式检验", "前景理论与损失厌恶", "参照点与锚定",
          "处置效应与 PGR/PLR", "羊群与反馈环", "套利限制", "偏差不等于策略"],
  sections=[
      ("22.1", "有效市场是一个可证伪的基准", sec(
          table(["形式", "信息集", "若成立则", "常见检验"], [
              ["弱式", "历史价量", "技术指标无法持续获得超额收益", "序列相关、游程、事件前后收益"],
              ["半强式", "全部公开信息", "财报/新闻公布后无持续漂移（除漂移本身争议）", "事件研究"],
              ["强式", "含内幕信息", "任何信息都无法持续套利", "内幕交易监管与执法数据"],
          ], ["14%", "22%", "32%", "32%"]),
          p("有效市场不是说价格永远等于价值，而是说<strong>扣除成本与风险后，公开信息难以被稳定套利</strong>。"
            "它是 H0，不是信仰：任何「我找到了规律」的主张都要先跨过成本、样本外与多重检验三道门槛。"),
      )),
      ("22.2", "前景理论：效用定义在变化上，而不是财富上", sec(
          eq("U(ΔW) 在亏损区更陡（损失厌恶），且价值函数对收益凹、对损失凸"),
          p("这解释了两个常见现象：<strong>处置效应</strong>（过早卖出盈利、过久持有亏损）与"
            "<strong>锚定</strong>（把买入价、历史高点当参照点）。"
            "第 17 章说的「支撑阻力」，在行为层面可以理解为大量持仓共用同一个参照点。"),
      )),
      ("22.3", "套利限制：为什么错误定价可以长期存在", sec(
          ul(["<strong>基本面风险</strong>：价格可能在收敛前继续远离价值。",
              "<strong>噪声交易者风险</strong>：其他人非理性使短期亏损扩大。",
              "<strong>实施成本</strong>：借券、保证金、流动性、期限与赎回压力。",
              "<strong>同步性</strong>：大家同时平仓时，相关性趋近 1（第 23 章）。"]),
          note("结论", "「别人错了」不等于「你能赚到」。可交易性是一个工程约束，"
               "不是一个观点。"),
      )),
  ],
  demos=[mk_demo(
      "code/22-disposition.py", "实验 22-1 · 处置效应的可测量版本（PGR / PLR）",
      "模拟带损失厌恶的卖出概率，计算实现盈利比例与实现亏损比例。",
      """N_DAYS, N_POS = 250, 1200
START, DRIFT, VOL = 50.0, 0.0004, 0.012
BASE_SELL = 0.03     # 基准卖出概率
GAIN_EXTRA = 0.12    # 盈利时的额外卖出倾向
STEEP = 60.0         # 概率函数陡峭程度""",
      """def sell_prob(pnl):
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
       statistics.fmean(lose_days) if lose_days else 0))""",
      [("fig/22-disposition.svg", "卖出概率随未实现盈亏上升的行为假设"),
       ("fig/22-pgr.svg", "实现盈利比例 PGR 与实现亏损比例 PLR")],
      "把 <code>GAIN_EXTRA</code> 设为 0（无偏差），PGR 与 PLR 应接近；再调大观察差值。",
      "当卖出概率随浮盈上升时，PGR 显著大于 PLR，且盈利持仓的平均持有期更短——"
      "这正是「拔掉鲜花、浇灌野草」的量化形式。此处偏差是<strong>人为注入的</strong>，"
      "真实市场需用账户数据检验。",
      "把 <code>DRIFT</code> 改成负数，观察整体浮盈变少后 PGR/PLR 的绝对水平如何变化。")],
  highlights=[("emh", "有效市场假说的三种形式与检验"),
              ("prospect", "前景理论与参照点依赖"),
              ("disposition", "处置效应的经典度量"),
              ("behavioral", "行为金融的偏差清单")],
  analogy="行为偏差是决策函数里的一个<strong>系统性偏置项</strong>："
          "<code>sell_prob = f(pnl, reference_point)</code> 而非 <code>f(期望收益)</code>。"
          "只要偏置稳定可测，就能写进模型；但它是否带来可交易的错误定价，是另一个问题。",
  bridge="第 21 章给出「理性基准下的收益分解」，本章补上系统性偏离；"
         "{{ch:23}} 讨论许多人同时偏离时会发生什么。",
  pitfalls=["把「市场不理性」直接推导成「我能赚钱」。",
            "用单一偏差解释所有价格现象。",
            "忽略套利限制与资金期限。",
            "把处置效应归因于税收或再平衡而不做对照。"],
  exercises=["推导 PGR/PLR 的定义，并说明为什么要用「比例」而非「次数」。",
             "在示例里加入一个理性对照组（sell_prob 为常数），比较两者 PGR−PLR。",
             "列举一个「看似行为偏差、其实是制度约束」的例子。"],
  further=["{{ch:23}} 拥挤与反转；{{ch:24}} 从论文里识别偏差类主张；{{ch:31}} 用决策日志约束自己。"]),

# ==================================================================== 23
C("23", "p4", "part4/23-flow-crowding", "资金流、情绪与拥挤交易",
  "当很多人用同一套信号时，因子暴露会变成流动性风险。",
  hours="3 学时",
  goals=["能定义资金流、拥挤度与情绪代理变量。",
         "能计算拥挤度分组后的前向收益并做对照。",
         "能解释「好策略被挤坏」的机制：同步性、冲击与反转。",
         "能说明另类数据的口径与可复现性问题。"],
  points=["资金流与净申购", "换手率与拥挤度", "情绪代理变量", "分箱与前向收益",
          "同步性与相关性上升", "反转效应", "另类数据", "容量与衰减"],
  sections=[
      ("23.1", "资金流是有口径的量", sec(
          p("「主力资金流入」在不同终端可能有完全不同的定义：按成交单笔金额分档、按主动买卖方向、"
            "或按基金净申购。三者不是同一个量，且都<strong>不对应真实的钱进入市场</strong>——"
            "每一笔买必有对应的卖。使用前必须写下：数据源、聚合窗口、方向判定规则、是否含 ETF 申赎。"),
          table(["代理变量", "可得性", "主要偏差"], [
              ["基金净申购 / 份额变化", "低（定期披露）", "滞后、无法区分申赎动机"],
              ["大单净额", "高（逐笔）", "拆单、冰山单、主动方向标记口径"],
              ["换手率 / 成交额分位", "高", "同时受波动与指数调样影响"],
              ["搜索量 / 舆情", "中", "样本选择、平台用户偏差、不可复现"],
          ], ["28%", "20%", "52%"]),
      )),
      ("23.2", "拥挤如何把收益变成风险", sec(
          eq("拥挤度高 → 持仓重叠 ↑ → 同时减仓时相关性 ↑ → 冲击成本 ↑ → 反转概率 ↑"),
          p("一个因子在少数人使用时是溢价，在所有人使用时就变成<strong>共同的退出通道</strong>。"
            "第 21 章的因子暴露是横截面的，这一章补上时间维度：暴露的<strong>密度</strong>。"
            "这也是为什么策略评估必须报告容量与换手，而不只报夏普。"),
      )),
      ("23.3", "检验方式：分箱 + 前向收益", sec(
          p("把拥挤度按分位分成若干箱，比较各箱<strong>未来</strong> N 日平均收益，"
            "是无模型、易复核的第一步。注意三点：分箱阈值必须用历史可得数据；"
            "收益要扣除成本；分组结果本身也是一次参数选择，需在样本外重复。"),
      )),
  ],
  demos=[mk_demo(
      "code/23-crowding.py", "实验 23-1 · 拥挤度分箱与前向收益",
      "合成「追涨资金流 → 拥挤 → 后续收益受压」的数据生成过程，并做分箱对照。",
      """N, FWD, BINS = 500, 20, 8
W = 20             # 拥挤度滚动窗口
GAMMA = 0.0009     # 拥挤对未来收益的压制系数
NOISE = 0.009      # 收益噪声""",
      """rng = random.Random(7)
rets, flow, crowd = [], [], []
for i in range(N):
    if i >= W:
        recent = flow[i - W:i]
        m = statistics.fmean(flow[:i])
        s = statistics.pstdev(flow[:i]) or 1.0
        c = (statistics.fmean(recent) - m) / s
    else:
        c = 0.0
    crowd.append(c)
    r = 0.0003 - GAMMA * c + rng.gauss(0, NOISE)
    rets.append(r)
    chase = 0.7 * (statistics.fmean(rets[-5:]) / NOISE) if rets else 0.0
    flow.append(chase + rng.gauss(0, 0.8))

prices, v = [], 1.0
for r in rets:
    v *= (1 + r)
    prices.append(v)
fwd = [prices[i + FWD] / prices[i] - 1 if i + FWD < N else None
       for i in range(N)]

lo, hi = min(crowd), max(crowd)
width = (hi - lo) / BINS
bucket = [[] for _ in range(BINS)]
for c, f in zip(crowd, fwd):
    if f is None:
        continue
    k = min(BINS - 1, int((c - lo) / width))
    bucket[k].append(f)
means = [statistics.fmean(b) if b else 0.0 for b in bucket]
counts = [len(b) for b in bucket]

c = Chart(FIG / "23-crowding.svg", "合成拥挤度时间序列", xlabel="交易日", ylabel="z 分数")
c.line(range(N), crowd, BLUE, label="拥挤度")
c.hline(2.0, RED, label="+2 高拥挤")
c.hline(-2.0, GREEN, label="−2 低拥挤")
print("拥挤图:", c.save())
b = Chart(FIG / "23-bins.svg", "拥挤度分箱后的 20 日前向平均收益", xlabel="拥挤度分箱", ylabel="平均收益 %",
          xticks=[(i, "Q%d" % (i + 1)) for i in range(BINS)])
b.bars(range(BINS), [100 * x for x in means], AMBER, label="前向收益")
b.hline(0.0, "#9aa6b2")
print("分箱图:", b.save())
valid = [(c, f) for c, f in zip(crowd, fwd) if f is not None]
mc = statistics.fmean(x for x, _y in valid); mf = statistics.fmean(y for _x, y in valid)
corr = sum((x - mc) * (y - mf) for x, y in valid) / math.sqrt(
    sum((x - mc) ** 2 for x, _y in valid) * sum((y - mf) ** 2 for _x, y in valid))
print("最低拥挤箱=%.3f%% 最高拥挤箱=%.3f%% 差=%+.3f%% | 相关系数=%.3f | 各箱样本 %s" %
      (100 * means[0], 100 * means[-1], 100 * (means[-1] - means[0]), corr, counts))""",
      [("fig/23-crowding.svg", "随时间变化的拥挤度及高/低阈值"),
       ("fig/23-bins.svg", "按拥挤度分箱的前向平均收益")],
      "把 <code>GAMMA</code> 设为 0（拥挤不影响未来收益），观察最高/最低箱之差是否只剩噪声。",
      "在数据生成过程里人为注入「拥挤压制未来收益」后，高拥挤箱的平均前向收益明显更低、"
      "相关系数为负。<strong>这是演示检验方法</strong>：真实数据是否如此，需要独立样本与成本扣除。",
      "把 <code>BINS</code> 改成 4 或 16，观察分箱数怎样影响极值箱的噪声与样本量。")],
  highlights=[("herding", "羊群行为与反馈环"),
              ("momentum", "横截面动量与反转"),
              ("volume", "成交量与换手率的信息含量"),
              ("market-micro", "拥挤平仓时的冲击成本机制")],
  analogy="拥挤度是「同一段代码被多少个进程同时执行」的指标。"
          "单进程时退出无成本，所有进程同时退出时，<strong>锁竞争把吞吐打没了</strong>。",
  bridge="第 21～22 章分别处理因子与个体偏差，本章处理它们的叠加；"
         "{{ch:24}} 给出阅读这类实证论文的标准清单。",
  pitfalls=["把「大单净流入」当成真实的资金进入。",
            "分箱阈值用全样本分位数，引入未来函数。",
            "只报最高/最低箱的差，不报中间箱与样本量。",
            "忽略拥挤策略的容量与换手成本。"],
  exercises=["说明为什么「每一笔买必有一笔卖」使净流入指标只能是代理变量。",
             "在示例里加入 0.1% 的换仓成本，观察高低箱收益差是否还显著。",
             "设计一个只用历史信息计算分箱阈值的版本。"],
  further=["{{ch:24}} 论文复现；{{ch:28}} 多重检验；{{ch:29}} 冲击成本。"]),

]
