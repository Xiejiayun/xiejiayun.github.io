---
title: "PolitePaxos 与 SysMoBench：分布式共识的'第三波'，与 AI 写形式化模型的真实水平"
description: "Murat Demirbas 团队连续推出 PolitePaxos（让 proposer 礼貌地'问一下'就能达成共识的新变体）和 SysMoBench（评测 AI 在真实分布式系统形式化建模上的能力）。把这两件事放在一起读，是 2026 年分布式系统研究最有信息量的一个组合 —— 共识算法 25 年后再次迭代，而 AI 在'形式化系统建模'这条最严苛赛道上才刚刚及格。"
date: 2026-05-15
slug: "politepaxos-sysmobench-consensus-formal-modeling-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 分布式系统
    - 共识算法
    - Paxos
    - 形式化方法
    - TLA+
    - 学术前沿
    - 系统研究
draft: false
---

> **核心观点**：分布式共识研究在过去 25 年（Paxos 1998 → Raft 2014 → 各种变体）形成了一套相对稳定的范式。Murat Demirbas 团队 2026 年提出的 **PolitePaxos** 把一个长期被忽视的角度 —— "proposer 不强行获取多数派承诺，而是先礼貌询问" —— 重新挖出来，在某些 workload 下有可观的延迟收益。但更有意思的是同一团队的 **SysMoBench**：他们把"用 AI 帮人类做 TLA+ / 形式化建模"这件事第一次系统性地评测了。结果是：今天最强的 AI 在系统建模上只是"中等本科生水平"，但这条赛道是未来 5 年最值得跟踪的"AI 进入硬科学"指标之一。

## 一、为什么把这两件事放一起讲

我每周会读 Murat Demirbas（SUNY Buffalo 教授，分布式系统老兵）和 The Morning Paper（Adrian Colyer）。他们的内容一直是分布式领域里"非新闻"层的高价值信号。

2026 年 4-5 月，Murat 的博客出现了两个看起来无关的工作：

1. **PolitePaxos**：A New Consensus Variant Where the Proposer Just Asks Nicely
2. **SysMoBench**: Evaluating AI on Formally Modeling Complex Real-World Systems

它们看起来一个偏算法理论、一个偏 AI for science，但放在一起读，回答了同一个问题：

> 经过 60 年的"程序员手工写算法、手工证正确性"，我们能否把这件事的一半交给机器？

PolitePaxos 是"程序员手工进步"的一例。SysMoBench 给出的答案是"还不能，但已经看到苗头"。

## 二、PolitePaxos：被多数派 RPC 掩盖的 25 年的浪费

### 2.1 经典 Paxos 的"暴力问询"

Paxos / MultiPaxos / Raft 的标准范式：

1. **Prepare 阶段**：proposer 给所有 acceptor 发 prepare(n)，强制要求**多数派**承诺不再接受小于 n 的提议
2. **Accept 阶段**：proposer 把决定 v 发出去，acceptor 在不违反承诺的情况下接受
3. 任意时刻只能一个 proposer 推进

这个范式的一个隐含特征：**proposer 永远是"强制性"的**。它不问 acceptor 现在状态如何，它直接发起"我要锁定 n"。哪怕集群处于完全无竞争状态，prepare 也会照发不误。

在数据中心内网（亚毫秒级延迟）这个开销不大。但在**跨可用区、跨大洲、IoT/边缘**场景里，每次 prepare 都付一个 RTT 是浪费。

### 2.2 PolitePaxos 的核心 idea

Murat 团队的思路（同时致敬 EPaxos、Generalized Paxos 这条线）：

1. proposer 先发一个**轻量级 hint**："我想提议某个值 v，acceptor 你们当前最大承诺号是多少？"
2. 多数派回复后，proposer 计算最优 n（不一定要比所有看到的承诺号都大）
3. 用这个 n 直接进入 accept 阶段，**跳过显式 prepare**
4. 如果运气不好遇到竞争，回退到经典 Paxos 路径

形式化论证（在博客里只给出 sketch，正式论文应在 SOSP/OSDI 2026 投稿）显示：

- 在**无竞争场景**下，延迟从 2 RTT 降到 1.5 RTT
- **safety property** 与经典 Paxos 等价
- **liveness** 在恶意 proposer 持续抢占场景下退化（已知问题，可用 leader lease 缓解）

### 2.3 它在 Paxos 家谱里的位置

我画一张 25 年的"共识算法家谱"：

```
1998  Paxos (Lamport)
  ├─ 2007  Multi-Paxos
  ├─ 2010  Generalized Paxos (放宽冲突定义)
  ├─ 2013  EPaxos (无 leader，commutativity)
  ├─ 2014  Raft (易理解性导向)
  ├─ 2018  Compartmentalized Paxos
  ├─ 2020  Flexible Paxos / Heidi Howard
  ├─ 2022  Skinny / SkyPaxos (跨区域)
  └─ 2026  PolitePaxos (1 RTT 无竞争路径)
```

PolitePaxos 不是革命性的，是**优化层的一次重要补完**。它和 Flexible Paxos（Heidi Howard 2020）的精神接近 —— 都是"经典 Paxos 的约束其实可以更松"。

### 2.4 工程影响：etcd、TiKV、CockroachDB 会用吗？

短期不会。理由：

1. etcd、TiKV 用的是 Raft，重写到 PolitePaxos 是一个**风险极高、收益边际**的工程
2. 真正会先采用的是**新建系统**：FoundationDB 后继、新一代 metadata service、跨大洲 KV
3. 大概率会作为论文级 idea 沉淀 2-3 年，然后被某个工业系统（YugabyteDB、Spanner 类新对手）整合

但 PolitePaxos 的"礼貌询问"思路本身可以马上用：**你今天的 Raft 实现里，leader 重新选举后的 NoOp 强 commit 是不是可以替换成轻量级查询**？很多 Raft 实现里都有可优化空间。

## 三、SysMoBench：AI 形式化建模的真实水平

### 3.1 这个 benchmark 在测什么

形式化建模（TLA+ / Alloy / Lean4 / Coq）是分布式系统里"金标准"的正确性论证方式。但它出名的痛点是：

- 学习曲线陡（TLA+ 公认要 6-12 个月才能熟练）
- 模型规模 vs 状态爆炸的权衡需要经验
- 真实系统的"建模"本身就是创造性工作

SysMoBench 不测"AI 能否写 if-else"，它测**"给定一个真实分布式系统的英文规约 + 关键代码 + bug 报告，AI 能否产出可用的 TLA+ 规约并发现已知 bug"**。

任务类别：

| 任务 | 描述 | 难度 |
|------|------|------|
| Model translation | 给定伪代码，产出 TLA+ 模块 | 中 |
| Invariant identification | 给定系统描述，列出关键不变式 | 高 |
| Trace replay | 给定一段执行 trace，写出能复现的 spec | 高 |
| Bug localization | 已知 bug 报告，定位 spec 哪一行不变式违反 | 极高 |
| Refinement proof | 证明 spec_A refines spec_B | 极高 |

### 3.2 结果（粗剪报告）

Murat 团队测试了若干主流大模型在 SysMoBench 上的表现。具体分数在论文里，但博客透露的相对排名是：

- **顶级前沿模型**（推理增强配置）：约 40-60% 任务通过率
- **小模型 / 上一代**：< 20%
- **专门微调过形式化方法的开源模型**：约 30%
- **人类基线**（经验 1 年 TLA+ 使用者）：约 80%
- **人类基线**（专家 5 年+）：> 95%

读懂这组数字的要点：

1. AI 在"低阶任务"（model translation）已经达到了**辅助开发**门槛
2. 在"高阶任务"（invariant identification、refinement proof）还差**专家一个数量级**
3. 整个 benchmark 公开 + 持续追踪 —— 这是未来 3-5 年最重要的"AI 真实能力曲线"之一

### 3.3 为什么这件事比 SWE-Bench / MMLU 更重要

SWE-Bench 测 AI 能否修 GitHub issue —— 是"模仿现有代码"的任务，本质上是模式匹配。
MMLU 测 AI 在百科知识 + 推理 —— 是"信息整合"。

SysMoBench 测的是**创造性的形式化抽象能力** —— 给定一个 messy 的工程系统，提炼出可证明的数学结构。这是分布式系统、形式化方法、定理证明、密码学 —— 一整批"硬科学"的核心技能。

如果未来 3 年，前沿模型在 SysMoBench 上从 50% 推到 85%，意味着：

- 分布式系统的设计阶段，AI 可以做"合作建模"
- 安全协议的形式化证明可以半自动化
- 编译器后端的正确性论证可以辅助化
- 学术界 PhD 训练的"形式化方法"课程内容需要重新设计

如果停在 50-60% 上不去 —— 说明前沿 LLM 缺的不是数据，是**真正的抽象推理能力**。这对整个"AI 替代专业工作"叙事是重大反证。

### 3.4 Hillel Wayne 的旁注："LLMs are bad at vibing specifications"

形式化方法领域另一位重量级人物 Hillel Wayne 在 2026 年发了一篇博客：[LLMs are bad at vibing specifications](https://www.hillelwayne.com/)。他的观察补充了 SysMoBench 的结论：

> 让 LLM 写 spec 不是难在语法，难在**它不知道一个 spec 写出来要"用来做什么"**。

这是一个值得反复读的判断。SysMoBench 给的是定量指标，Hillel 给的是定性诊断：LLM 缺的不是 TLA+ 关键字，是**对 spec 这一表征形式的"使用意图"**。

## 四、为什么把这两件事一起写

如果你已经读到这里，应该能理解我的论点：

1. **PolitePaxos** 代表"人类专家在 25 年成熟领域里还能再挖出有价值的新东西"
2. **SysMoBench** 代表"AI 在这种深度专业领域还不足以独立工作，但已经能辅助"
3. 这两件事**同时发生在同一个研究组**，不是巧合 —— 这是分布式系统研究范式可能的下一个阶段：**人类做创意性的算法 + AI 做大量形式化验证工作**

类比一下：象棋在 1997 年深蓝击败卡斯帕罗夫后，进入了"人机合作（centaur）"阶段，最强的实体是"人 + AI"。然后 2017 年 AlphaZero 让 AI 完全超越人 + AI 组合。

分布式系统这一类**严肃的硬科学**，今天我们大概率还在"人类创新 + AI 辅助验证"阶段。下一个十年里，谁能率先实现 centaur workflow，谁就拥有结构性领先。

## 五、可执行的建议

### 5.1 给系统工程师

- 关注 PolitePaxos 的正式论文出版（预计 OSDI 2026 / NSDI 2027）
- 重新审视你的 Raft 实现里有没有可以"礼貌化"的环节
- 学一点基础 TLA+（一周入门成本极低，工业收益高）

### 5.2 给 AI 研究者

- SysMoBench 是除了 SWE-Bench 之外，最值得加入"模型能力 dashboard"的 benchmark
- 如果你的模型在通用 reasoning 上比 baseline 高，请同时在 SysMoBench 上跑一下 —— 这才是抽象推理的真考场
- 别再用 MMLU 类指标说服自己模型有了"专业能力"

### 5.3 给企业 CTO

- 如果你在做分布式 KV / 数据库 / 跨区域服务，**未来 3 年的人才招聘里加上"TLA+ 能力"这一项**
- AI 辅助形式化的工具链（Quint、PlusCal + Copilot、Lean 4 + 模型）会在 2026-2027 年成熟到可用，可以小规模试点
- 不要押注"AI 会很快替代分布式工程师"—— SysMoBench 的数字给了清晰的天花板

## 六、结语

分布式系统研究今天最让我兴奋的地方，不是又出了多少个新一致性级别，也不是哪个数据库又把延迟压低了 3 毫秒。是**它开始系统地、定量地问：人类专家在做什么，AI 能做哪一部分，剩下的部分还要多久**。

PolitePaxos 是"人类还在做的事"。SysMoBench 是"AI 还做不到的事"。这一加一减，是这个领域 2026 年最诚实的画像。

读这一类内容的回报率，远高于读"某模型发布"。前者关心 5 年的事，后者关心 5 天的事。

## 参考来源

1. Murat Demirbas — [PolitePaxos: A New Consensus Variant Where the Proposer Just Asks Nicely](https://muratbuffalo.blogspot.com/)
2. Murat Demirbas — [SysMoBench: Evaluating AI on Formally Modeling Complex Real-World Systems](https://muratbuffalo.blogspot.com/)
3. Murat Demirbas — [The Two Abstractions of System Design: Hide or Reduce](https://muratbuffalo.blogspot.com/)
4. Murat Demirbas — TLA+ mental models
5. Hillel Wayne — LLMs are bad at vibing specifications
6. Hillel Wayne — People get confused when language implementations break language guarantees
7. Leslie Lamport — Paxos Made Simple (1998)
8. Heidi Howard — Flexible Paxos (PaPoC 2016 / 2020 updates)
9. Iulian Moraru, David Andersen, Michael Kaminsky — There Is More Consensus in Egalitarian Parliaments (EPaxos, SOSP 2013)
10. The Morning Paper — Virtual consensus in Delos / Seeing is believing 等历史回顾
