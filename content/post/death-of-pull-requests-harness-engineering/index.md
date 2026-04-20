---
title: "Pull Request已死，Harness Engineering万岁：软件开发的范式革命"
description: "GitHub首次允许关闭PR功能，Tokenmaxxing成为大厂怪象，Harness Engineering作为新学科崛起。从代码审查到Token编排，软件工程正经历21世纪以来最深刻的变革。"
date: 2026-04-20
slug: "death-of-pull-requests-harness-engineering"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 软件工程
    - AI编程
    - 开发者工具
    - Harness Engineering
draft: false
---

## Pull Request：一个21年的传统正在终结

2005年，Git诞生。GitHub随后将Pull Request（PR）普及为协作开发的核心工作流。21年后的2026年，GitHub做出了一个标志性决定：**首次允许开源项目禁用Pull Request**。

这不是一个小的功能调整。正如Latent Space的分析所言——对于过去15年学习编程的人来说，很难想象没有Git、GitHub和PR的世界。但PR之前有过生活，PR之后也将有新的生活。

驱动这一变革的核心力量是：**当80%的代码由AI Agent生成时，让人类逐行审查代码的流程在数学上就不成立了。**

## Harness Engineering：新学科的诞生

OpenAI的Ryan Lopopolo最近披露了一个震撼的数字：在他们的内部项目中，实现了**100万行代码、每天10亿token消耗、0%人类编写代码、0%人类代码审查**。

这催生了一个新概念——**Harness Engineering（控缰工程）**。Martin Fowler团队的Birgitta Böckeler将其定义为：驱动编程Agent高效工作的工程实践和心智模型。

软件工程技能栈正在经历三次迭代：

| 阶段 | 时间 | 核心技能 | 瓶颈 |
|------|------|---------|------|
| **Prompt Engineering** | 2023-2024 | 写好提示词 | 单次交互质量 |
| **Context Engineering** | 2024-2025 | 管理上下文窗口 | 信息组织和检索 |
| **Harness Engineering** | 2025-2026 | 编排Agent工作流 | 系统级验证和安全 |

Sebastian Raschka在"Components of A Coding Agent"中详细拆解了编程Agent的架构：工具调用、记忆管理、规划循环、自我纠错。这些组件的组合方式——而非模型本身——决定了Agent的实际效能。Harness Engineer的工作就是**设计和优化这个组合**。

## Tokenmaxxing：古德哈特定律的荒诞剧

当AI工具使用率成为KPI时，会发生什么？The Pragmatic Engineer的调查揭示了一个荒诞现象——**Tokenmaxxing**：

> 在Meta、Microsoft、Salesforce等大公司，开发者**故意刷token消耗**来满足AI使用指标。有人让Agent循环生成无用代码，有人反复触发相同的AI补全。

这是教科书级的**古德哈特定律**（当一个指标变成目标时，它就不再是好指标）在AI时代的表现：

- 管理层设定"AI工具使用率达到X%"作为目标
- 开发者发现最简单的达标方式是无意义地消耗token
- 公司在AI API上的花费激增，但实际生产力不变甚至下降
- 更有讽刺意味的是：Anthropic同期停止了企业计划的补贴

The Pragmatic Engineer的900+开发者调查显示了更真实的图景：AI工具确实在改变工作方式，但效果远比管理层期望的更加**非均匀**——资深工程师获益最多，初级工程师反而可能因为过度依赖AI而技能退化。

## Marc Andreessen的"浏览器之死"与DHH的编程新方式

Marc Andreessen——发明了网页浏览器的人——现在宣称浏览器时代正在终结。AI Agent不需要通过浏览器与服务交互，它们直接调用API和工具。这与DHH（Ruby on Rails创始人）最近展示的"新编程方式"形成呼应：不再是人在IDE中写代码，而是人在对话中描述意图，Agent在后台完成实现。

这构成了一个完整的范式转移：

```
旧范式: 人类写代码 → PR审查 → 合并 → 部署
新范式: 人类定义意图 → Agent生成代码 → 自动化验证 → 持续部署
```

## 对开发者的影响：残酷但真实

The Pragmatic Engineer的2026年调查数据揭示了几个关键趋势：

1. **成本转移**：公司在AI工具上的开支已超过部分初级开发者的薪资
2. **角色分化**：出现了"AI-native developer"和"traditional developer"的鸿沟
3. **入门门槛悖论**：编程变"简单"了，但理解系统设计的需求反而提高了
4. **新风险**：过度依赖AI生成的代码导致技术债务加速积累

## 我的预判

1. **2026年底**：50%以上的Fortune 500公司将引入某种形式的Harness Engineering角色
2. **2027年**：主流CI/CD流程将重新设计，从"代码审查"转向"Agent输出验证"
3. **最大风险**：当没有人真正理解代码库中80%的AI生成代码时，出现第一个大规模的"AI代码引发的安全事故"

**最尖锐的观点：** Pull Request的死亡不是工具的淘汰，而是一种人类认知局限的承认——我们审查代码的速度已经追不上AI生成代码的速度。问题不在于我们是否应该放弃PR，而在于我们是否已经准备好了替代方案。目前的答案是：没有。我们正在一边开飞机一边换引擎。

---

### 参考链接

- [Latent Space: RIP Pull Requests (2005-2026)](https://www.latent.space/p/ainews-rip-pull-requests-2005-2026)
- [Latent Space: Extreme Harness Engineering for Token Billionaires](https://www.latent.space/p/harness-eng)
- [Martin Fowler: Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html)
- [Sebastian Raschka: Components of A Coding Agent](https://magazine.sebastianraschka.com/p/components-of-a-coding-agent)
- [The Pragmatic Engineer: Tokenmaxxing as a weird new trend](https://newsletter.pragmaticengineer.com/p/the-pulse-tokenmaxxing-as-a-weird)
- [The Pragmatic Engineer: The impact of AI on software engineers in 2026](https://newsletter.pragmaticengineer.com/p/the-impact-of-ai-on-software-engineers-2026)
- [Latent Space: Marc Andreessen on The Death of the Browser](https://www.latent.space/p/pmarca)
