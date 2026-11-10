#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 06～11 章：行情数据模型、基金与固收、估值定价与指数套利。"""
from __future__ import annotations

from book_schema import C, eq, table
from chapter_kit import mk_demo, p, ul, note, warn, sec

CH = [

# ==================================================================== 06
C("06", "p1", "part1/06-data-model", "行情数据模型：OHLCV、复权与时间戳",
  "先校准数据，再谈策略：一根 K 线里最危险的不是价格，而是口径。",
  hours="3 学时",
  goals=["能写出一根 K 线的字段结构，并说明每字段的交易含义。",
         "能区分前复权、后复权与不复权，判断何时该用哪种。",
         "能识别拆股、分红造成的非交易性跳变并做修正。",
         "能说明时区、交易日历、缺失值与对齐如何造成伪信号。"],
  points=["OHLCV 数据结构", "成交量与成交额", "前复权与后复权", "拆股与公司行动",
          "除息与分红", "交易日历与时间戳", "时间序列对齐", "缺失值与停牌"],
  sections=[
      ("6.1", "一根 K 线是一个五元组加时间戳", sec(
          p("任何交易 App 的图表底层都是同一张表："
            "<code>(timestamp, open, high, low, close, volume, amount)</code>。"
            "K 线的周期（1 分钟 / 日 / 周）只是对逐笔成交的 <code>group by</code> 聚合："
            "open = 首笔、close = 末笔、high/low = 极值、volume = 求和。"),
          table(["字段", "聚合方式", "口径陷阱"], [
              ["open / close", "first / last", "集合竞价是否计入、收盘价是否为加权收盘价"],
              ["high / low", "max / min", "盘中瞬时插针，用错周期会消失"],
              ["volume", "sum", "拆股后股数翻倍，成交量口径需同步调整"],
              ["amount", "sum", "成交额含费用与否、币种换算"],
              ["timestamp", "group by key", "时区、交易日边界、是否用收盘时刻还是起始时刻"],
              ["adj_factor", "公司行动累积", "前复权会随新的公司行动整体改变历史值"],
          ], ["20%", "24%", "56%"]),
          p("关键结论：<strong>复权价不是行情，而是「为了可比较而构造的派生列」</strong>。"
            "真实下单用的是不复权价与当时的最小单位；做收益计算、回测与技术指标必须用复权后序列。"),
      )),
      ("6.2", "复权：把公司行动还原成连续收益", sec(
          eq("r_真实 ≈ (P_t × 调整因子_t) / (P_(t−1) × 调整因子_(t−1)) − 1"),
          p("1 股拆为 2 股时价格腰斩，但股东权益没变；若直接用不复权价算日收益，会得到一根 −50% 的假暴跌，"
            "进而触发所有止损、均线与波动指标。前复权把<strong>历史价格</strong>按比例缩小到当前口径，"
            "后复权把<strong>当前价格</strong>放大到历史口径；两者收益序列相同，绝对价格不同。"),
          ul(["<strong>不复权</strong>：还原当时可成交的价格，用于订单与盘口复盘。",
              "<strong>前复权</strong>：最新价格保持真实值，历史被缩放，看盘软件默认常用。",
              "<strong>后复权</strong>：起点价格保持真实值，后续被放大，做长期收益与回测最直观。",
              "<strong>注意</strong>：每次新增公司行动，前复权序列会整体变化，因此回测数据要记录快照版本（见第 25 章）。"]),
      )),
      ("6.3", "时间戳、对齐与缺失", sec(
          p("多资产分析要把不同交易日历、不同时区、不同停牌日对齐到同一条时间轴。"
            "三种常见错误：<code>forward fill</code> 把停牌日填成旧价制造零收益（低估波动）；"
            "用未来交易日的消息填充过去（数据泄漏）；把两个市场的收盘价直接相减（时差造成的伪相关）。"
            "工程上的正确做法是先定义<strong>统一日历与观察时刻</strong>，再 join，"
            "最后把「没成交」「没数据」「已退市」三类缺失显式编码，而不是静默填充。"),
          note("检查清单", "任何一条策略上线前，先问三句：价格复权了吗？时间戳是本地还是 UTC？"
               "缺失值是「没成交」还是「没数据」？"),
      )),
  ],
  demos=[mk_demo(
      "code/06-adjust.py", "实验 6-1 · 拆股造成的假暴跌与三种价格口径",
      "构造含一次 1 拆 2 的合成 OHLCV，比较不复权与前复权收益，并画出价格与收益对照。",
      """N = 60              # 交易日数
SPLIT_DAY = 30      # 拆股发生日
FACTOR = 2.0        # 1 股拆为 2 股
BASE = 20.0         # 起始价格
VOL = 0.015         # 日波动""",
      """rng = random.Random(7)
raw, px = [], BASE
for i in range(N):
    px *= (1 + rng.gauss(0.001, VOL))
    if i == SPLIT_DAY:
        px /= FACTOR
    raw.append(px)

adjusted = [v / FACTOR if i < SPLIT_DAY else v for i, v in enumerate(raw)]

ohlcv = []
for c in raw:
    o = c / (1 + rng.gauss(0, 0.004))
    h = max(o, c) * (1 + abs(rng.gauss(0, 0.003)))
    l = min(o, c) * (1 - abs(rng.gauss(0, 0.003)))
    v = int(1e6 * (1 + abs(rng.gauss(0, 0.3))))
    ohlcv.append((round(o, 3), round(h, 3), round(l, 3), round(c, 3), v))

raw_ret = [raw[i] / raw[i - 1] - 1 for i in range(1, N)]
adj_ret = [adjusted[i] / adjusted[i - 1] - 1 for i in range(1, N)]

c = Chart(FIG / "06-adjusted.svg", "拆股日前后：不复权价 vs 前复权价", xlabel="交易日", ylabel="价格")
c.line(range(N), raw, RED, label="不复权收盘价")
c.line(range(N), adjusted, BLUE, label="前复权收盘价")
c.vline(SPLIT_DAY, "#9aa6b2", label="拆股日")
print("价格图:", c.save())

r = Chart(FIG / "06-returns.svg", "同一个拆股日的日收益率", xlabel="交易日", ylabel="日收益")
r.line(range(1, N), raw_ret, RED, label="未复权（含假暴跌）")
r.line(range(1, N), adj_ret, GREEN, label="前复权（真实收益）")
r.hline(0.0, "#9aa6b2")
print("收益图:", r.save())
print("OHLCV 首行=%s" % (ohlcv[0],))
print("拆股日 未复权收益=%.2f%% 前复权收益=%.2f%% | 全期 未复权=%.2f%% 前复权=%.2f%%" %
      (100 * raw_ret[SPLIT_DAY - 1], 100 * adj_ret[SPLIT_DAY - 1],
       100 * (raw[-1] / raw[0] - 1), 100 * (adjusted[-1] / adjusted[0] - 1)))""",
      [("fig/06-adjusted.svg", "不复权价与前复权价的跳变对照"),
       ("fig/06-returns.svg", "复权前后的日收益率序列")],
      "观察 <code>raw_ret[29]</code> 附近的 −50% 尖峰；把 <code>FACTOR</code> 改成 1（无拆股）后尖峰应消失。",
      "不复权序列在拆股日产生约 −50% 的假收益，前复权序列保持连续。"
      "全期累计收益两者相差约一倍：这解释了为什么长期回测必须使用复权价。",
      "把 <code>SPLIT_DAY</code> 移到第 5 天，观察图形与累计收益如何变化。")],
  highlights=[("ohlc", "OHLC 四价的数据结构定义"),
              ("adjusted-close", "前复权/后复权与公司行动处理"),
              ("split", "拆股导致的价格与数量口径跳变"),
              ("akshare", "开源中文行情接口，便于课后替换真实数据")],
  analogy="复权因子是数据库里的<strong>版本化 migration</strong>：公司行动一到，历史行的含义就变了。"
          "不记录快照版本的回测，等于用今天的 schema 去解释昨天的数据。",
  bridge="第 04 章的规则产出「成交」，本章把这些成交整理成可计算的时间序列；"
         "{{ch:07}} 用同样的口径处理基金净值，{{ch:16}} 把 OHLCV 画成 K 线。",
  pitfalls=["用不复权价计算长期累计收益或均线。",
            "把前复权价格当成历史真实可成交价去下单。",
            "新增分红后未重新拉取前复权序列，导致历史回测结果悄悄变化。",
            "跨市场直接对齐收盘时刻，忽略时区与节假日差异。"],
  exercises=["推导为什么前复权与后复权的收益率序列完全相同（提示：两者只差一个常数因子）。",
             "给示例增加一次现金分红，写出对应的复权因子形式。",
             "列出三种「缺失值」语义，并说明各自应如何处理。"],
  further=["{{ch:16}} K 线与坐标；{{ch:25}} 数据管道与 point-in-time 快照；{{ch:26}} 回测中的价格口径。"]),

# ==================================================================== 07
C("07", "p1", "part1/07-funds-etf", "公募基金与 ETF：净值、申赎与跟踪",
  "基金不是一只股票，而是一份「按份额比例分配的组合净值」接口。",
  hours="3 学时",
  goals=["能说明场外基金申赎与 ETF 场内交易的区别。",
         "能计算 NAV、折溢价率与跟踪误差。",
         "能解释申赎套利为什么会把 ETF 价格拉回净值附近。",
         "能指出基金页面常见字段的口径（累计净值、单位净值、复权净值）。"],
  points=["单位净值与累计净值", "未知价申赎", "份额确认与到账", "ETF 一级与二级市场",
          "折溢价率", "申赎清单与套利", "跟踪误差与跟踪偏离", "费率与规模"],
  sections=[
      ("7.1", "两条交易链路", sec(
          ul(["<strong>场外开放式基金</strong>：按<strong>未知价</strong>向基金公司申赎，"
              "以当日收盘后计算的 NAV 成交；T 日申请、T+1 确认份额、赎回款再等若干日到账。",
              "<strong>ETF</strong>：二级市场像股票一样按盘中价格买卖；同时存在一级市场，"
              "授权参与商可用一篮子证券申购份额、或赎回换回一篮子，这是折溢价的收敛机制。"]),
          eq("NAV = (组合资产市值 − 负债) / 存续份额　|　折溢价率 = 场内价格 / NAV − 1"),
          p("净值字段要分清：<code>单位净值</code>是每份价格，<code>累计净值</code>加上历史分红，"
            "而做收益分析应该用<strong>复权净值</strong>（把分红再投资）。"
            "这与第 06 章的复权价是同一个思想。"),
      )),
      ("7.2", "跟踪误差不是「涨得少」", sec(
          eq("跟踪偏离 = r_基金 − r_指数　|　跟踪误差 = stdev(跟踪偏离)"),
          p("跟踪偏离是方向性偏差（费率、现金拖累、抽样复制），跟踪误差是波动。"
            "一只基金可以长期跑输指数 1%（偏离为负）但跟踪误差很小，说明它<strong>稳定地</strong>扣了成本；"
            "另一只基金平均打平但误差很大，说明复制机制不稳定。评估指数产品时两者都要看。"),
      )),
      ("7.3", "套利把溢价压回成本边界", sec(
          p("当 <code>|折溢价率| &gt; 申赎成本 + 冲击成本</code> 时，一级市场申购→二级卖出（或反向）"
            "存在无风险空间，套利资金会迅速把价差压回边界内。因此<strong>折溢价不是免费的择时信号</strong>，"
            "它更多反映流动性、停牌成分股与跨境时差。第 11 章会把这条机制写成可计算的边界。"),
          warn("别踩的坑", "跨境 ETF、商品 ETF 与含停牌成分股的 ETF 常出现较大且持续的折溢价，"
               "因为申赎受限、净值本身是滞后估计。看到「溢价 8%」先查申赎是否开放。"),
      )),
  ],
  demos=[mk_demo(
      "code/07-etf.py", "实验 7-1 · 净值、折溢价与申赎套利收敛",
      "合成指数与 ETF 净值，加入均值回复的折溢价与套利阻尼，计算跟踪误差与套利触发次数。",
      """N = 120             # 交易日
FEE_DAILY = 0.00002  # 管理费与现金拖累（按日）
TRACK_NOISE = 0.0004 # 抽样复制噪声
ARB_COST = 0.003     # 申赎 + 冲击成本边界
PREM_VOL = 0.002     # 折溢价冲击
PREM_AR = 0.85       # 折溢价自相关
ARB_DAMP = 0.55      # 套利发生后的收敛系数""",
      """rng = random.Random(7)
idx_ret = [rng.gauss(0.0004, 0.009) for _ in range(N)]
noise = [rng.gauss(0, TRACK_NOISE) for _ in range(N)]
noise_mean = statistics.fmean(noise)
noise = [e - noise_mean for e in noise]   # 去均值：让复制噪声只影响误差、不污染偏离
nav_ret = [r - FEE_DAILY + e for r, e in zip(idx_ret, noise)]

idx, nav, idx_v, nav_v = [], [], 1.0, 1.0
for ri, rn in zip(idx_ret, nav_ret):
    idx_v *= (1 + ri)
    nav_v *= (1 + rn)
    idx.append(idx_v)
    nav.append(nav_v)

prem, prem_series, arb_hits = 0.0, [], 0
for _ in range(N):
    if abs(prem) > ARB_COST:
        prem *= ARB_DAMP
        arb_hits += 1
    prem = PREM_AR * prem + rng.gauss(0, PREM_VOL)
    prem_series.append(prem)
price = [v * (1 + p) for v, p in zip(nav, prem_series)]

dev = [rn - ri for ri, rn in zip(idx_ret, nav_ret)]
tracking_error = statistics.pstdev(dev)
tracking_diff = statistics.fmean(dev)

c = Chart(FIG / "07-premium.svg", "ETF 折溢价率与套利成本边界", xlabel="交易日", ylabel="折溢价率")
c.line(range(N), prem_series, BLUE, label="折溢价率")
c.hline(ARB_COST, RED, label="套利上界")
c.hline(-ARB_COST, GREEN, label="套利下界")
c.hline(0.0, "#9aa6b2")
print("折溢价图:", c.save())
t = Chart(FIG / "07-tracking.svg", "指数与 ETF 净值（归一化）", xlabel="交易日", ylabel="净值")
t.line(range(N), idx, BLUE, label="标的指数")
t.line(range(N), nav, GREEN, label="ETF 净值")
print("跟踪图:", t.save())
print("年化跟踪误差=%.3f%% 日均跟踪偏离=%.5f%% | 平均|溢价|=%.3f%% 套利触发=%d 次" %
      (100 * tracking_error * math.sqrt(252), 100 * tracking_diff,
       100 * statistics.fmean(abs(x) for x in prem_series), arb_hits))""",
      [("fig/07-premium.svg", "折溢价率在套利成本边界附近被拉回"),
       ("fig/07-tracking.svg", "指数与基金净值的长期分离")],
      "把 <code>ARB_DAMP</code> 改成 1.0（套利失效），观察折溢价是否突破边界并持续不回归。",
      "套利阻尼让折溢价大多落在 ±成本边界内；跟踪误差主要来自复制噪声，"
      "而日均跟踪偏离主要由费率决定。<strong>稳定的负偏离与不稳定的误差是两件事。</strong>",
      "把 <code>FEE_DAILY</code> 提高十倍，跟踪偏离会明显变负，但跟踪误差几乎不变——验证两者的区别。")],
  highlights=[("nav", "基金份额净值的计算口径"),
              ("tracking-error", "跟踪误差的定义与使用"),
              ("etf", "一级/二级市场与申赎机制"),
              ("amac", "公募基金备案与行业数据")],
  analogy="基金份额是一个 <code>view</code>：NAV 是底层组合投影出的只读属性，申赎是对 view 的 insert/delete，"
          "折溢价则是两个不一致的数据副本之间的<strong>复制延迟</strong>。套利就是一致性修复进程。",
  bridge="第 06 章解决「价格序列可比」，本章解决「份额序列可比」；"
         "{{ch:11}} 把申赎机制写成无套利边界，{{ch:14}} 用基金实现资产配置。",
  pitfalls=["用单位净值直接算长期收益，漏掉分红。",
            "把场外基金按盘中价格申赎。",
            "把 ETF 的高溢价当作看涨信号，忽略申赎受限与净值滞后。",
            "只看跟踪误差，不看跟踪偏离的方向。"],
  exercises=["在示例中加入一次分红，说明单位净值、累计净值与复权净值各自怎么变。",
             "推导 <code>跟踪误差 × sqrt(252)</code> 年化的前提假设，并说明何时不成立。",
             "查一只跨境 ETF 的历史折溢价，判断它是否长期超出示例的成本边界。"],
  further=["{{ch:11}} 指数编制与折溢价套利；{{ch:14}} 用基金做资产配置；{{ch:27}} 相对基准的信息比率。"]),

# ==================================================================== 08
C("08", "p1", "part1/08-fixed-income", "债券、货币基金与逆回购：现金这一端",
  "组合里最不性感的一端，决定了你能不能活到策略生效的那一天。",
  hours="2 学时",
  goals=["能写出债券价格与到期收益率的折现关系。",
         "能解释利率上升为何使存量债券价格下跌。",
         "能计算逆回购的占款收益与货币基金的七日年化。",
         "能为「应急资金 / 短期资金 / 长期资金」选择不同的现金工具。"],
  points=["票息与面值", "到期收益率 YTM", "价格与利率反向", "货币基金与万份收益",
          "国债逆回购", "七日年化", "信用风险与流动性", "现金管理分层"],
  sections=[
      ("8.1", "债券是一组确定的现金流", sec(
          eq("P(y) = Σ_{t=1}^{T} C / (1+y)^t + F / (1+y)^T"),
          p("C 是票息、F 是面值、y 是到期收益率。价格与 y 单调递减，且曲线是<strong>凸的</strong>："
            "利率下降带来的涨幅大于同等幅度上升带来的跌幅。第 09 章会把这一阶、二阶敏感度写成久期与凸性。"),
          p("信用利差是 y 相对无风险利率的额外部分：同样的票息，信用资质越差，要求的 y 越高、价格越低。"
            "所以「高收益债」不是更聪明的选择，而是<strong>把违约风险换成了票息</strong>。"),
      )),
      ("8.2", "现金工具的三个口径", sec(
          table(["工具", "收益口径", "流动性", "要注意什么"], [
              ["活期 / 通知存款", "年利率按日计息", "极高", "利率最低，通常有存款保险上限"],
              ["货币基金", "万份收益 / 七日年化", "高（常有快赎额度）", "七日年化是短期年化，不代表长期收益"],
              ["国债逆回购", "年化报价 × 占款天数 / 365", "到期自动回款", "计息天数、手续费、跨节假日占款"],
              ["短债 / 同业存单指数基金", "净值波动 + 票息", "较高", "存在净值回撤，不是保本"],
          ], ["26%", "26%", "20%", "28%"]),
          p("逆回购收益有个容易错的细节：<code>利息 = 本金 × 年化利率 × 计息天数 / 365 − 手续费</code>，"
            "而资金<strong>实际占用天数</strong>可能与名义期限不同（跨周末、跨长假）。"
            "把「报价利率」直接当「到手收益率」会高估。"),
      )),
      ("8.3", "现金是仓位，不是空仓", sec(
          p("在资产配置里，现金同时承担三种角色：<strong>流动性缓冲</strong>（应急支出不迫使你在低点卖出）、"
            "<strong>期权价值</strong>（有机会时可调仓）、<strong>波动稀释</strong>。"
            "第 14 章的再平衡、第 30 章的保证金管理都依赖这一端有足够厚度。"),
      )),
  ],
  demos=[mk_demo(
      "code/08-cash.py", "实验 8-1 · 债券价格—收益率曲线与现金工具收益换算",
      "计算 5 年期债券在不同 YTM 下的价格，并把逆回购与货币基金换算到同一口径。",
      """FACE = 100.0       # 面值
COUPON = 0.03      # 年票息率
MATURITY = 5       # 年数
REPO_CAP = 100000.0
REPO_RATE = 0.018  # 逆回购年化报价
REPO_DAYS = 7      # 名义期限
REAL_DAYS = 9      # 跨周末的实际占款天数
REPO_FEE = 0.00001 # 手续费率
MM_DAILY = (0.000048, 0.000051, 0.000049, 0.000050, 0.000052, 0.000047, 0.000050)""",
      """def bond_price(y):
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
      (repo_interest, 100 * REPO_RATE, 100 * repo_effective, 100 * mm_7d, 100 * mm_annual))""",
      [("fig/08-bond-curve.svg", "债券价格随 YTM 单调下降且呈凸性"),
       ("fig/08-cash.svg", "逆回购报价与按实际占款天数折算后的收益差异")],
      "核对 <code>YTM=票息率</code> 时价格恰为 100；把 <code>REAL_DAYS</code> 改成 7 看折算收益如何回到报价。",
      "票息率等于 YTM 时债券平价；YTM 上升到 5% 后价格低于面值。"
      "逆回购因实际占款 9 天而非 7 天，<strong>真实年化低于报价</strong>——这是最典型的现金管理口径误差。",
      "把 <code>MATURITY</code> 改成 20，观察同一 YTM 变化带来的价格跌幅显著放大（引出第 09 章久期）。")],
  highlights=[("bond", "票息、面值、到期与信用风险"),
              ("money-market", "货币基金的运作与风险边界"),
              ("repo", "逆回购的抵押与期限结构"),
              ("fred", "免费利率与宏观时间序列，用于课后替换合成参数")],
  analogy="债券是一段确定的 <code>cashflow[]</code> 被 <code>discount()</code> 映射成现在的值；"
          "利率就是折现率参数。现金工具则是不同的 <code>settle()</code> 实现，"
          "计息天数与手续费藏在实现细节里。",
  bridge="第一阶段以「现金这一端」收尾；{{ch:09}} 把价格—利率关系升级为久期与凸性，"
         "正式进入第二阶段的定价。",
  pitfalls=["把逆回购报价年化直接当到手收益，忽略实际占款天数。",
            "把货币基金当保本存款，忽略极端赎回与利率风险。",
            "用「七日年化」推断未来一年收益。",
            "只看票息不看信用利差，把高风险债当高息存款。"],
  exercises=["推导为什么票息率等于 YTM 时债券价格等于面值。",
             "把示例的 <code>REAL_DAYS</code> 设为 14，计算实际年化并解释跨长假报价为何常升高。",
             "为「3 个月内要用的钱」和「3 年不用的钱」各选一种现金工具，写出理由与失效条件。"],
  further=["{{ch:09}} 久期、凸性与期限结构；{{ch:14}} 现金在资产配置中的角色。"]),

# ==================================================================== 09
C("09", "p2", "part2/09-bond-pricing", "债券定价、久期与期限结构",
  "把价格对利率的敏感度写成一阶导与二阶导，是全书最干净的一次「导数即风险」。",
  hours="3 学时",
  goals=["能计算麦考利久期、修正久期与凸性。",
         "能用一阶、二阶近似估计利率变动后的价格，并量化近似误差。",
         "能读收益率曲线并解释期限利差与倒挂。",
         "能说明久期匹配为什么不能完全免疫利率风险。"],
  points=["现金流折现", "麦考利久期", "修正久期", "凸性", "一阶与二阶近似",
          "收益率曲线", "期限利差与倒挂", "久期匹配与免疫"],
  sections=[
      ("9.1", "一阶：修正久期", sec(
          eq("D_mod = − (1/P) · dP/dy　|　ΔP/P ≈ − D_mod · Δy"),
          p("久期的量纲是<strong>年</strong>，直观含义是「收回全部现金流现值的加权平均时间」。"
            "零息债的麦考利久期等于到期期限；票息越高、到期越短，久期越短。"
            "组合层面久期可按市值加权，因此它是<strong>可加的风险预算单位</strong>——这一点会在第 30 章复用。"),
      )),
      ("9.2", "二阶：凸性修正近似误差", sec(
          eq("ΔP/P ≈ − D_mod · Δy + (1/2) · C · (Δy)^2　，C = (1/P) · d²P/dy²"),
          p("价格—收益率曲线是凸的，切线（久期）在利率大幅变动时会低估涨幅、高估跌幅。"
            "凸性项修正这个偏差。用数值微分可以直接算出 dP/dy 与 d²P/dy²，"
            "不必背闭式公式——这也是程序员最舒服的推导方式。"),
      )),
      ("9.3", "期限结构：一条曲线里的宏观信息", sec(
          table(["曲线形态", "典型含义", "对持仓的影响"], [
              ["向上倾斜", "长期要求期限溢价", "拉长久期可得额外票息，但承担更大价格敏感"],
              ["平坦", "长短端预期接近", "久期性价比下降"],
              ["倒挂", "短端高于长端", "常被视为衰退预期信号，但不可单独作为择时依据"],
              ["陡峭化 / 平坦化", "长短期利差变化", "曲线策略赚的是斜率变化，不是方向"],
          ], ["22%", "36%", "42%"]),
          note("边界", "久期免疫只在一阶、平行移动、且现金流确定的条件下成立。"
               "真实曲线会扭转，含权债券（可转债、可赎回债）的现金流本身随利率变化，"
               "此时需要有效久期与情景分析。"),
      )),
  ],
  demos=[mk_demo(
      "code/09-duration.py", "实验 9-1 · 久期、凸性与近似误差的数值验证",
      "用中心差分求一阶/二阶导数，比较三种价格估计，并画收益率曲线。",
      """FACE = 100.0
COUPON = 0.04      # 年票息率
MATURITY = 8       # 年
Y0 = 0.035         # 当前 YTM
H = 0.0001         # 数值微分步长
SHOCKS = (-0.020, -0.010, 0.0, 0.010, 0.020)
CURVE = [(1, 0.021), (2, 0.023), (3, 0.025), (5, 0.028),
         (10, 0.032), (20, 0.035)]""",
      """def bond_price(y):
    cf = [COUPON * FACE] * MATURITY
    cf[-1] += FACE
    return sum(c / (1 + y) ** t for t, c in enumerate(cf, 1))

p0 = bond_price(Y0)
d1 = (bond_price(Y0 + H) - bond_price(Y0 - H)) / (2 * H)
d2 = (bond_price(Y0 + H) - 2 * p0 + bond_price(Y0 - H)) / (H * H)
mod_dur, convexity = -d1 / p0, d2 / p0
macaulay = mod_dur * (1 + Y0)

ys = [0.005 + i * 0.0025 for i in range(25)]
actual = [bond_price(Y0 + dy) for dy in ys]
linear = [p0 + d1 * dy for dy in ys]
quad = [p0 + d1 * dy + 0.5 * d2 * dy * dy for dy in ys]
dys = [Y0 + dy for dy in ys]

c = Chart(FIG / "09-convexity.svg", "价格—收益率曲线与一阶/二阶近似", xlabel="YTM", ylabel="价格")
c.line(dys, actual, BLUE, label="精确价格")
c.line(dys, linear, RED, label="久期（切线）近似", dash="5 4")
c.line(dys, quad, GREEN, label="久期+凸性近似", dash="2 3")
c.vline(Y0, "#9aa6b2", label="当前 YTM")
print("近似图:", c.save())
cu = Chart(FIG / "09-curve.svg", "合成收益率曲线（期限结构）", xlabel="期限（年）", ylabel="YTM")
cu.line([t for t, _y in CURVE], [y for _t, y in CURVE], AMBER, label="收益率曲线")
print("曲线图:", cu.save())

rows = []
for dy in SHOCKS:
    px = bond_price(Y0 + dy) - p0
    e1 = d1 * dy - px
    e2 = d1 * dy + 0.5 * d2 * dy * dy - px
    rows.append((dy, px, e1, e2))
print("麦考利久期=%.3f 年 修正久期=%.3f 凸性=%.2f | 当前价格=%.3f" %
      (macaulay, mod_dur, convexity, p0))
print("期限利差 10Y-1Y=%.2f%% | Δy=+2%% 时 实际=%.3f 一阶误差=%.3f 二阶误差=%.3f" %
      (100 * (CURVE[4][1] - CURVE[0][1]), rows[-1][1], rows[-1][2], rows[-1][3]))""",
      [("fig/09-convexity.svg", "精确价格、切线近似与含凸性的二次近似"),
       ("fig/09-curve.svg", "按期限排列的收益率曲线")],
      "对照 <code>Δy=+2%</code> 与 <code>Δy=−2%</code> 的一阶误差符号，理解「凸性总是帮忙」。",
      "二阶近似的误差比切线近似小一到两个数量级，且利率变动越大差距越明显。"
      "久期与凸性都是用<strong>数值微分</strong>算出来的，不需要背公式。",
      "把 <code>MATURITY</code> 改成 20，久期与凸性同时增大，观察近似误差与价格敏感度如何变化。")],
  highlights=[("duration", "久期的一阶敏感度定义"),
              ("convexity", "凸性与二阶修正"),
              ("yield-curve", "期限结构与倒挂"),
              ("pbc", "利率与金融市场统计的官方来源")],
  analogy="久期是 <code>dP/dy</code>，凸性是 <code>d²P/dy²</code>。"
          "把债券当成一个黑箱函数，用中心差分求敏感度，比记闭式解更容易推广到含权与结构化产品。",
  bridge="第 08 章给出价格—利率的定性关系，本章把它量化；"
         "{{ch:10}} 换成股票现金流，{{ch:12}} 换成或有现金流，三者共用同一套折现思想。",
  pitfalls=["把麦考利久期与修正久期混用（相差一个 1+y 因子）。",
            "假设收益率曲线总是平行移动。",
            "对含权债券直接套用普通久期。",
            "把倒挂曲线当成可靠的择时信号，忽略期限溢价与政策因素。"],
  exercises=["推导零息债的麦考利久期等于期限。",
             "在示例里比较 <code>Δy=−2%</code> 与 <code>+2%</code> 的一阶误差，解释符号。",
             "用两种期限债券构造久期匹配的组合，说明为什么曲线扭转时仍会亏。"],
  further=["{{ch:10}} 股权现金流折现；{{ch:12}} 无套利定价；{{ch:30}} 用久期做风险预算。"]),

# ==================================================================== 10
C("10", "p2", "part2/10-equity-valuation", "股票估值：从 DCF 到相对倍数",
  "估值不是算出一个「正确价格」，而是把一组假设显式地写成可审计的模型。",
  hours="3 学时",
  goals=["能写出两阶段自由现金流折现模型并做敏感性分析。",
         "能解释 PE、PB、ROE 与增长之间的约束关系。",
         "能从市价反推隐含增长率，判断市场在定价什么。",
         "能说明 DCF 对折现率与永续增长率的极端敏感性。"],
  points=["自由现金流 FCF", "折现率与 WACC", "两阶段 DCF", "永续增长率",
          "终值占比", "PE 与 PB", "ROE 与杜邦分解", "隐含增长与敏感性"],
  sections=[
      ("10.1", "DCF 是一个参数化的假设容器", sec(
          eq("V_0 = Σ_{t=1}^{n} FCF_t / (1+r)^t + [FCF_(n+1) / (r − g)] / (1+r)^n"),
          p("其中 r 是折现率（通常用 WACC 近似），g 是永续增长率，且必须满足 <code>r &gt; g</code>。"
            "这个式子的价值不在于精度，而在于<strong>把「我看好这家公司」拆成四个可争论的数</strong>："
            "起步现金流、增长率、折现率、永续增长率。"),
          p("实操中终值常占估值的大半，因此 <code>r − g</code> 的微小变化会显著改变结果。"
            "把 DCF 当作「一个点估计」是误用；正确用法是<strong>敏感性表 + 反推隐含假设</strong>。"),
      )),
      ("10.2", "相对倍数：把绝对估值压缩成可比较的比值", sec(
          table(["倍数", "定义", "隐含假设", "失效场景"], [
              ["PE", "价格 / 每股收益", "盈利可持续、会计口径可比", "周期股盈利顶点、亏损公司"],
              ["PB", "价格 / 每股净资产", "净资产能反映价值", "轻资产、无形资产为主"],
              ["PS", "价格 / 每股收入", "利润率会回归正常", "长期无法盈利的商业模式"],
              ["ROE", "净利润 / 净资产", "杠杆与周转稳定", "高杠杆放大、一次性损益"],
          ], ["12%", "26%", "32%", "30%"]),
          p("可持续增长率 <code>g ≈ ROE × 留存率</code> 把 PB、ROE 与增长串起来："
            "高 PB 只有在高且可持续的 ROE 下才合理。这就是「贵不贵」与「好不好」之间的桥梁。"),
      )),
      ("10.3", "反推比预测更稳健", sec(
          p("与其预测未来，不如问：<strong>按今天的价格，市场隐含了多高的增长？</strong>"
            "用二分法求解 <code>dcf(r, g) = 市价</code> 得到一个隐含 g，再判断这个 g 是否超出行业与历史的可行区间。"
            "这是把估值从「预测题」转成「一致性检查」，对工程师尤其自然："
            "给定输出，反解输入，再验证输入是否落在合理域。"),
      )),
  ],
  demos=[mk_demo(
      "code/10-dcf.py", "实验 10-1 · 两阶段 DCF、敏感性矩阵与隐含增长",
      "用标准库实现 DCF，扫描折现率与增长率，并用二分法反推市价隐含的增长。",
      """FCF0 = 10.0        # 起始自由现金流
STAGE1 = 5         # 高增长阶段年数
G_TERM = 0.025     # 永续增长率
R0 = 0.10          # 基准折现率
G0 = 0.10          # 基准高增长阶段增长率
MARKET = 180.0     # 观察到的市值（合成示意）
R_LIST = [0.08, 0.09, 0.10, 0.11, 0.12]
G_LIST = [0.02, 0.06, 0.10, 0.14, 0.18]""",
      """def dcf(r, g1):
    fcf, pv = FCF0, 0.0
    for t in range(1, STAGE1 + 1):
        fcf *= (1 + g1)
        pv += fcf / (1 + r) ** t
    tv = fcf * (1 + G_TERM) / (r - G_TERM)
    return pv + tv / (1 + r) ** STAGE1

base = dcf(R0, G0)
matrix = [[dcf(r, g) for g in G_LIST] for r in R_LIST]
heatmap(FIG / "10-sensitivity.svg", matrix,
        ["r=%.0f%%" % (100 * r) for r in R_LIST],
        ["g=%.0f%%" % (100 * g) for g in G_LIST],
        title="两阶段 DCF 敏感性：折现率 × 高增长率",
        vmin=min(min(row) for row in matrix), vmax=max(max(row) for row in matrix))
print("敏感性图:", str(FIG / "10-sensitivity.svg"))

fcf_path, pv_path, fcf = [], [], FCF0
for t in range(1, STAGE1 + 1):
    fcf *= (1 + G0)
    fcf_path.append(fcf)
    pv_path.append(fcf / (1 + R0) ** t)
c = Chart(FIG / "10-dcf.svg", "高增长期现金流与其现值", xlabel="年", ylabel="金额")
c.bars(range(1, STAGE1 + 1), fcf_path, BLUE, label="FCF")
c.bars(range(1, STAGE1 + 1), pv_path, GREEN, label="折现后现值")
print("现金流图:", c.save())

lo, hi = -0.10, 0.60
for _ in range(80):
    mid = (lo + hi) / 2
    if dcf(R0, mid) < MARKET:
        lo = mid
    else:
        hi = mid
implied = (lo + hi) / 2
print("基准DCF=%.2f 终值占比=%.1f%% | 敏感性区间 %.1f ~ %.1f | 市价隐含 g=%.2f%%" %
      (base, 100 * (1 - sum(pv_path) / base),
       min(min(row) for row in matrix), max(max(row) for row in matrix), 100 * implied))""",
      [("fig/10-sensitivity.svg", "折现率与增长率共同决定估值的热力图"),
       ("fig/10-dcf.svg", "高增长期现金流与折现后现值")],
      "把 <code>R0</code> 上调 1 个百分点，观察估值下降幅度；再把 <code>G_TERM</code> 逼近 <code>R0</code> 看发散。",
      "敏感性表里同一列的变动往往比同一行更剧烈，说明 <code>r − g</code> 是估值的主控参数。"
      "反推的隐含增长率告诉你<strong>市场在假定什么</strong>，比直接预测更有可证伪性。",
      "把 <code>MARKET</code> 改成基准 DCF 的两倍，隐含增长率会升高；判断它是否超出行业合理区间。")],
  highlights=[("dcf", "现金流折现的标准定义与边界"),
              ("valuation", "相对估值与绝对估值的统一视角"),
              ("roe", "ROE 与杜邦分解"),
              ("sec", "上市公司披露文件，取真实财务数据的权威来源")],
  analogy="DCF 是一个纯函数 <code>dcf(params) -&gt; value</code>；估值的工程难点不是实现函数，"
          "而是<strong>为参数写取值范围与来源</strong>。反推隐含参数等价于给黑箱做逆向测试。",
  bridge="第 09 章用折现给债券定价，本章把同一算子用于不确定的股权现金流；"
         "{{ch:11}} 讨论一篮子股权如何被指数化，{{ch:21}} 讨论折现率如何被因子解释。",
  pitfalls=["把 <code>g</code> 设到接近或超过 <code>r</code>，得到爆炸性估值。",
            "用周期股顶点盈利做永续增长基数。",
            "把 DCF 的点估计当成目标价，不做敏感性分析。",
            "跨行业直接比较 PE，忽略资本结构与会计口径差异。"],
  exercises=["推导 <code>g ≈ ROE × 留存率</code>，并说明杠杆如何污染这个关系。",
             "在示例里固定 <code>r</code>，画出估值对 <code>G_TERM</code> 的曲线，解释非线性。",
             "找一家公司的年报，列出 DCF 四个参数各自的取数依据。"],
  further=["{{ch:11}} 指数编制与 ETF 套利；{{ch:21}} 因子视角下的期望收益。"]),

# ==================================================================== 11
C("11", "p2", "part2/11-index-arbitrage", "指数、折溢价与 ETF 套利机制",
  "指数不是资产，而是一份公开的、可复现的计算规则。",
  hours="3 学时",
  goals=["能实现价格加权、市值加权、等权三种指数并比较差异。",
         "能解释等权指数为何需要再平衡以及再平衡带来的换手。",
         "能写出 ETF 折溢价套利的成本边界与收益表达式。",
         "能说明指数成分调整对被动产品的影响。"],
  points=["价格加权指数", "市值加权指数", "等权指数", "除数与公司行动",
          "定期调样与再平衡", "折溢价与套利边界", "申赎清单 PCF", "跟踪误差来源"],
  sections=[
      ("11.1", "三种加权规则，三种隐含押注", sec(
          eq("I_price = ΣP_i / D　|　I_cap = Σ(P_i × Q_i) / D　|　I_equal = (1/n) Σ (P_i,t / P_i,0)"),
          p("价格加权让高价股天然权重大（并需要「除数」D 处理拆股）；市值加权让大公司主导，"
            "是主流宽基的规则；等权则内含<strong>小盘与反转暴露</strong>，因为要定期卖出涨多的、买入跌少的。"),
          table(["规则", "权重来源", "隐含偏向", "维护成本"], [
              ["价格加权", "股价", "高价股", "拆股需调整除数"],
              ["市值加权", "自由流通市值", "大市值 / 动量", "成分调整、自由流通因子"],
              ["等权", "1/n", "小盘 / 均值回复", "高频再平衡换手"],
              ["因子加权", "打分（价值、质量等）", "目标因子", "规则透明度与调样成本"],
          ], ["18%", "26%", "26%", "30%"]),
      )),
      ("11.2", "无套利边界：把折溢价写成不等式", sec(
          eq("套利空间 ≈ |价格 − NAV| − (申赎费 + 交易成本 + 冲击成本 + 资金成本)"),
          p("只有严格大于零才值得动手，且真实执行还受申赎清单、停牌成分股、跨境时差与 T+n 交收约束。"
            "因此<strong>折溢价通常不是错误定价，而是摩擦的报价</strong>。"
            "这也为第 29 章的执行成本提供了一个可观测的实例。"),
      )),
      ("11.3", "调样：规则里的隐式交易", sec(
          p("指数公司按规则定期调整成分股。被动基金必须在生效日附近交易，"
            "于是产生可预测的成交量与价格冲击；主动资金常提前布局。"
            "对程序员来说，指数是一段<strong>公开的版本化脚本</strong>：输入成分与价格，输出点位与权重，"
            "而每次调样就是一次强制发布。"),
      )),
  ],
  demos=[mk_demo(
      "code/11-index.py", "实验 11-1 · 三种指数加权规则、换手与套利边界",
      "合成五只成分股，计算三种加权指数，估计等权再平衡换手，并计算折溢价套利空间。",
      """N = 120             # 交易日
N_ASSETS = 5
START_PRICES = [12.0, 28.0, 45.0, 8.0, 60.0]
SHARES = [9.0e8, 4.0e8, 2.5e8, 1.2e9, 1.5e8]
REBAL_EVERY = 20     # 等权指数再平衡周期
PREMIUM = 0.012      # 观察到的溢价
ARB_COST = 0.003     # 申赎 + 交易 + 冲击成本
CAP = 1000000.0      # 套利资金""",
      """rng = random.Random(7)
mu = [0.0006, 0.0004, 0.0003, 0.0008, 0.0002]
paths = []
for j in range(N_ASSETS):
    px, row = START_PRICES[j], []
    for _ in range(N):
        px *= (1 + rng.gauss(mu[j], 0.012))
        row.append(px)
    paths.append(row)

price_idx = [sum(paths[j][i] for j in range(N_ASSETS)) /
             sum(START_PRICES) for i in range(N)]
cap0 = sum(START_PRICES[j] * SHARES[j] for j in range(N_ASSETS))
cap_idx = [sum(paths[j][i] * SHARES[j] for j in range(N_ASSETS)) / cap0
           for i in range(N)]
eq_idx = [statistics.fmean(paths[j][i] / START_PRICES[j]
                           for j in range(N_ASSETS)) for i in range(N)]

turnover, w = 0.0, [1.0 / N_ASSETS] * N_ASSETS
for i in range(1, N):
    vals = [w[j] * paths[j][i] / paths[j][i - 1] for j in range(N_ASSETS)]
    tot = sum(vals)
    w = [v / tot for v in vals]
    if i % REBAL_EVERY == 0:
        turnover += sum(abs(x - 1.0 / N_ASSETS) for x in w) / 2
        w = [1.0 / N_ASSETS] * N_ASSETS

arb = CAP * (abs(PREMIUM) - ARB_COST)
c = Chart(FIG / "11-index.svg", "三种加权规则的归一化指数", xlabel="交易日", ylabel="点位")
c.line(range(N), price_idx, BLUE, label="价格加权")
c.line(range(N), cap_idx, RED, label="市值加权")
c.line(range(N), eq_idx, GREEN, label="等权")
c.hline(1.0, "#9aa6b2")
print("指数图:", c.save())

labels = ["价格加权", "市值加权", "等权"]
rets = [100 * (x[-1] - 1) for x in (price_idx, cap_idx, eq_idx)]
b = Chart(FIG / "11-weights.svg", "期末累计收益与等权再平衡换手", xlabel="规则", ylabel="%",
          xticks=[(i, n) for i, n in enumerate(labels)])
b.bars(range(3), rets, AMBER, label="累计收益 %")
print("对照图:", b.save())
print("期末收益 价格加权=%.2f%% 市值加权=%.2f%% 等权=%.2f%% | 等权累计单边换手=%.2f%%" %
      (rets[0], rets[1], rets[2], 100 * turnover))
print("溢价=%.2f%% 成本=%.2f%% → 单位资金套利空间=%.2f%%（%.0f 元）" %
      (100 * PREMIUM, 100 * ARB_COST, 100 * (abs(PREMIUM) - ARB_COST), arb))""",
      [("fig/11-index.svg", "三种加权规则下的指数路径"),
       ("fig/11-weights.svg", "三种规则的期末收益对照")],
      "把 <code>REBAL_EVERY</code> 改成 5，观察换手率上升；再改成 1000（几乎不调仓）看等权如何退化为买入持有。",
      "三条指数用的是<strong>完全相同的成分股价格</strong>，差异只来自加权与再平衡规则。"
      "套利空间在扣除成本后仍为正才可执行，且这是理想化上界。",
      "把 <code>PREMIUM</code> 降到 0.002（低于成本），套利空间变负，说明溢价可能只是摩擦报价。")],
  highlights=[("csindex", "指数编制方案、成分股与估值数据"),
              ("spdji", "国际指数方法论与基准"),
              ("tracking-error", "跟踪误差与复制质量"),
              ("put-call", "无套利思想在期权中的对应形式")],
  analogy="指数是一份<strong>公开的纯函数</strong> <code>index(prices, shares, rule) -&gt; level</code>；"
          "除数 D 是处理 schema 变更的兼容层，调样是一次带公告的版本发布，"
          "折溢价则是两个副本之间的复制延迟。",
  bridge="第 10 章给单个资产定价，本章给一篮子资产定规则；"
         "{{ch:13}} 转向「如何主动选择权重」，{{ch:21}} 转向「权重背后的因子补偿」。",
  pitfalls=["把指数点位当成可交易资产，忽略 ETF 的净值与折溢价。",
            "低估等权/因子指数的再平衡换手成本。",
            "用当前成分股回测历史指数（幸存者偏差，见第 25 章）。",
            "把折溢价直接当无风险套利机会，忽略申赎限制与交收时滞。"],
  exercises=["推导拆股后价格加权指数的除数应如何调整才能保持点位连续。",
             "在示例里加入一只新股与一次剔除，观察三种指数点位是否需要调整。",
             "把 ARB_COST 分解到至少四项，并说明哪一项在极端行情里最不稳定。"],
  further=["{{ch:13}} 均值-方差组合；{{ch:21}} 因子与 Smart Beta；{{ch:25}} 成分股历史与幸存者偏差。"]),
]
