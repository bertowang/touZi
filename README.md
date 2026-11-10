# 投资理财：从产品到证据

> 一本写给「爱好买股票、基金、ETF 等投资理财产品的计算机专业学生」、覆盖本科到研究生的教材。全书不按技巧拼盘，而沿 **现金 → 产品 → 定价 → 组合 → 盘面 → 证据 → 执行 → 风险 → 复盘** 一条主线，把交易 App 上的每个入口还原成现金流权利、数据字段与可检验的假设；每章配一个只用 Python 3 标准库、可实跑、打印数值并自绘 SVG 图的分析脚本。

[![Static HTML](https://img.shields.io/badge/format-static%20HTML-orange)](./index.html)
[![Chapters](https://img.shields.io/badge/chapters-32%20%2B%20appendix-blue)](#内容结构)
[![Python 3](https://img.shields.io/badge/Python%203-32%20demos-3776AB)](#快速开始)
[![SVG charts](https://img.shields.io/badge/charts-59%20SVG-8a6316)](#每章包含什么)
[![Stdlib only](https://img.shields.io/badge/dependencies-stdlib%20only-2ea44f)](#约定与边界)
[![License](https://img.shields.io/badge/license-not%20specified-lightgrey)](#许可证)

**仓库**：[github.com/bertowang/touZi](https://github.com/bertowang/touZi) · **阅读入口**：[index.html](./index.html) · **版本**：v0.1 · 2026-11

---

## 目录

- [一眼看懂](#一眼看懂)
- [这本书的写法](#这本书的写法)
- [快速开始](#快速开始)
- [内容结构](#内容结构)
- [仓库结构](#仓库结构)
- [每章包含什么](#每章包含什么)
- [工具链与维护](#工具链与维护)
- [质量保障](#质量保障)
- [约定与边界](#约定与边界)
- [同系列教材](#同系列教材)
- [作者与 AI 使用说明](#作者与-ai-使用说明)
- [许可证](#许可证)

## 一眼看懂

| 项目 | 内容 |
| --- | --- |
| 读者定位 | 爱好股票 / 基金 / ETF 的计算机专业学生，本科到研究生；需要基础编程与一点概率统计 |
| 规模 | 32 章（00–31）+ 附录 A · 5 个学习阶段 · 34 个 HTML 页面 · 32 个 Python 脚本 · 59 张 SVG 图 |
| 内容形态 | 纯静态 HTML5 + CSS + 原生 JS；无外部依赖，离线 / `file://` 可读 |
| 分析脚本 | Python 3 **只用标准库**（`math` / `random` / `statistics` + 仓库内 `tools/chart.py`），固定 `random.seed(7)`，自包含合成数据 |
| 图表 | 由脚本运行时生成文本矢量 `fig/*.svg`，可提交、可 diff、可离线缩放，不依赖 matplotlib |
| 扩展资源 | 166 条外部链接（CSRC / 交易所 / CFA / MIT OCW / Ken French / FRED / Investopedia / Bogleheads 等） |
| 维护工具 | Python 3 生成器 / 抽取器 / 自检器 + `run_python.sh` 批量实跑 |
| 状态 | 32 章全部完稿；静态自检 0 错误 0 提示，32/32 脚本实跑通过 |

## 这本书的写法

投资不是「预测价格」，而是**在约束下管理一组带不确定性的现金流**。全书把这件事写成一条可复现的工程链路：目标是规格说明书，产品是接口，定价是折现算子，组合是带协方差正则的优化，盘面是事件流的可视化，策略是对历史数据的假设检验，实盘是带成本与延迟的部署。

- **有机组合**：先写「本章位置」说明承接与引出，再给「给程序员的翻译」把概念映射到计算概念（例如复权是版本化 migration、订单簿是双端优先队列、再平衡是负反馈控制器）。
- **高屋建瓴但落地**：第一、二篇先建立产品地图与定价，第三篇才讲看图识图；第四篇先讲「什么算证据」，第五篇才讲实盘——避免把盘面技巧当成投资的全部。
- **看图先校准数据**：K 线、均线、MACD、RSI、布林带、KDJ、双底形态全部先写公式与判定条件，再用代码画图验证；专门用一章复现「未来函数」如何制造虚假超额收益。
- **诚实的方法论**：过拟合、多重检验、幸存者偏差、前视偏差、样本外与执行成本各有独立章节，且都用可运行的对照实验量化，而不是只给警告。
- **零依赖手写**：OLS、二叉树定价、事件驱动回测、绩效归因、蒙特卡洛全部展开成可读循环；附录 A.6 给出与 `numpy` / `statsmodels` / `Backtrader` / `TA-Lib` 的迁移对照。

**不适合**：期待真实行情数据集、实时收益或具体操作建议的读者。本书所有行情与净值都是合成数据或模型示意，真实数据入口集中在附录 A.7。

## 快速开始

### 1. 阅读（无需构建、无需服务器）

```bash
git clone git@github.com:bertowang/touZi.git
cd touZi
open index.html          # macOS；Linux 用 xdg-open，Windows 双击即可
```

也可以直接点开 [index.html](./index.html)，或启用 GitHub Pages 后以 `index.html` 为入口发布成站点。侧栏、面包屑与上下章导航共用 [assets/toc.js](./assets/toc.js) 这一份数据。

### 2. 跑一个分析脚本（约 30 秒）

```bash
# 需要 Python 3.8+，不需要安装任何第三方包
python3 part1/03-product-map/code/03-products.py
# 热力图: .../fig/03-product-map.svg
# 排序图: .../fig/03-ranking.svg
# 建议顺序: 货币基金 > 宽基ETF > 国债/债券ETF > ... > 期权/期货
# 最高=0.295 最低=0.055 | 打分仅用于演示「先定维度再排序」的方法
```

脚本会打印可手算核对的数值，并在章节目录的 `fig/` 下写出 SVG 图；刷新章节页即可看到插图。

### 3. 批量运行与自检

```bash
./tools/run_python.sh                       # 跑完全部 32 个脚本并生成 59 张 SVG
python3 tools/check_book.py --run            # 静态自检 + 实跑全部脚本
python3 tools/check_book.py --urls           # 可选：联网探测 166 条外部链接
```

## 内容结构

| 阶段 | 章节 | 主题 |
| --- | --- | --- |
| 一 · 共同语言与产品地图 | 00–08 | 工程视角、复利与实际收益、风险度量、可交易产品分类、交易规则、账户费用、OHLCV 数据模型、基金与 ETF、固收与现金管理 |
| 二 · 定价、组合与资产配置 | 09–14 | 久期与凸性、DCF 估值、指数与 ETF 套利、期权 payoff 与平价、均值-方差与有效前沿、再平衡与生命周期 |
| 三 · 盘面语言与看图识图 | 15–20 | 订单簿与冲击、K 线与复权、均线趋势、四大指标公式、形态的可判定规则、SVG 画图与未来函数 |
| 四 · 从直觉到可验证的证据 | 21–28 | 因子与 FF3、行为偏差与处置效应、资金拥挤、论文复现、数据管道、事件驱动回测、绩效归因、过拟合与多重检验 |
| 五 · 实盘、风险与长期主义 | 29–31、附录 | 执行算法与滑点、仓位/杠杆/VaR/CVaR/凯利、IPS 与长期复盘、公式与术语速查 |

交易 App 相关的内容不是「平台教程」：书中把富途牛牛、东方财富 / 东方赢家一类终端抽象成共同的界面字段（代码、最小单位、盘口、复权、交易时段、费用、风险等级），只讲这些字段背后的机制，不评价任何平台或产品。

## 仓库结构

```text
touZi/
├── index.html                  # 总目录（唯一入口）
├── assets/
│   ├── style.css               # 统一排版样式
│   ├── app.js                  # 主题、侧栏、复制代码、上下章导航
│   └── toc.js                  # 由生成器写出的目录唯一数据源
├── part0/ … part6/             # 七个分部
│   └── NN-slug/
│       ├── index.html          # 章节正文（生成物，不要手改）
│       ├── code/NN-xxx.py      # 可运行分析脚本（由 extract_code.py 同步）
│       └── fig/*.svg           # 脚本运行生成的矢量插图
├── appendix/index.html         # 公式速查、术语表、检查清单、示例与资源总表
└── tools/
    ├── book_schema.py          # 分部、学习阶段、章节与示例数据接口
    ├── book_resources.py       # 166 条外部链接与知识点挂链规则
    ├── book_data.py            # 章节汇总与数据层一致性校验
    ├── chapter_kit.py          # 示例脚本样板与 HTML 片段助手
    ├── chapters_*.py           # 六份章节正文与 Python 示例数据源
    ├── chart.py                # 纯标准库 SVG 绘图（折线/柱/散点/K线/热力图）
    ├── build_book.py           # HTML + toc.js 生成器
    ├── extract_code.py         # 从 HTML 代码块同步 code/*.py
    ├── run_python.sh           # 批量运行示例并生成插图
    └── check_book.py           # 静态自检 + 可选实跑 / 链接探测
```

## 每章包含什么

- **本章位置 / 给程序员的翻译**：承接什么、引出什么，以及对应的计算概念。
- **学习目标 / 知识点地图**：可检验的动词；每条知识点挂 1～2 个直达链接。
- **原理小节 §x.y**：概念、公式推导、对照表、边界条件与常见误区。
- **Python 分析实例**：完整脚本 + 操作步骤 + 预期数值与判读 + 改参数提示 + 自绘 SVG 图。
- **本章参考资料 / 扩展学习**：按知识点挑选的机构、课程、数据、工具与检索入口。
- **常见误区 / 习题**：典型错误与可动手验证的思考题。

所有示例遵守同一契约：只用标准库 + `tools/chart.py`；自包含合成数据，不联网、不读外部文件；`random.seed(7)` 固定随机数；参数集中在「参数区」；打印可核对数值；生成 `fig/*.svg`；页面代码块与 `code/*.py` 自动同步。

## 工具链与维护

**不要直接编辑章节 HTML**，下次重建会被覆盖。改完数据后依次运行：

```bash
python3 tools/build_book.py --force    # 重建全部页面 + assets/toc.js
python3 tools/extract_code.py          # 同步 code/*.py
./tools/run_python.sh                  # 生成 fig/*.svg
python3 tools/check_book.py --run      # 静态自检 + 实跑
```

| 想改什么 | 编辑哪里 |
| --- | --- |
| 某章正文或 Python 示例 | `tools/chapters_*.py` 中的 `C(...)` / `mk_demo(...)` |
| 参考资料链接 | `tools/book_resources.py` 的 `R` / `TOPIC_RULES` / `CHAPTER_RESOURCES`，以及章节 `highlights` |
| 页面结构与总目录 | `tools/build_book.py` 的 `render()` / `render_index()` |
| 样式与交互 | `assets/style.css`、`assets/app.js` |
| 新增章节或分篇 | `tools/book_schema.py` 的 `PARTS` + 对应 `chapters_*.py` |
| 新增图表类型 | `tools/chart.py`（纯标准库 SVG） |

`python3 tools/build_book.py --list` 可列出全部章节；`python3 tools/extract_code.py --check` 只检查代码块与磁盘脚本是否一致。

## 质量保障

`check_book.py` 一次检查：章节 id / 目录 / 分部 / 字段完整性、资源 key 有效性、`toc.js` 与总目录链接一致性、状态与阶段徽章、每页页脚与占位符、全部内链与本地锚点、HTML 标签平衡、代码块与 `code/*.py` 同步、**59 张 SVG 的 XML 合法性与声明一致性**、脚本零依赖与语法、可选实跑、可选外部链接探测。

```text
$ python3 tools/check_book.py --run
实跑：32 / 32 个脚本通过
自检：34 个 HTML 页面，33 个章节，32 个 Python 脚本，59 张 SVG 图，0 条错误，0 条提示
```

## 约定与边界

- **教学材料，不构成投资建议**：所有行情、净值、回测与图表均为合成数据或模型示意，不构成任何投资建议、产品推荐或收益承诺；历史与回测表现不代表未来收益；杠杆、衍生品、跨境与场外产品可能导致本金全部损失。
- **真实投资**须遵守所在市场的法律法规、投资者适当性管理、券商与基金销售机构的风险揭示，并自行承担决策后果。
- **书中提及的券商 App 与行情网站**仅用于抽象零售交易界面的共同字段，不构成推荐或从属关系。
- **零第三方依赖**是刻意选择：为的是让每个公式、每张图都能被读懂和改动；工业实现见附录 A.6。

## 同系列教材

- [analogCircuits · 模拟电路：从读懂到设计](https://github.com/bertowang/analogCircuits)
- [imageProcessing · 数字图像处理：从经典算法到智能方法](https://github.com/bertowang/imageProcessing)
- [studyingEconomics · 经济学：从稀缺到证据](https://github.com/bertowang/studyingEconomics)

## 作者与 AI 使用说明

作者：汪亮（bertonwang）· 联系邮箱：47608843@qq.com

本教材的知识框架、正文、Python 分析示例与参考资料清单在 AI 辅助下整理生成，并经人工校订、实际运行与静态自检。公式、数值与运行结果请以 Python 3 实际输出及权威教材、官方文档为准；发现错漏欢迎通过上方邮箱勘误。

## 许可证

本仓库未显式声明许可证；如需复用或再发布，请先联系作者。外部参考资料均为各维护者的项目，本书与之无从属关系。
