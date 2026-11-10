#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 12～17 章：组合理论、盘面数据结构与看图识图基础。"""
from __future__ import annotations

from book_schema import C, eq, table
from chapter_kit import mk_demo, p, ul, note, warn, sec

CH = [

# ==================================================================== 12
C("12", "p2", "part2/12-option-payoff", "期权 payoff、平价关系与希腊字母",
  "或有权益把「折现」升级成「无套利」：价格不由预测决定，而由可复制关系约束。",
  hours="3 学时",
  goals=["能画出四种基本期权头寸的到期损益并写出分段函数。",
         "能用二叉树给出欧式看涨/看跌价格，并验证平价关系。",
         "能用数值差分计算 delta 与 gamma，理解对冲的含义。",
         "能说明时间价值衰减、隐含波动率与杠杆的关系。"],
  points=["看涨与看跌 payoff", "多头与空头", "内在价值与时间价值", "看跌-看涨平价",
          "二叉树与风险中性概率", "delta 与 gamma", "theta 与 vega", "保证金与非线性风险"],
  sections=[
      ("12.1", "payoff 是分段函数，不是预测", sec(
          eq("long call: max(S_T − K, 0) − C　|　long put: max(K − S_T, 0) − P"),
          p("把期权当成一段纯函数 <code>payoff(S_T)</code> 最不容易出错："
            "买入是收益无上界/损失有界，卖出恰好镜像；组合多个行权价就能拼出任意分段线性形状。"
            "交易 App 里的「期权策略组合」本质上就是这些分段函数的叠加预览。"),
          table(["头寸", "最大收益", "最大损失", "主要暴露"], [
              ["买入看涨", "无上界", "权利金", "方向上行 + 波动率上行"],
              ["卖出看涨", "权利金", "无上界", "方向上行的负凸性、保证金"],
              ["买入看跌", "K − P（S→0）", "权利金", "下行保护 + 波动率"],
              ["卖出看跌", "权利金", "K − P", "愿意在 K 接货 + 保证金"],
          ], ["20%", "22%", "22%", "36%"]),
      )),
      ("12.2", "无套利：平价关系与二叉树", sec(
          eq("C − P = S_0 − K · e^(−rT)"),
          p("左边是「合成股票」，右边是「现货 − 折现后的行权价」。若两边不等，"
            "可以买入便宜的一边、卖出贵的一边锁定无风险收益。用 CRR 二叉树把终端 payoff "
            "按风险中性概率折现，得到的 C、P 会自然满足平价关系——这是<strong>可运行的验证</strong>，"
            "不是需要相信的结论。"),
          eq("u = e^(σ√Δt), d = 1/u, p = (e^(rΔt) − d)/(u − d)"),
      )),
      ("12.3", "希腊字母就是偏导数", sec(
          eq("Δ = ∂V/∂S　|　Γ = ∂²V/∂S²　|　Θ = ∂V/∂t　|　ν = ∂V/∂σ"),
          p("对冲的工程含义是<strong>把一阶暴露调到零，再监控二阶残差</strong>。"
            "gamma 大的头寸需要更频繁地重平衡，theta 是这种维护的时间成本。"
            "第 30 章会把同样的「敏感度—再平衡」结构用于杠杆与保证金。"),
          warn("风险边界", "卖出期权的收益分布是「多次小赚 + 偶发巨亏」，"
               "最大损失在理论上无上界；保证金与强平发生在尾部，而不是平均情形。"),
      )),
  ],
  demos=[mk_demo(
      "code/12-option.py", "实验 12-1 · 到期损益、二叉树定价、平价关系与 delta",
      "用标准库实现 CRR 二叉树，验证平价关系，并用中心差分求 delta。",
      """S0, K = 100.0, 100.0
R, SIGMA, T = 0.03, 0.20, 1.0
STEPS = 60          # 二叉树步数""",
      """def crr(S, kind):
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
      (call, put, parity, delta, gamma))""",
      [("fig/12-payoff.svg", "三种头寸在到期日的分段线性损益"),
       ("fig/12-delta.svg", "由二叉树数值差分得到的 delta 曲线")],
      "把 <code>STEPS</code> 依次设为 10 / 60 / 200，观察平价残差与定价的收敛；"
      "再把 <code>SIGMA</code> 调大，看期权价格与 delta 曲线如何变化。",
      "只要用同一棵树算 call 与 put，平价残差应接近 0（数值精度量级）；"
      "delta 在平值附近约 0.5，向实值/虚值两端分别趋于 1 与 0。"
      "<strong>希腊字母就是数值导数，不需要额外公式。</strong>",
      "把 <code>K</code> 从 100 改成 120，delta 曲线整体右移，说明行权价改变了敏感度分布。")],
  highlights=[("option", "或有权益与非线性 payoff"),
              ("put-call", "看跌-看涨平价的无套利推导"),
              ("black-scholes", "连续时间闭式解，与二叉树结果对照"),
              ("cboe-edu", "交易所官方的期权与希腊字母教学材料")],
  analogy="期权定价是<strong>用可复制组合做类型检查</strong>："
          "<code>call − put ≡ stock − discounted_strike</code> 是一条编译期恒等式。"
          "二叉树只是把终端枚举 + 概率加权折现，等价于一次动态规划。",
  bridge="第 09～11 章都是「折现现金流」，本章第一次遇到现金流依赖未来状态的情形；"
         "接下来 {{ch:13}} 把多个风险资产放进同一个方差—协方差框架。",
  pitfalls=["把权利金当成最大损失的唯一来源，忽略卖出方的无限损失。",
            "用历史波动率直接当隐含波动率。",
            "把 delta 当成常数，忽略 gamma 带来的再平衡需求。",
            "忽略流动性差的期权合约上买卖价差可以吞掉全部时间价值。"],
  exercises=["用示例的二叉树给 K=90/100/110 三个行权价定价，画出波动率微笑需要什么额外信息。",
             "推导平价关系，并指出股息存在时公式应如何修改。",
             "用中心差分补出 vega（对 σ 求导）并与 delta 比较量纲。"],
  further=["{{ch:30}} 杠杆、保证金与强平；{{ch:29}} 期权组合的执行成本。"]),

# ==================================================================== 13
C("13", "p2", "part2/13-mean-variance", "均值-方差、有效前沿与夏普比率",
  "把「分散投资」写成协方差矩阵的二次型，风险就从形容词变成可算的数。",
  hours="3 学时",
  goals=["能从收益率序列估计协方差矩阵与相关系数。",
         "能计算组合期望收益、波动与夏普比率。",
         "能扫描权重得到有效前沿、最小方差组合与切点组合。",
         "能解释相关系数小于 1 时风险为何可以被分散。"],
  points=["协方差矩阵", "相关系数与分散化", "组合期望收益", "组合波动二次型",
          "最小方差组合", "有效前沿", "夏普比率与切点组合", "资本市场线"],
  sections=[
      ("13.1", "组合风险是二次型", sec(
          eq("E[r_p] = wᵀμ　|　σ_p² = wᵀΣw = Σ_i Σ_j w_i w_j σ_i σ_j ρ_ij"),
          p("关键是 <strong>ρ_ij</strong>：若两资产完全正相关（ρ=1），组合波动就是加权平均，没有分散效果；"
            "只要 ρ &lt; 1，就有 σ_p &lt; Σ w_i σ_i，差额就是分散化收益。"
            "这就是「不要把鸡蛋放在一个篮子里」的数学版本，也是全书第一次把风险写成矩阵运算。"),
          p("注意σ_p² 是<strong>非线性的</strong>：权重翻倍，方差变四倍；"
            "资产数量增加时，个体风险被平均掉，剩下的共同部分无法分散——"
            "这个残差正是第 21 章因子与市场 beta 的起点。"),
      )),
      ("13.2", "三个特征组合", sec(
          table(["组合", "优化目标", "用途", "对输入敏感吗"], [
              ["最小方差 GMV", "min σ_p²", "风险预算的起点", "对协方差敏感"],
              ["切点组合", "max (E[r_p] − r_f)/σ_p", "与无风险资产搭配的最优风险组合", "对 μ 极其敏感"],
              ["等权 1/n", "不优化", "稳健基线（常被用作对照组）", "几乎不敏感"],
          ], ["20%", "30%", "32%", "18%"]),
          p("均值-方差优化在工程上有个著名毛病：<strong>μ 的估计误差会被放大</strong>，"
            "最优权重常出现极端多空。教材里用网格扫描而非解析解，是为了让你直观看到"
            "「最优」对参数有多敏感。实践中常用约束、收缩估计或第 14 章的固定比例配置。"),
      )),
      ("13.3", "夏普比率衡量的是单位总风险", sec(
          eq("Sharpe = (E[r_p] − r_f) / σ_p"),
          p("它假设投资者只关心均值与方差，且收益可自由借贷。厚尾、路径依赖与杠杆成本都会让它失真，"
            "因此第 27 章会补上索提诺、Calmar 与信息比率，第 30 章补上尾部约束。"),
      )),
  ],
  demos=[mk_demo(
      "code/13-frontier.py", "实验 13-1 · 权重扫描、有效前沿与切点组合",
      "三资产、给定 μ/Σ，穷举权重网格，画风险—收益散点与有效前沿。",
      """MU = (0.08, 0.05, 0.12)      # 年化期望收益
SIG = (0.18, 0.08, 0.25)     # 年化波动
CORR = ((1.0, 0.20, 0.60),
        (0.20, 1.0, 0.10),
        (0.60, 0.10, 1.0))
RF = 0.02                    # 无风险利率
STEP = 0.02                  # 权重网格步长""",
      """COV = [[SIG[i] * SIG[j] * CORR[i][j] for j in range(3)] for i in range(3)]

def stats(w):
    er = sum(w[i] * MU[i] for i in range(3))
    var = sum(w[i] * w[j] * COV[i][j] for i in range(3) for j in range(3))
    return er, math.sqrt(max(var, 0.0))

points, grid = [], int(round(1.0 / STEP))
for a in range(grid + 1):
    for b in range(grid + 1 - a):
        w = (a * STEP, b * STEP, 1.0 - (a + b) * STEP)
        er, vol = stats(w)
        points.append((vol, er, w, (er - RF) / vol if vol > 0 else 0.0))

best = max(points, key=lambda x: x[3])
gmv = min(points, key=lambda x: x[0])
lo = min(er for _v, er, _w, _s in points)
hi = max(er for _v, er, _w, _s in points)
frontier = []
for k in range(41):
    target = lo + (hi - lo) * k / 40
    near = [x for x in points if target - 0.002 <= x[1] <= target + 0.002]
    if near:
        frontier.append(min(near, key=lambda x: x[0]))

c = Chart(FIG / "13-frontier.svg", "三资产组合的风险—收益可行集", xlabel="年化波动", ylabel="年化期望收益")
c.scatter([x[0] for x in points], [x[1] for x in points], "#9aa6b2", label="可行组合", radius=1.8)
c.line([x[0] for x in frontier], [x[1] for x in frontier], BLUE, label="有效前沿", width=2.6)
c.scatter([best[0]], [best[1]], RED, label="切点组合", radius=6)
c.scatter([gmv[0]], [gmv[1]], GREEN, label="最小方差", radius=6)
c.line([0.0, best[0] * 1.6], [RF, RF + (best[1] - RF) * 1.6], AMBER,
       label="资本市场线", dash="5 4")
print("前沿图:", c.save())

heatmap(FIG / "13-corr.svg", CORR, ["股票A", "债券B", "成长C"], ["A", "B", "C"],
        title="三资产相关系数矩阵")
print("相关图:", str(FIG / "13-corr.svg"))
print("最小方差 w=(%.2f,%.2f,%.2f) σ=%.2f%% | 切点 w=(%.2f,%.2f,%.2f) E=%.2f%% σ=%.2f%% Sharpe=%.3f" %
      (*gmv[2], 100 * gmv[0], *best[2], 100 * best[1], 100 * best[0], best[3]))""",
      [("fig/13-frontier.svg", "可行集、有效前沿、最小方差与切点组合"),
       ("fig/13-corr.svg", "三资产相关系数热力图")],
      "把 <code>CORR[0][1]</code> 与 <code>CORR[1][0]</code> 一起改成 −0.6，观察前沿如何向左移动；"
      "再只改其中一个，看看为什么协方差矩阵必须对称。",
      "前沿上的每一点都是「给定收益下波动最小」的组合；切点组合是夏普最大的那一点。"
      "相关系数越接近 −1，前沿越往左凸，分散化收益越大。",
      "把 <code>MU[2]</code> 提高 2 个百分点，切点权重会大幅挪向资产 C——这就是均值估计误差被放大的演示。")],
  highlights=[("mpt", "均值-方差框架的标准表述"),
              ("frontier", "有效前沿的定义与性质"),
              ("sharpe", "夏普比率的适用条件"),
              ("mit-ocw", "配套的投资组合理论课程与讲义")],
  analogy="组合优化就是在一个带 <code>wᵀΣw</code> 正则项的二次规划里搜参。"
          "网格扫描是最朴素的超参搜索；<strong>切点组合对 μ 的敏感</strong>与深度学习里对验证集过拟合是同一种病。",
  bridge="第 12 章处理单一标的的非线性 payoff，本章处理多标的的线性权重；"
         "{{ch:14}} 把最优权重问题退化成稳健的固定比例与再平衡规则。",
  pitfalls=["把相关系数矩阵写得不对称，导致方差出现负数。",
            "用短期样本估计 μ 后直接求「最优」权重，得到极端解。",
            "忽略无杠杆约束，让权重出现负值却未建模借券成本。",
            "把夏普比率当成唯一目标，忽略厚尾与回撤。"],
  exercises=["证明两资产 ρ=1 时组合波动等于加权平均。",
             "在示例里加入 w_i ≥ 0 与 w_i ≤ 0.6 的约束，比较切点组合变化。",
             "推导 wᵀΣw 对 w 的梯度，说明为什么解析最优解对 Σ 的误差敏感。"],
  further=["{{ch:14}} 资产配置与再平衡；{{ch:21}} 无法分散的共同部分如何变成因子；{{ch:27}} 绩效指标族。"]),

# ==================================================================== 14
C("14", "p2", "part2/14-allocation", "资产配置、再平衡与定投",
  "与其预测未来收益，不如先约定一条遇到任何行情都能执行的规则。",
  hours="3 学时",
  goals=["能解释战略配置与战术配置的分工。",
         "能模拟「买入持有」与「定期再平衡」的权重漂移与净值差异。",
         "能计算再平衡换手与成本，理解「再平衡溢价」的成立条件。",
         "能把生命周期、风险承受力与现金缓冲写进配置规则。"],
  points=["战略与战术配置", "目标权重与权重漂移", "定期再平衡与阈值再平衡",
          "再平衡换手与成本", "定投与一次性投入", "生命周期与人力资本", "风险承受力", "现金缓冲"],
  sections=[
      ("14.1", "配置是一个策略，不是一次购买", sec(
          p("第 13 章的最优组合依赖 μ 与 Σ 的估计，而这两个量在现实中极不稳定。"
            "实践中更稳健的做法是<strong>先固定一组目标权重</strong>（如股 60 / 债 40），"
            "再约定偏离到什么程度、多久把它拉回去。这样决策从「预测」变成<strong>状态机</strong>："),
          eq("若 max_i |w_i,t − w_i*| > 阈值 → 卖出超配、买入低配 → w = w*"),
          p("定期再平衡与阈值再平衡的区别，等同于定时任务与事件触发：前者成本可预期，后者响应更快但交易次数不确定。"),
      )),
      ("14.2", "再平衡为什么会改善风险调整收益", sec(
          p("两类资产负相关或低相关、且都均值回复时，再平衡会系统性地「高抛低吸」，"
            "带来所谓<strong>再平衡溢价</strong>。但在单边趋势市里，它会不断卖出赢家、买入输家，"
            "跑输买入持有；而权重漂移会让组合的实际风险暴露悄悄偏离目标。"
            "所以正确的比较不是「谁收益高」，而是<strong>谁的暴露更接近你声明的风险预算</strong>。"),
      )),
      ("14.3", "生命周期：把人力资本算进资产负债表", sec(
          table(["阶段", "人力资本", "合理风险暴露", "重点"], [
              ["在校 / 初入职场", "高（未来收入现值大）", "可偏高", "积累本金、建立应急金与纪律"],
              ["家庭形成期", "中高", "中高", "负债、保险、流动性需求上升"],
              ["临近退休", "低", "下降", "回撤承受力下降、提取顺序风险"],
              ["退休后", "接近 0", "低", "现金流匹配、提取率与费用"],
          ], ["22%", "26%", "22%", "30%"]),
          p("定投（DCA）本质上不是提高收益的技巧，而是<strong>把择时风险摊到时间上、把储蓄纪律自动化</strong>。"
            "在长期上行市场里一次性投入的期望终值通常更高，但定投的回撤体验与行为可持续性是它的真实价值（回顾第 00 章实验）。"),
      )),
  ],
  demos=[mk_demo(
      "code/14-allocation.py", "实验 14-1 · 买入持有 vs 年度再平衡",
      "合成 20 年月度股债收益，比较三种规则的风险、收益、回撤与权重漂移。",
      """YEARS = 20
MONTHS = YEARS * 12
TARGET = (0.60, 0.40)   # 股 / 债目标权重
REBAL_EVERY = 12        # 每 12 个月再平衡
V0 = 100000.0
COST = 0.001            # 单次调仓成本率""",
      """rng = random.Random(7)
rs, rb = [], []
for _ in range(MONTHS):
    z, z2 = rng.gauss(0, 1), rng.gauss(0, 1)
    rs.append(0.007 + 0.045 * z)
    rb.append(0.002 + 0.012 * (-0.2 * z + math.sqrt(1 - 0.04) * z2))

all_stock = [V0]
bh_series, rb_series = [V0], [V0]
bh_s, bh_b = V0 * TARGET[0], V0 * TARGET[1]   # 买入持有：份额固定
rb_s, rb_b = V0 * TARGET[0], V0 * TARGET[1]   # 再平衡：份额可调
turnover, w_bh, w_rb = 0.0, [], []
for i in range(MONTHS):
    all_stock.append(all_stock[-1] * (1 + rs[i]))
    bh_s *= (1 + rs[i]); bh_b *= (1 + rb[i])
    bh_value = bh_s + bh_b
    bh_series.append(bh_value)
    w_bh.append(bh_s / bh_value)

    if (i + 1) % REBAL_EVERY == 0:
        rb_value = rb_s + rb_b
        trade = abs(TARGET[0] - rb_s / rb_value) * rb_value
        turnover += trade
        rb_value -= trade * COST
        rb_s, rb_b = rb_value * TARGET[0], rb_value * TARGET[1]
    rb_s *= (1 + rs[i]); rb_b *= (1 + rb[i])
    rb_value = rb_s + rb_b
    rb_series.append(rb_value)
    w_rb.append(rb_s / rb_value)

def metrics(xs):
    rr = [xs[i] / xs[i - 1] - 1 for i in range(1, len(xs))]
    peak, mdd = xs[0], 0.0
    for v in xs:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1)
    cagr = (xs[-1] / xs[0]) ** (1 / YEARS) - 1
    return cagr, statistics.pstdev(rr) * math.sqrt(12), mdd

c = Chart(FIG / "14-equity.svg", "三种配置规则的账户净值", xlabel="月", ylabel="账户价值")
c.line(range(MONTHS + 1), all_stock, RED, label="100% 股票")
c.line(range(MONTHS + 1), bh_series, AMBER, label="60/40 买入持有")
c.line(range(MONTHS + 1), rb_series, BLUE, label="60/40 年度再平衡")
print("净值图:", c.save())
w = Chart(FIG / "14-weights.svg", "股票权重的漂移与拉回", xlabel="月", ylabel="股票权重")
w.line(range(MONTHS), w_bh, AMBER, label="买入持有（漂移）")
w.line(range(MONTHS), w_rb, BLUE, label="年度再平衡")
w.hline(TARGET[0], "#9aa6b2", label="目标 60%")
print("权重图:", w.save())
m1, m2, m3 = metrics(all_stock), metrics(bh_series), metrics(rb_series)
print("再平衡累计调仓金额=%.0f 元 | 期末权重 买入持有=%.1f%% 再平衡=%.1f%%" %
      (turnover, 100 * w_bh[-1], 100 * w_rb[-1]))
print("全股 CAGR=%.2f%% σ=%.2f%% MDD=%.1f%% | 买入持有 %.2f%% / %.2f%% / %.1f%% | 再平衡 %.2f%% / %.2f%% / %.1f%%" %
      (100 * m1[0], 100 * m1[1], 100 * m1[2], 100 * m2[0], 100 * m2[1], 100 * m2[2],
       100 * m3[0], 100 * m3[1], 100 * m3[2]))""",
      [("fig/14-equity.svg", "三种配置规则的净值路径"),
       ("fig/14-weights.svg", "股票权重漂移与再平衡拉回")],
      "把 <code>REBAL_EVERY</code> 改成 1（每月）与 120（几乎不调），比较波动、回撤与累计调仓金额。",
      "再平衡把权重拉回目标，牺牲一部分趋势收益换取<strong>风险暴露可控</strong>；"
      "买入持有的股票权重会随行情漂移，组合悄悄变得更激进。",
      "把股票月收益均值从 0.007 改为负数，观察再平衡在长期下跌市里的表现。")],
  highlights=[("asset-allocation", "战略/战术配置的框架"),
              ("rebalancing", "再平衡规则与再平衡溢价"),
              ("dca", "定投与一次性投入的现金流差异"),
              ("lifetime", "生命周期与人力资本视角")],
  analogy="配置策略是一个 <code>controller</code>：目标权重是 setpoint，实际权重是 process variable，"
          "再平衡是周期性的负反馈，成本是控制动作的代价。<strong>没有反馈的系统，暴露会随行情漂移。</strong>",
  bridge="第 13 章求「最优权重」，本章给出「稳健规则」；至此第二阶段结束，"
         "{{ch:15}} 起转入屏幕上的价格形成过程。",
  pitfalls=["把再平衡当作提高收益的技巧，忽略它在单边市中的劣势。",
            "只看收益比较，不看权重漂移造成的风险暴露变化。",
            "再平衡频率过高导致成本吞掉溢价。",
            "把生命周期规则写成固定年龄数字，忽略负债与收入稳定性。"],
  exercises=["实现阈值再平衡（偏离 5 个百分点才触发），与年度再平衡比较交易次数。",
             "解释为什么「定投更适合波动大的市场」不等于「定投期望收益更高」。",
             "在自己的 IPS 里写出目标权重、阈值、频率与暂停条件。"],
  further=["{{ch:27}} 绩效归因；{{ch:31}} 把配置规则写进投资政策说明书。"]),

# ==================================================================== 15
C("15", "p3", "part3/15-order-book", "盘口、分时与逐笔：价格是怎样形成的",
  "看盘之前先理解数据流：你看到的五档，是订单簿的一个有损快照。",
  hours="3 学时",
  goals=["能读写买卖五档盘口并计算价差、深度失衡。",
         "能模拟市价单逐档吃单，计算 VWAP 与冲击成本。",
         "能说明分时图、成交明细与 K 线之间的关系。",
         "能解释为什么盘口大单不等于真实买卖意愿。"],
  points=["限价订单簿", "买卖五档与价差", "深度与失衡", "市价单逐档成交",
          "VWAP 与滑点", "市场冲击", "逐笔成交与分时", "幌骗与冰山单"],
  sections=[
      ("15.1", "订单簿是一个双端优先队列", sec(
          p("买侧按价格降序、卖侧按价格升序排队，同价位按时间优先。"
            "最佳买价 bid 与最佳卖价 ask 之间的差就是 <strong>spread</strong>，"
            "它是流动性最直接的报价：你以 ask 买入、立刻以 bid 卖出，必然损失一个价差。"),
          eq("spread = ask_1 − bid_1　|　相对价差 = spread / mid　|　mid = (ask_1 + bid_1)/2"),
          table(["盘口字段", "含义", "误读"], [
              ["买一 / 卖一价量", "当前最优报价与挂单量", "挂单可瞬时撤单，不代表真实意愿"],
              ["五档累计深度", "前五档委托量之和", "不含隐藏单、冰山单与场外流动性"],
              ["委比 / 失衡", "(买量−卖量)/(买量+卖量)", "易被小额挂单操纵"],
              ["逐笔成交", "已撮合的成交记录", "主动买/卖方向依赖交易所的标记口径"],
          ], ["22%", "36%", "42%"]),
      )),
      ("15.2", "市价单的成本是一次遍历", sec(
          p("一笔数量为 Q 的市价买单会从卖一开始逐档吃掉，成交均价 VWAP 高于 mid，"
            "差额就是<strong>冲击成本 + 价差成本</strong>。订单越大、深度越薄，VWAP 越差，"
            "且这个关系通常是凸的。第 29 章会据此设计拆单。"),
          eq("VWAP(Q) = Σ(p_k × q_k) / Q　|　冲击 = VWAP(Q)/mid − 1"),
      )),
      ("15.3", "从逐笔到分时到 K 线", sec(
          ul(["<strong>逐笔</strong>：每笔成交的时间、价、量、方向，信息最全也最噪。",
              "<strong>分时</strong>：按分钟聚合的均价/最新价与成交量，常用于日内观察。",
              "<strong>K 线</strong>：按周期聚合 OHLCV（第 06、16 章），信息被压缩但结构清晰。",
              "<strong>盘口快照</strong>：某个时刻的委托分布，与成交序列是两种不同的数据源。"]),
          note("关键区分", "K 线的 high/low 不一定等于你能在那个价位成交；"
               "盘口挂单也不一定真的存在到你的订单到达。<strong>回测必须明确用的是哪一种数据</strong>。"),
      )),
  ],
  demos=[mk_demo(
      "code/15-book.py", "实验 15-1 · 五档盘口、深度失衡与市价单冲击",
      "构造订单簿快照，逐档吃单计算 VWAP，并画出订单量与冲击成本曲线。",
      """MID = 10.00
TICK = 0.01
LEVELS = 5
BASE_SIZE = 2000     # 每档基准挂单量
ORDER_QTY = 6000     # 待执行的市价买单
MAX_QTY = 20000      # 冲击曲线扫描上限""",
      """rng = random.Random(7)
bid_px = [round(MID - TICK / 2 - i * TICK, 2) for i in range(LEVELS)]
ask_px = [round(MID + TICK / 2 + i * TICK, 2) for i in range(LEVELS)]
bid_sz = [int(BASE_SIZE * (1 + abs(rng.gauss(0, 0.4)))) for _ in range(LEVELS)]
ask_sz = [int(BASE_SIZE * (1 + abs(rng.gauss(0, 0.4)))) for _ in range(LEVELS)]
spread = ask_px[0] - bid_px[0]
mid = (ask_px[0] + bid_px[0]) / 2
imbalance = (sum(bid_sz) - sum(ask_sz)) / (sum(bid_sz) + sum(ask_sz))

def execute(qty):
    left, cost, used = qty, 0.0, []
    for px, sz in zip(ask_px, ask_sz):
        take = min(left, sz)
        cost += take * px
        used.append((px, take))
        left -= take
        if left <= 0:
            break
    filled = qty - left
    return cost / filled if filled else mid, filled, used

vwap, filled, used = execute(ORDER_QTY)
impact = vwap / mid - 1

c = Chart(FIG / "15-depth.svg", "五档订单簿深度（买负 / 卖正）", xlabel="价格", ylabel="挂单量")
c.bars(ask_px, ask_sz, RED, label="卖盘")
c.bars(bid_px, [-s for s in bid_sz], GREEN, label="买盘")
c.hline(0.0, "#9aa6b2")
print("深度图:", c.save())

qs = list(range(1000, MAX_QTY + 1, 1000))
impacts = [(execute(q)[0] / mid - 1) * 100 for q in qs]
i = Chart(FIG / "15-impact.svg", "市价买单规模与价格冲击", xlabel="订单量（股）", ylabel="冲击 %")
i.line(qs, impacts, BLUE, label="冲击成本")
i.hline(0.0, "#9aa6b2")
print("冲击图:", i.save())
print("最优买=%.2f 最优卖=%.2f 价差=%.4f (%.3f%%) | 深度失衡=%+.3f" %
      (bid_px[0], ask_px[0], spread, 100 * spread / mid, imbalance))
print("市价买 %d 股 成交 %d 股 VWAP=%.4f 冲击=%.3f%% | 吃到第 %d 档" %
      (ORDER_QTY, filled, vwap, 100 * impact, len(used)))""",
      [("fig/15-depth.svg", "五档买卖挂单量的深度分布"),
       ("fig/15-impact.svg", "订单规模与冲击成本的非线性关系")],
      "把 <code>ORDER_QTY</code> 从 6000 提高到 15000，观察吃到第几档以及冲击的增幅是否线性。",
      "冲击成本随订单量<strong>加速上升</strong>（阶梯式、凸），因为便宜档位先被吃光。"
      "深度失衡只是快照，可瞬时撤单，不能单独作为方向信号。",
      "把 <code>BASE_SIZE</code> 减半（更薄的盘口），同一订单的冲击会明显变大。")],
  highlights=[("order-book", "限价订单簿与撮合的数据结构"),
              ("bid-ask", "买卖价差作为流动性成本"),
              ("market-micro", "价格形成与微观结构"),
              ("tradingview", "多周期图表与盘口展示的通用参照")],
  analogy="订单簿是两个按价格排序的优先队列；市价单是一次 <code>pop until filled</code>，"
          "VWAP 是加权平均，冲击是队列深度不足时的溢出成本。<strong>盘口快照是有损缓存，不是真相。</strong>",
  bridge="第三阶段从「价格如何形成」开始；{{ch:16}} 把逐笔聚合成 K 线，"
         "{{ch:17}}～{{ch:19}} 再逐层加指标与形态。",
  pitfalls=["把盘口挂单量当真实买卖意愿，忽略撤单与冰山单。",
            "用 mid 价回测成交，忽略价差与冲击。",
            "把逐笔主动买卖方向当成资金流入流出。",
            "用分时均价代替可成交价，忽略当时的档位深度。"],
  exercises=["推导为什么相对价差是「立刻反手平仓」的最小成本。",
             "在示例里加入冰山单（每档成交后补充挂单），观察冲击曲线如何变缓。",
             "说明「放量上涨」在逐笔、分时、K 线三个层次分别对应什么数据。"],
  further=["{{ch:16}} K 线与坐标；{{ch:29}} 拆单与执行算法；{{ch:26}} 回测中的成交价假设。"]),

# ==================================================================== 16
C("16", "p3", "part3/16-candlestick", "K 线、坐标与复权：看图前先校准数据",
  "一根蜡烛只是 OHLC 四价的一种编码，颜色与坐标约定比形态本身更容易骗人。",
  hours="3 学时",
  goals=["能从 OHLCV 生成 K 线，并说明实体、上影、下影的定义。",
         "能解释 A 股与海外市场颜色约定相反的原因。",
         "能说明线性坐标与对数坐标在长期图上的差别。",
         "能在看图前完成复权、周期与坐标三项校准。"],
  points=["K 线实体与影线", "颜色约定与涨跌", "开高低收的不变式", "线性坐标与对数坐标",
          "周期与聚合", "复权与拆股", "成交量与换手率", "缺口"],
  sections=[
      ("16.1", "把一根 K 线写成断言", sec(
          eq("low ≤ min(open, close) ≤ max(open, close) ≤ high　|　volume ≥ 0"),
          p("实体 = |close − open|，上影 = high − max(open, close)，下影 = min(open, close) − low。"
            "这三个量描述的是<strong>期内多空拉锯</strong>，不含任何预测能力。"
            "把上面那条不变式写成数据校验，能挡住绝大多数脏行情。"),
          table(["形态", "判定条件", "常见解读", "为什么容易误读"], [
              ["长实体阳线", "close > open 且实体/振幅大", "买方占优", "可能是低流动性下的少量成交"],
              ["长上影", "上影 ≫ 实体", "冲高回落", "可能是集合竞价或瞬时插针"],
              ["长下影", "下影 ≫ 实体", "探底回升", "停牌复牌、除权日会造成假影线"],
              ["十字星", "|close − open| ≈ 0", "多空均衡", "阈值取多少完全是人为约定"],
          ], ["18%", "28%", "22%", "32%"]),
      )),
      ("16.2", "三个必须先校准的口径", sec(
          ul(["<strong>复权</strong>：分红送转会造成价格断层，未复权图上的「暴跌」通常是假信号（第 06 章）。",
              "<strong>坐标</strong>：线性坐标下早期波动被压扁，对数坐标让等比例变化等距；"
              "长期比较收益率应该用对数刻度。",
              "<strong>周期</strong>：日线、周线、月线是对同一逐笔流的不同 group by，"
              "同一「支撑位」在不同周期未必是同一个价位。",
              "<strong>颜色</strong>：A 股习惯红涨绿跌，多数海外终端相反；先看图例，不要凭直觉判方向。"]),
          warn("合规提醒", "交易 App 上的 K 线叠加了许多默认指标与自选配色。"
               "把界面设置与数据口径记进实验记录，否则换一台设备就可能得到不同结论。"),
      )),
      ("16.3", "成交量是第二维，不是装饰", sec(
          p("成交量 tells 有多少份额换手，换手率把它按流通盘归一化，才便于跨标的比较。"
            "放量可以来自分歧加大，也可以来自指数调样、ETF 申赎或大单拆单；"
            "第 23 章会把资金流与拥挤度单独拿出来做证据检验。"),
      )),
  ],
  demos=[mk_demo(
      "code/16-candle.py", "实验 16-1 · 合成 OHLCV、K 线图与数据不变式校验",
      "生成 60 根带趋势与均线的合成 K 线，画 K 线+成交量+均线，并统计影线。",
      """N = 60              # K 线根数
START = 50.0        # 起始价
DRIFT = 0.0015      # 日漂移
VOL = 0.014         # 日波动
MA_FAST, MA_SLOW = 5, 20""",
      """rng = random.Random(7)
ohlcv, px = [], START
for _ in range(N):
    o = px
    px = o * (1 + rng.gauss(DRIFT, VOL))
    c = px
    h = max(o, c) * (1 + abs(rng.gauss(0, 0.004)))
    l = min(o, c) * (1 - abs(rng.gauss(0, 0.004)))
    v = int(800000 * (1 + abs(rng.gauss(0, 0.35))))
    ohlcv.append((o, h, l, c, v))

bad = 0
for o, h, l, c, v in ohlcv:
    if not (l <= min(o, c) and max(o, c) <= h and v >= 0):
        bad += 1
closes = [r[3] for r in ohlcv]

def sma(series, w):
    return [None if i + 1 < w else statistics.fmean(series[i + 1 - w:i + 1])
            for i in range(len(series))]

fast, slow = sma(closes, MA_FAST), sma(closes, MA_SLOW)
candlestick(FIG / "16-candle.svg", ohlcv,
            title="合成 K 线（60 根）· MA5 / MA20 · 成交量",
            overlays=[(fast, BLUE, "MA5"), (slow, AMBER, "MA20")],
            xticks=[(i, "T%d" % i) for i in range(0, N, 10)])
print("K 线图:", str(FIG / "16-candle.svg"))

up = sum(1 for r in ohlcv if r[3] >= r[0])
bodies = [abs(r[3] - r[0]) / r[0] for r in ohlcv]
upper = [(r[1] - max(r[0], r[3])) / r[0] for r in ohlcv]
lower = [(min(r[0], r[3]) - r[2]) / r[0] for r in ohlcv]
doji = sum(1 for b in bodies if b < 0.002)
print("不变式违规=%d | 阳线=%d 阴线=%d 十字星=%d | 平均实体=%.2f%% 上影=%.2f%% 下影=%.2f%%" %
      (bad, up, N - up, doji, 100 * statistics.fmean(bodies),
       100 * statistics.fmean(upper), 100 * statistics.fmean(lower)))""",
      [("fig/16-candle.svg", "K 线实体/影线、成交量与两条均线叠加")],
      "先核对「不变式违规=0」；把 <code>VOL</code> 调到 0.04，观察长影线与十字星数量如何变化。",
      "K 线图把 OHLC 四价编码成实体与影线，叠加均线后更容易看出趋势与滞后。"
      "所有统计都来自<strong>合成数据</strong>，说明形态只是数据描述，不含预测结论。",
      "把 <code>MA_FAST</code> 改成 3 与 10，对比均线穿越次数——引出第 17 章的滞后性。")],
  highlights=[("candlestick", "K 线实体、影线与颜色约定"),
              ("ohlc", "开高低收四价的数据结构"),
              ("adjusted-close", "前复权/后复权对长期图形的影响"),
              ("volume", "成交量与换手率的信息含量")],
  analogy="一根 K 线是 <code>group by bucket</code> 后的聚合记录，"
          "<code>low ≤ min(o,c) ≤ max(o,c) ≤ high</code> 是它的 schema 约束。"
          "颜色只是前端 <code>theme</code>，不是数据字段。",
  bridge="第 15 章讲价格如何形成，本章讲它如何被压缩成图；"
         "{{ch:17}} 起在这些数据上叠加均线、指标与形态规则。",
  pitfalls=["用不复权数据看长期 K 线，把除权跳空当暴跌。",
            "忽略 A 股与海外终端颜色相反，凭直觉读反方向。",
            "线性坐标下比较相隔十年的涨跌幅。",
            "把十字星、长影线当成确定性信号，而阈值其实由自己随意设定。"],
  exercises=["在示例里实现后复权序列，说明它与前复权图的形状是否一致。",
             "把日线聚合成周线，重新计算一根周 K 线的 OHLCV。",
             "设计一条「影线异常」的数据校验规则，用于拦截插针行情。"],
  further=["{{ch:17}} 均线、趋势与支撑阻力；{{ch:18}} 指标公式；{{ch:20}} 用代码画图与看图陷阱。"]),

# ==================================================================== 17
C("17", "p3", "part3/17-trend-ma", "均线、趋势与支撑阻力",
  "均线是低通滤波器：它削掉噪声的代价，是必然带来滞后。",
  hours="3 学时",
  goals=["能实现 SMA 与 EMA，并说明二者的权重分布差异。",
         "能计算交叉信号的滞后，并量化窗口长度与滞后的权衡。",
         "能把「趋势」「支撑阻力」写成可判定的规则。",
         "能解释为什么均线在震荡市里会频繁假信号。"],
  points=["简单移动平均 SMA", "指数移动平均 EMA", "低通滤波与滞后", "金叉与死叉",
          "趋势的定义", "支撑与阻力", "成交密集区", "假信号与震荡市"],
  sections=[
      ("17.1", "两种平滑，两种权重", sec(
          eq("SMA_n(t) = (1/n) Σ_{i=0}^{n−1} P_(t−i)　|　EMA(t) = αP_t + (1−α)EMA(t−1), α = 2/(n+1)"),
          p("SMA 对窗口内每一天等权，窗口滚动时会出现「旧数据掉出」造成的阶跃；"
            "EMA 对近端指数加权，反应更快且没有掉出效应，但永远不会完全忘记历史。"
            "从信号处理角度，两者都是<strong>低通滤波器</strong>：窗口越长噪声越少，滞后越大。"),
      )),
      ("17.2", "把主观词写成判定式", sec(
          table(["词", "可判定定义（示例）", "自由度"], [
              ["上升趋势", "close > SMA_n 且 SMA_n 较 k 期前上升", "n、k"],
              ["金叉", "fast_(t−1) ≤ slow_(t−1) 且 fast_t > slow_t", "fast、slow 窗口"],
              ["支撑位", "过去 m 期局部低点的密集价格带", "m、容差、聚类宽度"],
              ["突破", "close > 过去 m 期最高价 × (1 + ε)", "m、ε、成交量条件"],
          ], ["18%", "54%", "28%"]),
          p("注意每个定义都带<strong>自由参数</strong>。参数越多、越容易在历史上调出好看的结果，"
            "也就越容易过拟合（第 28 章）。把参数写进代码并固定下来，是让结论可讨论的前提。"),
      )),
      ("17.3", "支撑阻力：成交密集区的自我实现", sec(
          p("支撑与阻力常被解释为「前期成交密集区的记忆」：在某一价格带套牢的持仓者，"
            "回到成本附近时倾向卖出，从而形成供给。但这是一种<strong>行为假说</strong>，"
            "不是物理定律。第 22 章会从处置效应、锚定等角度给出更基础解释，"
            "第 24 章则讨论怎样检验这类假说。"),
      )),
  ],
  demos=[mk_demo(
      "code/17-trend.py", "实验 17-1 · SMA/EMA、交叉滞后与支撑阻力",
      "在带转折的合成价格上计算均线，检测交叉，量化窗口—滞后权衡。",
      """N = 160
TURN = 80           # 真实趋势转折点
START = 50.0
UP, DOWN = 0.004, -0.003
NOISE = 0.010
FAST, SLOW = 5, 20
LOOKBACK = 20""",
      """rng = random.Random(7)
px, prices = START, []
for i in range(N):
    drift = UP if i < TURN else DOWN
    px *= (1 + drift + rng.gauss(0, NOISE))
    prices.append(px)

def sma(series, w):
    return [None if i + 1 < w else statistics.fmean(series[i + 1 - w:i + 1])
            for i in range(len(series))]

def ema(series, w):
    a, out, prev = 2.0 / (w + 1), [], series[0]
    for v in series:
        prev = a * v + (1 - a) * prev
        out.append(prev)
    return out

fast, slow, ema_fast = sma(prices, FAST), sma(prices, SLOW), ema(prices, FAST)
crosses = []
for i in range(1, N):
    if None in (fast[i - 1], slow[i - 1], fast[i], slow[i]):
        continue
    if fast[i - 1] <= slow[i - 1] and fast[i] > slow[i]:
        crosses.append((i, "金叉"))
    if fast[i - 1] >= slow[i - 1] and fast[i] < slow[i]:
        crosses.append((i, "死叉"))

support = [min(prices[max(0, i + 1 - LOOKBACK):i + 1]) for i in range(N)]
resist = [max(prices[max(0, i + 1 - LOOKBACK):i + 1]) for i in range(N)]

def clean(series):
    xs = [i for i, v in enumerate(series) if v is not None]
    return xs, [series[i] for i in xs]

xf, yf = clean(fast)
x_slow, y_slow = clean(slow)
c = Chart(FIG / "17-trend.svg", "价格、SMA/EMA 与滚动支撑阻力", xlabel="交易日", ylabel="价格")
c.line(range(N), prices, "#9aa6b2", label="价格", opacity=0.8)
c.line(xf, yf, BLUE, label="SMA5")
c.line(x_slow, y_slow, AMBER, label="SMA20")
c.line(range(N), ema_fast, GREEN, label="EMA5")
c.line(range(N), support, RED, label="滚动支撑", dash="3 3")
c.line(range(N), resist, RED, label="滚动阻力", dash="6 3")
c.vline(TURN, "#8a6316", label="真实转折点")
print("趋势图:", c.save())

windows = [3, 5, 10, 20, 40]
lags = []
for w in windows:
    f, s = sma(prices, w), sma(prices, w * 2)
    first = next((i for i in range(TURN, N)
                  if f[i] and s[i] and f[i - 1] and s[i - 1]
                  and f[i - 1] >= s[i - 1] and f[i] < s[i]), N)
    lags.append(first - TURN)
l = Chart(FIG / "17-lag.svg", "均线窗口与转折信号滞后", xlabel="快线窗口", ylabel="滞后（根）",
          xticks=[(i, "n=%d" % w) for i, w in enumerate(windows)])
l.bars(range(len(windows)), lags, BLUE, label="死叉滞后")
print("滞后图:", l.save())
post_death = [x for x in crosses if x[0] >= TURN and x[1] == "死叉"]
print("交叉总数=%d 转折前噪声交叉=%d | 转折后首个死叉=%s | 窗口 %s 对应滞后 %s | 真实转折 T%d" %
      (len(crosses), len([x for x in crosses if x[0] < TURN]),
       post_death[0] if post_death else "无", windows, lags, TURN))""",
      [("fig/17-trend.svg", "价格、SMA/EMA 与滚动支撑阻力通道"),
       ("fig/17-lag.svg", "窗口长度与信号滞后的权衡")],
      "把 <code>SLOW</code> 从 20 改成 40，数一数交叉次数是否减少；再观察滞后图随窗口增大的趋势。",
      "转折后的趋势交叉必然<strong>滞后于真实转折</strong>，窗口越长滞后越大；"
      "转折前也可能因噪声出现假交叉。支撑/阻力在这里只是滚动极值，参数一改结论就变——"
      "这正是需要样本外检验的原因。",
      "把 <code>NOISE</code> 翻倍，短窗口的交叉次数会明显增多，说明噪声被误判成趋势。")],
  highlights=[("ma", "均线族与滞后性"),
              ("support", "支撑阻力的常见解释与争议"),
              ("technical-analysis", "价量研究的假设、流派与争议"),
              ("ta-lib", "技术指标的事实标准实现，可对照手写公式")],
  analogy="SMA 是长度固定的滑动窗口聚合，EMA 是带衰减因子的递归状态。"
          "交叉信号是 <code>sign(fast − slow)</code> 的变号事件；"
          "<strong>任何滤波都得在噪声与延迟之间付代价</strong>。",
  bridge="第 16 章把 OHLCV 画成图，本章加第一层平滑；"
         "{{ch:18}} 把平滑扩展成多指标公式，{{ch:19}} 把形态写成可判定规则。",
  pitfalls=["把均线当成有预测能力的模型，忽略它只是过去价格的函数。",
            "在震荡市里用短窗口频繁交易，成本吞掉全部信号。",
            "事后在图上画支撑线，把任意价位都能解释成「有效支撑」。",
            "把交叉点当日收盘当作可成交价（未来函数）。"],
  exercises=["推导 EMA 的等效权重之和为 1，并说明它为何没有 SMA 的掉出效应。",
             "在示例里统计震荡区间（去掉趋势段）的交叉次数，与趋势段比较。",
             "把「突破」写成带成交量的判定式，说明新增了哪些自由参数。"],
  further=["{{ch:18}} 指标的数学定义；{{ch:20}} 未来函数与画图陷阱；{{ch:28}} 参数扫描与过拟合。"]),
]
