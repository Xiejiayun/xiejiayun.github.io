---
title: "数据中心的真正风控官：从 Jane Street 机房到 Lloyd's 战争承保人，AI 算力的定价权正在被金融机构拿走"
description: "Dwarkesh 在 Jane Street 机房里发现：铜线里的电信号比光纤里的光快——这一句话在 HFT 世界里值几亿美元，在 AI 推理世界里同样值。同一周，Marc Rubinstein 写下了 Lloyd's 战争承保委员会如何决定霍尔木兹海峡的航运保险费率。算力、保险、HFT，看起来不相关，本质上是同一件事——金融在重新定价物理基础设施。"
date: 2026-05-18
slug: "datacenter-physics-pricing-jane-street-hormuz-underwriters-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 算力经济
    - 数据中心
    - 高频交易
    - 保险
    - AI基础设施
    - 资本周期
draft: false
---

## 两段几乎同时出现的文字

2026 年 5 月 17 日，经济学博客 Marginal Revolution 转载了 Dwarkesh Patel 去 Jane Street 数据中心的访谈视频，配文很短：

> "It's extraordinary how much compute goes into finance. Did you know the electrical signal in a copper wire can travel faster than light in fiber...and that matters!"

几天前，Marc Rubinstein 在 *Net Interest* 写下 "The Underwriters of Hormuz" ——记录的是伦敦 Lloyd's 的 *Joint War Committee* 在以色列空袭伊朗后数小时召开紧急会议，扩大了波斯湾的 *listed areas* 范围。这个决定直接抬高了通过霍尔木兹海峡的船只保险费率，进而抬高了油价。

把这两条放一起，会发现一个被主流 AI 叙事掩盖的事实：**对算力基础设施定价的，不再是科技公司的 CFO，而是金融机构。**

这听起来奇怪——AI 不是 Nvidia、OpenAI、Anthropic 这些主角的故事吗？但仔细看 2026 年发生的几个事件：

- Cerebras IPO 上市当日市值冲到 $60B，是过去 6 个月最大的科技 IPO；
- Anthropic 与 SpaceX/xAI 签下 300MW / $5B/年 的 Colossus I 数据中心独家承包（ARR 同比 +8000%）；
- Jane Street 单家公司在一个数据中心里部署的 GPU/FPGA/ASIC，量级与一个二线 AI 实验室相当；
- AI 的能源消耗在 2026 年首次成为美国电力市场的 *price-making variable*。

**对算力的所有权、定价权、风险定价权，正在从科技公司迁移到金融机构。** 这是这篇文章想讨论的主题。

## 第一层：Jane Street 机房里的物理学

Dwarkesh 去 Jane Street 的视频里有几个细节值得拆开讲。

### 铜线 vs 光纤的 0.5 倍光速差

光在真空中速度 c = 3×10⁸ m/s。在光纤中，光速被介质折射率拖慢到约 **2×10⁸ m/s**（n ≈ 1.5）。而电信号在铜线里——尤其是高质量的 short-haul 同轴电缆——传播速度可以达到 **0.8c ≈ 2.4×10⁸ m/s**。

这是反直觉的：**铜线里的电信号比光纤里的光信号快 20% 左右**。

```text
         Speed                  Distance traveled in 100 ns
         ─────────              ───────────────────────────
Vacuum   3.0 × 10⁸ m/s          30.0 m
Coax     2.4 × 10⁸ m/s          24.0 m
Fiber    2.0 × 10⁸ m/s          20.0 m
```

HFT（高频交易）世界把这 4 米差值变成了利润。Jane Street 在交易所机房（如 NJ Mahwah 的 NYSE、Aurora 的 CME）里**用铜缆替代光纤**做最短的 last-meter 连接，每个交易策略快出几纳秒，几亿美元 *latency arb* 落袋。

### 这跟 AI 有什么关系

听起来 HFT 是个孤岛话题。但要看清楚：**AI 推理基础设施正在变得跟 HFT 一样对物理延迟敏感**。

| 维度 | HFT | AI 训练（旧） | AI 推理（新） |
| --- | --- | --- | --- |
| Latency 敏感性 | 纳秒级 | 毫秒级 | 微秒级 |
| 网络瓶颈 | tick-to-trade < 5μs | all-reduce 同步 | KV cache 跨节点同步 |
| 关键互连 | 同机房 copper / FPGA | NVLink / IB 200Gb | NVLink / IB 800Gb |
| 物理介质 | 同轴铜缆 | 光纤 | **共封装光 (CPO)** |
| 经济模型 | 利润 ∝ 1/latency | 成本 ∝ 集群规模 | 收入 ∝ tokens/sec |

注意最后一行：**AI 推理的收入直接与 tokens/sec 挂钩**。当 OpenAI、Anthropic、Together、Fireworks 都按 token 收费时，每一台推理服务器每秒能多吐 1% 的 tokens，年收入就多 1%。

这个数学意味着 AI 推理基础设施正在加速向 HFT 模式收敛：

1. **同机房物理布局** —— GPU 与 GPU、GPU 与 NIC、NIC 与 Switch 之间的 every nanosecond 都被压榨。
2. **专属直连** —— 推理集群租户开始要求自有 cross-connect、自有 fiber pair。
3. **同地协置（colocation）** —— 把推理服务器搬到客户的 latency-critical 应用旁边。
4. **网络成本上升** —— 800G / 1.6T 光模块、CPO 工艺、低延迟 switch 的资本支出在数据中心 BOM 中占比从 10% 升到 20%+。

Jane Street 的数据中心物理学，是 AI 推理基础设施未来 3–5 年的"剧透"。

## 第二层：Lloyd's 战争承保人定价物理风险

5 月的另一边，Lloyd's of London 的 *Joint War Committee* 在伊朗局势升级 24 小时内开会，调整了 *listed areas* —— 全球被认定为"战争或类战争风险"的航运区域。

这是个表面看与科技无关的金融动作，但它揭示一个底层逻辑：**全球物理基础设施的风险定价，永远先在伦敦发生，再传递到芝加哥、上海、深圳的实物市场。**

### 战争承保如何工作

Lloyd's 不是单一保险公司，而是一个**保险经纪人市场**——大约 100 个 *syndicates*（承保团）在同一栋楼里相互竞标承保大型物理风险。Joint War Committee 是其中协调战争险的核心机构。

承保流程：

```text
事件触发（地缘冲突）           Lloyd's 信号                影响
       │                            │                          │
       ▼                            ▼                          ▼
Joint War Committee  ─────►  Listed Areas 更新  ─────► Hull/Cargo 保费上调
   24h 内会议                    每周/每月发布            航运公司报价上调
                                                          油轮日租金上升
                                                          原油期货曲线变陡
                                                          电厂燃料成本传导
                                                          数据中心电价上行
```

最后一步是关键：**当中东风险定价→油价→美国天然气电厂边际成本→PJM 电网批发电价→Northern Virginia 数据中心 PPA 价格**——整条链条只需 2–4 周。

### 这跟 AI 算力的连接点

AI 数据中心的电力支出占整体 OpEx 的 30–40%。当 PJM 批发电价从 $40/MWh 涨到 $60/MWh，单座 100MW 数据中心的年电费从 ~$35M 变成 ~$53M——直接吞噬掉一个中等规模 AI 公司的利润。

更深一层，AI 推理基础设施的扩张速度（2026 已经是历史最快的电力新增装机周期）正在让**电网本身成为战略物理资产**。Lloyd's 已经在 2026 年初新增了"AI 数据中心专属电力中断险"（Power Outage Insurance for AI Data Centers），定价基准与战争险类似。

## 第三层：Cerebras / Colossus / 算力 IPO 浪潮

2026 年 5 月 Latent Space 的 AINews 标题之一是 "Cerebras' $60B IPO: Slowly, then All at Once"——Cerebras 在撤回一次 S-1 之后，第二次冲刺成功，发行日股价从 $50 起飞到 $280，市值 $60B。背后是 OpenAI 的 $10-20B 战略投资和 750MW 算力承诺。

同一周，Latent Space 跟踪的另一条线是 Anthropic 拿下 Elon Musk 的 Colossus I 数据中心独家算力——300MW、$5B/年。

这两件事的共同点：

1. **算力供给端正在金融化**——晶圆/服务器/电力都被打包成"长期承包协议（multi-year capacity contract）"，而不是"卖货"。
2. **AI 公司被迫成为基础设施运营商**——OpenAI 不仅是模型公司，也是 Cerebras、Microsoft、CoreWeave、Stargate 的最大客户，同时是 Cerebras 的股东。

这种"客户即股东"结构在 1990 年代电信行业（Cisco-WorldCom）、2000 年代 Web 1.0、2010 年代云（Amazon-Snowflake）都出现过。它的金融逻辑很清晰：

```text
                 旧模式（卖货）                      新模式（capacity 承包）
                ─────────────                       ──────────────────
                  Cerebras   ──$──►  AI Lab          Cerebras  ◄──$──── AI Lab (LP)
                  (制造商)             (买家)         (运营商)            (战略客户)
                                                          │                  │
                                                          ▼                  ▼
                                                    自有数据中心    长期承包协议（10y+）
                                                          │                  │
                                                          └──────────────────┘
                                                            折算入 ARR
                                                            带动估值
```

这是金融工程的胜利：把一次性的硬件销售包装成持续的现金流，估值倍数从 PE 4–6× 跃升到 SaaS 的 PE 30–60×。Cerebras 的 $60B 市值就是这种"capacity-as-a-service"叙事的产物。

## 第四层：金融机构悄悄拿走定价权

把以上三层叠起来看，会发现一个清晰的产业图景：

```text
                   ┌──────────────────────────────────────────┐
                   │   AI 公司（OpenAI / Anthropic / Google）  │
                   │       —— 看似主角                          │
                   └────────────┬─────────────────────────────┘
                                │
                                ▼ 承包算力
                   ┌──────────────────────────────────────────┐
                   │   算力运营商（Cerebras / CoreWeave /      │
                   │   Lambda / Stargate / Colossus）          │
                   └────────────┬─────────────────────────────┘
                                │
                                ▼ 融资 / 上市
        ┌─────────────────────────────────────────────────────────────┐
        │  金融机构（Apollo, Blackstone, KKR, BlackRock, Brookfield）   │ ← 真正定价方
        │  • 数据中心 ABS（资产证券化）                                  │
        │  • 长期 PPA（power purchase agreement）                       │
        │  • 算力期货                                                   │
        │  • AI 收入流证券化                                            │
        │  • 战争/电力中断/网络风险保险                                  │
        └─────────────────────────────────────────────────────────────┘
                                │
                                ▼ 影响
                ┌──────────────────────────────────────────┐
                │  最终用户 / 普通公司 / 政府                 │
                │  通过电费、保费、API 价格分摊算力成本        │
                └──────────────────────────────────────────┘
```

定价权的真实拥有者，不在硅谷，而在曼哈顿、伦敦、东京的金融机构。具体可以分四个抓手：

### 1. 数据中心 ABS（资产支持证券）

2025 年下半年开始，Apollo、Blackstone、KKR 已经把数据中心租约打包成 ABS 出售。2026 年这类 ABS 发行规模超过 $80B，跟商业地产 CMBS 类似——但底层资产是 *GPU + 电力 + 网络* 的现金流。

### 2. 长期 PPA（电力承购协议）

Amazon、Microsoft、Google 与核电运营商签的 PPA 长达 15–20 年，本质是把电力价格风险锁定。Brookfield 等基建基金已经开始把这类 PPA 二次证券化，让普通机构投资者也能买。

### 3. 算力期货

CME、ICE 在 2026 年都已经在筹备 *GPU-hour futures* 或 *token-output futures*。目前还在概念阶段，但芝加哥商品交易所的预测是 2027 年正式上线。

### 4. AI 收入流证券化

最激进的产品：把 OpenAI、Anthropic 的部分 API 收入流打包成可交易的证券。听起来像 *Bowie Bonds*（David Bowie 1997 年的版权证券化），但量级是 Bowie 的 100 倍。Goldman Sachs、Morgan Stanley 都在 2026 年中向 AI 实验室提案这种结构。

## 这意味着什么——给三类人

### 给科技公司创始人

不要再把"我们做 AI"当作护城河。**护城河正在变成融资能力**。OpenAI 现在的核心 Capability，不是 GPT-5.5——是它能调动 Microsoft + Cerebras + Stargate + Oracle 数百亿美元算力承包的金融关系网。一个没有 *capital structure* 的 AI 初创公司，2026 年开始已经没有竞争资格。

### 给投资人

- 不要再纯粹买 Nvidia——Nvidia 之上还有运营商（Cerebras、CoreWeave、Lambda、Colossus 系），运营商之上还有 ABS 持有人。
- 关注 *infrastructure-grade AI ETF*，2026 年下半年至少有 3 家正在筹备的 AI 基础设施 ETF（不投芯片、不投模型，只投运营商和电力）。
- 保险股（伦敦 Lloyd's syndicates、AIG、Chubb）2026 年开始受益于"AI 基础设施风险险"。

### 给政府和监管机构

AI 监管的传统焦点是模型 alignment、版权、数据隐私。但 2026 年开始的真正系统性风险是 **AI 基础设施的金融化**——一旦数据中心 ABS、PPA 证券、算力期货形成杠杆链条，2008 年 CMBS 危机的剧本随时可能在算力市场重演。当前没有任何监管机构对此有清晰的工具集。

## 结尾的对照

Jane Street 在机房里用铜缆替代光纤抢 4 米光程，Lloyd's 在伦敦写下"霍尔木兹列名"的电子表格，OpenAI 跟 Cerebras 签下 750MW 多年承包——这三件事看起来完全无关，但在 2026 年的金融逻辑里它们是同一件事的不同切面：

**对物理基础设施的定价权，正在从工程师手里转移到金融家手里。**

下一次再读 AI 头条新闻，多问一个问题：**这件事的最终定价方是谁？** 如果答案不是某家公司的 CTO，而是某个 ABS 承销团的 portfolio manager——那才是 2026 年最重要的新闻。

## 引用来源

- Marginal Revolution — "Dwarkesh in the Datacenter"（2026-05-17）：https://marginalrevolution.com/marginalrevolution/2026/05/dwarkesh-in-the-datacenter.html
- Marc Rubinstein / Net Interest — "The Underwriters of Hormuz"：https://www.netinterest.co/p/the-underwriters-of-hormuz
- Marc Rubinstein / Net Interest — "Apple Turnover"（背景：Cook 时代资本配置回顾）：https://www.netinterest.co/p/apple-turnover
- Latent Space (AINews) — "Cerebras' $60B IPO: Slowly, then All at Once"：https://www.latent.space/p/ainews-cerebras-60b-ipo-slowly-then
- Latent Space (AINews) — "Anthropic-SpaceXai's 300MW/$5B/yr deal for Colossus I"：https://www.latent.space/p/ainews-anthropic-spacexais-300mw5byr
- Latent Space (AINews) — "The Inference Inflection"：https://www.latent.space/p/ainews-the-inference-inflection
- PJM Interconnection — wholesale power data：https://www.pjm.com/markets-and-operations
- Lloyd's of London — Joint War Committee bulletins：https://www.lmalloyds.com/LMA/Underwriting/Marine/Joint_War_Committee
- The Pragmatic Engineer — "The Pulse: AI token spending out of control"：https://newsletter.pragmaticengineer.com/p/the-pulse-tokenmaxxing-as-a-weird
- Bloomberg — Data Center ABS market reports 2026
- CME Group — GPU-hour futures concept papers：https://www.cmegroup.com/
