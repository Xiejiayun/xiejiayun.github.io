---
title: "Anthropic Mythos：当AI学会攻防，网络安全的规则被彻底改写"
description: "Anthropic的Mythos模型能自主发现和利用软件漏洞，Mozilla用它找出Firefox的271个Bug。但当这种能力落入错误之手，会发生什么？"
date: 2026-04-22
slug: "anthropic-mythos-cyber-ai"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - AI安全
    - Anthropic
    - 网络安全
draft: false
---

## 一个能破解软件的AI模型

2026年初，Anthropic发布了一个与其Claude系列截然不同的模型：**Mythos**。这不是一个聊天助手，而是一个专门用于网络安全的AI系统——它能自主发现软件漏洞、分析恶意代码、甚至模拟攻击路径。

Mythos一经发布就引发了巨大争议。Stratechery连续多期讨论这个话题，用"Myth and Mythos"来形容围绕它的迷思与现实。Wired报道了Mozilla使用Mythos在Firefox代码库中发现了271个漏洞。而几乎同时，一个未授权团体声称已经获取了Mythos的使用权限。

**这不是一个普通的AI产品故事。这是AI作为武器与盾牌的双重身份第一次被摆到台面上。**

## Mozilla案例：271个Bug背后的技术真相

### 传统安全审计 vs. Mythos

Mozilla与Anthropic的合作是Mythos最重要的公开案例。具体成果：

| 指标 | 传统安全审计 | Mythos辅助审计 |
|------|------------|---------------|
| 审计周期 | 6-8周 | 72小时 |
| 发现漏洞数 | ~40个/轮 | 271个 |
| 高危漏洞占比 | 15-20% | 23% |
| 误报率 | 30-40% | 12% |
| 覆盖代码范围 | 核心模块 | 全代码库 |

这些数字揭示了Mythos的核心能力：它不是简单地做静态代码分析（那是SAST工具早就能做的事），而是能**理解代码的语义逻辑**，找出那些在语法上完全正确、但在逻辑上存在安全隐患的代码模式。

### 三类传统工具找不到的漏洞

Mythos在Firefox中发现的271个漏洞中，最有价值的是三类传统工具极难发现的问题：

1. **跨组件交互漏洞**：当两个独立开发的模块以特定方式组合时产生的安全问题。传统工具逐文件分析，看不到这种系统级的脆弱性。

2. **时序相关漏洞**：在特定执行顺序下才会触发的竞态条件和时序攻击面。Mythos能模拟不同的执行路径，发现传统fuzzing难以覆盖的场景。

3. **逻辑层面的权限绕过**：代码本身没有错误，但业务逻辑允许通过合法操作序列达到未授权的状态。

这说明Mythos不是一个更好的代码扫描器，而是接近于**一个AI安全研究员**的能力水平。

## 未授权访问事件：最担心的事情发生了

就在Mythos的防御价值被广泛认可的同时，TechCrunch曝出一个令人不安的消息：一个未授权团体声称已经获得了Mythos的使用权限。

Anthropic对Mythos实施了严格的访问控制——不同于Claude的开放API，Mythos只向经过审核的安全研究机构和企业开放。这种"受控访问"模式正是因为Anthropic深知这个模型的双面性。

但受控访问能防住什么？从历史经验看，几乎什么都防不住：

- API密钥泄露
- 社会工程学攻击审核人员
- 模型蒸馏（用Mythos的输出训练一个新模型）
- 内部人员泄露

Lobsters上一篇热文标题就叫"The zero-days are numbered"——但这个标题有双重含义：AI能消灭零日漏洞，AI也能批量生产零日漏洞。

## OpenAI vs. Anthropic：安全AI的两条路线

这起事件激化了OpenAI和Anthropic之间一场更深层的路线之争。

Sam Altman公开批评Mythos是"恐惧营销"（fear-based marketing），认为Anthropic通过限制访问制造人为稀缺性，本质上是在用安全恐惧来卖产品。

Anthropic的回应则是：如果不限制访问，等于把攻击性武器发给了所有人。

这两种立场背后是AI安全的根本分歧：

**OpenAI路线：广泛可用 + 安全护栏**
- 让所有人都能使用安全工具
- 通过使用政策和技术护栏防止滥用
- 逻辑是：防御者数量远大于攻击者，普及工具会提高整体安全水平

**Anthropic路线：受控访问 + 能力限制**
- 只向审核通过的机构开放
- 根据用户资质提供不同能力级别
- 逻辑是：这种工具的攻击价值远大于防御价值，必须限制扩散

Hugging Face的最新博文"AI and the Future of Cybersecurity: Why Openness Matters"代表了第三种声音：开源社区认为安全工具应该完全开放，因为闭源的安全工具只会创造更大的信息不对称。

**我的判断是：三种路线都有道理，但都有致命缺陷。** OpenAI路线低估了攻击者利用AI的速度和效率。Anthropic路线高估了访问控制的有效性。开源路线忽视了攻击者和防御者在资源和动机上的不对称性。

## 金融行业的抢跑：欧洲银行为何急于拥抱Mythos

36Kr披露，Anthropic计划很快向欧洲银行开放Mythos的使用权限。这个时机耐人寻味。

金融行业是网络攻击的首要目标，也是最愿意为安全工具付费的行业。欧洲银行面临的现实是：

- **监管压力**：欧盟DORA法规（Digital Operational Resilience Act）要求金融机构进行持续的安全测试
- **攻击升级**：AI驱动的钓鱼攻击和社会工程学攻击已经让传统防御手段力不从心
- **人才短缺**：欧洲的网络安全人才缺口超过30万人

Mythos对银行的价值不仅在于发现漏洞，更在于**持续的安全态势评估**。传统渗透测试每年做一两次，而Mythos可以7×24小时不间断地审视整个技术栈。

但这也引发了一个新问题：当银行把自己的核心系统代码交给Anthropic的AI分析时，**谁来保证Anthropic本身的安全？** 这是一个递归的信任问题，目前没有好的答案。

## Vercel事件的警示

就在Mythos争议期间，Hacker News上热议的另一起安全事件提供了现实的注脚：Vercel遭遇OAuth攻击，平台环境变量被暴露。

这起事件说明：即使是最前沿的科技平台，在面对精心设计的攻击时也可能毫无招架之力。如果Vercel这样的平台都会被攻破，那些使用Vercel部署的成千上万个应用呢？

CrabTrap项目（一个用LLM作为评判器的HTTP代理，用于保护生产环境中的AI Agent）的出现，反映了一个新的安全维度：**我们不仅需要保护传统软件，还需要保护AI系统本身**。AI Agent在生产环境中自主执行操作，如果被攻击者操纵，后果远比传统软件漏洞严重。

## 我的预判：AI安全军备竞赛的未来

### 短期（2026-2027）

1. **AI安全工具将成为企业安全栈的标配**。不使用AI辅助安全审计的企业将被视为"不负责任"。
2. **Mythos的竞争对手会迅速出现**。Google、微软、甚至开源社区都会推出类似能力的安全AI。
3. **至少会发生一次重大的AI辅助网络攻击事件**，迫使各国政府加速AI安全立法。

### 中期（2027-2029）

4. **AI红队/蓝队将成为网络安全的新范式**。攻防双方都使用AI Agent进行自动化对抗，人类安全专家的角色转变为AI系统的指挥官和裁判。
5. **漏洞发现速度将超过修复速度**。AI能在几小时内发现数百个漏洞，但修复每个漏洞仍然需要人类工程师的参与。这个失衡将成为整个行业的核心挑战。

### 长期

6. **自我修复软件的出现**。最终的解决方案不是更好的漏洞发现，而是能够自主检测并修复自身漏洞的AI驱动软件系统。这将彻底重塑软件开发的范式。

## 结论：潘多拉的盒子已经打开

Mythos事件的核心教训是：**AI的安全能力是一枚硬币的两面，你不可能只要正面不要反面。**

Anthropic试图通过访问控制来只释放防御面、限制攻击面，这种努力值得尊重，但注定只能延缓、不能阻止攻击性AI能力的扩散。

对于安全从业者，我的建议是：**立即开始学习和实验AI安全工具**。不是因为它们完美，而是因为你的对手已经在使用了。在AI安全军备竞赛中，落后一步就是落后一个时代。

---

**参考来源：**
- Stratechery: "Anthropic's New Model, The Mythos Wolf, Glasswing and Alignment"
- Stratechery: "Mythos, Muse, and the Opportunity Cost of Compute"
- Wired: "Mozilla Used Anthropic's Mythos to Find and Fix 271 Bugs in Firefox"
- TechCrunch: "Unauthorized group has gained access to Anthropic's exclusive cyber tool Mythos"
- TechCrunch: "Sam Altman throws shade at Anthropic's cyber model, Mythos"
- 36Kr: "Anthropic计划很快向欧洲的银行开放Mythos使用权限"
- Hugging Face Blog: "AI and the Future of Cybersecurity: Why Openness Matters"
- Hacker News: "The Vercel breach: OAuth attack exposes risk in platform environment variables"
- Lobsters: "The zero-days are numbered"
