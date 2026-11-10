#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全书外部参考资料与检索链接的唯一来源。

分类：教材 / 课程 / 机构 / 行情 / 数据 / 工具 / 百科。
按用途给每章配一组精读链接；知识点地图用 TOPIC_RULES 逐条挂 1～2 个直达链接。

说明：本开发环境对 en.wikipedia.org 等站点无法稳定访问，链接探测会把它们
归为「本环境不可达」而非失效；链接本身为各机构/项目的标准入口，建议在可联网
环境下打开。书中提及的券商 App 仅用于抽象「零售交易界面的共同字段」，
不构成推荐或从属关系。
"""
from __future__ import annotations

import html as html_mod
from urllib.parse import quote

R = {
    # ---------------- 机构与监管 ----------------
    "csrc": ("中国证监会 CSRC", "https://www.csrc.gov.cn/", "监管规则、投资者保护与行政处罚的权威来源", "机构"),
    "sse": ("上海证券交易所", "https://www.sse.com.cn/", "交易规则、集合竞价、ETF 与债券业务规则", "机构"),
    "szse": ("深圳证券交易所", "https://www.szse.cn/", "交易规则、创业板与基金业务规则", "机构"),
    "chinaclear": ("中国证券登记结算", "https://www.chinaclear.cn/", "登记、托管、交收与结算规则", "机构"),
    "amac": ("中国证券投资基金业协会", "https://www.amac.org.cn/", "基金备案、从业规范与公募数据", "机构"),
    "csindex": ("中证指数", "https://www.csindex.com.cn/", "指数编制方案、成分股与估值数据", "机构"),
    "cffex": ("中国金融期货交易所", "http://www.cffex.com.cn/", "股指期货/期权合约与交易规则", "机构"),
    "pbc": ("中国人民银行", "http://www.pbc.gov.cn/", "利率、货币政策与金融市场统计", "机构"),
    "hkex": ("香港交易所 HKEX", "https://www.hkex.com.hk/", "港股、ETF、牛熊证与衍生品规则", "机构"),
    "sfc": ("香港证监会 SFC", "https://www.sfc.hk/", "适当性、杠杆产品与投资者警示", "机构"),
    "sec": ("美国 SEC", "https://www.sec.gov/", "披露文件、基金监管与执法信息", "机构"),
    "investor": ("Investor.gov（SEC 投资者教育）", "https://www.investor.gov/", "复利、费用、风险与常见投资骗局的官方说明", "机构"),
    "finra": ("FINRA", "https://www.finra.org/", "美国券商自律规则与投资者工具", "机构"),
    "cboe": ("Cboe 期权交易所", "https://www.cboe.com/", "期权合约、VIX 与波动率产品资料", "机构"),
    "cboe-edu": ("Cboe Options Institute", "https://www.cboe.com/education/", "期权 payoff、希腊字母的官方教学材料", "机构"),
    "cme": ("CME Group", "https://www.cmegroup.com/", "期货与期权合约规格、保证金规则", "机构"),
    "fed": ("美联储", "https://www.federalreserve.gov/", "政策利率与经济数据", "机构"),
    "imf": ("IMF", "https://www.imf.org/", "全球金融稳定报告与跨国数据", "机构"),
    "bis": ("国际清算银行 BIS", "https://www.bis.org/", "市场结构、杠杆与系统性风险研究", "机构"),
    "cfa": ("CFA Institute", "https://www.cfainstitute.org/", "投资组合管理、道德准则与从业者教育", "机构"),
    "spdji": ("S&P Dow Jones Indices", "https://www.spglobal.com/spdji/en/", "指数方法论与基准数据", "机构"),
    "spiva": ("SPIVA 主动/被动业绩对比", "https://www.spglobal.com/spdji/en/research-insights/spiva/", "主动基金相对基准的长期胜率统计", "机构"),
    "morningstar": ("Morningstar", "https://www.morningstar.com/", "基金评级、费率与持仓的研究入口", "机构"),
    "nber": ("NBER", "https://www.nber.org/", "资产定价与实证金融工作论文", "机构"),
    "ssrn": ("SSRN", "https://www.ssrn.com/", "金融学预印本与因子研究检索", "机构"),

    # ---------------- 行情与零售交易界面 ----------------
    "futu": ("富途牛牛 / 富途证券", "https://www.futunn.com/", "港股/美股零售交易界面的产品分类与行情模块示例", "行情"),
    "eastmoney": ("东方财富", "https://www.eastmoney.com/", "A 股行情、基金与资讯模块的界面示例", "行情"),
    "ttjj": ("天天基金", "https://fund.eastmoney.com/", "公募基金净值、费率、持仓的查询界面示例", "行情"),
    "ths": ("同花顺", "https://www.10jqka.com.cn/", "行情看盘与技术指标模块的界面示例", "行情"),
    "xueqiu": ("雪球", "https://xueqiu.com/", "组合展示、讨论与复权行情的界面示例", "行情"),
    "tradingview": ("TradingView", "https://www.tradingview.com/", "多周期图表、指标脚本与 K 线形态的通用参照", "行情"),
    "ibkr": ("Interactive Brokers", "https://www.interactivebrokers.com/", "多市场订单类型与保证金账户的界面示例", "行情"),
    "nasdaq": ("Nasdaq", "https://www.nasdaq.com/", "美股行情、公司行动与股息数据入口", "行情"),

    # ---------------- 数据与开放资料 ----------------
    "fred": ("FRED", "https://fred.stlouisfed.org/", "利率、通胀、信用利差等免费时间序列", "数据"),
    "yahoo": ("Yahoo Finance", "https://finance.yahoo.com/", "全球股票/ETF 历史行情常用入口", "数据"),
    "stooq": ("Stooq", "https://stooq.com/", "可下载的免费历史行情数据", "数据"),
    "french": ("Ken French Data Library", "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html", "Fama-French 因子与组合收益的原始数据", "数据"),
    "shiller": ("Robert Shiller 数据集", "http://www.econ.yale.edu/~shiller/data.htm", "长周期股价、盈利与利率历史", "数据"),
    "worldbank": ("World Bank Data", "https://data.worldbank.org/", "跨国宏观与金融深度指标", "数据"),
    "oecd": ("OECD Data", "https://www.oecd.org/", "养老金、储蓄与家庭金融统计", "数据"),
    "akshare": ("AKShare", "https://github.com/akfamily/akshare", "开源中文金融数据接口（A 股/基金/宏观）", "数据"),
    "tushare": ("Tushare", "https://tushare.pro/", "中文量化数据平台（部分数据需积分）", "数据"),
    "arxiv": ("arXiv q-fin", "https://arxiv.org/list/q-fin/recent", "量化金融与因子研究预印本", "数据"),

    # ---------------- 工具与编程 ----------------
    "python-docs": ("Python 3 文档", "https://docs.python.org/3/", "本书脚本的语言与标准库权威参考", "工具"),
    "python-math": ("Python math / random / statistics", "https://docs.python.org/3/library/math.html", "标准库数学与统计函数", "工具"),
    "python-random": ("Python random", "https://docs.python.org/3/library/random.html", "固定种子与可复现的合成数据", "工具"),
    "python-statistics": ("Python statistics", "https://docs.python.org/3/library/statistics.html", "均值、方差、正态分位数等标准库实现", "工具"),
    "mdn-svg": ("MDN · SVG", "https://developer.mozilla.org/en-US/docs/Web/SVG", "本书自绘图表所用矢量格式参考", "工具"),
    "numpy": ("NumPy", "https://numpy.org/", "从手写循环迁移到向量化计算的工业标准", "工具"),
    "pandas": ("pandas", "https://pandas.pydata.org/", "时间序列对齐、分组与缺失处理的工业标准", "工具"),
    "matplotlib": ("Matplotlib", "https://matplotlib.org/", "本书 SVG 自绘替代方案的成熟绘图库", "工具"),
    "statsmodels": ("statsmodels", "https://www.statsmodels.org/", "回归、因子检验与时间序列建模", "工具"),
    "scipy": ("SciPy", "https://scipy.org/", "优化器与分布函数", "工具"),
    "jupyter": ("Project Jupyter", "https://jupyter.org/", "把公式、代码、图表、结论放在同一份笔记里", "工具"),
    "backtrader": ("Backtrader", "https://github.com/mementum/backtrader", "事件驱动回测框架的参考实现", "工具"),
    "vectorbt": ("vectorbt", "https://vectorbt.dev/", "向量化回测与参数扫描框架", "工具"),
    "zipline": ("Zipline", "https://github.com/quantopian/zipline", "经典事件驱动回测引擎（归档项目）", "工具"),
    "pyfolio": ("pyfolio", "https://github.com/quantopian/pyfolio", "组合绩效与风险归因报告", "工具"),
    "ffn": ("ffn", "https://github.com/pmorissette/ffn", "绩效指标计算与权重优化工具", "工具"),
    "quantstats": ("QuantStats（PyPI）", "https://pypi.org/project/QuantStats/", "夏普、回撤、月度收益表等绩效报告", "工具"),
    "ta-lib": ("TA-Lib", "https://ta-lib.org/", "技术指标的事实标准实现（对照本书手写公式）", "工具"),
    "yfinance": ("yfinance（PyPI）", "https://pypi.org/project/yfinance/", "下载真实行情做课后实验", "工具"),

    # ---------------- 教材与课程 ----------------
    "mit-ocw": ("MIT OpenCourseWare · Finance", "https://ocw.mit.edu/search/?q=finance", "投资学、资产定价与衍生品的免费课程材料", "课程"),
    "khan": ("Khan Academy · Finance", "https://www.khanacademy.org/economics-finance-domain/core-finance", "复利、估值与账户基础的入门讲解", "课程"),
    "coursera": ("Coursera · Finance", "https://www.coursera.org/", "投资组合、风险管理等结构化课程检索", "课程"),
    "bogleheads": ("Bogleheads Wiki", "https://www.bogleheads.org/wiki/Main_Page", "长期指数投资、再平衡与税费的实践型百科", "课程"),
    "core-econ": ("CORE Econ", "https://www.core-econ.org/", "理解利率、通胀与宏观背景的开放经济学教材", "课程"),
    "openstax": ("OpenStax · Principles of Economics", "https://openstax.org/details/books/principles-economics-3e", "金融市场与利率背景的开放教材", "课程"),
    "investopedia": ("Investopedia", "https://www.investopedia.com/", "产品、账户、订单与指标的术语速查", "教材"),

    # ---------------- 百科：收益、风险与组合 ----------------
    "compound-interest": ("Compound interest", "https://en.wikipedia.org/wiki/Compound_interest", "复利、计息频率与终值公式", "百科"),
    "real-return": ("Real interest rate", "https://en.wikipedia.org/wiki/Real_interest_rate", "名义收益扣除通胀后的购买力收益", "百科"),
    "inflation": ("Inflation", "https://en.wikipedia.org/wiki/Inflation", "通胀对长期实际财富的侵蚀", "百科"),
    "rate-of-return": ("Rate of return", "https://en.wikipedia.org/wiki/Rate_of_return", "简单收益、对数收益与年化", "百科"),
    "log-return": ("Logarithmic return", "https://en.wikipedia.org/wiki/Logarithmic_return", "可跨期相加的连续复利收益", "百科"),
    "vol-drag": ("Volatility drag", "https://en.wikipedia.org/wiki/Volatility_tax", "算术均值与几何均值的差额", "百科"),
    "normal-dist": ("Normal distribution", "https://en.wikipedia.org/wiki/Normal_distribution", "标准差、置信区间与正态假设", "百科"),
    "fat-tails": ("Heavy-tailed distribution", "https://en.wikipedia.org/wiki/Heavy-tailed_distribution", "极端行情与正态假设的失效", "百科"),
    "skewness": ("Skewness / kurtosis", "https://en.wikipedia.org/wiki/Skewness", "收益分布的不对称与尖峰厚尾", "百科"),
    "drawdown": ("Drawdown (economics)", "https://en.wikipedia.org/wiki/Drawdown_(economics)", "峰值到谷底的回撤与恢复难度", "百科"),
    "var-risk": ("Value at risk", "https://en.wikipedia.org/wiki/Value_at_risk", "分位数意义下的潜在损失", "百科"),
    "cvar": ("Expected shortfall (CVaR)", "https://en.wikipedia.org/wiki/Expected_shortfall", "尾部超过 VaR 的平均损失", "百科"),
    "mpt": ("Modern portfolio theory", "https://en.wikipedia.org/wiki/Modern_portfolio_theory", "均值-方差框架与分散化", "百科"),
    "frontier": ("Efficient frontier", "https://en.wikipedia.org/wiki/Efficient_frontier", "给定风险下最高期望收益的组合集合", "百科"),
    "diversification": ("Diversification (finance)", "https://en.wikipedia.org/wiki/Diversification_(finance)", "相关系数小于 1 时的风险削减", "百科"),
    "sharpe": ("Sharpe ratio", "https://en.wikipedia.org/wiki/Sharpe_ratio", "单位总风险的超额收益", "百科"),
    "sortino": ("Sortino ratio", "https://en.wikipedia.org/wiki/Sortino_ratio", "只用下行波动衡量风险调整收益", "百科"),
    "information-ratio": ("Information ratio", "https://en.wikipedia.org/wiki/Information_ratio", "相对基准的主动收益/跟踪误差", "百科"),
    "calmar": ("Calmar ratio", "https://en.wikipedia.org/wiki/Calmar_ratio", "年化收益与最大回撤之比", "百科"),
    "capm": ("Capital asset pricing model", "https://en.wikipedia.org/wiki/Capital_asset_pricing_model", "beta 与期望收益的线性关系", "百科"),
    "beta": ("Beta (finance)", "https://en.wikipedia.org/wiki/Beta_(finance)", "资产对市场因子的敏感度", "百科"),
    "alpha": ("Jensen's alpha", "https://en.wikipedia.org/wiki/Jensen%27s_alpha", "相对因子模型残差的超额收益", "百科"),
    "fama-french": ("Fama–French three-factor model", "https://en.wikipedia.org/wiki/Fama%E2%80%93French_three-factor_model", "规模与价值因子对 CAPM 的扩展", "百科"),
    "factor-investing": ("Factor investing", "https://en.wikipedia.org/wiki/Factor_investing", "把实证因子转成可交易策略", "百科"),
    "smart-beta": ("Smart beta", "https://en.wikipedia.org/wiki/Smart_beta", "规则化因子指数与 ETF", "百科"),
    "momentum": ("Momentum investing", "https://en.wikipedia.org/wiki/Momentum_(finance)", "横截面动量与反转效应", "百科"),
    "emh": ("Efficient-market hypothesis", "https://en.wikipedia.org/wiki/Efficient-market_hypothesis", "价格是否已反映可用信息", "百科"),
    "behavioral": ("Behavioral finance", "https://en.wikipedia.org/wiki/Behavioral_finance", "系统性偏离理性的行为偏差", "百科"),
    "prospect": ("Prospect theory", "https://en.wikipedia.org/wiki/Prospect_theory", "参照点依赖与损失厌恶", "百科"),
    "disposition": ("Disposition effect", "https://en.wikipedia.org/wiki/Disposition_effect", "过早卖出盈利、过久持有亏损", "百科"),
    "herding": ("Herd behavior", "https://en.wikipedia.org/wiki/Herd_behavior", "拥挤交易与反馈环", "百科"),
    "asset-allocation": ("Asset allocation", "https://en.wikipedia.org/wiki/Asset_allocation", "战略/战术配置与长期风险预算", "百科"),
    "rebalancing": ("Rebalancing investments", "https://en.wikipedia.org/wiki/Rebalancing_investments", "定期回归目标权重与再平衡溢价", "百科"),
    "dca": ("Dollar cost averaging", "https://en.wikipedia.org/wiki/Dollar_cost_averaging", "定投与一次性投入的现金流差异", "百科"),
    "risk-parity": ("Risk parity", "https://en.wikipedia.org/wiki/Risk_parity", "按风险贡献而非资金额分配", "百科"),
    "kelly": ("Kelly criterion", "https://en.wikipedia.org/wiki/Kelly_criterion", "长期增长率最优的仓位上界", "百科"),
    "lifetime": ("Lifecycle investing", "https://en.wikipedia.org/wiki/Lifecycle_investing", "人力资本与年龄下的风险承受力", "百科"),

    # ---------------- 百科：产品、定价与账户 ----------------
    "stock": ("Stock", "https://en.wikipedia.org/wiki/Stock", "股权、投票权与剩余索取权", "百科"),
    "bond": ("Bond (finance)", "https://en.wikipedia.org/wiki/Bond_(finance)", "票息、面值、到期与信用风险", "百科"),
    "duration": ("Bond duration", "https://en.wikipedia.org/wiki/Bond_duration", "价格对利率的一阶敏感度", "百科"),
    "convexity": ("Bond convexity", "https://en.wikipedia.org/wiki/Bond_convexity", "久期之外的二阶价格修正", "百科"),
    "yield-curve": ("Yield curve", "https://en.wikipedia.org/wiki/Yield_curve", "期限结构、倒挂与远期利率", "百科"),
    "credit-spread": ("Credit spread (bond)", "https://en.wikipedia.org/wiki/Credit_spread_(bond)", "信用风险的额外补偿", "百科"),
    "etf": ("Exchange-traded fund", "https://en.wikipedia.org/wiki/Exchange-traded_fund", "场内交易、申赎与跟踪指数", "百科"),
    "index-fund": ("Index fund", "https://en.wikipedia.org/wiki/Index_fund", "被动复制与费率优势", "百科"),
    "mutual-fund": ("Mutual fund", "https://en.wikipedia.org/wiki/Mutual_fund", "净值申赎与开放式基金运作", "百科"),
    "nav": ("Net asset value", "https://en.wikipedia.org/wiki/Net_asset_value", "基金份额净值的计算口径", "百科"),
    "tracking-error": ("Tracking error", "https://en.wikipedia.org/wiki/Tracking_error", "组合与基准收益差的标准差", "百科"),
    "expense-ratio": ("Expense ratio", "https://en.wikipedia.org/wiki/Expense_ratio", "长期复利下最确定的负项", "百科"),
    "money-market": ("Money market fund", "https://en.wikipedia.org/wiki/Money_market_fund", "现金管理的低波动工具与风险边界", "百科"),
    "repo": ("Repurchase agreement", "https://en.wikipedia.org/wiki/Repurchase_agreement", "逆回购的抵押与期限结构", "百科"),
    "convertible": ("Convertible bond", "https://en.wikipedia.org/wiki/Convertible_bond", "债底 + 转股权的混合结构", "百科"),
    "reit": ("Real estate investment trust", "https://en.wikipedia.org/wiki/Real_estate_investment_trust", "分红型不动产证券化产品", "百科"),
    "option": ("Option (finance)", "https://en.wikipedia.org/wiki/Option_(finance)", "或有权益与非线性 payoff", "百科"),
    "put-call": ("Put–call parity", "https://en.wikipedia.org/wiki/Put%E2%80%93call_parity", "看涨看跌与现货的无套利约束", "百科"),
    "greeks": ("Greeks (finance)", "https://en.wikipedia.org/wiki/Greeks_(finance)", "delta/gamma/theta/vega 敏感度", "百科"),
    "implied-vol": ("Implied volatility", "https://en.wikipedia.org/wiki/Implied_volatility", "从期权价格反解出的市场预期波动", "百科"),
    "black-scholes": ("Black–Scholes model", "https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model", "连续时间无套利定价闭式解", "百科"),
    "futures": ("Futures contract", "https://en.wikipedia.org/wiki/Futures_contract", "保证金、逐日盯市与基差", "百科"),
    "margin": ("Margin (finance)", "https://en.wikipedia.org/wiki/Margin_(finance)", "融资杠杆、维持保证金与强平", "百科"),
    "short": ("Short (finance)", "https://en.wikipedia.org/wiki/Short_(finance)", "卖空的借券、成本与无限损失", "百科"),
    "dividend": ("Dividend", "https://en.wikipedia.org/wiki/Dividend", "分红、除息与股息税", "百科"),
    "split": ("Stock split", "https://en.wikipedia.org/wiki/Stock_split", "拆股与价格/数量的口径跳变", "百科"),
    "valuation": ("Stock valuation", "https://en.wikipedia.org/wiki/Stock_valuation", "相对估值与现金流折现的统一视角", "百科"),
    "pe": ("Price–earnings ratio", "https://en.wikipedia.org/wiki/Price%E2%80%93earnings_ratio", "盈利口径下的估值倍数", "百科"),
    "dcf": ("Discounted cash flow", "https://en.wikipedia.org/wiki/Discounted_cash_flow", "把未来现金流折成现值", "百科"),
    "roe": ("Return on equity", "https://en.wikipedia.org/wiki/Return_on_equity", "股东权益回报率与杜邦分解", "百科"),
    "settlement": ("Settlement (finance)", "https://en.wikipedia.org/wiki/Settlement_(finance)", "成交与交收分离、T+1 与货银对付", "百科"),
    "bid-ask": ("Bid–ask spread", "https://en.wikipedia.org/wiki/Bid%E2%80%93ask_spread", "流动性成本的最小单位", "百科"),
    "limit-order": ("Limit order", "https://en.wikipedia.org/wiki/Limit_order", "限价单的成交不确定性与价格保护", "百科"),
    "order-book": ("Order book", "https://en.wikipedia.org/wiki/Order_book", "买卖档位、深度与逐笔撮合", "百科"),
    "market-micro": ("Market microstructure", "https://en.wikipedia.org/wiki/Market_microstructure", "价格形成、冲击成本与做市机制", "百科"),

    # ---------------- 百科：图表、指标与策略工程 ----------------
    "ohlc": ("OHLC chart", "https://en.wikipedia.org/wiki/Open-high-low-close_chart", "开高低收四价的数据结构", "百科"),
    "candlestick": ("Candlestick chart", "https://en.wikipedia.org/wiki/Candlestick_chart", "K 线实体、影线与颜色约定", "百科"),
    "adjusted-close": ("Adjusted closing price", "https://en.wikipedia.org/wiki/Adjusted_closing_price", "前复权/后复权与公司行动处理", "百科"),
    "ma": ("Moving average", "https://en.wikipedia.org/wiki/Moving_average", "均线族与滞后性", "百科"),
    "macd": ("MACD", "https://en.wikipedia.org/wiki/MACD", "双指数均线差与柱状能量", "百科"),
    "rsi": ("Relative strength index", "https://en.wikipedia.org/wiki/Relative_strength_index", "涨跌幅度比的震荡指标", "百科"),
    "bollinger": ("Bollinger Bands", "https://en.wikipedia.org/wiki/Bollinger_Bands", "均值 ± k 倍标准差通道", "百科"),
    "stochastic": ("Stochastic oscillator", "https://en.wikipedia.org/wiki/Stochastic_oscillator", "KDJ 类指标原始定义", "百科"),
    "technical-analysis": ("Technical analysis", "https://en.wikipedia.org/wiki/Technical_analysis", "价量研究的假设、流派与争议", "百科"),
    "chart-pattern": ("Chart pattern", "https://en.wikipedia.org/wiki/Chart_pattern", "头肩、双底、三角等形态", "百科"),
    "support": ("Support and resistance", "https://en.wikipedia.org/wiki/Support_and_resistance", "成交密集区与自我实现的价位", "百科"),
    "volume": ("Volume (finance)", "https://en.wikipedia.org/wiki/Volume_(finance)", "成交量与换手率的信息含量", "百科"),
    "backtesting": ("Backtesting", "https://en.wikipedia.org/wiki/Backtesting", "用历史数据检验策略的流程与陷阱", "百科"),
    "lookahead": ("Look-ahead bias", "https://en.wikipedia.org/wiki/Look-ahead_bias", "用到未来信息的隐形数据泄漏", "百科"),
    "survivorship": ("Survivorship bias", "https://en.wikipedia.org/wiki/Survivorship_bias", "只看存活基金/成分股导致的虚高收益", "百科"),
    "overfitting": ("Overfitting", "https://en.wikipedia.org/wiki/Overfitting", "样本内拟合、样本外失效", "百科"),
    "data-snooping": ("Data dredging", "https://en.wikipedia.org/wiki/Data_dredging", "反复试参数造成的假发现", "百科"),
    "walk-forward": ("Walk forward optimization", "https://en.wikipedia.org/wiki/Walk_forward_optimization", "滚动训练/验证的样本外检验", "百科"),
    "montecarlo": ("Monte Carlo method", "https://en.wikipedia.org/wiki/Monte_Carlo_method", "用模拟逼近分布与尾部风险", "百科"),
    "slippage": ("Slippage (finance)", "https://en.wikipedia.org/wiki/Slippage_(finance)", "下单价格与实际成交价的差", "百科"),
    "twr": ("Time-weighted return", "https://en.wikipedia.org/wiki/Time-weighted_return", "剔除外部现金流后的策略收益", "百科"),
    "mwr": ("Money-weighted return", "https://en.wikipedia.org/wiki/Money-weighted_return", "投资者实际体验到的IRR", "百科"),
    "attribution": ("Performance attribution", "https://en.wikipedia.org/wiki/Performance_attribution", "配置效应、选股效应与交互项", "百科"),
    "ips": ("Investment policy statement", "https://en.wikipedia.org/wiki/Investment_policy_statement", "把目标、约束与流程写成契约", "百科"),
    "p-hacking": ("p-hacking", "https://en.wikipedia.org/wiki/Data_dredging", "多重检验下的假阳性膨胀", "百科"),
}

TOPIC_RULES = [
    ("复利", ["compound-interest", "vol-drag"]), ("通胀", ["inflation", "real-return"]),
    ("实际收益", ["real-return", "inflation"]), ("收益", ["rate-of-return", "log-return"]),
    ("对数", ["log-return", "rate-of-return"]), ("年化", ["rate-of-return", "compound-interest"]),
    ("波动", ["normal-dist", "vol-drag"]), ("标准差", ["normal-dist", "fat-tails"]),
    ("分布", ["normal-dist", "fat-tails"]), ("厚尾", ["fat-tails", "skewness"]),
    ("回撤", ["drawdown", "calmar"]), ("VaR", ["var-risk", "cvar"]),
    ("尾部", ["cvar", "fat-tails"]), ("风险", ["mpt", "var-risk"]),
    ("相关", ["diversification", "mpt"]), ("分散", ["diversification", "mpt"]),
    ("组合", ["mpt", "frontier"]), ("均值-方差", ["mpt", "frontier"]),
    ("有效前沿", ["frontier", "sharpe"]), ("夏普", ["sharpe", "sortino"]),
    ("索提诺", ["sortino", "sharpe"]), ("信息比率", ["information-ratio", "tracking-error"]),
    ("Calmar", ["calmar", "drawdown"]), ("CAPM", ["capm", "beta"]),
    ("beta", ["beta", "capm"]), ("alpha", ["alpha", "capm"]),
    ("因子", ["fama-french", "factor-investing"]), ("Smart", ["smart-beta", "factor-investing"]),
    ("动量", ["momentum", "factor-investing"]), ("有效市场", ["emh", "behavioral"]),
    ("行为", ["behavioral", "prospect"]), ("前景理论", ["prospect", "disposition"]),
    ("处置效应", ["disposition", "prospect"]), ("羊群", ["herding", "behavioral"]),
    ("配置", ["asset-allocation", "rebalancing"]), ("再平衡", ["rebalancing", "asset-allocation"]),
    ("定投", ["dca", "asset-allocation"]), ("风险平价", ["risk-parity", "asset-allocation"]),
    ("凯利", ["kelly", "drawdown"]), ("生命周期", ["lifetime", "asset-allocation"]),
    ("股票", ["stock", "valuation"]), ("股权", ["stock", "dividend"]),
    ("债券", ["bond", "duration"]), ("久期", ["duration", "convexity"]),
    ("凸性", ["convexity", "duration"]), ("期限结构", ["yield-curve", "duration"]),
    ("收益率曲线", ["yield-curve", "credit-spread"]), ("信用", ["credit-spread", "bond"]),
    ("ETF", ["etf", "index-fund"]), ("指数基金", ["index-fund", "etf"]),
    ("基金", ["mutual-fund", "nav"]), ("净值", ["nav", "tracking-error"]),
    ("跟踪误差", ["tracking-error", "etf"]), ("费率", ["expense-ratio", "index-fund"]),
    ("折溢价", ["etf", "nav"]), ("申赎", ["etf", "mutual-fund"]),
    ("货币基金", ["money-market", "repo"]), ("逆回购", ["repo", "money-market"]),
    ("可转债", ["convertible", "option"]), ("REIT", ["reit", "dividend"]),
    ("期权", ["option", "put-call"]), ("payoff", ["option", "put-call"]),
    ("平价", ["put-call", "option"]), ("希腊", ["greeks", "implied-vol"]),
    ("隐含波动", ["implied-vol", "black-scholes"]), ("Black-Scholes", ["black-scholes", "greeks"]),
    ("期货", ["futures", "margin"]), ("保证金", ["margin", "futures"]),
    ("杠杆", ["margin", "kelly"]), ("卖空", ["short", "margin"]),
    ("分红", ["dividend", "split"]), ("除权", ["split", "adjusted-close"]),
    ("拆股", ["split", "adjusted-close"]), ("估值", ["valuation", "pe"]),
    ("PE", ["pe", "valuation"]), ("DCF", ["dcf", "valuation"]),
    ("ROE", ["roe", "valuation"]), ("结算", ["settlement", "chinaclear"]),
    ("交收", ["settlement", "chinaclear"]), ("T+1", ["settlement", "sse"]),
    ("盘口", ["order-book", "bid-ask"]), ("订单簿", ["order-book", "market-micro"]),
    ("买卖价差", ["bid-ask", "market-micro"]), ("微观结构", ["market-micro", "order-book"]),
    ("限价", ["limit-order", "slippage"]), ("市价", ["limit-order", "slippage"]),
    ("滑点", ["slippage", "market-micro"]), ("冲击", ["market-micro", "slippage"]),
    ("OHLC", ["ohlc", "candlestick"]), ("K 线", ["candlestick", "ohlc"]),
    ("蜡烛", ["candlestick", "chart-pattern"]), ("复权", ["adjusted-close", "split"]),
    ("坐标", ["adjusted-close", "ohlc"]), ("成交", ["volume", "ohlc"]),
    ("均线", ["ma", "macd"]), ("趋势", ["ma", "support"]),
    ("支撑", ["support", "chart-pattern"]), ("MACD", ["macd", "ma"]),
    ("RSI", ["rsi", "stochastic"]), ("KDJ", ["stochastic", "rsi"]),
    ("布林", ["bollinger", "normal-dist"]), ("技术指标", ["technical-analysis", "macd"]),
    ("形态", ["chart-pattern", "support"]), ("缺口", ["chart-pattern", "ohlc"]),
    ("未来函数", ["lookahead", "backtesting"]), ("技术分析", ["technical-analysis", "emh"]),
    ("回测", ["backtesting", "walk-forward"]), ("样本外", ["walk-forward", "overfitting"]),
    ("过拟合", ["overfitting", "data-snooping"]), ("幸存者", ["survivorship", "backtesting"]),
    ("数据泄漏", ["lookahead", "survivorship"]), ("多重检验", ["p-hacking", "data-snooping"]),
    ("p-hacking", ["p-hacking", "walk-forward"]), ("蒙特卡洛", ["montecarlo", "var-risk"]),
    ("归因", ["attribution", "twr"]), ("时间加权", ["twr", "mwr"]),
    ("资金加权", ["mwr", "twr"]), ("IPS", ["ips", "asset-allocation"]),
    ("投资政策", ["ips", "lifetime"]), ("Python", ["python-docs", "python-math"]),
    ("标准库", ["python-docs", "python-statistics"]), ("SVG", ["mdn-svg", "python-docs"]),
    ("随机种子", ["python-random", "montecarlo"]), ("模拟", ["montecarlo", "python-random"]),
    ("图表", ["mdn-svg", "matplotlib"]), ("可视化", ["matplotlib", "mdn-svg"]),
    ("pandas", ["pandas", "numpy"]), ("向量化", ["numpy", "pandas"]),
    ("富途", ["futu", "hkex"]), ("东方", ["eastmoney", "ttjj"]),
    ("App", ["tradingview", "futu"]), ("界面", ["tradingview", "investopedia"]),
    ("监管", ["csrc", "investor"]), ("交易所", ["sse", "hkex"]),
    ("适当性", ["sfc", "investor"]), ("费率", ["expense-ratio", "investor"]),
    ("税", ["investor", "bogleheads"]), ("合规", ["csrc", "amac"]),
]

CHAPTER_RESOURCES = {
    "00": (["cfa", "mit-ocw", "investopedia", "bogleheads", "investor"], "personal investment curriculum portfolio management risk"),
    "01": (["compound-interest", "real-return", "inflation", "investor", "khan"], "compound interest inflation real return long term wealth"),
    "02": (["normal-dist", "fat-tails", "drawdown", "python-statistics", "mdn-svg"], "risk volatility drawdown fat tails python visualization"),
    "03": (["stock", "bond", "etf", "futu", "eastmoney", "investopedia"], "tradable products stocks bonds ETF options retail broker app"),
    "04": (["sse", "hkex", "sec", "settlement", "csrc"], "trading rules T+1 price limit auction settlement A share HK US"),
    "05": (["chinaclear", "investor", "expense-ratio", "amac", "ttjj"], "brokerage account settlement fees taxes fund distribution"),
    "06": (["ohlc", "order-book", "adjusted-close", "pandas", "akshare"], "OHLCV order book adjusted close market data model"),
    "07": (["etf", "nav", "tracking-error", "expense-ratio", "mutual-fund"], "ETF creation redemption NAV premium discount tracking error"),
    "08": (["bond", "money-market", "repo", "yield-curve", "fred"], "fixed income money market fund reverse repo cash management"),
    "09": (["duration", "convexity", "yield-curve", "credit-spread", "dcf"], "bond pricing yield duration convexity term structure"),
    "10": (["valuation", "pe", "dcf", "roe", "sec"], "equity valuation financial statements DCF ROE PE ratio"),
    "11": (["etf", "nav", "tracking-error", "put-call", "csindex"], "ETF arbitrage premium discount NAV tracking error index methodology"),
    "12": (["option", "put-call", "greeks", "implied-vol", "cboe-edu"], "option payoff put call parity Greeks implied volatility"),
    "13": (["mpt", "frontier", "diversification", "sharpe", "mit-ocw"], "mean variance optimization efficient frontier diversification"),
    "14": (["asset-allocation", "rebalancing", "dca", "risk-parity", "bogleheads"], "strategic asset allocation rebalancing dollar cost averaging lifecycle"),
    "15": (["order-book", "bid-ask", "market-micro", "limit-order", "tradingview"], "intraday chart order book depth bid ask spread tape"),
    "16": (["candlestick", "ohlc", "adjusted-close", "volume", "split"], "candlestick chart OHLC volume adjusted close log scale"),
    "17": (["ma", "support", "technical-analysis", "tradingview"], "moving average trend support resistance crossover"),
    "18": (["macd", "rsi", "bollinger", "stochastic", "ta-lib"], "MACD RSI Bollinger Bands stochastic indicator formula"),
    "19": (["chart-pattern", "support", "technical-analysis", "emh"], "chart patterns head shoulders double bottom gap multi timeframe"),
    "20": (["mdn-svg", "lookahead", "matplotlib", "python-docs"], "programmatic chart rendering SVG look ahead bias detection"),
    "21": (["fama-french", "factor-investing", "smart-beta", "french", "spiva"], "Fama French factors smart beta factor investing evidence"),
    "22": (["emh", "behavioral", "prospect", "disposition", "cfa"], "efficient market hypothesis behavioral finance prospect theory biases"),
    "23": (["herding", "market-micro", "volume", "momentum", "nber"], "fund flow sentiment crowding alternative data"),
    "24": (["ssrn", "arxiv", "p-hacking", "spiva", "nber"], "reading factor papers data mining out of sample evidence"),
    "25": (["survivorship", "adjusted-close", "pandas", "akshare", "tushare"], "data pipeline survivorship bias corporate action alignment"),
    "26": (["backtesting", "lookahead", "slippage", "backtrader", "vectorbt"], "event driven backtest engine transaction cost slippage"),
    "27": (["sharpe", "sortino", "calmar", "attribution", "pyfolio"], "performance attribution Sharpe Sortino maximum drawdown Brinson"),
    "28": (["overfitting", "data-snooping", "p-hacking", "walk-forward", "ssrn"], "overfitting multiple testing walk forward analysis"),
    "29": (["limit-order", "slippage", "market-micro", "ibkr", "cme"], "order execution market impact slippage algorithmic execution"),
    "30": (["var-risk", "cvar", "kelly", "margin", "montecarlo"], "position sizing leverage margin call value at risk CVaR"),
    "31": (["ips", "twr", "mwr", "investor", "bogleheads", "spiva"], "investment policy statement performance review tax compliance"),
    "A": (["cfa", "investopedia", "mit-ocw", "python-docs", "french", "fred"], "investment formulas cheat sheet terminology data sources"),
}

DEFAULT_KEYS = ["cfa", "investopedia", "investor"]


def anchor(key, label=None):
    name, url, _desc, _cat = R[key]
    return ('<a href="' + html_mod.escape(url, quote=True) + '" target="_blank" rel="noopener">'
            + html_mod.escape(label or name) + "</a>")


def links_for_point(chapter_id, point, max_links=2):
    hits = []
    for kw, keys in TOPIC_RULES:
        if kw.lower() in point.lower():
            for k in keys:
                if k in R and k not in hits:
                    hits.append(k)
            if len(hits) >= max_links:
                break
    if not hits:
        hits = list(CHAPTER_RESOURCES.get(chapter_id, (DEFAULT_KEYS, ""))[0])[:max_links]
    return " · ".join(anchor(k) for k in hits[:max_links])


def resource_card(key, why=""):
    """章节「本章参考资料」卡片。"""
    name, url, desc, cat = R[key]
    out = ['<div class="repo-card">', "<h3>" + anchor(key, name) + "</h3>",
           '<span class="tag">' + html_mod.escape(cat) + " · 参考资料</span>",
           "<p>" + html_mod.escape(desc) + "</p>"]
    if why:
        out.append('<span class="why"><strong>怎么用</strong>：' + html_mod.escape(why) + "</span>")
    out.append('<p style="margin:0"><code>' + html_mod.escape(url) + "</code></p></div>")
    return "\n".join(out)


def search_url(query, site="web"):
    if site == "scholar":
        return "https://scholar.google.com/scholar?q=" + quote(query)
    if site == "ocw":
        return "https://ocw.mit.edu/search/?q=" + quote(query)
    if site == "arxiv":
        return "https://arxiv.org/search/?query=" + quote(query) + "&searchtype=all"
    return "https://www.google.com/search?q=" + quote(query)


def chapter_links_html(chapter_id, root="../../"):
    keys, query = CHAPTER_RESOURCES.get(chapter_id, (DEFAULT_KEYS, "investment"))
    out = ["<p>以下资料按本章知识点挑选，可直接精读或对照真实数据；知识点地图里每一条也挂了 1～2 个直达链接。</p>", "<ul>"]
    for k in keys:
        if k not in R:
            continue
        name, _url, desc, cat = R[k]
        out.append("<li><strong>" + html_mod.escape(name) + "</strong>（" + html_mod.escape(cat) + "）："
                   + html_mod.escape(desc) + "<br>" + anchor(k) + "</li>")
    out.append("</ul>")
    out.append('<p class="code-hint">继续扩展：'
               '<a href="' + search_url(query, "scholar") + '" target="_blank" rel="noopener">在 Google Scholar 检索本章相关论文</a> · '
               '<a href="' + search_url(query, "ocw") + '" target="_blank" rel="noopener">在 MIT OCW 检索配套课程</a> · '
               '<a href="' + search_url(query, "arxiv") + '" target="_blank" rel="noopener">在 arXiv 检索预印本</a> · '
               '<a href="' + root + 'index.html#resources">全书参考资源总表</a> · '
               '<a href="' + root + 'appendix/index.html">附录 A 速查与链接总表</a></p>')
    return "\n".join(out)


def all_resources_html():
    cats = {}
    for key, (name, url, desc, cat) in R.items():
        cats.setdefault(cat, []).append((key, name, desc))
    order = ["教材", "课程", "机构", "行情", "数据", "工具", "百科"]
    out = ["<p>本书全部外部链接的唯一来源，按用途分组；各章的「知识点地图」「本章参考资料」「扩展学习」都指向这里。"
           "券商与行情网站仅用于抽象零售交易界面的共同字段，不构成推荐。</p>"]
    for cat in order:
        if cat not in cats:
            continue
        out.append("<h3>" + cat + "（" + str(len(cats[cat])) + "）</h3>")
        out.append('<table><thead><tr><th style="width:30%">名称</th><th>说明</th></tr></thead><tbody>')
        for key, name, desc in cats[cat]:
            out.append("<tr><td>" + anchor(key, name) + "</td><td>" + html_mod.escape(desc) + "</td></tr>")
        out.append("</tbody></table>")
    return "\n".join(out)
