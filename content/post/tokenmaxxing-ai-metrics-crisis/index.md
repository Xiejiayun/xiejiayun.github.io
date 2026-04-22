---
title: "Tokenmaxxing：当AI使用量成为KPI，硅谷正在系统性地烧钱"
description: "Meta、Microsoft、Salesforce的工程师正在刻意消耗AI Token来冲击KPI——这不是个案，而是一场关于AI价值度量的系统性危机"
date: 2026-04-22
slug: "tokenmaxxing-ai-metrics-crisis"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - AI治理
    - 企业管理
    - Token经济
    - 效能度量
draft: false
---

## 一个荒诞的新词：Tokenmaxxing

2026年4月，The Pragmatic Engineer揭露了硅谷的一个公开秘密：在Meta、Microsoft、Salesforce等科技巨头中，工程师们正在进行一种被称为**Tokenmaxxing**的行为——**故意大量消耗AI Token来满足公司的AI使用率KPI**。

具体操作包括：
- 用AI重复生成已经知道答案的代码
- 将一行shell命令就能完成的任务提交给AI处理
- 编写自动化脚本定时向AI发送查询
- 在AI生成的代码上再让AI"优化"一遍

这不是几个懒惰员工的小把戏。这是一场**有组织的、系统性的指标游戏**。当管理层将"AI工具使用率"列为绩效考核指标时，工程师的理性反应就是最大化这个指标——无论实际价值如何。

## 古德哈特定律的AI版本

经济学家查尔斯·古德哈特在1975年提出了一个简洁的观察：**"当一个度量指标成为目标时，它就不再是好的度量指标。"**

Tokenmaxxing是古德哈特定律在AI时代的教科书级案例。但它的破坏力比传统的指标博弈更大，原因有三：

**1. 成本乘数效应**
传统的"刷指标"行为（如代码行数注水）主要浪费人力时间。但Tokenmaxxing直接消耗计算资源——每一个无意义的Token都对应着真实的GPU算力、电力和碳排放。以Claude Opus 4.7的定价为例，一个工程师如果每天消耗100万Token用于Tokenmaxxing，年成本约为$3000-5000。乘以一个万人工程团队中20%的参与率，仅这一项的年浪费就在**$600万-$1000万**。

**2. 噪声污染**
企业用AI使用数据来指导基础设施投资决策。当30%的Token消耗是人为膨胀时，这些数据驱动的决策本身就建立在虚假的基础上。公司可能会基于膨胀的使用量采购更多GPU、签订更大的模型API合约——形成一个**虚假需求的正反馈循环**。

**3. 文化腐蚀**
当"看起来在用AI"比"用AI创造价值"更重要时，整个工程文化都会被腐蚀。这会驱逐那些真正在思考如何有效利用AI的工程师，留下那些善于表演的人。

## 不只是硅谷的问题：AI ROI的全球性困境

Tokenmaxxing只是冰山一角。更深层的问题是：**整个行业都缺乏衡量AI实际价值产出的可靠框架。**

MIT Technology Review近期的报道指出，企业AI应用正在快速从实验走向日常运营——到2025年底，一半的公司在至少三个业务功能中使用AI。但同时，绝大多数企业无法量化AI的实际投资回报率。

当前企业衡量AI价值的常见指标，以及它们各自的致命缺陷：

| 常见指标 | 表面合理性 | 致命缺陷 |
|---------|-----------|---------|
| Token消耗量 | 使用量=价值？ | Tokenmaxxing证明这完全不可靠 |
| AI辅助代码比例 | AI写了多少代码 | 不衡量代码质量和维护成本 |
| 工程师自报效率提升 | 用户满意度 | 自我报告偏差极大，且受KPI影响 |
| 工单处理速度 | 产出效率 | 不衡量解决质量和客户满意度 |
| AI功能采纳率 | 渗透率 | 不区分主动使用和被迫使用 |

## NVIDIA的"Token工厂"叙事：繁荣还是泡沫？

有趣的是，Tokenmaxxing现象与NVIDIA推动的"Token工厂"叙事形成了一种矛盾的张力。

NVIDIA将数据中心重新定义为"Token工厂"，核心指标从计算能力转向**每Token成本**。这个叙事的前提是：Token产出=智能产出=商业价值。但如果相当比例的Token消耗是无效的——是Tokenmaxxing、是重复查询、是低效的Prompt设计——那么"Token工厂"的经济学模型就需要打一个大大的折扣。

这不是说NVIDIA的方向错了——AI推理确实在成为数据中心的主要工作负载。但当我们将AI基础设施的投资决策建立在Token消耗量上时，需要认真区分**有效Token**和**无效Token**。

Stratechery的Ben Thompson在分析Mythos和计算成本时指出了一个关键洞察：**AI能力的提升带来了计算的机会成本问题。** 同样的GPU算力，用于运行Mythos发现安全漏洞，还是用于处理Tokenmaxxing产生的垃圾查询？这两者的单位价值差异可能是1000倍。

## Claude Opus 4.7与模型价值悖论

Latent Space报道Claude Opus 4.7发布时用了一个精确的描述："literally one step better than 4.6 in every dimension"（在每个维度上都比4.6好一步）。

这引出了一个价值悖论：**当模型能力持续提升，但企业无法准确度量AI的产出价值时，模型的商业价值如何定价？**

当前的定价模式——按输入/输出Token计费——本质上是在卖"原材料"。就像卖面粉的人不关心客户是用面粉做了面包还是把它倒进垃圾桶一样，模型提供商对Token的有效利用率是漠不关心的。

但这种商业模式的长期可持续性令人怀疑。当企业开始认真审视AI的ROI时（我预计这将在2026年Q3财报季开始），按Token计费的模式将面临压力——企业会要求**按成果计费（outcome-based pricing）**。

## 破局之道：从度量Token到度量Impact

解决Tokenmaxxing和AI ROI困境的关键，在于度量框架的根本转变：

**1. 引入"有效Token率"指标**
类似于网络广告行业的"有效展示"概念，企业需要区分导致实际行动（代码合并、工单关闭、决策制定）的Token和纯粹的消耗。

**2. A/B测试AI的因果效应**
不是比较"使用AI"vs"不使用AI"的工程师（这有自选择偏差），而是在相似任务上随机分配AI辅助和非AI辅助的工作流程，度量实际产出差异。

**3. 从使用量KPI转向价值KPI**
不要衡量"你用了多少AI"，而是衡量"AI帮你多快/多好地完成了任务"。但这需要更精细的度量基础设施。

**4. 匿名使用模式分析**
通过分析Token消耗的时间模式、查询复杂度分布、结果采纳率等数据，自动识别Tokenmaxxing行为——不是为了惩罚，而是为了校准数据。

## 我的判断

**1. 2026年Q3将是AI ROI的清算时刻。** 上半年的疯狂投入将在下半年面临财务审视。那些无法证明AI投入回报的项目将被砍掉或缩减。

**2. Tokenmaxxing将促使行业建立新的AI效能度量标准。** 就像Enron的会计造假最终催生了SOX法案一样，Tokenmaxxing的荒诞将催生AI效能的行业标准。

**3. 按成果计费将在2027年成为企业AI的主流商业模式。** 先行者已经在尝试——按成功的代码review收费、按关闭的安全漏洞收费、按完成的数据分析收费。

**4. AI使用率将从KPI中消失。** 没有人会把"电脑使用率"作为KPI——AI终将达到同样的普及程度，届时衡量使用率将毫无意义。

Tokenmaxxing看似荒诞，但它揭示的是一个严肃的行业问题：**在AI能力指数级增长的同时，我们衡量其价值的能力几乎没有进步。** 解决这个问题，可能比训练下一个更大的模型更重要。

---

### 参考来源

1. [The Pragmatic Engineer - Tokenmaxxing as a weird new trend](https://newsletter.pragmaticengineer.com/p/the-pulse-tokenmaxxing-as-a-weird)
2. [NVIDIA Blog - Rethinking AI TCO: Why Cost per Token Is the Only Metric That Matters](https://blogs.nvidia.com/blog/lowest-token-cost-ai-factories/)
3. [Stratechery - Mythos, Muse, and the Opportunity Cost of Compute](https://stratechery.com/2026/mythos-muse-and-the-opportunity-cost-of-compute/)
4. [Latent Space - Claude Opus 4.7 launch](https://www.latent.space/p/ainews-anthropic-claude-opus-47-literally)
5. [MIT Technology Review - AI needs a strong data fabric to deliver business value](https://www.technologyreview.com/2026/04/22/1135295/ai-needs-a-strong-data-fabric-to-deliver-business-value/)
6. [Cloudflare Blog - The AI engineering stack we built internally](https://blog.cloudflare.com/ai-engineering-stack)
