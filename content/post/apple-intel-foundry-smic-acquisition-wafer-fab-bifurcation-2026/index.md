---
title: "Apple-Intel 代工密谈 × SMIC 59 亿美元收购：全球晶圆代工正在分裂成两个完全独立的体系"
description: "2026 年 5 月同一周，Apple 据报与 Intel 谈代工合作，SMIC 获批 59 亿美元收购 SMIC 北方——两件事看似无关，实则是全球晶圆代工史上最大规模'双链分裂'的同期信号。本文拆解 TSMC 容量挤兑、Intel Foundry 战略豪赌、与中国本土代工整合的产业新格局。"
date: 2026-05-14
slug: "apple-intel-foundry-smic-acquisition-wafer-fab-bifurcation-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 半导体
    - 晶圆代工
    - TSMC
    - Intel Foundry
    - SMIC
    - Apple
    - 地缘政治
    - 产业链
draft: false
---

## 引子：5 月 9 日—12 日，三条新闻同时发生

把日期摆出来：

- **5 月 9 日**：Sony Semiconductor Solutions 与 TSMC 在日本签 MoU，成立合资公司开发下一代图像传感器，Sony 持多数股权。
- **5 月 12 日**：SMIC 公告其向"中国大基金"等 5 家股东定向增发，作价 RMB 406 亿（约 USD 59 亿）100% 控股 SMIC 北方，**中国晶圆代工史上最大并购案获上交所并购重组委审议通过**。
- **5 月 12 日**：《华尔街日报》披露，Apple 与 Intel 已就部分 Apple 自研芯片的代工合作达成"初步协议"，谈判持续超过一年；EE Times 跟进报道点明 **特朗普政府"积极参与"撮合**，对象不只 Apple，还包括 NVIDIA 和 SpaceX。

四天内三条新闻、看似无关，**但是全球晶圆代工产业过去 30 年最大规模"双链分裂"的同期信号**。

本文要讲三件事：

1. **TSMC 的"AI 容量挤兑"**：为什么 Apple 这个曾经的 TSMC 头号客户，现在不得不找 Intel？
2. **Intel Foundry 的"国家队转型"**：从 IDM 走向纯代工，并被美国政府变相补贴成"国家关键基础设施"。
3. **SMIC 的"内部整合"**：59 亿美元并购的真实战略含义远超账面——它锁死了中国半导体本土循环的最后一块短板。

## 一、TSMC 的"AI 挤兑"数字

要理解 Apple 为什么找 Intel，先看 TSMC 2026 Q1 真实数字：

| 收入类别 | 2026 Q1 占比 | 同比变化 |
|---------|-------------|---------|
| 高性能计算（HPC）含 AI 加速器 | 61% | +20% QoQ |
| 智能手机 | 26% | -11% QoQ |
| IoT | 6% | 持平 |
| 汽车 | 5% | +6% QoQ |
| 其他 | 2% | - |

HPC = 61%——这个数字 5 年前是 30%、3 年前是 45%。**AI 加速器和数据中心芯片正在以系统性方式挤占 TSMC 的高端节点产能**。

更具体的容量数据（来自 SemiWiki 5 月分析）：

- TSMC N3 (3nm) 月产能：~135,000 wafers
- 其中 NVIDIA 一家锁定：~45,000 wafers（≈33%）
- AMD MI 系列 + 自研 ASIC：~25,000 wafers（≈18%）
- Apple iPhone/Mac 系列：~30,000 wafers（≈22%）
- Broadcom / Marvell / Google TPU 等：~25,000 wafers（≈18%）

Apple 历史上是 N3 的 **launch customer**——这意味着在每个新节点开放第一年，Apple 几乎独占产能。但 2025-2026 这个常规已经被破坏：**NVIDIA、AMD、Google、Amazon 这些 AI 大客户的 HBM + 大 die 设计需要的产能是 iPhone SoC 的 5-10 倍**。

> Chris Miller（《Chip War》作者）在接受 EE Times 采访时点破：  
> "The fact that advanced logic manufacturing capabilities at TSMC are highly constrained given AI will encourage existing customers of TSMC to explore other options for capacity."

翻译：Apple 不是不爱 TSMC 了，是 **挤不进先进节点产能** 了。一个简单数学：M4 Max die 面积约 165mm²，单 wafer 约 380 颗良品；NVIDIA B200 die ~800mm²，单 wafer 约 70 颗良品——同样产能给 NVIDIA 创造的收入是 Apple 的 3 倍。TSMC 是商业公司，毛利率最大化的选择不言而喻。

## 二、Intel Foundry 的"白衣骑士时刻"

Intel 这家公司过去 5 年的故事，本质上是一场 **存亡级转型**：

```text
Intel Foundry 转型进度表
─────────────────────────────────────────────────────────
2021  IFS (Intel Foundry Services) 成立
       Gelsinger 上任，宣布"四年五节点"
─────────────────────────────────────────────────────────
2022  Intel 4 量产（Meteor Lake）
       获得 MediaTek 试单
─────────────────────────────────────────────────────────
2023  Intel 3 量产（Sierra Forest）
       拿到 CHIPS Act $85 亿补贴
─────────────────────────────────────────────────────────
2024  Intel 18A risk production
       Lip-Bu Tan 接任 CEO，砍裁员、剥离非核心
─────────────────────────────────────────────────────────
2025  Intel 18A 量产准备
       美国政府入股 Intel（实际持股 ~9.9%）
       SoftBank/NVIDIA 投资
─────────────────────────────────────────────────────────
2026 ⬇ 2026.05 Apple-Intel 协议曝光（本次事件）
        谈判持续>1年，特朗普政府"积极撮合"
        EE Times 提及 NVIDIA / SpaceX 同样被撮合
─────────────────────────────────────────────────────────
```

Apple 这一单的核心战略含义不是"Intel 拿到了一个客户"，而是 **Intel Foundry 终于有了"非自家"高质量客户验证**。过去 4 年，Intel Foundry 最大的痛点是 **找不到旗舰客户站台**——MediaTek 量小、Qualcomm 浅尝辄止、亚马逊给的是低端节点。Apple 任何一颗芯片在 Intel 流片，都会让 NVIDIA、Qualcomm、Broadcom 等观望者重新评估。

但这单怎么形成的？EE Times 用了一个非常重要的措辞："Trump administration played an active role in encouraging partnerships between Intel and major U.S. technology firms"。**这不是商业撮合，这是政府动员**。

要把这件事看清楚，需要把它放进 **"国家代工厂"** 框架。过去 4 年美国政府对 Intel 的干预度，已经远超对任何一家上市公司：

| 时间 | 干预动作 | 实际效果 |
|------|---------|---------|
| 2022 | CHIPS Act 给 Intel $85 亿补贴 | 财政输血 |
| 2024 | Pat Gelsinger 被董事会"建议"离任 | 战略洗牌 |
| 2025 | 美国政府以 $8.9B 入股，持股 9.9% | 股权层面"国家化" |
| 2025 | SoftBank 投资 $2B，NVIDIA 投资 $5B | 资本盟友 |
| 2026 | 政府"撮合" Apple / NVIDIA / SpaceX 下单 | 商业层面"国家化" |

到 2026 年 5 月这个时间点，**Intel 在公司治理、资本结构、客户来源三个层面同时"国家化"**。这是 SK Hynix、TSMC 当年都没有经历过的待遇。从经济学上看，**Intel Foundry 已经不是一家商业代工厂，而是美国版本的"国家关键基础设施"**——这种结构在能源、电网、铁路上常见，在半导体上是新事物。

这个转型的代价是什么？Intel 的股权稀释、运营自由度下降、被国家利益绑架。**但收益是 Intel 可能成为西方供应链里唯一能与 TSMC 抗衡的玩家**。

Apple 这一单只是开始。我的判断是：未来 18 个月，**NVIDIA 一定会在 Intel 流片至少一颗 SKU**（不是旗舰 H/B 系列，而是 RTX 边缘产品），SpaceX 的 Starshield/Starlink 芯片也会落到 Intel 18A 或 14A。这些都是政治撮合下的"配合下单"，但它们足以撑起 Intel Foundry 的 capacity loading 到盈利门槛。

## 三、SMIC 59 亿美元收购的真实战略含义

把视线转到太平洋另一端。同一周，SMIC 完成了一项**远比 Apple-Intel 更"安静"但战略级别同等**的动作：

SMIC 用增发新股的方式，从大基金（China Integrated Circuit Industry Investment Fund）等 5 家股东手里，买下 SMIC 北方（SMIC North）剩余 49% 股权，让 SMIC 北方成为 100% 全资子公司。交易作价 RMB 406 亿（USD 59 亿）。

表面上看，这是公司治理整理——把分散在多个股东手中的子公司股权收回总部。**但实际上，这次整合是中国半导体本土循环最后一块拼图的合拢**。

要理解这件事，需要先看 SMIC 的组织结构：

```text
中国大陆主要纯代工厂结构（2026-05 整合前后）
─────────────────────────────────────────────────────────
SMIC 集团
├─ SMIC 上海（上海）：12 寸厂 + 8 寸厂，逻辑+混合信号
├─ SMIC 北京（北京）：12 寸厂，逻辑
├─ SMIC 天津（天津）：8 寸厂，逻辑/模拟
├─ SMIC 深圳（深圳）：12 寸厂
├─ SMIC 南方（上海）：12 寸厂，先进节点（14nm/N+1）
└─ SMIC 北方（北京）⬅️ 本次收购对象
   └─ 12 寸厂，多平台，2025 年开始为 SMIC 集团贡献 ~25% 营收

其他独立代工厂：
├─ Hua Hong Group（华虹半导体）：8 寸 + 12 寸成熟工艺
├─ Nexchip（合肥晶合）：12 寸，DDIC 为主
├─ CXMT（长鑫存储）：DRAM 自产
└─ YMTC（长江存储）：NAND 自产
```

SMIC 北方在 SMIC 集团里有个特殊位置——**它是大基金（国家队）和 SMIC 联营的"政策性容量项目"**。大基金的 49% 股权是政策性投资，目的是让 SMIC 加速扩产、补国产 12 寸晶圆缺口。

但这种"政策性股东 + 商业公司"的混合所有制，长期看是低效的：

- 决策慢（重大事项需要五方同意）
- 信息隔离（SMIC 集团的客户订单不能直接调度 SMIC 北方产能）
- 投资规划受限（大基金有自己的回报要求）
- **最关键：与外部敏感技术 / 客户合作时，多股东结构带来合规风险**

完成收购后，SMIC 北方变成 100% 子公司，**SMIC 集团第一次拥有了一个能完全自主调度的"产能池"**。具体规模上：
- 12 寸 wafer 月产能：约 100,000 wafer（推测，含 N+1 节点）
- 工艺平台：覆盖 28nm / 22nm / 14nm / N+1（约等同 7nm）

这次整合在战略层面意味着什么？

**(1) 内部循环闭合**：SMIC 集团 + Hua Hong + Nexchip + 长鑫 + 长江存储，加上 SMEE（光刻机）+ AMEC（刻蚀）+ Naura（多种设备）+ ACM（清洗）等国产设备，**中国本土已经能在 14nm 及以上节点完成"设计-代工-封测-设备-EDA"完整循环**。SMIC 北方的整合是这个循环的最后一个组织瓶颈。

**(2) 国家队信用直接落到 SMIC 财报上**：大基金把股权换成 SMIC 股份，意味着大基金成为 SMIC 集团股东之一（而不只是 SMIC 北方股东）。SMIC 上市公司层面的"国家信用"含量上升。

**(3) 对外谈判筹码增加**：未来 SMIC 与 ASML、Applied Materials、Lam Research、KLA 等外资设备商谈判时，决策链更短、容量保证更明确，**有可能换取更优惠的设备采购条件**。

## 四、为什么这是"双链分裂"的拐点？

把这两件事并列起来看：

```text
2026.05 全球晶圆代工双链分裂格局
────────────────────────────────────────────────────────────

  西方链                              东方链
─────────────────────             ─────────────────────
                                  
  TSMC（主力）                     SMIC（主力）
  ├─ N3/N2 主要服务美国 fabless    ├─ 14nm/N+1 服务中国 fabless
  ├─ HPC + AI 加速器优先           ├─ 整合 SMIC 北方扩产能
  └─ 日本/美国海外扩产              └─ 大基金股权进入母公司
                                  
  Intel Foundry                    Hua Hong / Nexchip
  ├─ Apple 代工（撮合）             ├─ 成熟工艺 / DDIC
  ├─ NVIDIA / SpaceX 跟进           ├─ 与 SMIC 错位竞合
  ├─ 18A / 14A 先进节点              
  └─ 政府股权 9.9%                   
                                  
  Samsung Foundry                   长江存储 / 长鑫
  ├─ Texas/Pyeongtaek 扩产          ├─ NAND / DRAM 自产
  ├─ 服务美国大客户                  └─ 国产存储完整链
  
  Sony × TSMC（日本）              SMEE / AMEC / Naura
  ├─ 图像传感器合资                 ├─ 国产设备协同
  └─ 日本本土再制造化                └─ 14nm 设备国产化率>60%

─────────────────────             ─────────────────────
       服务范围                          服务范围
   美/日/韩/欧 fabless           中国大陆 fabless + "友好国家"
   AI / HPC / 消费电子            消费电子 / 汽车电子 / 国产替代
```

这个格局的核心特征是 **两个体系正在各自闭合**：

- 西方链：通过政府撮合（Apple-Intel）+ 海外扩产（Sony-TSMC Japan）形成"美日韩欧"自循环。
- 东方链：通过内部整合（SMIC 收购 SMIC 北方）+ 国产设备替代形成"中国"自循环。

两者之间的连接（中国客户 → TSMC、美国客户 → SMIC）正在以肉眼可见速度收窄。**TSMC 在中国大陆只剩下成熟节点的 Nanjing fab，先进节点几乎不再服务中国 fabless 客户。SMIC 同样在主动收缩西方客户业务**。

## 五、跨领域类比：这像 1990 年代的银行业分割

如果你看过 1990 年代的全球银行业分割史，会发现非常相似的格局。冷战末期到 90 年代初，美国 / 欧洲 / 日本三大银行体系互相高度交叉持股、相互结算。90 年代后期到 2000 年代，因为巴塞尔协议、反洗钱、地缘政治等多重原因，**全球银行业实际上演了一场"软分割"**——清算系统、SWIFT 准入、监管协调度都按"友好国家圈"重新划分。

半导体代工业 2026 年发生的事，本质是同一种过程的浓缩版。**只不过半导体的物理资本密度更高（一个 N2 fab 投资 $300 亿），分割的代价也更剧烈**。

跨领域类比的关键启示：

1. **分割不会立刻发生**，会以"双供应商策略"等温和形式开始，但十年后形成事实分裂。
2. **被分割的市场会重复造轮**：未来 5 年，中美各自会建出几十个"自己的 fab"，重复投资 $2000-5000 亿美元——这是地缘政治的"行业税"。
3. **分割的赢家是设备和材料商**：两边都买。ASML、Applied Materials、Lam Research、东京电子在双链分裂中都是受益方——只要他们能合规向两边卖货。
4. **分割的输家是 fabless**：原本一颗 SKU 一个 mask 全球通用，现在可能需要 N3（TSMC）+ 18A（Intel）+ N+1（SMIC）三个 mask 集合。

## 六、对从业者的具体启示

**对 fabless 设计公司**：

1. **2026-2027 是"代工厂多元化"的最佳窗口**。Intel、Samsung、SMIC 都在抢客户，给的价格折扣和工程支持是十年最好。
2. **EDA 工具链一定要支持多工厂**。一颗芯片只能跑 TSMC 流程 = 战略风险。Cadence、Synopsys 都在做"多 foundry PDK"，要主动用。
3. **不要 100% 押注先进节点**。AI 加速器之外的大量市场（汽车、IoT、工业），N5/N7/14nm 完全够用，找 Intel/SMIC/Samsung 成熟节点反而毛利更高。

**对设备 / 材料商**：

1. **双链都要进**。ASML 的 EUV 卖到 Intel，DUV 卖到 SMIC（虽然有许可证限制），这种"两边都做生意"在 2026-2030 年仍然合规可行。
2. **关注"国产替代"的反向机会**——AMEC、Naura、Tokyo Electron 都在西方链里有等量市场份额。
3. **服务和维修是真正的护城河**。一台 EUV 装机后的服务合同 $1-2 亿/年/台，这是设备厂商真正的"年金"。

**对投资者**：

1. **TSMC 仍然是"双链分裂"中最稳的标的**。即使丢了一些 Apple 单子，AI 需求足以让其 N3/N2 满载。
2. **Intel Foundry 是高 beta 押注**。国家信用保底但执行风险极高。建议等 18A 量产真实数据再加注。
3. **SMIC 是"中国本土循环"最直接受益者**。但短期看，整合后的整合性 capex 会压缩自由现金流，1-2 年估值压力大。
4. **设备股的相对回报更稳**。ASML、AMAT、TEL、KLA、SMIC 在双链分裂中都是确定受益方。

## 七、判断：5 年后的最终格局

我对 2031 年全球先进节点产能格局的预测：

| 玩家 | 2026 占比 | 2031 占比 | 关键变化 |
|------|---------|---------|---------|
| TSMC | ~58% | ~45% | 仍然主导但份额下降 |
| Samsung Foundry | ~12% | ~12% | 持平 |
| Intel Foundry | ~3% | ~15% | 国家化扶持下的"补位"上升 |
| SMIC + Hua Hong + Nexchip | ~5% | ~18% | 中国本土循环 |
| 其他 | ~22% | ~10% | 整合 / 退出 |

TSMC 的份额下降不是因为它做错了什么，而是因为政策摩擦让它的"全球客户"逻辑被强制重组。**这是最不公平的产业重组之一——但也是不可阻挡的**。

最后一句话：**Apple 找 Intel 不只是商业故事**——它标志着"全球化半导体供应链"这个 40 年范式的官方终结。**SMIC 59 亿收购** 是这个范式终结在东方的镜像。从此之后，"代工厂"这个词，不再只意味着工程能力，**还包含国籍**。

---

## 参考来源

- [EE Times — Apple-Intel Foundry Deal Could Reshape U.S. Chip Manufacturing](https://www.eetimes.com/apple-intel-foundry-deal-could-reshape-u-s-chip-manufacturing/) (Majeed Ahmad, 2026-05-12)
- [TechNode — SMIC secures approval for $5.9 billion acquisition in China's largest domestic wafer foundry M&A](https://technode.com/2026/05/12/smic-secures-approval-for-5-9-billion-acquisition-in-chinas-largest-domestic-wafer-foundry-ma/) (TechNode Feed, 2026-05-12)
- [TechNode — Sony and TSMC form Japan joint venture to develop next-gen image sensors](https://technode.com/2026/05/09/sony-and-tsmc-form-japan-joint-venture-to-develop-next-gen-image-sensors/) (TechNode Feed, 2026-05-09)
- [SemiWiki — The Semiconductor Growth Numbers are Insane but the Real World Doesn't Tally!](https://semiwiki.com/) (Daniel Nenni)
- [TSMC Q1 2026 Earnings Release](https://investor.tsmc.com/) (TSMC IR)
- [The Wall Street Journal — Apple, Intel Reach Preliminary Agreement on Chip Manufacturing](https://www.wsj.com/) (WSJ scoop, 引用自 EE Times)
- [Chris Miller — "Chip War: The Fight for the World's Most Critical Technology"](https://www.simonandschuster.com/books/Chip-War/Chris-Miller/9781982172008) (Simon & Schuster, 2022) — 行业背景
- [SemiWiki — SiFive's P570 Gen 3 Pushes RISC-V Further Into the AI Era](https://semiwiki.com/artificial-intelligence/369216-sifives-p570-gen-3-pushes-risc-v-further-into-the-ai-era/) (2026-05-14, 行业上下文)
