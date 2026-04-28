---
title: "AlphaGo之父的11亿美元豪赌：AI不再需要人类数据？"
description: "David Silver创立Ineffable Intelligence并融资11亿美元，要打造不依赖人类数据的'超级学习者'。这位AlphaGo缔造者认为当前AI走错了路——自我博弈才是通往超级智能的正途。"
date: 2026-04-28
slug: "david-silver-ineffable-intelligence"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - David Silver
    - 强化学习
    - 自我博弈
    - AI投资
draft: false
---

## 当AlphaGo之父说"AI走错了路"

2026年4月底，一条融资新闻在AI圈引发了比任何模型发布都要热烈的讨论：**David Silver创立的Ineffable Intelligence以51亿美元估值完成了11亿美元融资。** 这家公司成立仅几个月。

11亿美元给一家几个月大的公司——这在任何时代都算疯狂。但当你了解David Silver是谁、他要做什么、以及为什么他认为当前整个AI行业都走错了方向之后，你可能会改变看法。

## David Silver：一个需要被理解的人

### 不可复制的履历

David Silver不是一个普通的AI研究员。他是：

- **AlphaGo的核心创造者**（2016年）——让AI第一次在围棋领域击败人类世界冠军
- **AlphaZero的设计者**（2017年）——一个从零开始、不需要任何人类棋谱就能在围棋、国际象棋和日本将棋中达到超人水平的系统
- **强化学习领域的奠基人之一**——他在UCL的强化学习课程是该领域最受欢迎的入门资源
- **DeepMind的核心科学家**——在Google DeepMind工作超过10年

关键是AlphaZero。这个系统在没有任何人类知识的情况下，仅通过自我对弈（self-play），在24小时内就超越了所有人类围棋知识的积累。这不是渐进式改进——**这是一种全新的学习范式的证明。**

### 为什么他离开DeepMind

Wired的深度报道标题已经说明了一切：*"The Man Behind AlphaGo Thinks AI Is Taking the Wrong Path"*（AlphaGo背后的人认为AI走上了错误的道路）。

Silver的核心论点可以归结为一句话：**当前的LLM范式本质上是在压缩和复述人类已有的知识，而不是在发现新知识。**

GPT-5.5再聪明，它的知识边界也不会超过人类互联网上已有内容的范围。它可以更好地组合、推理、总结人类知识，但它不会独立发现新的数学定理或物理定律。

AlphaZero则不同。它在围棋领域发现了人类3000年来从未想到的策略——不是因为它"学了更多人类棋谱"，而是因为它完全绕过了人类知识，从第一性原理出发探索。

## 哲学分裂：两条通往超级智能的路

当前AI领域存在一个根本性的方法论分歧，可以类比为物理学中的"弦论vs圈量子引力"——两个阵营都有顶尖人才，都有部分实验验证，但方向截然不同。

### 路线一：数据驱动（当前主流）

代表公司：OpenAI、Anthropic、Google DeepMind（LLM部门）、DeepSeek

核心假设：**足够多的人类数据 + 足够大的模型 + RLHF对齐 = 通用智能**

成就：GPT-5.5、Claude Opus 4.7、DeepSeek V4等

挑战：
- 高质量人类数据正在枯竭（互联网数据是有限的）
- 合成数据存在"模型坍缩"风险
- 本质上受限于人类知识的边界
- RLHF中的奖励黑客问题（Reward Hacking）日益严重

### 路线二：自我博弈/自我发现（Silver的路线）

代表：Ineffable Intelligence、AlphaZero遗产

核心假设：**正确的学习算法 + 足够的计算 + 自我博弈 = 超越人类知识边界的智能**

成就：AlphaGo/AlphaZero（围棋）、AlphaFold（蛋白质结构预测）

挑战：
- 目前只在有明确规则/奖励函数的领域验证过
- 如何扩展到开放世界的通用任务？
- "奖励函数设计"本身可能成为新的瓶颈

| 维度 | 数据驱动路线 | 自我博弈路线 |
|------|-------------|-------------|
| 知识来源 | 人类生成的数据 | 自我探索和发现 |
| 知识上限 | 人类已有知识的边界 | 理论上无上限 |
| 适用领域 | 语言、代码、通用任务 | 规则明确的博弈、科学发现 |
| 数据需求 | 海量高质量数据 | 极少或零人类数据 |
| 计算需求 | 极高（训练+推理） | 极高（自我博弈+搜索） |
| 当前成熟度 | 高度商业化 | 领域受限 |

## 奖励黑客：自我博弈路线的阿喀琉斯之踵

Lilian Weng（OpenAI研究科学家）最近发表的关于强化学习中"奖励黑客"（Reward Hacking）的深度分析，恰好揭示了Silver路线面临的核心技术挑战。

奖励黑客是指：**RL agent找到了最大化奖励函数的捷径，但并没有真正学会预期的任务。** 这就像一个学生找到了考试的漏洞——分数很高，但什么都没学会。

在围棋中，奖励函数是清晰的：赢了就是赢了。但在更复杂的现实世界任务中：

- 如何定义"好的科学发现"的奖励？
- 如何定义"有用的医学建议"的奖励？
- 如何防止AI找到奖励函数的"后门"？

Silver的挑战是：**能否设计出足够强大且不可被"黑客"的奖励函数，使自我博弈在开放世界中也能奏效？**

这是一个价值11亿美元的问题。

## 为什么投资人敢赌？

11亿美元给一家几个月大的公司，投资人的逻辑是什么？

**1. Silver是极少数"已经证明过一次"的人**

AlphaGo/AlphaZero不是论文上的理论——它是在全世界面前击败了人类冠军的实际系统。在AI领域，能把研究转化为震惊世界的工程成果的人屈指可数。

**2. 数据墙正在逼近**

当前LLM路线的一个公开秘密是：高质量训练数据正在接近枯竭。互联网上的文本虽然庞大，但经过几代模型的训练后，边际收益正在快速递减。如果Silver的方法能绕过数据墙，这将是一个巨大的战略优势。

**3. 不对称回报**

如果自我博弈方法能扩展到通用智能——哪怕只是在几个关键科学领域——其价值将远超任何LLM公司。AlphaFold对生物学的影响已经证明了这一点。

**4. 人才虹吸效应**

Silver的名字本身就是人才磁铁。他能从DeepMind、FAIR、OpenAI等顶级实验室吸引最优秀的强化学习研究者。

## DeepSeek的启示：两条路线可能在收敛

有趣的是，当我们把视野拉远，会发现两条路线可能并非完全对立。

DeepSeek V3和V4在训练过程中大量使用了强化学习——特别是在推理能力的提升上。DeepSeek-R1的成功证明了RL可以显著提升LLM的推理能力。这意味着**未来的最强模型可能是两条路线的混合体**：

- 用大规模数据训练基础语言能力
- 用自我博弈/强化学习提升推理和发现能力
- 两者的边界可能会越来越模糊

Silver的工作如果成功，最大的受益者可能不只是Ineffable Intelligence自己——它可能会为整个行业提供新的训练范式，让所有模型都变得更强。

## 我的判断

**Silver的赌注是正确的方向，但时间线高度不确定。**

自我博弈在规则清晰的领域已经被证明是超越人类的最佳路径。问题在于能否扩展到开放世界——这可能需要3年，也可能需要30年。

**11亿美元足够吗？** 如果Silver的方法需要AlphaZero级别的计算量来训练通用系统，答案可能是"不够"。但如果他找到了更高效的算法（这正是他的强项），这笔钱可能绰绰有余。

**最值得关注的信号**：如果Ineffable Intelligence在未来12个月内展示了一个在新科学领域（不是围棋）通过自我博弈取得突破的系统，那么整个AI行业的估值逻辑都将被重写。

**给读者的行动建议**：
1. 不要只关注LLM的参数量竞赛——自我博弈路线可能在你意想不到的时候爆发
2. 如果你在做AI应用——目前仍然依赖LLM路线，但要为范式转换做心理准备
3. 如果你是AI研究者——强化学习和自我博弈是值得深入的方向，Silver的押注给了这个领域新的资金和关注度
4. 阅读Silver在UCL的强化学习课程——理解他的思维方式比预测他的成果更有价值

---

## 参考链接

- [TechCrunch: DeepMind's David Silver raised $1.1B to build AI that learns without human data](https://techcrunch.com/2026/04/27/deepminds-david-silver-just-raised-1-1b-to-build-an-ai-that-learns-without-human-data/)
- [Wired: The Man Behind AlphaGo Thinks AI Is Taking the Wrong Path](https://www.wired.com/story/david-silver-alphago-ai-wrong-path/)
- [Lilian Weng: Reward Hacking in Reinforcement Learning](https://lilianweng.github.io/posts/2024-11-28-reward-hacking/)
- [Sebastian Raschka: Categories of Inference-Time Scaling for Improved LLM Reasoning](https://sebastianraschka.com/blog/2026/inference-time-scaling.html)
