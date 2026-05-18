---
title: "在硅光晶圆上'印'激光器：Ghent + imec 的微转移印刷，给硅光集成开了第三条工艺路径"
description: "硅光集成多年的卡点不是设计，是工艺——硅本身不能直接做激光器，III-V 族化合物半导体又难以与 CMOS 共存。Ghent 大学与 imec 的最新论文把'微转移印刷'（Micro-Transfer Printing, MTP）从实验室原型推到了规模化整合的边缘——把激光器、调制器、单光子探测器像'印刷'一样转移到硅光晶圆上。这是 800G 之后光互连扩散的关键工艺底座。"
date: 2026-05-18
slug: "micro-transfer-printing-silicon-photonics-heterogeneous-integration-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 硅光集成
    - 异构集成
    - 微转移印刷
    - 半导体工艺
    - 数据中心光互连
draft: false
---

## 硅光的"激光器问题"

硅光子学（silicon photonics）这十年从研究走到 Nvidia GB200 NVL72、Marvell 1.6T DSP 的真实产品里。但它一直没有解决一个根本难题：**硅本身不能做激光器**。

硅是**间接带隙半导体**，电子-空穴复合时大部分能量以热释放，不发光（或发光效率极低）。所有真正的高效激光器都是**直接带隙**——InP（磷化铟）、GaAs（砷化镓）、InGaAsP——属于 III-V 族化合物半导体。

要把激光器和硅光波导集成在同一颗芯片上，过去 15 年业界只有两条工艺路线：

| 路线 | 代表玩家 | 原理 | 问题 |
| --- | --- | --- | --- |
| **Hybrid Integration（混合集成）** | Intel Silicon Photonics、Acacia/Cisco | 把单独封装的 InP 激光器贴到硅光载板旁边 | 集成密度低，对齐精度低，成本高 |
| **Heterogeneous Wafer Bonding（异质晶圆键合）** | Intel + UCSB（John Bowers 团队）、Aeluria | 把整片 III-V 晶圆键合到 SOI（绝缘体上硅）晶圆，再图案化 | III-V 材料浪费严重（90%+ 浪费），热膨胀失配，CMOS 后端兼容性差 |
| **Direct Epitaxy（直接外延）** | UCL、AIM Photonics 早期研究 | 在硅上直接生长 III-V | 缺陷密度高，量产困难 |

每条路线都有 trade-off。直到 2026 年 5 月 Ghent 大学和 imec 在 *IEEE Journal of Lightwave Technology* 发表的综述论文，把第四条工艺路线推上了规模化的舞台：**Micro-Transfer Printing（微转移印刷，简称 MTP）**。

## MTP 是什么：硅光世界的"光刻外接组装线"

MTP 不是新概念——X-Display、X-Celeprint 这几家公司从 2017 年起就用它做 Micro-LED 显示。但把它放到硅光集成里，几个核心特性正好打中行业痛点：

```text
   Source Wafer (III-V or thin-film LiNbO3)        Destination Wafer (Silicon Photonics)
   ┌─────────────────────────────────────┐        ┌─────────────────────────────────────┐
   │  ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓     │        │     □  □  □  □  □  □  □  □          │
   │  ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓     │        │  Si Photonic PIC                    │
   │  ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓     │        │     □  □  □  □  □  □  □  □          │
   │  (Lasers / Modulators / SPADs)       │        │  Waveguides + Couplers              │
   └─────────────────────────────────────┘        └─────────────────────────────────────┘
                  │                                                  ▲
                  │     ┌──────────────────┐                         │
                  └────►│ PDMS Stamp       │────────────────────────►│
                        │ (elastomer head) │  Pick + Place per chiplet
                        └──────────────────┘
                              ▲   ▼
                              │   │
                          Adhesion control
                          (geometric & surface chemistry)
```

工艺分三步：

1. **Release（释放）**：在 III-V 或 LiNbO3 源晶圆上，每个微器件（激光器/调制器）下方蚀刻一层牺牲层（sacrificial layer），让器件悬浮但仍与基底有微小连接（tether）。
2. **Pick（拾取）**：用一块 PDMS（聚二甲基硅氧烷）软质印章压上去，利用范德华力与速度依赖的粘附特性，瞬间拉断 tether 把器件提起。
3. **Place（放置）**：把印章对准目标硅光晶圆，缓慢释放——粘附力反转，器件落下并被低温键合工艺固化。

整个过程：

- **低温**（< 200°C），不破坏 CMOS 后段；
- **高吞吐**（每小时可转移 10000+ 个器件，理论上限可达 10^6/小时）；
- **高材料效率**（III-V 源晶圆只用到激光器部分，浪费 < 5%，对比键合方案的 90%+）；
- **可在 CMOS 后端集成**（先做硅光，再在最后阶段印刷激光器）。

最后一点尤其重要——它意味着 MTP 可以无缝接入现有的 CMOS Foundry 流程。

## 为什么这个时间点重要：800G/1.6T 的工艺墙

到 2026 年，数据中心光互连的主流速率已经从 400G/800G 进入 1.6T 量产。下一代 *co-packaged optics*（CPO）要求把数千个激光器、调制器集成在与 GPU/Switch ASIC 同封装的 interposer 上。

按照 LightCounting、Yole 的预测，**2026–2030 全球数据中心光互连市场规模将从 ~$15B 涨到 ~$50B**，而光引擎中"激光器+调制器+探测器"加起来占成本的 60%+。

每一代速率翻倍，要求：

| 代际 | 通道数 (per fiber) | 单通道速率 | 激光器需求量级 | 集成密度要求 |
| --- | --- | --- | --- | --- |
| 100G QSFP28 | 4 | 25G | 1× | 低 |
| 400G | 4 / 8 | 50G/100G | 4–8× | 中 |
| 800G | 8 | 100G PAM4 | 8× | 高 |
| 1.6T | 8 / 16 | 200G PAM4 | 8–16× | 很高 |
| 3.2T (2028 路线图) | 16+ | 200G+ | 16×+ | 极高 |
| **CPO (片上 / 同封装)** | 数百 → 数千 / interposer | 多通道并行 | **>1000×** | **每平方毫米十几个激光器** |

到 CPO 阶段，**没有 MTP 这类高吞吐微集成工艺，物理上做不出来**。

## 工艺成熟度：从实验室到 fab 的距离

Ghent + imec 综述论文的核心贡献，是把分散在过去 10 年的 MTP 研究工作整理成一份"工艺成熟度路线图"。关键数据点：

### 当前可用的 MTP demo（2025–2026）

- **集成 III-V 激光器到 SOI 硅光波导**——耦合效率 > 3 dB，光路对位精度 < 200 nm（imec 团队的 EPSRC 项目）
- **薄膜电光调制器（thin-film LiNbO3 / EO modulator）转移到硅光**——驱动电压 < 1V，带宽 > 100 GHz（Padova 与 Ghent 联合）
- **InGaAs SPAD（单光子探测器）转移**——暗计数率（DCR）< 1 kHz，量子效率 > 60%（CERN 高能物理项目，用于粒子探测器读出）
- **多波长 DFB 激光器阵列转移**——单片上 8 通道 WDM 阵列，已用于实验室级 1.6T 收发器

### 仍未解决的工程问题

- **良率**：单器件 MTP 转移成功率 > 99.9%，但 1000 个器件全部成功的累计良率仍在 95–98%。要做到 fab 级量产需要 > 99.99%。
- **热膨胀失配**：III-V 与硅的 TEC 差异在大尺寸晶圆上仍会引入应力，影响激光器中长期稳定性（10+ 年）。
- **供应链成熟度**：目前全球能做大规模 MTP 设备的公司只有 X-Celeprint（已被 X Development 收购）、ITX Display、imec 自建产线——产能集中。
- **可靠性认证**：通信级激光器需要通过 Telcordia GR-468 这类长期可靠性认证，MTP 转移的器件目前还在 1000–2000 小时老化测试阶段，远未达到 10⁵ 小时门槛。

按 IEEE Lightwave Tech 综述的判断，MTP 工艺会在 **2027–2028 年达到 Foundry 试产水平，2029–2030 进入主流商用 CPO 产品**。

## 谁会是赢家

### 工艺 IP 端

- **X-Celeprint / X Development**（Google 母公司 Alphabet）：MTP 工艺核心专利持有者，硅光产业出货的隐形授权方。
- **imec**（比利时）：全球硅光中立研发中心，对所有 fab 输出工艺套件，是 MTP 商业化的"瑞士银行"。
- **CEA-Leti**（法国）、**Tyndall National Institute**（爱尔兰）：欧洲第二、第三梯队，与 imec 形成竞争。

### Foundry 端

- **GlobalFoundries**：已经在 22FDX 平台上把硅光做成标准 PDK（process design kit），下一步必然集成 MTP。
- **TSMC**：硅光 PDK 落后于 GF，但 2026 年宣布 *SoIC-OE* 平台（Optical Element 同封装），需要类似 MTP 工艺。
- **Tower Semiconductor**：长期与 imec 合作。
- **中芯国际、华虹**：国内对应路线滞后 2–3 代。

### 系统玩家

- **Nvidia / Marvell / Broadcom**：CPO 路线图直接受 MTP 工艺进度影响。Nvidia 在 GB300/GB400 路线图里的"In-package Optics"对应窗口正好是 2027–2028。
- **Lightmatter / Ayar Labs**：纯光互连初创，已经在自有产品中采用类似 MTP 工艺。
- **Anello Photonics / OpenLight**：异构集成第二梯队。

### 中国玩家

- **国家信息光电子创新中心**（武汉）、**华为光产品线**、**中际旭创**：硅光集成产品出货全球前列，但工艺仍以 *hybrid* 为主，MTP 自主能力空白。
- 武汉大学、扬州大学（论文作者）在 MTP 学术研究上有参与——这是中国进入这条工艺的窗口。

## 产业含义：800G 之后，工艺成为护城河

过去 5 年硅光的竞争是"哪个 Foundry 工艺平台更成熟"，2026 年之后竞争会变成"哪家**能跟上 CPO 集成密度需求的工艺组合**"。MTP 是这个组合中最关键的一块拼图——但不是唯一的。

完整组合包括：

1. **MTP** —— 激光器、调制器异构集成。
2. **TSV（Through-Silicon Via）+ 高密度 interposer** —— 与电芯片同封装。
3. **Hybrid Bonding** —— GPU/Switch ASIC 与硅光 PIC 之间的电气连接。
4. **3D 堆叠** —— 多层硅光 PIC + 电芯片立体集成。
5. **In-package laser cooling** —— 同封装内激光器热管理。

谁能把这 5 项工艺协同到一颗 5x5cm 的 interposer 上，谁就拥有 2028–2030 数据中心光互连的工艺主权。

## 投资视角

对二级市场投资者：

- **MTP 设备供应链**是隐形赢家，关注 X Development 是否分拆 X-Celeprint 上市。
- **数据中心光模块龙头**（Coherent、Lumentum、Marvell、Innolight）需要看其 MTP 路线图进展。
- **Foundry**：GlobalFoundries 在硅光赛道的话语权比制程数字更重要。
- **欧洲资产**：imec、Aeluria、Tower 这条线相对被低估。

对一级市场：

- 任何"自建 MTP 产线"的初创公司估值容易虚高——这个工艺不是创业公司能独立从 0 做的。
- 但围绕 MTP 工艺的**辅助工艺**（PDMS 印章定制、tether 蚀刻控制、对位光学系统）有真实初创窗口。

## 一句话

如果说 EUV 是 7nm 之后逻辑芯片不可绕过的工艺，那 MTP 就是 800G 之后硅光集成不可绕过的工艺。**它不会出现在 keynote 上，也不会被消费者记住，但它会决定 2028–2030 谁能把数据中心光互连的 BOM 成本砍掉一半**。

下一次再听到"800G 光模块成本反降"、"CPO 进入量产"、"光引擎良率突破"——别只看上层产品的发布会，看看下面的工艺。微转移印刷正在悄悄重写产业基线。

## 引用来源

- IEEE Journal of Lightwave Technology — Y. Chen et al., "Micro-Transfer Printing on Silicon Photonics: Tutorial, Recent Progress and Outlook"（2026-04）：https://ieeexplore.ieee.org/document/11501716（DOI 10.1109/JLT.2026.3689409）
- SemiEngineering 综述 — "Micro-Transfer Printing (MTP) As A Promising Scalable Approach to Heterogeneous Integration for Silicon Photonics"（2026-05-15）：https://semiengineering.com/micro-transfer-printing-mtp-as-a-promising-scalable-approach-to-heterogeneous-integration-for-silicon-photonics-ghent-u-imec-et-al/
- imec — Silicon Photonics 研究平台：https://www.imec-int.com/en/expertise/cmos-advanced/silicon-photonics
- Ghent University — Photonics Research Group：https://photonics.intec.ugent.be/
- X-Celeprint MTP 技术白皮书：https://www.x-celeprint.com/technology
- Tyndall National Institute — Photonics：https://www.tyndall.ie/research/photonics-and-photonics-packaging/
- LightCounting — "Data Center Optical Interconnect Forecast 2026"：https://www.lightcounting.com/
- Yole — "Silicon Photonics & Photonic ICs Report 2026"：https://www.yolegroup.com/
- IEEE — Photonics Society publications：https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=8782770
- John Bowers Lab (UCSB) — Heterogeneous Integration：https://optoelectronics.ece.ucsb.edu/
