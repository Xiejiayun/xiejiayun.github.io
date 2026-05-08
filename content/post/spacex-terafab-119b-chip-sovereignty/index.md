---
title: "SpaceX Terafab：1190 亿美元的芯片工厂，是算力主权的新形态还是 Musk 式豪赌？"
description: "当火箭公司开始建芯片工厂，当 Intel 为 SpaceX 代工，算力产业的版图正在被重新绘制。"
date: 2026-05-08
slug: "spacex-terafab-119b-chip-sovereignty"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - SpaceX
    - 芯片制造
    - 算力主权
    - 产业战略
draft: false
---

## 引言：火箭公司为什么要造芯片？

2026 年 5 月，德州 Grimes 县的一份公开听证文件揭示了 SpaceX「Terafab」项目的惊人规模：**初始投资 550 亿美元，总投资可能膨胀至 1190 亿美元**。目标是每年生产 200 GW 计算能力的芯片，远期规划是太空部署的 1 TW 算力。

这不是一家芯片公司的故事——这是一家火箭公司、一家汽车公司、和一家正在破产边缘挣扎的传统半导体巨头的三角联盟。

## 项目解剖：Terafab 到底要造什么

### 规模对标

| 指标 | Terafab | TSMC 亚利桑那 | Intel Ohio | Samsung Taylor |
|------|---------|-------------|----------|---------------|
| 总投资 | $1190 亿 | $400 亿 | $280 亿 | $170 亿 |
| 位置 | 德州 Austin | 亚利桑那 | 俄亥俄 | 德州 Taylor |
| 预计产能 | 200 GW/年 | ~5万片/月 | ~5万片/月 | ~3万片/月 |
| 主要客户 | SpaceX/Tesla | 自有客户 | 自有+代工 | 自有+代工 |

1190 亿美元是什么概念？这超过了 TSMC 全球所有在建工厂的投资总和。即使只看初始的 550 亿美元，也已经与 Intel 的 Ohio Mega-Site 相当。

### 三方联盟的逻辑

**SpaceX**：需要抗辐射、低功耗的太空级芯片用于 Starlink 卫星和星际飞船的自主导航。目前 Starlink 的芯片依赖外部供应商，在地缘政治风险上升的环境下，垂直整合是合理选择。

**Tesla**：需要大量定制 AI 推理芯片用于自动驾驶（FSD）和 Optimus 机器人。Dojo 超级计算机的芯片也需要自主供应。

**Intel**：作为 Terafab 的设计与制造合作伙伴，Intel 获得了一个规模空前的「锚定客户」。Intel 的声明——「我们在设计、制造和封装超高性能芯片方面的能力，将帮助加速 Terafab 的目标」——暗示了 Intel Foundry Services (IFS) 的关键角色。

## 「200 GW/年」意味着什么

Terafab 用「瓦特」而非「晶圆数」来衡量产能，这本身就是一种叙事策略。传统半导体行业用每月晶圆产量（wafers per month, WPM）来衡量工厂规模。SpaceX 用算力功率作为指标，暗示其芯片不是通用处理器，而是**专用 AI 加速器**——类似于 TPU 或 Trainium 的定位。

200 GW 年产量如果折算成 NVIDIA H200 等级的加速器（约 700W TDP），意味着约 28.6 万颗芯片/年。这个数字看似不大，但如果 SpaceX 的芯片功效比足够高，实际的计算能力可能远超表面数字。

更有趣的是「1 TW 太空部署」的远期目标。这意味着 SpaceX 设想在近地轨道部署大规模太空数据中心——利用太阳能供电、真空散热、和全球覆盖的低延迟网络（Starlink）。这听起来像科幻，但如果 Starship 将发射成本降到 $10/kg，太空算力的经济学就开始成立。

## Colossus 数据中心：SpaceX 的算力野心已经落地

Terafab 不是 SpaceX 在算力领域的第一步。其位于 Memphis 的「Colossus」数据中心已经与 Anthropic 签约，为 Claude 系列模型提供推理算力。这意味着 SpaceX 已经是 AI 基础设施的供应商——Terafab 只是将这一战略从「买芯片」升级到「造芯片」。

## 地缘博弈：算力制造的回流

Terafab 的选址（德州 Austin 附近）和税收减免申请揭示了一个更大的棋局：**美国正在通过产业政策将算力制造从亚洲拉回本土**。

CHIPS Act 提供了直接补贴，但真正的杠杆是「锚定需求」——SpaceX/Tesla 作为自身最大客户，消除了传统代工厂的产能利用率焦虑。这是一种新型的产业政策模式：不是政府补贴 → 工厂建设 → 寻找客户，而是**客户自建工厂 → 申请政府补贴 → 产能自消化**。

## 风险分析：为什么这可能失败

### 1. 制程技术差距

SpaceX/Tesla 没有半导体制造经验。即使有 Intel 的支持，从零开始建立世界级芯片工厂需要 3-5 年的良率爬坡。Intel 自身的 18A/14A 制程尚在验证中，能否为 Terafab 提供成熟技术是个问号。

### 2. 资金来源的不确定性

1190 亿美元从哪来？SpaceX 的估值约 $2500 亿，Tesla 的市值约 $8000 亿。即使两家公司联合，这个投资规模也需要大量外部融资或政府补贴。

### 3. Musk 因素

Elon Musk 同时运营 SpaceX、Tesla、xAI、Neuralink、The Boring Company 等多家公司。Terafab 需要持续的管理注意力和战略一致性——而 Musk 的注意力是整个 Musk 帝国最稀缺的资源。

### 4. 需求预测风险

200 GW/年的产能假设了 AI 算力需求的持续指数增长。如果 AI 效率提升速度快于需求增长（类似于 Jevons 悖论的反面），这些产能可能过剩。

## 判断

Terafab 是 2026 年最大胆的产业赌注，没有之一。它同时赌注了三件事：AI 算力需求持续爆发、美国本土制造可以与亚洲竞争、以及太空数据中心在 2030 年代成为现实。

任何一个赌注失败，Terafab 都会缩水为一个昂贵的教训。但如果三个赌注都对了，SpaceX 将从一家发射服务公司变成**全球算力基础设施的垂直整合商**——从芯片制造到太空数据中心到全球网络，完整闭环。

不管 Terafab 最终是否按计划完成，它已经改变了一个事实：**算力主权不再只是国家行为，私人公司也开始下注千亿级的芯片制造**。这对全球半导体产业格局的影响，可能比任何政府政策都深远。

## 参考链接

- [SpaceX has a $55 billion plan to build AI chips in Texas](https://www.theverge.com/ai-artificial-intelligence/926356/spacex-tera) — The Verge
- [Intel Earnings, Intel's Differentiation?, Whither Terafab](https://stratechery.com/2026/intel-earnings-intels-differentiation-whither-terafab/) — Stratechery
- [Amazon Earnings, Trainium and Commodity Markets](https://stratechery.com/2026/amazon-earnings-trainium-and-commodity-markets/) — Stratechery
- [CHIPS and Science Act](https://www.congress.gov/bill/117th-congress/house-bill/4346) — U.S. Congress
