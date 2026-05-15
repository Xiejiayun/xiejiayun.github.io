---
title: "美国万亿美元 AI 算力豪赌：电力缺口才是真正的'硬约束'，所有估值模型都得重写"
description: "Apricitas Economics 同时甩出两枚信号弹 —— 美国 AI 资本开支已逼近 1 万亿美元，但美国电网在 2026-2030 年缺口至少 80 GW。本文把'算力支出曲线'和'发电增量曲线'真正叠在一张图上，得出一个反共识结论：决定 AI 公司估值上限的，不是 GPU 价格、不是模型能力，而是它们的'电力获取能力'。这条线在主流投行报告里几乎没有被定价。"
date: 2026-05-15
slug: "america-trillion-dollar-ai-electricity-capex-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - AI 资本开支
    - 电力
    - 数据中心
    - 算力经济学
    - 美国电网
    - 估值
draft: false
---

> **核心观点**：2026 年美国 AI 资本开支即将突破 1 万亿美元，而美国电网在同一时期至少有 80 GW 的可调度容量缺口。把这两条曲线叠加，得到一个被主流投行严重低估的事实：**未来 3 年决定一家 AI 公司估值上限的不是 GPU 价格，不是模型能力，而是它能否抢到电力**。电力获取能力即将成为新的"FAANG 之外的护城河"。从 OpenAI 与 SpaceXai/Anthropic 的 300 MW Colossus 合约、到马斯克在田纳西河谷的天然气电厂自建，行业前沿玩家已经悄悄定价这件事，散户和大部分投行分析师还在卖 GPU 周期股的故事。

## 一、两条曲线必须叠在一起看

### 1.1 算力资本开支曲线

Apricitas Economics 的 [America's $1T AI Gamble](https://apricitas.io/) 给出关键数字（汇编自 Microsoft、Google、Meta、Amazon、Oracle 四份 FY2026 capex guidance + OpenAI/Anthropic/xAI 私募与项目融资）：

- 2024 年：约 2400 亿美元
- 2025 年：约 5600 亿美元
- **2026 年（估）：约 9500 亿美元 - 1.1 万亿美元**
- 2027 年（预测）：1.4-1.7 万亿美元
- 2028 年（区间预测）：1.5-2 万亿美元

这不是 dot-com 时代电信骨干那种"赌错也只是亏",这是把美国 GDP 的 3-4% 全部压在一个新产业**单年**资本开支上的赌局。

### 1.2 电力供给曲线

Apricitas 的姐妹文章 [America's Electricity Gap](https://apricitas.io/) 数据：

- 美国 2024 年总发电量：约 4,150 TWh
- 数据中心 2024 年用电占比：约 4.5%
- 2030 年数据中心用电预测：占比 12-18%（保守-激进区间）
- 折算新增电力需求：**+ 220-380 TWh 年用电量**
- 折算需要新增装机：**+ 60-110 GW 可调度容量**

但美国实际**新增装机**进度是这样的：

| 年份 | 新增可调度容量 | 退役（主要是燃煤） | 净增量 |
|------|----------------|---------------------|---------|
| 2024 | +18 GW | -15 GW | +3 GW |
| 2025 | +25 GW（估） | -12 GW | +13 GW |
| 2026 (规划) | +30 GW | -10 GW | +20 GW |
| 2027 (规划) | +35 GW | -8 GW | +27 GW |
| 2028-2030 (规划) | +120 GW 累计 | -20 GW 累计 | +100 GW 累计 |

注意"规划"两个字。**实际并网时间 vs 规划时间的 slip 中位数是 18-30 个月**（PJM、ERCOT、CAISO 三大调度机构 2025 年互联队列年报）。所以更现实的净增量预测：

- 2026-2030 年累计净增量：60-80 GW（vs 需求 60-110 GW）
- 缺口（基准情景）：**0-50 GW**
- 缺口（激进情景）：**50-110 GW**

把两条曲线放一起：算力以 50% / 年增长，电力以 5-10% / 年增长。**这是一个数量级的不匹配**。

## 二、为什么 GPU 短缺会被电力短缺取代

2024 年的稀缺资源是 H100。2025 年是 HBM。2026 年的稀缺资源正在变成 **电力 + 输电容量 + 冷却水**。

### 2.1 一个 100 MW 数据中心的现实

行业标杆"AI Factory"项目（OpenAI / Anthropic / Stargate / xAI 等）每个目标算力规模在 1-5 GW。一个 100 MW 的数据中心已经是中等规模。

要让 100 MW 数据中心在美国某地并网，时间表大致是：

| 阶段 | 耗时 | 关键卡点 |
|------|------|----------|
| 选址 + 土地 | 3-6 个月 | 距离变电站 < 10 mile、冷却水源、地方政府税收 |
| 输电互联申请 | **24-48 个月** | 排队、负荷研究、PJM/ERCOT 升级需求 |
| 变电站建设 / 升级 | 12-24 个月 | 变压器 lead time 现在是 36 个月+ |
| 园区建设 | 12-18 个月 | 跟互联并行 |
| GPU 安装 | 3-6 个月 | 此时 GPU 早已不是瓶颈 |

**变压器** 是最被低估的卡点。Hitachi Energy、Siemens Energy、ABB 三家全球高压变压器供应商的订单簿已排到 2029 年。

### 2.2 谁先意识到这件事

行业前沿玩家在 2024-2025 年就开始绕开电网：

1. **xAI / Colossus（孟菲斯）**：直接在场地搭建燃气轮机（VoltaGrid 提供，~150 MW 移动式），不等公共电网升级
2. **Anthropic-SpaceXai 合作（Stratechery 报道）**：2025-2026 年签下 300 MW、$5 B/year 的算力供应合约，背后的电力来源高度依赖 SpaceX 旗下私有电力设施
3. **Meta**：在路易斯安那签下 1.5 GW 长期 PPA + 2 座新建燃气电厂
4. **Microsoft**：与 Constellation Energy 重启 Three Mile Island 1 号机组（核电），20 年 PPA
5. **Amazon**：与 Talen Energy 同样在 Susquehanna 核电站做"behind-the-meter"互联
6. **OpenAI / Stargate**：阿布扎比 + 德州双站点，前者直接靠 ADIA 主权基金 + 当地能源公司，跳出美国电网逻辑

这些动作的共同特征是：**把"电力来源"从一个不动产问题变成战略并购问题**。

### 2.3 资本市场还没有定价这件事

主流投行报告（Goldman、MS、JPM）的 AI capex 模型里，电力还是按"输入成本 0.05-0.08 USD/kWh"的常数处理。但现实是：

- PJM 2025 年容量拍卖结算价：相比 2024 年涨 8 倍（$269/MW-day）
- ERCOT 现货高峰电价：动辄 $5,000-9,000/MWh
- 数据中心 PPA 长期合约价：从 2023 年的 $30/MWh 升至 2026 年的 $65-90/MWh

把电力成本的真实曲线套进 AI 数据中心 TCO 模型，会发现：

> **电费在数据中心 10 年 TCO 中的占比，从 2022 年的 15-20% 上升到 2026 年的 35-50%**。

这意味着：

- 估值"算力投入产出比"的核心分母变了
- 持有低价长期电力合约的公司有结构性优势
- 在偏远州（爱达荷、北达科他、怀俄明）的"建在风/太阳能场旁边"的数据中心方案重新获得估值
- "迁移到加拿大魁北克 / 冰岛 / 沙特"的方案从"小众"变成"主流备选"

## 三、Marc Rubinstein 与 Byrne Hobart 的旁注

科技金融领域的几位敏锐写作者已经在不同侧面捕捉这件事：

### 3.1 Marc Rubinstein（Net Interest）："Money for Nothing"

Marc 在 5 月的 [Money for Nothing](https://www.netinterest.co/) 里指出：**AI 数据中心 capex 的资本结构正在从"超大科技公司自有资本 + 经营现金流"转向"项目融资 + ABS（资产支持证券）"**。

意义：

- 2024 年 Microsoft、Google、Meta 主要用自由现金流盖数据中心
- 2025-2026 年开始引入 Blackstone、Brookfield、KKR、Stonepeak 等基础设施基金（已宣布的就有 $500B 级别承诺）
- 项目融资意味着电力供应合约（PPA）和容量预约成为关键抵押品
- 这把 AI 算力直接接入了**基建金融的成熟资本池**，规模上限从万亿美元打开到数万亿美元

### 3.2 Byrne Hobart（The Diff）：电网的"Solid-State Economics"

Byrne 的视角更基础：[Stripe and Solid-State Economics](https://thediff.co/) 里他的核心论点是，**当一个产业的关键投入从"流动的"变成"长期锁定的"，估值倍数会本质改变**。

数据中心电力 PPA 是典型的"长期锁定" —— 一旦签了 15-20 年 $50/MWh 的合约，你就有了一项资产负债表上看不到、但 EBITDA 模型里巨大的隐藏价值。Microsoft 重启 Three Mile Island 的真实长期价值，可能是会计报表上数字的 3-5 倍。

### 3.3 Apricitas 自己的"$1T 赌局"判断

Joseph Politano 在 Apricitas 文章里给出的最重要一句话不是数字，是这句：

> "**America is making a $1 trillion bet that AI will deliver returns commensurate with the scale of investment, and that we can build the electricity infrastructure to power it. Neither outcome is guaranteed.**"

这话比所有"AI 是泡沫" / "AI 是革命"的极端论调都更有信息量。它把不确定性放回到正确的位置：是**两个独立的赌注**叠加，每个都需要兑现。

## 四、对不同读者的可执行结论

### 4.1 给一二级市场投资人

- **不要把电力供应能力当作背景常数**，而要作为核心 KPI 跟踪
- 关注美国电力设备龙头：Eaton、Schneider Electric、GE Vernova、Hitachi Energy、Vertiv —— 这些是"卖铲子的铲子"
- 重点跟踪：变压器交付周期、PJM 容量价格、各 AI 巨头的 PPA 披露
- 警惕：把 AI 算力公司估值乘数推得太高的报告，如果它们的电力成本假设还是 2023 年水平

### 4.2 给数据中心运营方与企业 CTO

- 长期电力合约现在的边际价值远高于一年前；如果你的合约 18 个月内到期，**立刻开始新合约谈判**
- 评估"小型模块化反应堆（SMR）+ 燃气调峰"作为 2028-2030 年的方案
- 重新考虑地理分布：美国东海岸 / 加州的扩张可能要让位于田纳西河谷、得州 Permian、爱达荷
- 提高 PUE 之外的指标 —— **每 kWh 输入产出的 token 数**会成为新的运营基准

### 4.3 给政策制定者

- 美国当前电网互联队列改革（FERC Order 2023 等）远不足以应对 AI capex 增速
- 中国能源结构的相对优势在 AI 时代被放大：中国 2024 年新增装机 ~430 GW，是美国的 10 倍
- 这是地缘政治意义上的 AI 竞赛中，**最被低估**的不对称
- 政策上"批准核电延寿 + 加速 SMR 部署 + 输电线建设许可改革"是三大杠杆

### 4.4 给 AI 创业者
- 你的下一轮融资 deck 里应该加一栏："电力供应保障"。投资人在 2027 年会问这个问题
- 别假设云厂商会无限给你 H100 / B200 配额，他们自己在做电力分配优化
- 在偏远低电价地区（北达科他、怀俄明、加拿大 Manitoba）做 inference 边缘节点，可能是创业公司绕开巨头算力垄断的少见路径

## 五、结语：算力经济学的"硬约束"回归

20 世纪 90 年代有一句话流传至今："**Software is eating the world.**"
2010 年代它升级成："**Compute is eating software.**"
2026 年，我们看到的现实是：

> **Electricity is eating compute.**

这不是诗意化的说法。它是 Apricitas 的数据 + Marc Rubinstein 的资本结构观察 + Byrne Hobart 的长期合约理论的合力结论。

万亿美元 AI 算力豪赌的真正瓶颈，不在台积电、不在 SK Hynix、不在 NVIDIA 路线图、也不在 Anthropic 的下一代模型 —— **它在变电站和 230 kV 输电线上**。

主流叙事还在演"模型能力 vs 模型能力"。但聪明钱已经悄悄在演"**谁先拿到下一个 1 GW**"。

这是 2026 年中段，AI 行业最值得记下来的一句话。

## 参考来源

1. Apricitas Economics — [America's $1T AI Gamble](https://apricitas.io/)
2. Apricitas Economics — [America's Electricity Gap](https://apricitas.io/)
3. Apricitas Economics — [The Tariff Exemption Behind the AI Boom](https://apricitas.io/)
4. Marc Rubinstein — [Money for Nothing](https://www.netinterest.co/)，Net Interest
5. Marc Rubinstein — [Bye the Index](https://www.netinterest.co/)
6. Byrne Hobart — [Stripe and Solid-State Economics](https://thediff.co/)
7. Stratechery — [SpaceX and Anthropic, xAI's Two Companies, Elon Musk and SpaceXAI's Future](https://stratechery.com/)
8. Latent Space — [Anthropic-SpaceXai's 300MW/$5B/yr deal for Colossus I](https://www.latent.space/)
9. PJM Interconnection — 2025-26 Base Residual Auction Results
10. ERCOT — Capacity, Demand, and Reserves (CDR) Report, December 2025
11. Marginal Revolution — [Data centers are good](https://marginalrevolution.com/) （反方视角）
12. FERC Order 2023 — Improvements to Generator Interconnection Procedures
