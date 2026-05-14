---
title: "【好文共赏】Emacs 化的软件世界：当 AI Agent 让每个人都能写自己的原生应用"
description: "Thomas Ptacek 用一篇短文重新定义了 AI 编程时代的软件形态——它不是 Electron 的死亡，而是 Emacs 文化的逃逸：个人化、原生、量身定制，源码不重要，重要的是 prompt。"
date: 2026-05-14
slug: "good-read-emacsification-of-software"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - AI Agent
    - Claude
    - 软件工程
    - 个人软件
    - Emacs
    - 原生UI
    - Thomas Ptacek
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
>
> 原文：[The Emacsification of Software](https://sockpuppet.org/blog/2026/05/12/emacsification/)
> 作者：Thomas Ptacek（sockpuppet.org / Quarrelsome） | 发布于：2026-05-12 | 阅读时长：约 8 分钟
>
> **一句话推荐理由**：这是 2026 年迄今为止我读过的、关于 "AI Agent 到底改变了什么" 最锋利、最反直觉的一篇短文——它不预测 Electron 之死，不鼓吹 vibe coding，而是把镜头对准了一个被忽视的角落：**每一台开发者电脑上正在悄悄长出 Emacs 文化的孢子**。

## 为什么值得读

过去一年关于 AI 编程的讨论，绝大多数都在两条赛道上：要么是 "Agent 能不能替代工程师"（劳动力视角），要么是 "Agent 应该怎么集成进 CI/IDE/Code Review"（流程视角）。Ptacek 这篇文章的特别之处，在于它绕开了这两条主路，提出了一个我们其实早就感受到、却没说清的事实：**AI Agent 正在让"个人软件"重新成为一个有意义的类别**。

为什么这很重要？因为过去 15 年——大致从 Electron 普及开始——软件世界默认了一个事实：写一个真正可用的原生桌面应用，是一件需要专业团队、几个月时间、足够商业回报支撑的事情。结果就是 Slack 是 Electron，Signal 是 Electron，VS Code 是 Electron，Discord 是 Electron。每个 "原生" 应用其实都拖着一份秘密的 Chromium。

Ptacek 的观察是：这个均衡正在崩塌。不是因为 Electron 突然不能用了，而是因为 **写一个挠自己痒的、丑陋的、专用的原生小工具的边际成本，已经塌缩到几十分钟**。这件事的连锁后果，比大多数人意识到的更深远，也比"AI 替代程序员"这种俗套预言更有意思。

而且 Ptacek 不是路人——他是 Matasano 的创始人、知名安全研究员、HN 上常年活跃的 tptacek。一个干了二十多年漏洞研究、对一切炒作保持怀疑的人，写出这样一篇近乎乐观的文章，本身就值得读一遍。

## 核心观点提炼

### 1. 从 Markdown 阅读器讲起的"小故事"，是整篇文章的特洛伊木马

文章开头用了一个看似日常到无聊的痛点：**作者想要一个好用的 Markdown 查看器**。TUI 工具（glow、markless）因为终端等宽字体太累眼；Obsidian / Typora / Bear 都是编辑器，会破坏他的窗口布局；App Store 上的查看器要么不支持搜索、要么不支持复制、要么塞着 IAP。

然后他做了一件非常 2026 年的事：让 Claude 给他"挤"一个出来。整个过程"interactive"的部分只花了 30 分钟，其余时间他在 Facebook 上对城市规划政策开火。产物叫 [MDV.app](https://github.com/tqbf/mdv)，一个带 SQLite FTS 索引、书签、阅读位置记忆、讲究字体的 macOS 原生 Markdown 查看器。

> 原文：It took several hours to generate a better Markdown viewer than I could find on the App Store, but only about 30 minutes of that was interactive.（来源：sockpuppet.org）

这个故事不是炫技。它是论文的引理。它在说：**那个原本不存在的需求—供给曲线交点，现在存在了。**

### 2. "Emacs 化"是什么意思：个人软件成为默认形态

Ptacek 把这种新形态命名为 "Emacsification"，是一个精准到近乎残忍的类比。Emacs 用户做了几十年的事情，正在外溢到整个软件世界：

- **它是个人软件**。绝大多数程序只服务于它的作者，然后被遗忘。就像他自己 `.emacs` 里那些早已废弃的小函数。
- **偶尔有一个会"逃逸出容器"**，被几个人使用。但即便如此，最终被分享出来的"成品"并不是最重要的东西。
- **源码也不是最重要的**。如果 Agent 写了项目里所有的 SwiftUI 代码，认真读它能学到什么？

这里有一个关键转折，是我读完后反复琢磨的地方——他说：**人们更想要的是 prompt，而不是源码**。这一句话把开源运动建立 30 年的一个隐含假设（"source is the truth"）拆掉了一角。在 Agent 时代，"如何让它被生成出来"的描述，比"它被生成成了什么"更接近作者的真实意图。

### 3. Electron 的城墙不是被推倒的，而是被绕过的

文章中段有一个让我会心一笑的段落：作者抱怨每次有人给他发 Signal 消息，屏幕就闪一下；这是因为 Signal 是 Electron 应用，相当于一整个 Chromium 在后台渲染一个秘密网页。

Ptacek 的判断很冷静：Electron 不好，但它一直"够用"。原因不是技术，而是**人**——能写出 production-grade 原生 UI 的开发者太稀缺。

> 原文：Capable macOS native UI developers are rare birds. But Claude isn't just a replacement-level SwiftUI developer. Claude is actually good.（来源：sockpuppet.org）

这两句话连在一起，揭示了一个供给侧的相变：**原生 UI 工程师的稀缺性，作为一个经济约束，正在被 LLM 抹平**。Ptacek 没有说 Electron 会死——他甚至特意声明这不是一篇唱衰 Electron 的文章。但他说了一件更微妙的事：当原生 UI 的供给曲线变平之后，Electron 一直占据的"经济上唯一合理"那块生态位，正在缩小。

### 4. "构建"软件这个动词，正在被悄悄换掉

文章里有一句话被很多人转发——大意是：当你和 Agent 一起做软件的时候，"building"这个词其实有点用力过猛，**你在做的事情更像"configuring"，在一个突然变得可配置很多的平台上**。

这是一个非常有 Lisp 哲学味道的洞察。Emacs 的核心精神从来不是"它是个编辑器"，而是"它是一个可以一直按你的意思继续长下去的运行时"。在 Agent 时代，你的整台操作系统、你的整个工具链，正在拥有同样的 malleability（可塑性）。你不是在购买软件，你是在按需让软件被挤压成型——为你一个人。

### 5. 它带来的不是消费品，而是"挠痒痒"的复兴

文章最后一段提供了一个意外乐观的注脚：那些"装机时收藏的、永远没做完的小项目"，正在被 AI-pilled 开发者一个接一个地完成；而且这次的成品居然能让人愉快地使用。Brendan Gregg 当年为了让 bpftrace 在终端里出可视化吃了多少苦——以后没必要再吃了。

> 原文：Building native UI is now fun; a lot more fun than building web interfaces ever was.（来源：sockpuppet.org）

Ptacek 是漏洞研究员，他承认大多数读者面对 Agent 的进步只有"dread（恐惧）"。但他给出的这个角度是少见的"unalloyed good（纯粹的好事）"：你终于可以为了一个只有你一个人才会遇到的痛点写一个真的好用的小程序了，而且不必把它做成产品。

## 我的延伸思考

这篇文章踩中了一个我自己今年在反复琢磨的问题：**AI Agent 时代，"软件"的颗粒度会变小，还是变大？**

主流叙事是变大——Agent 能写更复杂的系统，所以产品会更宏大、更整合、更"全栈"。但 Ptacek 提出了一个反向力量：颗粒度同时也在变小，**变小到一个人一个软件、一个痛点一个软件、用完就扔的程度**。这两股力量一起作用，结果可能是软件生态的"中间层"被掏空——巨大的、像 Salesforce 那样统治一切的平台依然存在，但介于"大产品"和"个人脚本"之间的中型 SaaS（值得几百万 ARR 但养不起 50 人团队的那种），会被两头挤压。

在我自己的中国语境里，这件事还多了一层：**中文软件生态长期被微信/钉钉/飞书"超级 App"吸走了一切个人化的空间**。你不能写一个只为自己用的微信小插件；你不能在飞书里塞自己的 `.emacs`。Ptacek 描述的那种"开发者私人原生小工具的复兴"，在 macOS / Linux / Windows 桌面上是顺理成章的，但要在国内的移动 + IM 主导生态里发生，还需要更底层的开放协议。这反过来也提示了我：**国内开发者对 AI Coding Agent 最高效的用法之一，恰恰是为自己的工作流挤出那些小工具——浏览器扩展、本地 CLI、桌面小程序——而不是去和大厂卷 Agent 平台**。

但这篇文章也不是没有可质疑之处。我至少看到两个值得追问的地方：

1. **Ptacek 几乎没有谈维护成本**。一个由 Claude 生成的 SwiftUI 应用，半年后 macOS 更新一个 SDK，作者还有能力（或耐心）让 Agent 修好它吗？Emacs 的 `.emacs` 之所以能存活几十年，是因为底层非常稳定且作者真懂 elisp。Agent 化的软件如果作者本身不读源码、不懂底层框架，长期来看是一种新的债务。
2. **"想要 prompt 多于想要源码"是一个漂亮的洞察，但它假设了 prompt 是稳定可复现的产物**。在不同模型、不同时间、不同上下文窗口下，同一个 prompt 产出的代码可能完全不同。Prompt-as-truth 这种新型 source-of-truth，需要新的版本管理、新的回放协议——这块基础设施今天几乎不存在。

这两点不否定文章的判断，反而让它指向了更深的工程问题：**Emacsification 是一种文化趋势，但它需要被一整套尚未发明的工程范式来支撑**。

它让我想起两篇可以对照阅读的东西：一个是 [Geoffrey Litt 2023 年的 "Malleable Software"](https://www.inkandswitch.com/essay/malleable-software/) 系列——Ink & Switch 多年来一直在论证个人化软件的价值，但他们的路径是新的协议（local-first、CRDT）；Ptacek 的路径是新的劳动力（Agent）。两条路径正在汇合。另一个是 Paul Graham 那句老话："The future is already here, it's just unevenly distributed."—— Emacs 用户已经在那个未来里活了 40 年，他们只是没等到剩下的人加入。

## 谁应该读这篇文章

1. **独立开发者 / Indie Hacker**：这是关于你的下一波机会窗口的文章。重点读"个人软件的经济学发生了什么"。
2. **企业架构师 / 平台型团队负责人**：思考"我们的内部工具是否还有理由集中开发"——大概率没有，让员工各自 Emacs 化才是更好的设计。
3. **桌面 / 原生 UI 工程师**：长期被 Web 抢饭碗的群体，请认真读最后三段。供给侧约束被打掉之后，原生开发的复兴可能比你想象的早到。
4. **AI 编程工具的产品经理（Cursor / Windsurf / Codex 等）**：你的产品下一阶段的杀手级用例，不是写大型项目，而是"让我五分钟做一个只有我自己用的小玩意"。重点读 "prompts > source code" 那段。
5. **关心开源运动未来的人**：Ptacek 提的"源码不再是 truth"，是一个比所有许可证讨论都更激进的议题。值得作为引子读一读。

## 阅读原文

不要被 9000 字的篇幅骗了——这是一篇会让你在地铁上读完之后还要再翻一遍的文章。强烈建议读英文原文，Ptacek 的语气和段落节奏本身就是论证的一部分（注意他在文章里用 `❦` 这个图案做分隔——很 Ptacek）。

👉 **[The Emacsification of Software — sockpuppet.org](https://sockpuppet.org/blog/2026/05/12/emacsification/)**

读完之后，作为对作者的回应，我推荐你做一件事：**今晚开 Claude / Codex，挑你工作流里那个最小的、烦了你最久的痒点，挤一个只属于你的小工具出来。** 你会比读这篇文章本身学到更多。
