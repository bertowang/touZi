#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 24～29 章：论文复现、数据管道、回测、绩效、过拟合与执行。"""
from __future__ import annotations

from book_schema import C, eq, table
from chapter_kit import mk_demo, p, ul, note, warn, sec

CH = [

# ==================================================================== 24
C("24", "p4", "part4/24-read-papers", "怎样读一篇因子论文：从摘要到可复现",
  "论文的结论是一个条件命题：先读条件，再读结论。",
  hours="3 学时",
  goals=["能列出论文复现所需的最小信息清单。",
         "能识别样本选择、成本假设与样本外声明中的漏洞。",
         "能量化「选择性剔除 + 零成本」对夏普的抬升。",
         "能把论文的结论写成可检验的 H0 与评估协议。"],
  points=["样本期与样本外", "组合构建口径", "成本与容量假设", "数据来源与 point-in-time",
          "t 值与多重检验", "选择性剔除与幸存者", "夏普比率的敏感性", "复现协议"],
  sections=[
      ("24.1", "一份最小复现清单", sec(
          table(["项目", "必须问清", "缺失时的后果"], [
              ["样本", "起止时间、市场、剔除规则", "无法判断是否做过样本选择"],
              ["数据", "价格复权、退市/停牌处理、可用时刻", "幸存者偏差与前视偏差"],
              ["组合", "权重、调仓频率、多空约束", "权重口径不同可得相反结论"],
              ["成本", "佣金、价差、冲击、借券费", "毛夏普无法转成净收益"],
              ["推断", "t 值、Newey-West、检验次数", "多重检验下的假发现"],
              ["样本外", "参数何时固定、是否真未使用", "样本内过拟合"],
          ], ["16%", "42%", "42%"]),
          p("读论文时把这张表当成<strong>接口契约</strong>：任何一格缺失，结论就只能算「有意思的观察」，"
            "还不能算可执行的证据。"),
      )),
      ("24.2", "夏普比率对成本与样本选择极敏感", sec(
          eq("Sharpe_net ≈ (μ_gross − cost) / σ × √252"),
          p("日频策略里，0.03% 的双边成本就能吃掉相当一部分日均值；"
            "而「剔除最差的 10% 交易日」这种看似无害的清洗，等价于用了未来信息做样本选择。"
            "两者叠加足以把一个无 alpha 的策略包装成高夏普。"),
      )),
      ("24.3", "把结论改写成协议", sec(
          ul(["<strong>H0</strong>：该因子在扣除成本后的样本外平均收益为 0。",
              "<strong>冻结</strong>：在开始评估前写死参数、样本切分与成本假设。",
              "<strong>评估</strong>：报告净夏普、t 值、最大回撤、换手与容量。",
              "<strong>复现</strong>：换数据源、换市场、换时间窗，看符号是否稳定。"]),
      )),
  ],
  demos=[mk_demo(
      "code/24-replication.py", "实验 24-1 · 同一策略的四种报告口径",
      "量化「选择性剔除 + 零成本 + 样本内」对夏普的抬升，并与净额/样本外对照。",
      """N, SPLIT = 600, 300
MU, SIG = 0.0004, 0.010   # 合成策略的日均毛收益与波动
COST = 0.0003             # 每日双边成本
TRIM = 0.10               # 论文口径「剔除最差 10% 交易日」
ANN = 252""",
      """rng = random.Random(7)
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
      (s_paper, s_net, s_is, s_oos, s_paper - s_net))""",
      [("fig/24-sharpe.svg", "四种报告口径下的年化夏普对比"),
       ("fig/24-equity.svg", "论文口径与净额口径的净值曲线")],
      "把 <code>TRIM</code> 设为 0（不剔样本）、<code>COST</code> 设为 0，观察四种口径是否收敛。",
      "「剔掉最差 10% 交易日」与「不计成本」各自都能显著抬高夏普，且都不需要任何真实预测能力。"
      "样本外净额通常最低。<strong>报告口径本身就是结论的一部分。</strong>",
      "把 <code>MU</code> 设为 0（无真实 alpha），论文口径仍可能显示正夏普——这是纯样本选择的结果。")],
  highlights=[("ssrn", "金融学预印本与因子研究检索"),
              ("arxiv", "q-fin 量化金融预印本"),
              ("p-hacking", "多重检验下的假阳性膨胀"),
              ("spiva", "主动/被动长期业绩的公开统计")],
  analogy="读论文像做 code review：先看输入数据的 schema 与时间边界，再看有没有隐藏的全局常量，"
          "最后才看输出指标。<strong>缺少复现协议的漂亮结果，等于没有测试的 benchmark。</strong>",
  bridge="第四阶段以「怎样判断一个主张是否可信」收尾；"
         "{{ch:25}} 起进入第五阶段的第一部分：把评估协议落成可运行的数据与回测流水线。",
  pitfalls=["只看摘要里的夏普与 t 值，不读样本与成本附录。",
            "把作者自己报告的「样本外」当成真正的样本外。",
            "忽略因子数量与检验次数。",
            "用自己的数据口径复现失败后直接归咎于市场变化。"],
  exercises=["给一篇真实论文填本章的最小复现清单，指出至少两处缺失信息。",
             "在示例里加入 Newey-West 调整的思路，说明自相关怎样影响 t 值。",
             "写出一份「评估前冻结」的 JSON 配置，列出所有参数与数据版本。"],
  further=["{{ch:25}} point-in-time 数据；{{ch:28}} 多重检验与滚动样本外；{{ch:31}} 复盘协议。"]),

# ==================================================================== 25
C("25", "p5", "part5/25-data-pipeline", "数据管道：对齐、公司行动与幸存者偏差",
  "回测里最贵的 bug 不在策略，而在数据：看不见的样本已经替你把收益抬高了。",
  hours="3 学时",
  goals=["能描述一条 point-in-time 数据管道的各个阶段。",
         "能解释幸存者偏差如何抬高基金/指数回测收益。",
         "能处理停牌、退市、拆股与成分股历史变更。",
         "能为数据快照写明版本、可用时刻与来源。"],
  points=["point-in-time 快照", "数据版本与可用时刻", "公司行动对齐", "停牌与退市处理",
          "成分股历史", "幸存者偏差", "前视偏差", "可复现的数据契约"],
  sections=[
      ("25.1", "一条可信的数据管道", sec(
          ul(["<strong>采集</strong>：行情、净值、财报、公司行动、指数成分，各带发布时间与来源。",
              "<strong>对齐</strong>：统一交易日历、时区、币种；缺失值显式编码为「未成交 / 未披露」。",
              "<strong>版本化</strong>：每条记录带 <code>as_of</code>（何时可知）与 <code>effective</code>（何时生效）。",
              "<strong>快照</strong>：回测只读取 <code>as_of ≤ t</code> 的数据，禁止读取后来修订过的版本。",
              "<strong>校验</strong>：复权不变式、价格非负、成分股权重和为 1、无未来时间戳。"]),
          p("第 06 章处理了价格口径，本章处理<strong>时间口径</strong>："
            "财报会被追溯修订，指数成分会被回溯调整，基金清盘后数据常被从数据库里删除。"
            "三者都会让历史回测「自动变好看」。"),
      )),
      ("25.2", "幸存者偏差是可以量化的", sec(
          eq("偏差 = E[r | 存活到期末] − E[r | 全部样本（含清盘）]"),
          p("若表现差的基金被清盘并从历史库里移除，那么「用今天还活着的基金回测过去」"
            "等价于<strong>提前删掉所有失败路径</strong>。这不是小误差，而是对收益分布的条件化裁剪。"),
      )),
      ("25.3", "把数据契约写进代码", sec(
          p("建议每个数据集都配一份 <code>manifest</code>：来源 URL、拉取时间、字段 schema、"
            "复权方式、公司行动版本、缺失语义与校验和。回测启动时打印这份 manifest，"
            "让每次实验都能被第三方复跑。这与软件工程里的依赖锁文件是同一个思想。"),
      )),
  ],
  demos=[mk_demo(
      "code/25-survivorship.py", "实验 25-1 · 基金清盘造成的幸存者偏差",
      "合成 200 只基金，差的被清盘；比较「只看存活基金」与「含清盘全样本」的指数收益。",
      """N_FUNDS, N_DAYS = 200, 500
ANN = 252
SIG = 0.012        # 日波动
KILL = 0.65        # 净值跌破该比例即清盘
LIQUID = -0.05     # 清盘时的额外损失""",
      """rng = random.Random(7)
funds, alive_by_day = [], [0] * N_DAYS
for _ in range(N_FUNDS):
    mu = rng.gauss(0.0002, 0.0004)      # 管理人能力异质
    v, row, alive = 1.0, [], True
    for t in range(N_DAYS):
        if alive:
            r = rng.gauss(mu, SIG)
            v *= (1 + r)
            if v < KILL:
                r += LIQUID
                alive = False
            else:
                alive_by_day[t] += 1
            row.append(r)
        else:
            row.append(0.0)             # 清盘后资金回到指数（简化）
    funds.append((row, alive))

survivors = [p for p, a in funds if a]
biased = [statistics.fmean(p[t] for p in survivors) for t in range(N_DAYS)]
unbiased = [statistics.fmean(p[t] for p, _a in funds) for t in range(N_DAYS)]

def curve(rets):
    v, out = 1.0, [1.0]
    for r in rets:
        v *= (1 + r)
        out.append(v)
    return out

cb, cu = curve(biased), curve(unbiased)
cagr_b = cb[-1] ** (ANN / N_DAYS) - 1
cagr_u = cu[-1] ** (ANN / N_DAYS) - 1

c = Chart(FIG / "25-survivorship.svg", "只看存活基金 vs 含清盘全样本", xlabel="交易日", ylabel="净值")
c.line(range(N_DAYS + 1), cb, RED, label="只看存活（有偏）")
c.line(range(N_DAYS + 1), cu, BLUE, label="全样本（无偏）")
print("净值图:", c.save())
f = Chart(FIG / "25-funnel.svg", "随时间存活的基金数量", xlabel="交易日", ylabel="只数")
f.line(range(N_DAYS), alive_by_day, GREEN, label="存活基金")
print("存活图:", f.save())
print("期初=%d 期末存活=%d | 有偏年化=%.2f%% 无偏年化=%.2f%% 偏差=%+.2f 个百分点" %
      (N_FUNDS, len(survivors), 100 * cagr_b, 100 * cagr_u, 100 * (cagr_b - cagr_u)))""",
      [("fig/25-survivorship.svg", "有偏与无偏指数净值的分离"),
       ("fig/25-funnel.svg", "基金样本随时间减少的漏斗")],
      "把 <code>KILL</code> 改成 0.0（永不退市），观察两条曲线是否重合；再收紧到 0.85 看偏差放大。",
      "存活样本池随时间缩小；只用「今天还活着」的基金回测，年化收益被系统性抬高。"
      "这与第 24 章的选择性剔除是同一类错误，只是发生在<strong>标的物维度</strong>而非时间维度。",
      "把 <code>LIQUID</code> 改成 −0.20（清盘损失更大），有偏与无偏的差距会进一步扩大。")],
  highlights=[("survivorship", "幸存者偏差的定义与经典案例"),
              ("adjusted-close", "公司行动与复权口径"),
              ("pandas", "时间序列对齐与分组的工业实现"),
              ("akshare", "中文行情与基金数据的开源接口")],
  analogy="数据仓库里的 <code>DELETE FROM funds WHERE status='liquidated'</code> "
          "会让回测自动获得前视能力。正确做法是软删除 + <code>as_of</code> 字段，"
          "让查询条件写成 <code>as_of &lt;= t</code>。",
  bridge="第 24 章给出评估协议，本章给出支撑协议的数据层；"
         "{{ch:26}} 在此基础上实现事件驱动回测引擎。",
  pitfalls=["用当前指数成分股回测十年前（成分股幸存者偏差）。",
            "使用被追溯修订过的财报数据。",
            "把停牌日填成 0 收益，人为降低波动。",
            "前复权序列更新后仍沿用旧回测结果，未重新生成。"],
  exercises=["写出一份数据 manifest 的字段清单，并说明每个字段如何被校验。",
             "在示例里加入「清盘基金收益继续按指数计」与「按 0 计」两种口径，比较差异。",
             "举一个「财报追溯修订」导致前视偏差的具体路径。"],
  further=["{{ch:26}} 回测引擎；{{ch:28}} 样本外协议；{{ch:20}} 未来函数。"]),

# ==================================================================== 26
C("26", "p5", "part5/26-backtest", "事件驱动回测引擎：从信号到成交",
  "回测不是向量化的乘法，而是一条有状态、有时序、有成本的事件链。",
  hours="3 学时",
  goals=["能写出事件驱动回测的主循环与账户状态。",
         "能说明 t 时刻信号必须在 t+1 成交。",
         "能把手续费、滑点与资金约束写进每次成交。",
         "能量化「同根成交」假设带来的虚假收益。"],
  points=["事件循环与账户状态", "信号—下单—成交时序", "同根成交的错误", "手续费与滑点",
          "仓位与资金约束", "订单状态机", "基准与对照", "回测的可复现性"],
  sections=[
      ("26.1", "最小可用引擎的五个状态", sec(
          p("一个事件驱动引擎至少要维护：<code>cash</code>、<code>position</code>、"
            "<code>pending_orders</code>、<code>last_signal</code>、<code>equity</code>。"
            "每根 K 线依次执行：<strong>接收行情 → 更新持仓市值 → 计算信号 → 生成订单 → "
            "按下一根可成交价格撮合 → 计费与交割 → 记录快照</strong>。"),
          warn("时序铁律", "信号在 <code>t</code> 收盘后产生，最早只能在 <code>t+1</code> 成交。"
               "任何 <code>equity[t] *= (1 + signal[t] * ret[t])</code> 都在用还没发生的收盘价下已经知道的信号。"),
      )),
      ("26.2", "成本必须发生在成交那一刻", sec(
          eq("净收益 = Σ (exposure_t × r_(t+1)) − Σ (fee_t + slippage_t + 借券费_t)"),
          p("把成本写成「年底统一减 1%」会掩盖高换手策略的真实衰减："
            "成本与信号频率、成交量、波动同时相关，必须逐笔计提。"
            "第 29 章会把滑点从常数升级为订单规模的函数。"),
      )),
      ("26.3", "对照实验比漂亮净值更重要", sec(
          table(["对照组", "目的"], [
              ["始终持有", "检验择时是否真的加了价值"],
              ["同根成交（错误版）", "量化前视偏差有多大"],
              ["零成本版", "分离信号质量与成本拖累"],
              ["随机信号", "给出一个不依赖策略的基线分布"],
          ], ["30%", "70%"]),
      )),
  ],
  demos=[mk_demo(
      "code/26-backtest.py", "实验 26-1 · 事件驱动主循环与「同根成交」泄漏",
      "实现信号→下一根成交→计费的状态链，并与错误版、零成本版、持有基准对照。",
      """N, W = 400, 10
START, DRIFT, VOL = 50.0, 0.0004, 0.014
FEE = 0.0005       # 换仓费率
SLIP = 0.0003      # 换仓滑点""",
      """rng = random.Random(7)
px, prices = START, []
for _ in range(N):
    px *= (1 + rng.gauss(DRIFT, VOL))
    prices.append(px)
rets = [prices[t] / prices[t - 1] - 1 for t in range(1, N)]
sig = [0] * N
for t in range(W, N):
    sig[t] = 1 if prices[t] > statistics.fmean(prices[t + 1 - W:t + 1]) else 0

def run(mode, with_cost=True):
    v, eq_curve, prev, trades, cost = 1.0, [1.0], 0, 0, 0.0
    for t in range(1, N):
        exposure = sig[t] if mode == "same_bar" else sig[t - 1]
        r = rets[t - 1]
        if exposure != prev:
            trades += 1
            if with_cost:
                slip = SLIP
                v *= (1 - FEE)
                cost += FEE + slip
            else:
                slip = 0.0
        else:
            slip = 0.0
        v *= (1 + exposure * (r - slip))
        prev = exposure
        eq_curve.append(v)
    return eq_curve, trades, cost

naive, naive_trades, _ = run("same_bar", False)
legal_nc, trades, _ = run("next_bar", False)
legal, _t2, total_cost = run("next_bar", True)
hold, v = [1.0], 1.0
for r in rets:
    v *= (1 + r)
    hold.append(v)

c = Chart(FIG / "26-backtest.svg", "四种口径的账户净值", xlabel="交易日", ylabel="净值")
c.line(range(N), naive, RED, label="同根成交（含前视偏差）")
c.line(range(N), legal_nc, AMBER, label="下一根成交 · 零成本")
c.line(range(N), legal, BLUE, label="下一根成交 · 扣费")
c.line(range(N), hold, GREEN, label="始终持有")
print("净值图:", c.save())
b = Chart(FIG / "26-cost.svg", "终值对照", xlabel="口径", ylabel="净值",
          xticks=[(i, n) for i, n in enumerate(["同根成交", "零成本", "扣费", "持有"])])
b.bars(range(4), [naive[-1], legal_nc[-1], legal[-1], hold[-1]], BLUE, label="期末净值")
b.hline(1.0, "#9aa6b2")
print("对照图:", b.save())
print("同根成交=%.3f 零成本=%.3f 扣费=%.3f 持有=%.3f | 换仓 %d 次 累计成本=%.4f | 泄漏=%.3f" %
      (naive[-1], legal_nc[-1], legal[-1], hold[-1], trades, total_cost,
       naive[-1] - legal_nc[-1]))""",
      [("fig/26-backtest.svg", "四种口径的净值曲线"),
       ("fig/26-cost.svg", "期末净值对照柱状图")],
      "对照 <code>泄漏</code> 数值；把 <code>FEE</code> 与 <code>SLIP</code> 同时设为 0，两条合法曲线应重合。",
      "同根成交版把「收盘后才知道的信号」用于同一根收益，净值被系统性抬高；"
      "下一根成交 + 逐笔计费才是可执行的口径。<strong>差额就是泄漏量。</strong>",
      "把 <code>W</code> 改成 3，换仓次数增加，观察成本项如何放大。")],
  highlights=[("backtesting", "回测流程与常见陷阱"),
              ("lookahead", "前视偏差的标准定义"),
              ("slippage", "成交价与预期价的差额"),
              ("backtrader", "事件驱动回测框架的参考实现")],
  analogy="回测引擎是一个状态机：<code>bar</code> 是事件，<code>order</code> 是待处理队列，"
          "<code>fill</code> 是下一个事件。<strong>把信号与成交放在同一个 tick，等于让请求先于响应返回。</strong>",
  bridge="第 25 章保证输入数据可信，本章保证执行时序可信；"
         "{{ch:27}} 用同一条净值曲线计算绩效，{{ch:28}} 检验参数是否过拟合。",
  pitfalls=["信号与成交同根，制造前视偏差。",
            "成本年底一次性扣除，忽略换手与成交时点的耦合。",
            "不检查资金是否足够、是否可做空、是否涨跌停不可成交。",
            "只报一条净值曲线，不给基准与对照组。"],
  exercises=["给示例加入「最多 80% 仓位」约束，说明引擎状态需要新增哪些字段。",
             "在涨跌停日让订单无法成交，观察净值与换仓次数的变化。",
             "写出随机信号对照组，重复 100 次得到终值分布，与策略结果比较。"],
  further=["{{ch:27}} 绩效与归因；{{ch:29}} 执行算法；{{ch:04}} 制度约束。"]),

# ==================================================================== 27
C("27", "p5", "part5/27-performance", "绩效度量与归因：夏普、回撤与 Brinson",
  "同一个组合，用不同指标可以讲出不同故事；先约定度量，再讨论好坏。",
  hours="3 学时",
  goals=["能计算夏普、索提诺、Calmar、信息比率与跟踪误差。",
         "能区分 TWR（策略收益）与 MWR（投资者体验收益）。",
         "能完成一次 Brinson 配置/选股/交互归因。",
         "能说明各指标的适用条件与盲点。"],
  points=["年化收益与波动", "夏普与索提诺", "最大回撤与 Calmar", "跟踪误差与信息比率",
          "TWR 与 MWR", "内部收益率 IRR", "Brinson 归因", "月度收益表"],
  sections=[
      ("27.1", "一张指标表与它的盲点", sec(
          table(["指标", "公式", "惩罚什么", "盲点"], [
              ["Sharpe", "(μ − r_f)/σ", "全部波动", "把大涨也算风险"],
              ["Sortino", "(μ − r_f)/σ_下行", "下行波动", "目标收益 MAR 人为设定"],
              ["Calmar", "年化收益 / |MDD|", "最深回撤", "只看一个历史极值"],
              ["信息比率", "(μ_p − μ_b)/σ_(p−b)", "相对基准的偏离波动", "依赖基准选择"],
              ["MDD", "min(V_t/peak_t − 1)", "路径痛苦", "不说明持续时间"],
          ], ["18%", "30%", "24%", "28%"]),
          p("第 02 章定义的五个风险量在这里全部派上用场："
            "<strong>只报一个比率，等于只报平均延迟</strong>。完整报告应同时给出收益、波动、回撤、"
            "尾部、换手与相对基准的差。"),
      )),
      ("27.2", "TWR 与 MWR：策略视角 vs 投资者视角", sec(
          eq("TWR = ∏(1 + r_t) − 1　|　MWR = 使 Σ CF_i / (1 + r)^i = 0 的 r"),
          p("TWR 剔除了外部现金流，衡量<strong>策略本身</strong>；MWR（IRR）把申赎时点算进去，"
            "衡量<strong>投资者实际体验</strong>。若你在大涨前追加、在回撤前赎回，"
            "TWR 很好看而 MWR 很难看——这不是矛盾，是两个不同的问题。"),
      )),
      ("27.3", "Brinson 归因：把超额收益拆成三块", sec(
          eq("配置效应 = Σ(w_p − w_b)·r_b　|　选股效应 = Σ w_b·(r_p − r_b)　|　交互 = Σ(w_p − w_b)·(r_p − r_b)"),
          p("三项之和等于组合收益减基准收益。工程上它就是一次<strong>逐项差分</strong>："
            "权重差 × 基准收益、基准权重 × 收益差、以及两者的乘积。"
            "归因能告诉你钱从哪里来，但不能告诉你是能力还是运气——那需要更长样本与第 28 章的检验。"),
      )),
  ],
  demos=[mk_demo(
      "code/27-performance.py", "实验 27-1 · 全套绩效指标、TWR/MWR 与 Brinson 归因",
      "合成 36 个月组合与基准收益，计算指标族、IRR 与两部门归因。",
      """N_MONTHS = 36
ANN = 12
RF_M = 0.02 / 12          # 月度无风险利率
CONTRIB = (12, 10.0)      # 第 12 个月追加投入
WP, WB = (0.60, 0.40), (0.50, 0.50)
RP, RB = (0.012, 0.004), (0.010, 0.005)""",
      """rng = random.Random(7)
port = [rng.gauss(0.008, 0.035) for _ in range(N_MONTHS)]
bench = [0.6 * p + rng.gauss(0.001, 0.020) for p in port]

def curve(rets):
    v, out = 1.0, [1.0]
    for r in rets:
        v *= (1 + r)
        out.append(v)
    return out

cp, cb = curve(port), curve(bench)
excess = [p - RF_M for p in port]
down = [min(0.0, x) for x in excess]
down_sd = math.sqrt(statistics.fmean(x * x for x in down))
sharpe = statistics.fmean(excess) / statistics.pstdev(port) * math.sqrt(ANN)
sortino = statistics.fmean(excess) / down_sd * math.sqrt(ANN) if down_sd else 0.0
peak, mdd = cp[0], 0.0
for v in cp:
    peak = max(peak, v)
    mdd = min(mdd, v / peak - 1)
cagr = cp[-1] ** (ANN / N_MONTHS) - 1
calmar = cagr / abs(mdd) if mdd else 0.0
active = [p - b for p, b in zip(port, bench)]
te = statistics.pstdev(active) * math.sqrt(ANN)
ir = statistics.fmean(active) * ANN / te if te else 0.0

acct = 100.0
for i, r in enumerate(port):
    if i == CONTRIB[0]:
        acct += CONTRIB[1]
    acct *= (1 + r)
cf = [-100.0] + [0.0] * N_MONTHS
cf[CONTRIB[0]] -= CONTRIB[1]
cf[-1] += acct

def npv(rate):
    return sum(c / (1 + rate) ** i for i, c in enumerate(cf))

lo, hi = -0.50, 0.50
for _ in range(120):
    mid = (lo + hi) / 2
    if npv(mid) > 0:
        lo = mid
    else:
        hi = mid
mwr_m = (lo + hi) / 2

alloc = sum((WP[i] - WB[i]) * RB[i] for i in range(2))
select = sum(WB[i] * (RP[i] - RB[i]) for i in range(2))
inter = sum((WP[i] - WB[i]) * (RP[i] - RB[i]) for i in range(2))
r_p, r_b = sum(WP[i] * RP[i] for i in range(2)), sum(WB[i] * RB[i] for i in range(2))

c = Chart(FIG / "27-equity.svg", "组合与基准的累计净值", xlabel="月", ylabel="净值")
c.line(range(N_MONTHS + 1), cp, BLUE, label="组合")
c.line(range(N_MONTHS + 1), cb, GREEN, label="基准")
print("净值图:", c.save())
matrix = [[100 * port[y * 12 + m] for m in range(12)] for y in range(3)]
heatmap(FIG / "27-monthly.svg", matrix, ["第1年", "第2年", "第3年"],
        ["M%d" % (m + 1) for m in range(12)], title="组合月度收益热力图（%）",
        vmin=-8, vmax=8)
print("月度图:", str(FIG / "27-monthly.svg"))
print("CAGR=%.2f%% Sharpe=%.3f Sortino=%.3f MDD=%.1f%% Calmar=%.3f TE=%.2f%% IR=%.3f" %
      (100 * cagr, sharpe, sortino, 100 * mdd, calmar, 100 * te, ir))
print("TWR=%.2f%% MWR年化=%.2f%% | Brinson 配置=%.3f%% 选股=%.3f%% 交互=%.3f%% 合计=%.3f%% (实际 %.3f%%)" %
      (100 * (cp[-1] - 1), 100 * ((1 + mwr_m) ** ANN - 1),
       100 * alloc, 100 * select, 100 * inter,
       100 * (alloc + select + inter), 100 * (r_p - r_b)))""",
      [("fig/27-equity.svg", "组合与基准的累计净值"),
       ("fig/27-monthly.svg", "三年月度收益热力图")],
      "核对 Brinson 三项之和是否等于 <code>r_p − r_b</code>；再改动 <code>CONTRIB</code> 的时点看 MWR 变化。",
      "TWR 只反映策略收益，MWR 把追加资金时点算进去，两者可以明显不同。"
      "Brinson 三项精确相加等于超额收益，是一次可逐项核对的差分分解。",
      "把 <code>WP</code> 改成与 <code>WB</code> 相同，配置效应与交互项应归零。")],
  highlights=[("sharpe", "夏普比率的定义与假设"),
              ("sortino", "下行波动口径的风险调整收益"),
              ("twr", "时间加权收益，剔除外部现金流"),
              ("attribution", "绩效归因的标准分解")],
  analogy="绩效指标是一组监控面板：Sharpe 是吞吐/抖动比，MDD 是最长故障，TE 是相对 SLO 的偏差，"
          "MWR 是用户实际感知的延迟。<strong>单看一块面板做容量决策一定会误判。</strong>",
  bridge="第 26 章产出可信的净值曲线，本章把它翻译成可比指标；"
         "{{ch:28}} 检验这些指标是否来自过拟合。",
  pitfalls=["用月度收益的标准差直接当年化波动，忘记乘 √12。",
            "把 TWR 当投资者实际收益，忽略申赎时点。",
            "更换基准后仍沿用旧的信息比率。",
            "Brinson 归因未覆盖全部资产或权重和不为 1。"],
  exercises=["推导 Brinson 三项之和等于 r_p − r_b。",
             "在示例里把追加资金挪到最大回撤前，比较 TWR 与 MWR 的差距。",
             "说明 Sortino 的 MAR 参数变化会怎样改变排序。"],
  further=["{{ch:28}} 样本内/外对照；{{ch:31}} 年度复盘与 IPS。"]),

# ==================================================================== 28
C("28", "p5", "part5/28-overfitting", "过拟合、多重检验与滚动样本外",
  "试了 20 组参数再挑最好的那一组，等于做了 20 次实验却只报告一次 p 值。",
  hours="3 学时",
  goals=["能量化参数网格搜索带来的样本内乐观偏差。",
         "能说明多重检验为何抬高假阳性率，并给出 Bonferroni 思路。",
         "能实现 walk-forward（滚动训练/验证）评估。",
         "能把「冻结协议」写成可执行的样本外切分。"],
  points=["样本内与样本外", "参数网格搜索", "多重检验与 Bonferroni", "数据窥探",
          "IS/OOS 夏普落差", "walk-forward", "冻结评估协议", "Deflated Sharpe 思想"],
  sections=[
      ("28.1", "搜索次数也是实验次数", sec(
          eq("P(至少一次假阳性) = 1 − (1 − α)^M　，M 为尝试过的策略/参数数"),
          p("α=0.05、M=20 时，至少出现一次「显著」结果的概率约 64%。"
            "这不是统计技巧的问题，而是<strong>报告口径的问题</strong>："
            "只报告胜出的那组参数，等于隐去了另外 19 次试验。"
            "Bonferroni 修正把单次阈值改成 α/M，是最保守也最容易实现的一层防线。"),
      )),
      ("28.2", "样本内最优 ≠ 样本外最优", sec(
          p("在合成数据上做网格搜索，可以清楚看到：样本内夏普最高的参数组合，"
            "在样本外往往只是中游。原因有两层：一是参数在样本内拟合了噪声，"
            "二是「挑最大值」这个动作本身带有正向选择偏差。"
            "第 24 章的论文复现清单在这里变成了一段可运行的实验。"),
      )),
      ("28.3", "walk-forward：把切分滚动起来", sec(
          ul(["把样本分成若干连续窗口，每个窗口<strong>只用前段</strong>选参数。",
              "在紧接着的后段（模型从未见过）执行并记录净收益。",
              "窗口整体前移，重复；最后把所有样本外段拼成一条净值曲线。",
              "报告这条曲线的夏普，而不是任何单段的最优值。"]),
          note("工程对应", "这等价于 <code>TimeSeriesSplit</code> 交叉验证。"
               "关键是<strong>不能打乱时间顺序</strong>，也不能让验证段的任何统计量回流到训练段。"),
      )),
  ],
  demos=[mk_demo(
      "code/28-overfit.py", "实验 28-1 · 16 组参数的样本内/外落差与滚动验证",
      "在同一条合成价格上扫描均线参数，比较 IS 最优组合的 OOS 排名与中位数。",
      """N, SPLIT = 800, 400
START, DRIFT, VOL = 50.0, 0.0003, 0.014
FAST_GRID = (3, 5, 10, 20)
SLOW_GRID = (20, 40, 60, 80)
FEE, ANN = 0.0005, 252
ALPHA = 0.05""",
      """rng = random.Random(7)
px, prices = START, []
for _ in range(N):
    px *= (1 + rng.gauss(DRIFT, VOL))
    prices.append(px)
rets = [prices[t] / prices[t - 1] - 1 for t in range(1, N)]

def sma(series, w):
    return [None if i + 1 < w else statistics.fmean(series[i + 1 - w:i + 1])
            for i in range(len(series))]

def sharpe(xs):
    s = statistics.pstdev(xs)
    return statistics.fmean(xs) / s * math.sqrt(ANN) if s else 0.0

def strategy(fast, slow):
    f, s = sma(prices, fast), sma(prices, slow)
    sig = [0] * N
    for t in range(N):
        if f[t] is not None and s[t] is not None:
            sig[t] = 1 if f[t] > s[t] else 0
    out = []
    for t in range(1, N):
        cost = FEE if t > 1 and sig[t - 1] != sig[t - 2] else 0.0
        out.append(sig[t - 1] * rets[t - 1] - cost)
    return out

rows, records = [], []
for fi, fast in enumerate(FAST_GRID):
    row = []
    for slow in SLOW_GRID:
        rr = strategy(fast, slow)
        is_s, oos_s = sharpe(rr[:SPLIT]), sharpe(rr[SPLIT:])
        row.append(is_s)
        records.append((fast, slow, is_s, oos_s))
    rows.append(row)

best = max(records, key=lambda x: x[2])
oos_sorted = sorted(x[3] for x in records)
rank = sum(1 for x in oos_sorted if x > best[3]) + 1
median_oos = statistics.median(oos_sorted)
bh_oos = sharpe(rets[SPLIT:])
m_tests = len(records)
fam_rate = 1 - (1 - ALPHA) ** m_tests

heatmap(FIG / "28-heatmap.svg", rows,
        ["fast=%d" % f for f in FAST_GRID], ["slow=%d" % s for s in SLOW_GRID],
        title="样本内夏普（%d 组参数）" % m_tests,
        vmin=min(min(r) for r in rows), vmax=max(max(r) for r in rows))
print("热力图:", str(FIG / "28-heatmap.svg"))
c = Chart(FIG / "28-isoos.svg", "样本内 vs 样本外夏普（每点一组参数）",
          xlabel="样本内夏普", ylabel="样本外夏普")
c.scatter([x[2] for x in records], [x[3] for x in records], BLUE,
          label="参数组合", radius=4)
c.scatter([best[2]], [best[3]], RED, label="IS 最优", radius=6)
c.hline(0.0, "#9aa6b2")
print("散点图:", c.save())
print("M=%d 至少一次假阳性概率=%.1f%% Bonferroni 单次阈值=%.4f" %
      (m_tests, 100 * fam_rate, ALPHA / m_tests))
print("IS 最优 fast=%d slow=%d IS=%.3f OOS=%.3f | OOS 排名=%d/%d 中位=%.3f 持有基准=%.3f" %
      (best[0], best[1], best[2], best[3], rank, m_tests, median_oos, bh_oos))""",
      [("fig/28-heatmap.svg", "16 组参数的样本内夏普热力图"),
       ("fig/28-isoos.svg", "样本内与样本外夏普的散点对照")],
      "观察 IS 最优点（红色）在 OOS 轴上的位置；把 <code>ALPHA</code> 固定，"
      "把参数网格扩大到 40 组，看 <code>1−(1−α)^M</code> 如何上升。",
      "样本内挑出的最优组合在样本外通常只排中游，甚至为负；"
      "M 次试验使「至少一次显著」的概率大幅上升。<strong>报告 M，或冻结协议</strong>，二者必须做到一个。",
      "把 <code>DRIFT</code> 改成 0（纯噪声），IS 与 OOS 夏普会趋近于无相关。")],
  highlights=[("overfitting", "样本内拟合与样本外失效"),
              ("data-snooping", "反复试参数造成的假发现"),
              ("walk-forward", "滚动训练/验证的样本外检验"),
              ("ssrn", "多重检验与因子动物园的方法论讨论")],
  analogy="调参是超参搜索，样本外是测试集。"
          "<code>max(trials)</code> 天然带有正向偏差，"
          "所以要么扣 Bonferroni，要么用 <code>TimeSeriesSplit</code> 把选择过程也纳入评估。",
  bridge="第 26～27 章给出可执行的净值与指标，本章检验它们是否只是搜索出来的幻觉；"
         "{{ch:29}} 开始处理真金白银下单时的最后一公里。",
  pitfalls=["试过很多参数只报告最好的一组。",
            "样本外段被用来反复调参，逐渐变成样本内。",
            "随机打乱时间序列做交叉验证。",
            "忽略交易成本对高频参数组合的额外惩罚。"],
  exercises=["推导 <code>1−(1−α)^M</code> 并计算 M=50 时的数值。",
             "在示例里实现三段 walk-forward，把样本外段拼成一条净值曲线。",
             "说明为什么「样本外也调过几次」会破坏评估的独立性。"],
  further=["{{ch:24}} 论文复现清单；{{ch:31}} 把冻结协议写进 IPS。"]),

# ==================================================================== 29
C("29", "p6", "part6/29-execution", "订单执行、滑点与市场冲击",
  "信号再好，也要经过「下单」这个有摩擦的物理过程才能变成账户里的钱。",
  hours="3 学时",
  goals=["能分解滑点：价差、临时冲击、永久冲击、时机风险。",
         "能模拟市价一次性、TWAP、VWAP 与限价单的成交结果。",
         "能说明成交量曲线与订单规模如何决定冲击。",
         "能把执行成本反馈到策略容量评估。"],
  points=["到达价与成交均价", "买卖价差", "临时与永久冲击", "市场冲击模型",
          "TWAP 与 VWAP", "限价单与成交不确定性", "拆单与时机风险", "容量评估"],
  sections=[
      ("29.1", "执行差额是一个可分解的量", sec(
          eq("Implementation Shortfall = 成交均价 − 决策到达价 = 价差 + 冲击 + 时机成本 + 机会成本"),
          p("第 15 章用订单簿算过一次静态冲击；本章加入<strong>时间维度</strong>："
            "拆得越细，单笔临时冲击越小，但暴露在价格漂移里的时间越长；"
            "拆得太快，又会推高永久冲击。这是一道明确的权衡题，不是「越慢越好」。"),
          table(["成本", "来源", "随什么增大"], [
              ["价差", "跨买卖档位", "流动性差、tick 大"],
              ["临时冲击", "短期吃掉深度", "单笔下单速度"],
              ["永久冲击", "订单被认为含信息", "累计成交量 / 日均量"],
              ["时机/机会成本", "等待期间价格漂移或未成交", "执行时长、限价偏离"],
          ], ["20%", "36%", "44%"]),
      )),
      ("29.2", "三种基准算法", sec(
          ul(["<strong>一次性市价</strong>：立即完成，冲击最大、时机风险最小。",
              "<strong>TWAP</strong>：按时间等分，实现简单，忽略真实成交量分布。",
              "<strong>VWAP</strong>：按历史成交量曲线分配，目标是贴近当日成交量加权均价。",
              "<strong>限价单</strong>：价格受保护，但可能只部分成交，剩余敞口成为机会成本。"]),
      )),
      ("29.3", "容量：策略能吃下多少钱", sec(
          p("若策略日均收益 μ、单次冲击成本 c(Q)，容量大致由 <code>μ × Q &gt; c(Q)</code> 决定。"
            "冲击通常随参与率超线性上升，所以<strong>提高资金规模会降低单位资金的净收益</strong>。"
            "报告策略时应同时给出净值曲线与容量估计，否则高夏普没有可执行含义。"),
      )),
  ],
  demos=[mk_demo(
      "code/29-execution.py", "实验 29-1 · 市价、TWAP、VWAP 与限价单的执行差额",
      "用 U 形成交量曲线与临时/永久冲击模型，比较四种执行方式的成交均价。",
      """Q = 100000         # 总订单量（股）
SLICES = 20        # 日内切片数
ARRIVAL = 10.00    # 决策到达价
ETA = 0.002        # 临时冲击系数
PERM = 0.0015      # 永久冲击系数
LIMIT_PX = 10.01   # 限价单价格上限""",
      """rng = random.Random(7)
base = [ARRIVAL]
for _ in range(SLICES):
    base.append(base[-1] * (1 + rng.gauss(0, 0.0008)))
vol_curve = [1.2 - 0.8 * math.sin(math.pi * t / (SLICES - 1)) for t in range(SLICES)]
tot_vol = sum(vol_curve)
vwap_q = [Q * v / tot_vol for v in vol_curve]
twap_q = [Q / SLICES] * SLICES
market_q = [Q] + [0.0] * (SLICES - 1)

def execute(qtys, limit=None):
    cum, cost, filled, marks = 0.0, 0.0, 0.0, []
    for t, q in enumerate(qtys):
        if q <= 0:
            marks.append(None)
            continue
        px = base[t] * (1 + PERM * cum / Q)
        temp = ETA * (q / (Q / SLICES))
        fill_px = px + temp
        if limit is not None and fill_px > limit:
            marks.append(None)
            continue
        cost += q * fill_px
        filled += q
        cum += q
        marks.append(fill_px)
    return (cost / filled if filled else 0.0), filled / Q, marks

results = {
    "市价一次性": execute(market_q),
    "TWAP": execute(twap_q),
    "VWAP": execute(vwap_q),
    "限价单": execute(twap_q, limit=LIMIT_PX),
}

c = Chart(FIG / "29-execution.svg", "基准价格与两类执行点", xlabel="日内切片", ylabel="价格")
c.line(range(SLICES), base[:SLICES], BLUE, label="无冲击基准价")
marks = results["TWAP"][2]
c.scatter([t for t, m in enumerate(marks) if m], [m for m in marks if m], GREEN,
          label="TWAP 成交价", radius=4)
mm = results["市价一次性"][2]
c.scatter([0], [mm[0]], RED, label="市价一次性", radius=6)
print("执行图:", c.save())

names = list(results)
slips = [10000 * (v[0] / ARRIVAL - 1) if v[0] else 0.0 for v in results.values()]
b = Chart(FIG / "29-slippage.svg", "四种执行方式的滑点（基点）", xlabel="方式", ylabel="bp",
          xticks=[(i, n) for i, n in enumerate(names)])
b.bars(range(len(names)), slips, AMBER, label="滑点 bp")
print("滑点图:", b.save())
print("到达价=%.3f | 滑点(bp) 市价=%.1f TWAP=%.1f VWAP=%.1f 限价=%.1f | 成交率 限价=%.0f%%" %
      (ARRIVAL, *slips, 100 * results["限价单"][1]))""",
      [("fig/29-execution.svg", "日内基准价格与不同执行点"),
       ("fig/29-slippage.svg", "四种执行方式的滑点对照")],
      "把 <code>ETA</code> 调大（流动性更差），观察市价一次性与拆单之间差距扩大；"
      "再放宽 <code>LIMIT_PX</code> 看限价单成交率上升。",
      "一次性市价单因临时冲击最大而滑点最高；TWAP/VWAP 通过拆单降低单笔冲击；"
      "限价单价格受保护但可能部分成交。<strong>滑点与成交率必须一起看。</strong>",
      "把 <code>Q</code> 翻倍，观察滑点是否线性放大——这正是策略容量的约束来源。")],
  highlights=[("limit-order", "限价单的价格保护与成交不确定性"),
              ("slippage", "成交价与预期价之差"),
              ("market-micro", "冲击成本与价格形成"),
              ("ibkr", "多市场订单类型与执行设置的界面示例")],
  analogy="执行是对一个有限队列做速率限制：一次性提交会触发限流（冲击），"
          "分片提交把峰值摊平但拉长延迟（时机风险）。"
          "<strong>吞吐与时延的权衡，在交易里同样成立。</strong>",
  bridge="第五阶段结束、第六阶段开始：{{ch:26}} 的回测里滑点是常数，"
         "本章把它变成订单规模的函数；{{ch:30}} 继续把「下多大」写成硬约束。",
  pitfalls=["回测里用收盘价成交，忽略到达价与成交价之差。",
            "只比较滑点，不比较成交率与未完成敞口。",
            "用当日成交量决定 VWAP 权重，引入未来信息。",
            "忽略涨跌停、停牌与最小报价单位对拆单的限制。"],
  exercises=["推导为什么临时冲击随参与率超线性上升会使容量有限。",
             "在示例里把 VWAP 曲线改成单调递增，观察成交均价如何变化。",
             "给限价单加入「未成交部分次日补单」，讨论机会成本如何计量。"],
  further=["{{ch:30}} 仓位与杠杆约束；{{ch:15}} 订单簿深度；{{ch:04}} 制度限制。"]),

]
