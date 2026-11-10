#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 30～31 章与附录 A：实盘风险、长期复盘与全书速查。"""
from __future__ import annotations

from book_schema import C, eq, table
from chapter_kit import mk_demo, p, ul, note, warn, sec

CH = [

# ==================================================================== 30
C("30", "p6", "part6/30-risk-sizing", "仓位、杠杆、VaR/CVaR 与凯利上界",
  "风险管理不是预测下跌，而是保证「预测错了也还活着」。",
  hours="3 学时",
  goals=["能用蒙特卡洛估计不同杠杆下的强平概率与尾部损失。",
         "能计算历史 VaR / CVaR 并说明其边界。",
         "能写出凯利公式并解释为什么实盘常用其分数。",
         "能把仓位上界写成可执行、可监控的硬约束。"],
  points=["仓位与风险预算", "杠杆与逐日盯市", "维持保证金与强平", "蒙特卡洛模拟",
          "VaR 与 CVaR", "凯利准则", "分数凯利与参数不确定性", "尾部风险与压力测试"],
  sections=[
      ("30.1", "杠杆把分布整体拉伸，也把尾部拉断", sec(
          eq("r_杠杆 ≈ L · r − (L − 1) · 融资成本　|　净值 = 1 + Σ L·r_t（逐日盯市）"),
          p("杠杆不仅放大波动，还引入了<strong>路径依赖</strong>："
            "一次足够大的回撤会触发维持保证金与强平，之后即使标的反弹，账户也无法复原。"
            "因此杠杆策略不能用终值期望评估，必须看<strong>吸收壁（ruin barrier）</strong>与尾部。"),
      )),
      ("30.2", "凯利是一个上界，不是一个目标", sec(
          eq("f* ≈ μ / σ²（连续近似）　|　实盘常用 f = c · f*，c ∈ [0.25, 0.5]"),
          p("凯利最大化长期几何增长率，但它假设 μ、σ 已知且分布稳定。"
            "现实中参数估计误差、厚尾与融资约束都会让全凯利过于激进；"
            "更严重的是，<strong>几何增长率最优并不意味着回撤可承受</strong>。"
            "把凯利值当上界、再用最大回撤与保证金约束往下压，是更稳健的顺序。"),
      )),
      ("30.3", "把风险写成监控规则", sec(
          table(["约束", "可监控的量", "触发动作"], [
              ["单一标的 ≤ 10%", "每日收盘权重", "超限次日减仓"],
              ["组合杠杆 ≤ 1.5", "总敞口 / 净值", "禁止新开仓"],
              ["回撤 ≤ 15%", "相对历史峰值", "降杠杆并复核假设"],
              ["CVaR_95 ≤ 3%", "滚动模拟尾部均值", "暂停策略、检查厚尾"],
          ], ["30%", "34%", "36%"]),
          warn("顺序很重要", "先定「最大可承受损失」，再定仓位；"
               "不要先看到预期收益，再倒推一个能解释它的杠杆。"),
      )),
  ],
  demos=[mk_demo(
      "code/30-risk.py", "实验 30-1 · 杠杆、强平概率与 CVaR 的蒙特卡洛",
      "模拟含厚尾的日收益，扫描杠杆，估计强平概率、终值分位数与 CVaR。",
      """N_PATHS, N_DAYS = 2000, 250
LEVERAGES = (0.5, 1.0, 1.5, 2.0, 3.0)
MU, SIG = 0.0004, 0.012
P_STRESS, STRESS_MULT = 0.02, 4.0
RUIN_BARRIER = 0.25     # 净值低于初始的 25% 视为触发强平
ANN = 252""",
      """rng = random.Random(7)
kelly = MU / (SIG ** 2)
rows = []
for lev in LEVERAGES:
    finals, ruins = [], 0
    for _ in range(N_PATHS):
        eq = 1.0
        ruined = False
        for _d in range(N_DAYS):
            sig = SIG * STRESS_MULT if rng.random() < P_STRESS else SIG
            r = rng.gauss(MU, sig)
            eq *= (1 + lev * r)
            if eq <= RUIN_BARRIER:
                ruined = True
                break
        finals.append(eq)
        ruins += 1 if ruined else 0
    finals.sort()
    k = max(1, int(0.05 * len(finals)))
    cvar = statistics.fmean(finals[:k])
    rows.append((lev, ruins / N_PATHS, statistics.median(finals), finals[k - 1], cvar))

c = Chart(FIG / "30-ruin.svg", "杠杆与强平概率（合成厚尾收益）", xlabel="杠杆 L", ylabel="概率")
c.bars([x[0] for x in rows], [100 * x[1] for x in rows], RED, label="强平概率 %")
print("强平图:", c.save())
t = Chart(FIG / "30-terminal.svg", "终值中位数与 5% 分位数", xlabel="杠杆 L", ylabel="期末净值")
t.line([x[0] for x in rows], [x[2] for x in rows], BLUE, label="中位数")
t.line([x[0] for x in rows], [x[3] for x in rows], AMBER, label="5% 分位")
t.hline(1.0, "#9aa6b2", label="本金")
print("终值图:", t.save())
print("凯利 f*=%.2f（上界）| 强平概率 L=1: %.1f%% L=3: %.1f%%" %
      (kelly, 100 * rows[1][1], 100 * rows[-1][1]))
print("L=3 终值中位=%.3f 5%%分位=%.3f CVaR95=%.3f | 年化波动=%.1f%%" %
      (rows[-1][2], rows[-1][3], rows[-1][4], 100 * SIG * math.sqrt(ANN)))""",
      [("fig/30-ruin.svg", "不同杠杆下的强平概率"),
       ("fig/30-terminal.svg", "终值中位数与 5% 分位数随杠杆的变化")],
      "把 <code>P_STRESS</code> 设为 0（正态分布），比较 L=3 的强平概率；再调到 0.05 看尾部恶化。",
      "厚尾 + 杠杆会显著提高触及吸收壁的概率；终值中位数可能随杠杆上升，但 5% 分位与 CVaR 明显恶化。"
      "凯利值是<strong>上界</strong>，实盘还要被回撤与保证金约束继续压低。",
      "把 <code>RUIN_BARRIER</code> 提高到 0.5（更严格的保证金），强平概率会成倍上升。")],
  highlights=[("var-risk", "分位数意义下的潜在损失"),
              ("cvar", "尾部平均损失，相对 VaR 更保守"),
              ("kelly", "长期增长率最优仓位与其实用限制"),
              ("margin", "融资杠杆、维持保证金与强平规则")],
  analogy="杠杆是给随机过程加了一条<strong>吸收壁</strong>："
          "没有壁时只看期望，有壁时必须看路径。风控规则就是给系统加 circuit breaker，"
          "让一次尾部事件不至于终止整个进程。",
  bridge="第 29 章决定「怎么下单」，本章决定「下多大」；"
         "{{ch:31}} 把这些约束写成一份可长期执行的契约。",
  pitfalls=["用正态假设估计杠杆产品的尾部风险。",
            "把凯利值当成推荐仓位，忽略参数估计误差。",
            "只看终值期望，不看强平概率与路径。",
            "把风险阈值写成事后解释，而不是事前触发动作。"],
  exercises=["推导 <code>f* ≈ μ/σ²</code> 的来源（对几何增长率求导）。",
             "在示例里加入融资成本，观察高杠杆的终值中位数如何变化。",
             "写出一份包含四条硬约束的监控配置，并说明各自的触发动作。"],
  further=["{{ch:02}} 尾部度量；{{ch:12}} 期权卖方风险；{{ch:31}} 投资政策说明书。"]),

# ==================================================================== 31
C("31", "p6", "part6/31-ips-review", "投资政策说明书与长期复盘",
  "把目标、约束、流程与例外写下来，才轮得到讨论今年赚了多少。",
  hours="3 学时",
  goals=["能写出一份含目标、约束、规则与例外的 IPS。",
         "能模拟「按纪律执行」与「随意偏离」的长期差异。",
         "能区分决策质量与结果质量，并用决策日志复盘。",
         "能把 TWR、MWR、费用与合规检查纳入年度复盘。"],
  points=["投资政策说明书 IPS", "目标与约束", "再平衡规则与例外", "决策日志",
          "TWR / MWR 复盘", "费用与税", "行为约束与冷却期", "年度回顾清单"],
  sections=[
      ("31.1", "IPS 是一份给自己签的 SLA", sec(
          table(["章节", "内容", "可检查的形式"], [
              ["目标", "用途、时间 horizon、所需现金流", "可量化的目标区间，而非「多多益善」"],
              ["约束", "流动性、最大回撤、杠杆、集中度、合规", "带数值的硬阈值"],
              ["规则", "目标权重、再平衡带、定投额、下单方式", "可执行的 if-then"],
              ["例外", "允许偏离的条件、审批与冷却期", "书面记录 + 生效日期"],
              ["复盘", "频率、指标、归因、日志归档", "固定模板与数据 manifest"],
          ], ["14%", "44%", "42%"]),
          p("写下来的意义不在于预测未来，而在于<strong>让未来的你无法悄悄改规则</strong>。"
            "这与工程里把 SLO、回滚条件与值班手册提前写死是同一个道理。"),
      )),
      ("31.2", "复盘要看决策质量，不只看收益", sec(
          p("好决策可能亏钱，坏决策可能赚钱。年度复盘应至少回答四问："
            "是否遵守了 IPS？偏离时有没有记录理由？收益来自配置、选股、因子还是运气（第 27 章归因）？"
            "成本与税能否再降（第 05 章）？"
            "把答案与当时的市场信息一起存进决策日志，才能避免用结果反推过程。"),
      )),
      ("31.3", "全书收束：一条可复现的链路", sec(
          eq("目标(IPS) → 产品(03) → 定价(09–12) → 组合(13–14) → 盘面(15–20) → "
             "证据(21–28) → 执行(29) → 风险(30) → 复盘(31)"),
          p("这条链路的每一环都可以用本书的 Python 脚本替换成你自己的数据与参数："
            "改参数 → 重跑 → 看图 → 写结论。<strong>把投资变成可复现的工程，"
            "是这门课唯一想留下的习惯。</strong>"),
          note("最后一句", "所有示例都是合成数据与模型示意，不构成投资建议、产品推荐或收益承诺。"
               "真实投资请遵守所在市场的法规、适当性要求与风险揭示。"),
      )),
  ],
  demos=[mk_demo(
      "code/31-ips.py", "实验 31-1 · 按 IPS 执行的五年账户与复盘表",
      "模拟月度定投、阈值再平衡与决策日志，输出 TWR/MWR、费用与合规检查。",
      """YEARS, ANN = 5, 12
MONTHS = YEARS * ANN
MONTHLY = 5000.0           # 每月投入
TARGET, BAND = 0.70, 0.03  # 股票目标权重与再平衡带
FEE = 0.001                # 调仓成本率""",
      """rng = random.Random(7)
rs, rb = [], []
for i in range(MONTHS):
    z, z2 = rng.gauss(0, 1), rng.gauss(0, 1)
    rs.append((0.012 if i < 30 else -0.004) + 0.045 * z)
    rb.append(0.0015 + 0.008 * (-0.15 * z + math.sqrt(1 - 0.0225) * z2))

cash_in, value, stock_part, bond_part = 0.0, 0.0, 0.0, 0.0
unit, w_prev = 1.0, TARGET
values, contributed, weights, log = [], [], [], []
for i in range(MONTHS):
    unit *= (1 + w_prev * rs[i] + (1 - w_prev) * rb[i])
    cash_in += MONTHLY
    stock_part += MONTHLY * TARGET
    bond_part += MONTHLY * (1 - TARGET)
    stock_part *= (1 + rs[i])
    bond_part *= (1 + rb[i])
    value = stock_part + bond_part
    w = stock_part / value
    if abs(w - TARGET) > BAND:
        trade = abs(TARGET - w) * value
        value -= trade * FEE
        stock_part, bond_part = value * TARGET, value * (1 - TARGET)
        w = TARGET
        log.append((i, "再平衡", round(trade, 0)))
    w_prev = w
    values.append(value)
    contributed.append(cash_in)
    weights.append(w)

twr = unit - 1
cf = [0.0] * (MONTHS + 1)
for i in range(MONTHS):
    cf[i] -= MONTHLY
cf[-1] += values[-1]

def npv(rate):
    return sum(c / (1 + rate) ** i for i, c in enumerate(cf))

lo, hi = -0.30, 0.30
for _ in range(120):
    mid = (lo + hi) / 2
    if npv(mid) > 0:
        lo = mid
    else:
        hi = mid
mwr = (1 + (lo + hi) / 2) ** ANN - 1

c = Chart(FIG / "31-plan.svg", "账户价值与累计投入", xlabel="月", ylabel="金额")
c.line(range(MONTHS), values, BLUE, label="账户价值")
c.line(range(MONTHS), contributed, GREEN, label="累计投入")
print("计划图:", c.save())
d = Chart(FIG / "31-drift.svg", "股票权重与 IPS 再平衡带", xlabel="月", ylabel="权重")
d.line(range(MONTHS), weights, AMBER, label="实际权重")
d.hline(TARGET, BLUE, label="目标 70%")
d.hline(TARGET + BAND, RED, label="上界")
d.hline(TARGET - BAND, RED, label="下界")
print("权重图:", d.save())
max_drift = max(abs(w - TARGET) for w in weights)
print("期末账户=%.0f 累计投入=%.0f TWR(单位净值)=%.2f%% MWR年化=%.2f%%" %
      (values[-1], cash_in, 100 * twr, 100 * mwr))
print("决策日志 %d 条 | 最大偏离=%.2f%% 带宽=%.1f%% | 合规=%s" %
      (len(log), 100 * max_drift, 100 * BAND, "是" if max_drift <= BAND + 0.02 else "需复核"))""",
      [("fig/31-plan.svg", "账户价值与累计投入的长期轨迹"),
       ("fig/31-drift.svg", "股票权重与 IPS 再平衡带")],
      "把 <code>BAND</code> 改成 0.15，观察决策日志条数与最大偏离；再改回 0.03 比较费用。",
      "阈值再平衡让权重始终落在事先声明的带内，决策日志把每次偏离都变成可审计记录。"
      "TWR 与 MWR 不同是因为存在持续现金流，两者分别回答「策略」与「投资者」的问题。",
      "把 <code>MONTHLY</code> 设为 0 并给初始资金，TWR 与 MWR 应趋于一致。")],
  highlights=[("ips", "投资政策说明书的标准要素"),
              ("twr", "时间加权收益与策略评估"),
              ("mwr", "资金加权收益与投资者体验"),
              ("spiva", "长期主动/被动业绩对照，用于校准预期")],
  analogy="IPS 是配置文件 + SLO + 变更日志：目标权重是 config，再平衡带是告警阈值，"
          "决策日志是 audit log。<strong>没有日志的系统无法复盘，也无法证明自己没有临场改规则。</strong>",
  bridge="全书终章。回望 {{ch:00}} 提出的七层工程分解：目标、约束、数据、假设、检验、执行、复盘，"
         "到本章正好闭环。",
  pitfalls=["把 IPS 写成收益目标而不是约束与流程。",
            "行情不利时临时放宽再平衡带且不留记录。",
            "用结果好坏评价决策质量。",
            "复盘只看收益率，不看费用、税、归因与合规。"],
  exercises=["写一份自己的 IPS，至少包含四条带数值的硬约束与两条例外条款。",
             "在示例里加入「偏离超带但延迟一个月才调仓」，量化成本与合规差异。",
             "设计一份年度复盘模板，列出至少六项指标与各自的判断标准。"],
  further=["回看 {{home#roadmap}} 与 {{home#toc}}；公式与术语见附录 A；资源总表见 {{home#resources}}。"]),

# ==================================================================== A
C("A", "pa", "appendix", "公式速查、术语表与工具索引",
  "把全书的可查内容收在一页：公式、术语、界面字段、常见坑与全部实例索引。",
  hours="随时查阅",
  goals=["能快速定位全书任何一条公式与对应章节。",
         "能把产品、账户、指标术语映射到统一的英文与数据字段。",
         "能在上线前用检查清单逐项自查。",
         "能找到全书 Python 实例、参考资源与工业库对照。"],
  points=["收益与风险公式", "定价与组合公式", "指标公式", "绩效与风险公式",
          "中英术语对照", "交易界面字段", "上线检查清单", "示例与资源索引"],
  sections=[
      ("A.1", "全书公式速查", sec(
          table(["主题", "公式", "章节"], [
              ["实际收益", "1 + r_实际 = (1 + r_名义)/(1 + π) − 1", "01"],
              ["波动拖累", "g ≈ μ − σ²/2", "01"],
              ["最大回撤", "MDD = min(V_t / peak_t − 1)", "02"],
              ["债券价格", "P(y) = Σ C/(1+y)^t + F/(1+y)^T", "08、09"],
              ["修正久期 / 凸性", "D_mod = −(1/P)dP/dy；C = (1/P)d²P/dy²", "09"],
              ["两阶段 DCF", "V₀ = ΣFCF_t/(1+r)^t + TV/(1+r)^n", "10"],
              ["看跌-看涨平价", "C − P = S₀ − K·e^(−rT)", "12"],
              ["组合方差", "σ_p² = wᵀΣw", "13"],
              ["夏普 / 信息比率", "(μ − r_f)/σ；(μ_p − μ_b)/σ_(p−b)", "13、27"],
              ["MACD / RSI / %B", "DIF=EMA12−EMA26；RSI=100−100/(1+RS)；%B=(P−下轨)/(上轨−下轨)", "18"],
              ["三因子模型", "r_i − r_f = α + β_m MKT + β_s SMB + β_h HML + ε", "21"],
              ["凯利上界", "f* ≈ μ/σ²", "30"],
              ["Brinson 归因", "配置 + 选股 + 交互 = r_p − r_b", "27"],
          ], ["26%", "62%", "12%"]))),
      ("A.2", "术语与数据字段对照", sec(
          table(["中文", "英文 / 缩写", "数据字段或口径"], [
              ["开高低收", "OHLC", "open / high / low / close，须满足 low ≤ min(o,c) ≤ max(o,c) ≤ high"],
              ["前复权 / 后复权", "adjusted close", "adj_factor；前复权随新公司行动整体变化"],
              ["净值 / 折溢价", "NAV / premium", "price/NAV − 1"],
              ["跟踪误差", "tracking error", "stdev(r_fund − r_index)"],
              ["买卖价差", "bid-ask spread", "ask_1 − bid_1"],
              ["时间加权 / 资金加权", "TWR / MWR", "TWR 剔除现金流；MWR 为 IRR"],
              ["样本外", "out of sample", "参数冻结后未参与选择的数据段"],
              ["前视偏差", "look-ahead bias", "特征使用了 t 时刻尚不可得的数据"],
              ["投资政策说明书", "IPS", "目标、约束、规则、例外、复盘的书面契约"],
          ], ["24%", "24%", "52%"]))),
      ("A.3", "交易界面的共同字段", sec(
          p("富途牛牛、东方财富 / 东方赢家一类终端的栏目划分不同，但字段结构高度相似。"
            "本书只抽象这些<strong>共同字段</strong>，不评价任何平台或具体产品："),
          table(["分组", "字段", "读图/下单前必须确认"], [
              ["标的", "代码、名称、市场、币种", "同名不同市场、最小交易单位、是否含衍生品"],
              ["价格", "现价、昨收、涨跌、买一/卖一", "是否复权、线性还是对数坐标、集合竞价口径"],
              ["量", "成交量、成交额、换手率、五档深度", "是否含 ETF 申赎、索引调样"],
              ["规则", "交易时段、T+n、涨跌停、风险等级", "回测是否建模了不可成交日"],
              ["成本", "佣金、印花税、管理费、申赎费", "毛收益与净收益的差额"],
          ], ["14%", "38%", "48%"]))),
      ("A.4", "上线前十条检查", sec(
          ul(["价格是否已复权？公司行动与分红口径是否记录版本？",
              "所有特征是否只用 <code>history_up_to_t</code>？信号是否在下一根成交？",
              "是否用当前成分股/当前存活基金回测历史？",
              "涨跌停、停牌、最小报价单位与交收规则是否建模？",
              "手续费、价差、冲击、借券费与税是否逐笔计提？",
              "参数在样本外评估之前是否已冻结？试过多少组参数是否报告？",
              "是否同时给出持有基准、零成本版与随机信号对照组？",
              "是否报告净夏普、最大回撤、CVaR、换手与容量，而不只报收益率？",
              "仓位、杠杆、集中度、回撤四类硬约束是否有触发动作？",
              "IPS、决策日志与数据 manifest 是否归档，能否被第三方复跑？"]),
          warn("免责声明", "本附录与全书所有数值均为合成数据或模型示意，不构成投资建议、"
               "产品推荐或收益承诺；历史与回测表现不代表未来收益。"))),
  ],
  demos=[],
  highlights=[("cfa", "从业者教育框架与术语标准"),
              ("investopedia", "产品、账户与指标的术语速查"),
              ("mit-ocw", "投资学与资产定价的免费课程"),
              ("python-docs", "本书全部脚本的语言与标准库参考")],
  analogy="附录是全书的 <code>README + API reference + checklist</code>："
          "A.1 是函数签名，A.2 是类型定义，A.3 是外部接口字段，A.4 是 CI 检查项，"
          "A.5～A.7 由生成器自动维护，永远与正文同步。",
  bridge="全书速查入口。示例索引用 A.5、手写实现与工业库对照用 A.6、"
         "外部链接总表用 A.7；章节目录见 {{home#toc}}。",
  pitfalls=["把速查公式当成可直接下单的规则。",
            "忽略公式的适用条件（如 r &gt; g、收益率曲线平行移动）。",
            "只看字段名称、不核对口径与币种。",
            "把检查清单当成一次性任务，而不是每次实验都跑的 CI。"],
  exercises=["为 A.1 中任意三条公式写出对应的 Python 实现。",
             "给自己常用的交易终端填一遍 A.3 的字段表，标出你尚未确认的三项。",
             "把 A.4 的检查项写成一个可执行的自检脚本。"],
  further=["全书目录 {{home#toc}}；使用说明 {{home#howto}}；参考资源 {{home#resources}}；维护约定 {{home#contribute}}。"]),

]
