---
title: "【好文共赏】\"那些被 vibecode 出来的 Photoshop 在哪？\"：demoscene 老兵 gizmo64k 用三层编码框架，把\"指控\"本身送上了被告席"
description: "Christoph 'gizmo64k' Mütze 用一句反问把 2026 年最热的鄙视链拆穿：如果 vibecoding 真像它的批评者说的那样\"让任何人都能写出复杂软件\"，那这两年下来怎么没有一个 vibecoded Photoshop、vibecoded Blender、vibecoded compiler？指控本身才是真正的 vibecode——没定义、没证伪、没成本，只靠'感觉对'。"
date: 2026-05-19
slug: "good-read-vibecoded-photoshops-gizmo-levels-of-coding"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - AI编程
    - vibecoding
    - 编程哲学
    - 工程文化
    - demoscene
draft: false
---

> 📌 **好文共赏 \| Editor's Pick**
>
> 原文：[Where Are the Vibecoded Photoshops?](https://indiepixel.de/blog/posts/where-are-the-vibecoded-photoshops/) — Christoph "gizmo64k" Mütze，2026-05-18，阅读约 6 分钟
>
> 多模评分：**Opus 9.0 / Sonnet 8.8 / Gemini 8.6（综合 8.80 / 10）**
>
> 一句话推荐：当全世界都在为"AI 让程序员过时 vs AI 是被高估的玩具"吵成一团时，一位汉堡的 demoscene 老兵把战场重新搬到一个谁也回避不了的具体问题上——**所谓的"vibecoded 神器"到底在哪？**——并顺手揭穿了一个更难堪的真相：**绝大多数发出"这就是 vibecoded"指控的人，自己才是真正在 vibecode 的人。**

## 为什么值得读

过去 12 个月，"vibecoded" 已经从 Andrej Karpathy 推特上一个半开玩笑的词，变成了开发者社群里最廉价的鄙视武器。任何一段你不熟悉的代码、任何一个超出你审美的项目、任何一位"看起来不像传统码农"的作者，都可能被一句 "looks vibecoded" 永远埋葉——它的杀伤力来自于：**作出指控不需要任何证据，反驳却必须把作者历年的工程笔记翻出来一一证明。** 这是典型的"举证责任倒置"陷阱。

Christoph Mütze（在网上以 demoscene 时代 ID **gizmo64k** 著称）是这种指控的高频受害者：他四月份在 HN 发了一篇《[在原版 C=64 上跑一个 transformer 模型](https://news.ycombinator.com/item?id=47839645)》，立刻被人评论 "OBVIOUSLY vibecoded, because you have an art and design background, which doesn't seem to match the deep knowledge of Transformers or assembly required."

他回敬了三篇文章，越写越锋利。第一篇是技术性的（"我确实不懂 6510 汇编"），第二篇是哲学性的（"宫本茂大概率从没编译过一行代码，但他依然比你们大多数人都更会 coding"），到第三篇——也就是这次的主角——**他不再解释自己，而是把矛头对准提问者本身**。

这篇文章配得上"好文共赏"有三个理由：

1. **它给出了一个真正能用、真正能改变讨论质量的框架**——**编码的三个 Level**（Typing / Verifying / Deciding）；
2. **它对"指控"这种话语行为本身做了一次元批评**——指出绝大多数 vibecoded 指控本身才是没有 falsification、没有 definition 的 vibecode；
3. **作者拥有罕见的 voice**——demoscene 文化、被指控者的真实经验、神经多样性视角，这些东西在中文/英文技术圈关于 AI 编程的讨论里几乎完全缺席。

这与我之前导读过的[《资深开发者为何"说不清"自己的价值：Speed 与 Scale 的两个循环》](/post/good-read-senior-developer-speed-scale-decoupling/)、[《把学习外包给 AI：Addy Osmani 用三项 2026 年新研究》](/post/good-read-addy-osmani-dont-outsource-learning/)、[《Emacs 化的软件世界》](/post/good-read-emacsification-of-software/)构成了一组完美的对话——这些文章从产业经济、认知科学、软件形态三个角度讨论"AI 编程时代什么是真正的工程能力"，而 gizmo 的文章则从**身份政治和话语权**这一最少被技术人正面回应的角度切入。

## 核心观点深度解读

### 1. "Show me the evidence"：用一个空集证伪一整套修辞

文章一上来就抛出一道送命题：

> **原文**：Where is the vibecoded Photoshop. The vibecoded Excel. The vibecoded Maya. The vibecoded Blender. The vibecoded compiler that compiles itself. The vibecoded database, the vibecoded OS, the vibecoded anything-that-requires-architectural-judgment-to-hold-together. Huh?

注意他不是在问 "AI 能不能写复杂软件"——他问的是一个更精确的事实问题：**按"vibecoding 让任何人都能 prompt 出复杂软件"的强口号推演两年下来，这个集合应该已经满溢，但实证上它是空的。**

这是一个非常工程师的论证手法：**用证据缺席去否证一个被反复重复的命题**。Karl Popper 会高兴地拍手。它有趣的地方在于，它**同时戳穿了两个对立阵营**：

- AI 乐观主义者：你们承诺的 vibecoded 复杂软件在哪？
- vibecoded 指控者：既然这种东西不存在，那你指控的"vibecoded 神器"到底是什么？

gizmo 在文中明确说，他不是在否认"slop 存在"——一次性的 prompt-and-pray 玩具应用确实满地都是。他在意的是那个**被无限放大的修辞缝隙**：人们用"vibecoded"这个词指代的从来不是 slop（那本来就没人当回事），而是指代**任何使用了 AI 的、复杂的、看起来太成熟的项目**。一旦把两者分开，整个攻击就失去支点。

（这与我在[《Andy Warhol 时代的终结》](/post/good-read-leicht-frontier-ai-access-cutoff/)中提到的"特权用户名单"现象互为镜像——一个是上游的资源准入，一个是下游的话语准入。）

### 2. 三层编码模型：Typing / Verifying / Deciding

这是全文最值得记下的一块。gizmo 把"编码"这个被语义压扁的词，重新拆成三层：

| Level | 名称 | 内容 | AI 的影响 |
|-------|------|------|-----------|
| **L1** | Typing（打字） | 语法、`;`、指针算术、记得哪个 header file | **被 AI 几乎完全代工** |
| **L2** | Verifying（验证） | 测试套件、harness、对 90 次"几乎对"的尝试果断扔掉的反射 | **几乎不受影响** |
| **L3** | Deciding（决断） | 决定要不要做、决定哪种架构能撑十年、决定哪些 trade-off 是不可逆的 | **完全不受影响** |

他更早的[宫本茂那篇](https://indiepixel.de/blog/posts/shigeru-miyamoto-has-probably-never-compiled-a-line-of-code-in-his-life-and-is-still-a-better-coder-than-most-of-you/)给这个框架奠了基。论证的关键步骤是：

> **原文**：The gate was never at Level 1. The gate was at Levels 2 and 3, where the work that holds together actually happens.

如果你接受这个三分法（我认为这比 Brooks 的"essential vs accidental complexity"更具操作性），那么"AI 让任何人都能 vibecode 复杂软件"这条口号就被精确地拆碎了：**AI 把 L1 的边际成本压到接近 0，但 L2 和 L3 完全不动**——而 Photoshop、Blender、Excel 之所以是 Photoshop，全部价值都在 L2 和 L3。

这恰好对应了我之前导读过的[《当 AI 不再等你说完》](/post/good-read-thinking-machines-interaction-models/)里 Thinking Machines 的观察：模型把"产生看起来对的输出"这个动作做到了无成本，但"产生在长时间尺度上能 hold 住的判断"完全是另一种能力。

### 3. 指控的元批评：指控本身才是真正的 vibecode

这一段在我看来是全文最锋利的地方，因为它把对方的武器原样反掷回去：

> **原文**：The accusation that someone produced unverified output is itself being produced as unverified output. […] The thing they accuse vibecoders of is the very thing they are doing: No definition. No test. No falsification. Just a claim, shipped fast, never checked.

这是一句非常严谨的元批评。请注意，"vibecoded" 这个词作为指控，有四个最低要求才能算合法：

1. **definition**：什么样的产出叫 vibecoded？（"用了 AI"显然不够，"用了 AI 而且没有质量"也是循环论证）
2. **falsifier**：什么证据能让你撤回这个指控？
3. **检查成本**：你为做出这个判断花了多少分钟？
4. **校准记录**：你过去多少次被证伪？

绝大多数发出 "looks vibecoded" 的人四项全部为 0。**这意味着指控本身就是 prompt-and-ship、没有 harness、没有验证的——完全符合他们自己对 vibecoding 的描述。**

gizmo 没有这样列表化地写，但这段话的逻辑可以被精确地编成上面这四条，因此具有可重复使用的批评价值：下次再有人对你的项目说 "this is vibecoded"，你可以问回这四个问题。

### 4. Level 1 危机：身份建立在被租用的层上

这是文章里我读了之后停下来想了三分钟的一段：

> **原文**：The accusers cannot see this. They are not at the gate. They were at Level 1. Level 1 was their identity, their hours, their proof of belonging, their reason to feel at home in this profession. When AI made Level 1 cheap, it did not threaten the gate. It threatened them. Because they bet their self-worth on the layer that just got rented out.

这是一个**社会学解释**，不是技术解释——但它解释了一件之前一直让我困惑的事：**为什么 vibecoded 指控里携带的情感强度远远超出技术讨论的常规范围？** 因为它本质上不是技术辩论，是身份保卫战。

如果你的 15 年职业生涯主要花在"记住 STL 容器细节、调试 segfault、把 leetcode 中等难度题型熟练到肌肉记忆"这些纯 L1 工作上，那么 L1 的边际成本被 AI 压到 0 这件事——**对你不是"工具升级"，而是"履历清零"**。你被迫面对一个之前可以不面对的问题：**那我在 L2 和 L3 上的存款是多少？** 大部分人没准备好回答这个问题，所以他们攻击让问题出现的人，而不是回答问题。

这一点是 Tuhin Nair 在[《资深开发者的 Speed/Scale 双循环》](/post/good-read-senior-developer-speed-scale-decoupling/)中那个"复杂度恐惧 vs 不确定性恐惧"分歧的更尖锐表述——Nair 把它包装得职业、得体；gizmo 不留情面地把它说成 "you bet your self-worth on the layer that just got rented out"。

### 5. demoscene 的 epistemics：harness 是真正的作品

文章的中段，gizmo 给出了他对自己 SoulPlayer C64 项目的描述——这个细节非常重要，因为它实际定义了什么叫"非 vibecoded"的工作：

- **4 套位元一致的参考实现**：浮点参考、整数参考、内存忠实 shadow、emitted asm
- **90 个测试**：任何不全部一致的实现不出货
- 整个 Python pipeline 的代码量比它生成的最终产物大几个数量级

这是 demoscene 文化的核心 trade：**花极不合理的 toolchain 投入，让最终的 ~6KB 二进制能塞进 1985 年的硬件**。gizmo 借此点破：

> **原文**：Nobody bolts a four-way harness onto a vibecoded project.

这是一个非常精确的反射弧：**如果你想检验某项工作是不是 vibecoded，不要看代码本身，看代码周围的 harness。** 真正的工程师投资在 L2，因为 L2 是 L1 量产时代里唯一不会贬值的资本。

这一观察与[《把 200 万行 Haskell 跑在每年 2480 亿美元的资金流上：Mercury 的可靠性工程师》](/post/good-read-haskell-mercury-production-engineering/)的隐含主题完全合拍——Mercury 那边把"语言学家当可靠性工程师"，本质就是给关键金融逻辑套上 demoscene 级别的 harness。

### 6. 拒绝以同样的指控反击：作者的道德选择

很多读者读到这里会以为 gizmo 接下来要把"反 vibecoded"的招牌打过去——但他做了一个反方向选择：

> **原文**：My demoscene background alone would allow me to turn around and call other people's work vibecoded. I could punch down at every prompt-and-pray app on the internet and land a lot of hits. **I will not.**

理由是他在自己身上认出了"被指控不属于这里"这种攻击的形状——neurodivergent、Tics、freelancer-not-by-choice、demoscene-not-industry、artist-not-CS、disabled。这些标签在他生命中都被作为"你不真正属于这里"的攻击点用过。

他在结尾说了一个非常重要的观察：

> **原文**：The accusation doesn't have to be true. It just has to cost the target enough time and morale that the next person stops sharing their work.

这是一句**信息战命题**。指控的实际目标不是被指控者，而是**潜在的下一个分享者**。它的胜利标准不是"对方被证明是错的"，而是"下一个有创意的人选择不公开发表"。从这个角度看，"vibecoded" 这个词在当下的功能，与 1990 年代的 "code monkey"、2010 年代的"不是 real engineer"是完全同构的——**它是一个守门工具，目标是减少新人涌入**。

### 7. 一个被 HN 高赞 stevex 提出的、值得直面的反驳

HN 上对这篇文章最被支持的反驳来自 stevex（首条高赞评论），值得我们认真处理，否则这篇导读就是一边倒：

> "vibecoded Photoshops 不会出现。但人们不再需要 Photoshop——他们用 ChatGPT 直接做图。vibecoded 项目就是 disposable 个人工具，它的特征恰恰是不需要复用、不需要发布、解决完一次问题就丢。"

这个反驳很有力。它在某种意义上**承认了 gizmo 的事实命题**（"没有 vibecoded Photoshop"），但提出**这个事实不重要**——因为软件的形态本身正在从"通用应用"转向"一次性 prompted 工具"。

这与我之前导读[《Emacs 化的软件世界》](/post/good-read-emacsification-of-software/)中 Thomas Ptacek 的观点几乎完全一致：当生成软件的成本接近 0，"软件作为商品"的模型让位于"软件作为定制器物"的模型。

所以一个公允的结论是：**gizmo 的论证完美适用于"AI 让 Photoshop 这种集合性工程艺术变得任何人可造"这一强主张；但它无法反驳"AI 让 Photoshop 这种集合性工程艺术不再被需要"这一弱主张。** 前者是修辞泡沫，后者是真问题。

## 延伸阅读图谱

### gizmo64k 的"AI/coding"系列五部曲（按发表顺序）

1. [How about putting a transformer model on a stock C=64?](https://indiepixel.de/blog/posts/how-about-putting-a-transformer-model-on-a-stock-commodore-64/)（2026-04-08）—— 起点：在 25,000 参数 int8 transformer 上构建演示
2. [I have no clue how 6510 assembly works!](https://indiepixel.de/blog/posts/i-have-no-clue-how-6510-assembly-works/)（2026-04-22）—— 第一次回击 vibecoded 指控，主张"harness 才是工作"
3. [Shigeru Miyamoto … better coder than most of you](https://indiepixel.de/blog/posts/shigeru-miyamoto-has-probably-never-compiled-a-line-of-code-in-his-life-and-is-still-a-better-coder-than-most-of-you/)（2026-04-23）—— Level 1/2/3 框架的正式提出
4. [Paradise Is Always Five Years Away](https://indiepixel.de/blog/posts/paradise-five-years-away/)（2026-02-28）—— 对"奇点必将到来"的怀疑论文章
5. **[Where Are the Vibecoded Photoshops?](https://indiepixel.de/blog/posts/where-are-the-vibecoded-photoshops/)**（2026-05-18）—— 整个系列的总结性反击，本期主推荐

### 五本与"L2/L3 至上"思想暗合的工程经典

- *The Mythical Man-Month* — Brooks 的 essential vs accidental 区分，L1 = accidental，L2/L3 = essential
- *Design of Design* — Brooks 后期作品，更直接讨论 L3 工作
- *Code Complete 2* — Steve McConnell，把 L2 verification 系统化
- *A Philosophy of Software Design* — John Ousterhout，complexity 的几何学（L3 核心训练）
- *Working Effectively with Legacy Code* — Michael Feathers，几乎全是 L2 心法

### 三篇反方观点 / 不同视角

- HN [`@stevex` 评论](https://news.ycombinator.com/item?id=48177228)：vibecoded 应用就是 disposable 个人工具，本来就不会替代 Photoshop
- Simon Willison [Vibe Coding 词源考](https://simonwillison.net/2025/Feb/2/vibe-coding/)：Karpathy 创词时的原义其实接近 gizmo 反对的那种用法
- METR [Early 2025 AI experienced OS dev study](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)：在熟悉代码库上 AI 让资深开发者**变慢** 19%

### 我之前在本博客的相关导读（强相关，建议交叉阅读）

- [《资深开发者为何"说不清"自己的价值：Speed 与 Scale 的两个循环》](/post/good-read-senior-developer-speed-scale-decoupling/)
- [《把学习外包给 AI：Addy Osmani 用三项 2026 年新研究》](/post/good-read-addy-osmani-dont-outsource-learning/)
- [《Emacs 化的软件世界：当 AI Agent 让每个人都能写自己的原生应用》](/post/good-read-emacsification-of-software/)
- [《教会 Claude"为什么"》](/post/good-read-anthropic-teaching-claude-why/)
- [《CTF 场景已死：澳洲安全工程师 Kabir Acharya》](/post/good-read-ctf-scene-is-dead-frontier-ai/)
- [《把 200 万行 Haskell 跑在每年 2480 亿美元的资金流上：Mercury》](/post/good-read-haskell-mercury-production-engineering/)
- [《Andy Warhol 时代的终结：Anton Leicht 的特权用户名单》](/post/good-read-leicht-frontier-ai-access-cutoff/)

## 编辑延伸思考

读完这篇文章三遍，我想留下三个超出原文范围的笔记：

**第一，"四个最低条件"是个可立即落地的微型工具。** 我建议把"definition / falsifier / 检查成本 / 校准记录"这四问做成一张卡片，下一次在 code review 或者技术讨论里看见任何"这看起来就是…"的判断式语言，无论它是 "vibecoded"、"over-engineered"、"premature optimization"、"not idiomatic"，都把这四问拿出来对照一下。这个工具不偏袒任何阵营——它对 AI 乐观派的 "this changes everything" 同样有效。**它的本质是把"感觉对"和"研究过"分开，这恰恰是 gizmo 三层编码模型里的 L2 在话语层面的应用。**

**第二，Level 1/2/3 框架对个人职业规划有非常直接的指导意义。** 如果你今天处在一个 L1 占比 > 60% 的工作里（典型例子：把需求文档翻译成 boilerplate、修偶发的语法错、把 API 接到前端），那么不管你愿不愿意承认，**你的可替代成本已经在过去 18 个月跌了一个数量级**。补救路径不是"学一门新语言"——那还是 L1。是要刻意接触一些**只在 L2/L3 才能学到的东西**：写复杂系统的 chaos test、参与跨团队的架构 review、做一次完整的事故复盘、为一个开源项目的 release pipeline 写一份 verification harness。这些工作 AI 现阶段帮不上多少忙，因为它们的难度恰恰来自"在不完整信息下作出不可逆判断"。

**第三，关于"指控经济学"的更普适视角。** gizmo 在文末提到的"指控的成本不对称性"，其实是一个比技术圈更大的问题。任何**指控（accusation）成本远低于反驳（refutation）成本**的话语环境，最终都会演化成噪声主导的劣币驱逐良币。技术圈过去 30 年至少经历过四次类似的指控话语周期：「不是 real programmer」（90s）、「code monkey」（00s）、「不是 senior engineer」（10s）、「vibecoded」（20s）。每一次的形式都是：**用一个语义模糊但情感强烈的词，把一个外部群体污名化，从而保护内部群体的身份和报酬。** 看穿这一结构以后，你大概率会更小心地使用这些词——这本身就是对作者最好的致敬。

最后，写一句不那么编辑、更个人一些的话：在 AI 让我们所有人都能更便宜地产生"看起来对"的输出的这个时代，那种愿意花九十个测试去证明自己作品正确的人，恰恰是我们最需要珍惜的同行者。如果有人想用一个廉价的标签把这些人吓回阴影里——我们都应该愿意花十分钟，把这种指控本身的成本拉回到与它的代价相称的高度。

## 配套资料导览

本目录下另外三个文件：

- `concept-cards.md` — 12 张关键概念卡片：从"Level 1/2/3"到"指控的元批评"到"demoscene 的 harness 文化"，每张可作为讨论引子
- `glossary.md` — 35 条英中对照术语表，覆盖 demoscene 文化术语、AI 编程话语术语、软件工程概念
- `mindmap.svg` — 全文论证的思维导图，深色背景，从"空集证伪"分四支铺开
- `cover.svg` — 封面图

## 谁应该读

- 任何一位最近被人评论过 "looks vibecoded" 的开发者
- 任何一位最近评论过别人 "looks vibecoded" 的开发者（这一条尤其重要）
- 在 AI 编程辩论中觉得"两边都不太对劲但说不清哪里不对"的人
- 团队 lead / 工程经理：这篇文章给你提供了一套讨论 AI 政策时不被语言绑架的工具
- 对 demoscene 文化或者"工具即作品"哲学好奇的人
- 任何想把 Brooks 的 "essential vs accidental" 升级到一个更精细分层模型的人
