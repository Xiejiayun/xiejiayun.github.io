---
title: "Pull Request已死：当1000万行代码库实现零人类代码、零人类审查"
description: "从Latent Space宣告PR已死，到Notion的Token Town实验，再到DHH重新拿起键盘——2026年的软件工程正在经历自Git发明以来最大的范式转变。Tokenmaxxing取代了Lines of Code，AI编排取代了Code Review。"
date: 2026-04-21
slug: "death-of-pull-requests-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 软件工程
    - AI编程
    - 开发者工具
draft: false
---

## Pull Request：一个21年的工作流走到了终点

2005年，GitHub的Pull Request机制彻底改变了开源协作方式。21年后的2026年，Latent Space发出了一个大胆的判断：**"RIP Pull Requests (2005-2026)"**。

这不是标题党。数据说话：在采用了极限AI编程工作流的团队中，有团队实现了**100万行以上代码库、每天10亿token消耗、0%人类编写代码、0%人类代码审查**。这个数字出自Latent Space对"Extreme Harness Engineering"实践的深度报道。

当代码的生产者和审查者都不再是人类时，Pull Request这个为人类协作设计的机制，自然失去了存在的意义。

## 从Lines of Code到Tokenmaxxing

软件工程正在经历一次度量革命。The Pragmatic Engineer将"**Tokenmaxxing**"称为2026年最怪异的新趋势——工程师不再按代码行数衡量产出，而是按消耗的AI token数量来衡量。

| 旧范式 | 新范式 | 含义变化 |
|--------|--------|----------|
| Lines of Code（代码行数） | Tokens consumed（消耗token数） | 从"我写了多少"到"AI帮我做了多少" |
| PR review time（审查时间） | Verification pipeline（验证管线） | 从"人看代码"到"自动化验证" |
| Code coverage（代码覆盖率） | Mutation test survival（变异测试存活率） | 从"测试了吗"到"测试有效吗" |
| Sprint velocity（冲刺速度） | Agent throughput（Agent吞吐量） | 从"团队效率"到"Agent编排效率" |

**这背后的本质转变是：软件工程师的核心技能从"写代码"变成了"编排AI Agent"。**

## Notion的Token Town：一个极端案例的深度解剖

Notion的实验尤其值得关注。根据Latent Space的报道，Notion的"Token Town"项目做了以下尝试：

- **5次完整重建**产品的不同模块
- 部署了**100+个AI工具**
- 在MCP（Model Context Protocol）和CLI之间做了深度对比
- 构建了完整的"软件工厂"概念

Simon Last（Notion工程负责人）的核心洞察是：**未来的软件开发不是一个人用AI写代码，而是一个人管理一个AI代码工厂**。

这里的关键转变是：

```
传统模式：  开发者 → 写代码 → PR → 审查 → 合并 → 部署
Token Town：开发者 → 定义意图 → Agent群编码 → 自动验证 → 自动部署
```

人类在第二种模式中的角色完全不同：从"手工匠人"变成了"工厂厂长"。

## DHH和行业领袖为什么又开始写代码了？

一个看似矛盾的现象是：在AI编程大行其道的2026年，**多位知名技术领袖重新开始亲自写代码**。DHH（Ruby on Rails创始人）公开分享了他的"新编码方式"，多位行业高管也在"回归编码"。

这不矛盾。他们回归的不是传统编码，而是**AI辅助编码**——用AI作为"极速助手"来验证想法、快速原型、探索架构。正如Steve Yegge在与The Pragmatic Engineer的对话中所说：**"从IDE到AI Agent"不是工具升级，而是工作方式的根本重塑。**

## AI Agent真的在帮忙吗？

The Pragmatic Engineer提出了一个尖锐的问题：**"AI agents实际上在拖慢我们吗？"**

答案是复杂的：

**AI Agent确实在拖慢的场景：**
- 简单任务被过度工程化（用Agent做了直接写代码5分钟就能完成的事）
- Agent生成的代码引入了新的bug，调试时间超过了节省的时间
- 上下文切换成本——等待Agent响应打断了心流

**AI Agent确实在加速的场景：**
- 大规模重构和迁移
- 安全审计和漏洞修复
- 样板代码和CRUD操作
- 多语言/多框架的移植

**关键判断：AI编程的收益遵循"J曲线"——短期内效率可能下降（学习成本+工具适配），但跨过临界点后效率呈指数级提升。**

## Staff Engineer 2027：AI时代的高级工程师画像

The Pragmatic Engineer关于"2027年及以后Staff Engineer角色"的讨论，勾勒出了一个清晰的未来：

| 传统Staff Engineer | 2027 Staff Engineer |
|---|---|
| 深度技术专家 | AI系统架构师 |
| 代码审查把关人 | 验证策略设计师 |
| 跨团队技术协调 | 人机协作流程设计 |
| 技术决策制定者 | AI Agent编排专家 |
| Mentoring初级工程师 | 训练和微调团队AI工具 |

**核心变化：Staff Engineer从"最好的代码写手"变成"最好的AI使用者"。**

## 什么取代了Pull Request？

Pull Request死后，空缺需要被填补。目前行业正在探索的替代方案包括：

1. **持续变异测试**（Trail of Bits的方向）：不依赖人类审查代码质量，而是通过自动化的变异测试来验证代码的正确性
2. **形式化验证**：对关键代码路径使用数学证明而非人工审查
3. **AI对抗审查**：用一个AI Agent审查另一个AI Agent的代码，类似GAN的思路
4. **意图验证**：不审查代码本身，而是验证代码是否满足了开发者的原始意图

## 三个预判

1. **2026年底，50%以上的硅谷初创公司将废弃传统PR流程**。替代方案是AI驱动的持续验证管线。

2. **"Prompt Engineer"头衔将在2027年消失，被"AI Systems Engineer"取代**。这不是改名，而是技能栈的根本升级——从写prompt到设计和维护AI工作流系统。

3. **代码所有权的概念将被重新定义**。当代码是AI生成的，"谁写的这段代码"将变成"谁定义的这个行为意图"。法律和管理框架需要跟上。

## 给开发者的行动建议

- **立即开始**：在你的工作流中引入至少一个AI编码Agent（Claude Code、Cursor、Copilot），熟悉"人-AI协作"模式
- **投资验证能力**：学习变异测试、属性测试等自动化验证技术，这将比代码编写技能更有价值
- **重新思考职业路径**：如果你的核心竞争力是"写代码快"，你需要尽快转型到"设计系统好"

---

### 参考链接

- [Latent Space: RIP Pull Requests (2005-2026)](https://www.latent.space/p/ainews-rip-pull-requests-2005-2026)
- [Latent Space: Extreme Harness Engineering](https://www.latent.space/p/harness-eng)
- [The Pragmatic Engineer: DHH's new way of writing code](https://newsletter.pragmaticengineer.com/p/dhhs-new-way-of-writing-code)
- [The Pragmatic Engineer: Are AI agents actually slowing us down?](https://newsletter.pragmaticengineer.com/p/are-ai-agents-actually-slowing-us)
- [The Pragmatic Engineer: Tokenmaxxing as a weird new trend](https://newsletter.pragmaticengineer.com/p/the-pulse-tokenmaxxing-as-a-weird)
- [The Pragmatic Engineer: From IDEs to AI Agents with Steve Yegge](https://newsletter.pragmaticengineer.com/p/from-ides-to-ai-agents-with-steve)
- [Latent Space: Notion's Token Town](https://www.latent.space/p/notion)
- [Trail of Bits: Mutation testing for the agentic era](https://blog.trailofbits.com/2026/04/01/mutation-testing-for-the-agentic-era/)
- [Sebastian Raschka: Components of A Coding Agent](https://magazine.sebastianraschka.com/p/components-of-a-coding-agent)
