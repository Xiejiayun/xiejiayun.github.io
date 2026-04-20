---
title: "Claude Mythos与Project Glasswing：AI安全的「核武器时刻」到来了吗？"
description: "Anthropic宣布Claude Mythos Preview因网络攻击能力过强而不公开发布，同时启动Project Glasswing用该模型发现并修复软件漏洞。这是AI安全治理的分水岭，还是精心设计的竞争壁垒？"
date: 2026-04-20
slug: "claude-mythos-glasswing-ai-safety-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - AI安全
    - Anthropic
    - 网络安全
    - 大模型
draft: false
---

## 一个"太危险而不能发布"的模型

2026年4月，Anthropic做出了AI行业史上最引人注目的决定之一：宣布Claude Mythos Preview模型因其**网络攻击能力过于强大**，将不对公众开放。与此同时，他们启动了Project Glasswing——用这个"危险"模型扫描公共和私有软件代码库，目标是**发现并修补所有可利用的漏洞**。

这是一个充满张力的叙事：一家公司同时扮演了"发现核武器"和"核不扩散条约执行者"的角色。

安全研究者Bruce Schneier在分析中指出，网络安全行业正在为Mythos的能力"着迷"——Glasswing本质上是用攻击性AI来构建防御体系。但问题在于：**谁来监督监督者？**

## 真正的安全顾虑，还是竞争壁垒？

Stratechery的Ben Thompson对此持审慎态度。他指出，Anthropic声称模型"太危险"有理由值得怀疑，但如果Anthropic是对的，那引发的问题反而更深：

| 维度 | "真安全"情景 | "营销策略"情景 |
|------|-------------|---------------|
| **动机** | 真实发现了零日漏洞挖掘的突破性能力 | 制造稀缺性，建立"最强模型"品牌认知 |
| **Glasswing价值** | 价值千亿的网络安全基础设施 | 付费漏洞扫描的商业包装 |
| **对开源的影响** | 证明能力封锁的必要性 | 打压开源竞争对手的合法性 |
| **监管影响** | 支持AI能力许可制度 | 主动拥抱监管以构建护城河 |

我的判断：**两者兼有，但安全顾虑是真实的。** 理由如下——

来自arXiv的最新研究"Subliminal Transfer of Unsafe Behaviors in AI Agent Distillation"提供了一个令人不安的证据：不安全的Agent行为可以通过模型蒸馏**隐性传递**，即使训练数据在语义上与这些行为无关。这意味着：一旦一个具有强攻击能力的模型被公开，其能力可能通过蒸馏扩散到整个开源生态中，且**无法溯源、无法控制**。

## 从AI实验室到网络安全公司

Anthropic正在$30B ARR的基础上进行一次战略性转型。Glasswing不只是一个安全项目，它是一种新的商业模式原型：

**传统路径：** 训练模型 → 提供API → 按token收费

**Glasswing路径：** 训练超强模型 → 不公开 → 用模型提供安全服务 → 按漏洞价值收费

这类似于核电站的逻辑：你不出售浓缩铀，你出售电力。模型本身是"核燃料"，对外提供的是安全加固后的"电力"。

Trail of Bits最近关于"Mutation testing for the agentic era"的研究进一步印证了这个方向：当AI Agent成为软件开发的主力，安全测试必须进化为**由AI驱动的对抗性测试**。Glasswing可能是这个新范式的第一个大规模实现。

## 各实验室AI安全策略对比

| 实验室 | 安全策略 | 模型发布策略 | 安全投入占比 |
|--------|---------|-------------|-------------|
| **Anthropic** | Constitutional AI + RSP + Glasswing | 限制性发布，能力封锁 | ~25%（推测） |
| **OpenAI** | RLHF + 红队测试 + 外部审计 | 渐进式开放 | ~15% |
| **Google DeepMind** | 内部安全团队 + 发布前评估 | 开源小模型，封闭大模型 | ~20% |
| **Meta** | 开源为主 + 社区驱动安全 | 全面开源 | ~10% |

## 信任悖论：人类如何信任AI Agent？

Schneier引用的最新研究揭示了一个深层矛盾：在策略博弈实验中，人类倾向于**假设AI对手是理性且合作的**——这种过度信任意味着，当AI Agent被部署到安全关键领域时，人类监督者可能系统性地**低估AI的对抗能力**。

这与Glasswing的前提形成完美的闭环：如果我们不能信任人类来评估AI的攻击能力，那么只能用AI来评估AI。但这又引出了一个无限递归的问题——谁来评估评估AI的AI？

## 我的预判

1. **短期（6个月内）：** Glasswing将发现至少一个影响数十亿设备的关键漏洞，验证其价值并引发监管关注
2. **中期（1-2年）：** 其他实验室将推出类似的"能力封锁+安全服务"模式，形成AI安全的寡头格局
3. **长期趋势：** AI能力的"核不扩散"框架将成为国际讨论焦点，但执行力度将远弱于预期——因为代码比铀容易复制得多

**最尖锐的观点：** Anthropic的Glasswing模式本质上是在说——未来的AI安全不是民主化的，而是集中式的。你要么信任少数几家公司来保护你，要么面对一个所有人都拥有网络核武器的世界。这不是一个令人舒适的选择，但它可能是我们唯一的选择。

---

### 参考链接

- [Stratechery: Anthropic's New Model, The Mythos Wolf, Glasswing and Alignment](https://stratechery.com/2026/anthropics-new-model-the-mythos-wolf-glasswing-and-alignment/)
- [Schneier on Security: On Anthropic's Mythos Preview and Project Glasswing](https://www.schneier.com/blog/archives/2026/04/on-anthropics-mythos-preview-and-project-glasswing.html)
- [Schneier on Security: Human Trust of AI Agents](https://www.schneier.com/blog/archives/2026/04/human-trust-of-ai-agents.html)
- [Latent Space: Anthropic @ $30B ARR, Project GlassWing](https://www.latent.space/p/ainews-anthropic-30b-arr-project-glasswing)
- [arXiv: Subliminal Transfer of Unsafe Behaviors in AI Agent Distillation](https://arxiv.org/abs/2604.15559)
- [Trail of Bits: Mutation testing for the agentic era](https://blog.trailofbits.com/2026/04/17/mutation-testing-for-the-agentic-era/)
