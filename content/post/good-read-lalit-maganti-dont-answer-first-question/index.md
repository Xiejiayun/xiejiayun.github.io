---
title: "【好文共赏】别回答第一个问题：Perfetto 团队的 Lalit Maganti 把\"工程支持\"做成了一门读心术"
description: "Google Perfetto 资深工程师 Lalit Maganti 用一篇 1600 词的随笔，把工具维护者每天都在做的\"用户提问诊断\"提炼成四种结局：你是缺哲学，还是没找到入口，还是真的该改产品。"
date: 2026-05-18
slug: "good-read-lalit-maganti-dont-answer-first-question"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - 工程文化
    - 性能工程
    - Perfetto
    - 平台思维
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
>
> **原文**：[Don't answer the first question](https://lalitm.com/post/dont-answer-the-first-question/) · 作者：Lalit Maganti（Google Perfetto 团队 Senior Staff Engineer）· 发布：2026-05-16 · 阅读时长：约 8 分钟
>
> **多模评分**：Opus 8.7 / Sonnet 8.6 / Gemini 8.5（综合 **8.6 / 10**）
>
> **一句话推荐**：当一个用户问你"怎么把 trace 文件切成多块"的时候，你在那一秒做出的选择，决定了你是一个写工具的程序员，还是一个做平台的工程师。Lalit Maganti 把这个一秒钟摊开来，写了一份只有内部人才写得出的"工具维护者读心术"。

---

## 1. 为什么值得读

Lalit Maganti 不是一个会上 Twitter 喊"AI 杀死了某某"的工程师。他是 Google 内部 Perfetto 项目的 Senior Staff Engineer——Perfetto 就是 Android 上那套你打开开发者选项里"系统追踪"功能背后的工具链，也是几乎所有 Pixel/Google Cloud/Chrome 团队做性能分析时的事实标准。这个项目不需要 marketing，它的用户就是 Google 内部那几百个性能敏感的工程团队，外加一群在 Github 上提 issue 的 Android OEM。

这种"做工具给工程师用"的位置极其特殊：你的用户都是熟练程序员，他们提的问题表面看每一条都"合理"，所以你下意识会去**直接回答**。Lalit 这篇随笔的全部张力，就在于他指出：直接回答，是这个职位上最常见、也最昂贵的错误。

文章本身只有 1600 词左右，但密度极高。他把"用户问一个怪问题"这件事拆成了四种结局：

1. 用户**缺哲学**——他不理解工具的设计意图；
2. 用户**没找到入口**——工具已经能干这事，只是路径被藏起来了；
3. 工具**真该改**——但用户描述不出他真正要的是什么；
4. 还有一个常常被忽略的**第四种**：现在改，是错的，要等。

更难得的是，每一种结局他都给了 Perfetto 里的真实例子：metric 计算的滥用、trace splitting 的隐藏路径、UI 自定义带来的一年技术债、还有他们"忍住一年才做对" 的 trace merge。每一个例子都是只有维护者自己才知道的内部史。

这篇文章的归宿，不是"如何做客户支持"——而是**所有给工程师做基础设施的人，每天工作的精髓**。我把它放在和 [matklad《学习软件架构》](/post/good-read-matklad-learning-software-architecture/)、[Google IDE 编年史](/post/good-read-history-of-ides-at-google/)、[Resident 软件工程的速度与规模](/post/good-read-senior-developer-speed-scale-decoupling/)、[Mercury 把语言学家当 SRE](/post/good-read-haskell-mercury-production-engineering/)同一个抽屉里——它们都在回答同一个问题：**资深工程师每天在做什么，那些做不出来的人看不到？**

## 2. 一个反例：XY problem 远远不够

任何在 Stack Overflow 待过几年的人都听过 XY problem——用户其实想要解 X，但他问的是怎么做 Y。社区的标准做法是：识别出 X，回答 X，礼貌地告诉他 Y 是岔路。

Lalit 第一段就把这条街道给截断了。他说 XY problem 只走了一步：

> 原文：It treats the user's stated question as a puzzle to decode: figure out what they really meant, answer that, move on. I think we can go much further.

XY 把用户的问题当成一个**密码**——破译完了就过，关掉 tab。但 Lalit 的视角是：那个让用户问错问题的**困惑本身**才是金矿。它是产品故障的指纹，是用户心智模型的截图，也是平台演化的种子。

这个视角差异看起来很微妙，但落到一个长期项目上，效果是质变的。XY 思维下，你每天回答 100 个工单，第 101 天还在回答同一类的 100 个工单。Lalit 的思维下，你回答 100 个工单之后，能识别出其中 30 个有同一种困惑模式，于是你要么改文档、要么改 UI、要么承认确实缺一个功能、要么决定**再等等**。

这是一种把"客服"翻译成"产品研究"的能力，而它的前提是你愿意在每一次"奇怪提问"面前先停下来。

## 3. 诊断那一刻：三个内部 checklist

文章里有一段是我反复读了几遍的——Lalit 描述他遇到一个"看起来怪"的请求时，**脑子里跑的三步检查**：

1. 我见过这个吗？见过就快答；没见过就慢下来。
2. 这个问题和我见过的问题比，听起来合理吗？不合理的话，**底下藏着的"正常问题"长什么样**？
3. 它符合工具的形状吗？还是用户在和架构搏斗而不自知？

这三个问题看似平淡，但每一句都是经验。第二条尤其漂亮：维护者脑子里对"这个生态里合理的问题分布"有一张图，遇到落在分布外的样本，他不会先去解它，而是先去算"这个样本来自哪个偏移"。这正是统计学家、Site Reliability 工程师和精神科医生干的事——**先把样本放回它该在的总体里**。

第三条则是建筑学的视角：用户是不是在和工具的形状打架？如果一个 trace 工具的用户拼命想把 trace 切小，那大概率不是"切分功能"缺失，而是他对"trace 该多长"的认知和工具的设计意图脱钩了。

我想起 [Kerkour 写给 Rust 团队的劝退信](/post/good-read-kerkour-limits-of-rust/) 里有一句类似的话：当你看到一群人都在和你的工具搏斗，问题大多数时候不在他们手上。Lalit 这篇文章是把那句话翻译成了**问答场上的肌肉记忆**。

## 4. 第一种结局：用户缺哲学

文章的第一种结局是最常见的——用户根本不知道 Perfetto 是用来做什么的。

Lalit 给的例子很具体：用户发现 Perfetto trace 是"一段时间内系统所有事件的高保真录像"，然后立刻冒出一个想法：那我能不能从 trace 里**算出帧率**？算出内存占用？算出任何指标？

理论上，能。一段足够细的录像里，任何指标都可以重新计算。但 Lalit 用一句话把这个幻想戳穿：

> 原文：traces are expensive to collect and process: you're collecting all the data about the system rather than samply a single number. You're going to waste a lot of resources when instead, a dedicated metric collection system would do the job much more efficiently.

trace 是**全息**的，metric 是**采样**的。当你想知道帧率，你不需要全息——你需要一个一直在跑的、廉价的、专门算帧率的子系统。把 trace 当成 metric 系统来用，就像把 4K 60fps 录像剪辑软件当成秒表来按。

这里有个更深的工程哲学：**工具是有形状的，形状是它的世界观**。Perfetto 的世界观是"事件级、按需触发、深度调试"。如果你的问题是"持续测量"，那不是 Perfetto 该解的——那是另一个子系统。Lalit 说他工作的很大一部分，**不是教别人怎么用 Perfetto，而是教别人怎么做性能工程本身**：怎么想 startup，怎么想掉帧，怎么想内存和功耗。

这就是"平台型工程师"的真正工作内容——他在用每一次问答传授**性能工程的世界观**，工具只是这个世界观的载体。

## 5. 第二种结局：路径被藏起来了

第二种是最让人愉快的结局：用户问的问题虽然怪，但工具其实早就解决了，只是入口没暴露好。

Lalit 用 trace splitting 这个具体例子贯穿了整篇文章。用户的提问是"怎么把一个大 trace 切成几个文件"，他反问"你为什么要收一个这么长的 trace"。对方答：因为有几个感兴趣的时间窗，想分开看，一是为性能，二是为可视化。

Lalit 的回应是 Perfetto 早就支持"周期性 trace 快照"（periodic trace snapshots）——不是收一段长录像然后切，而是**反复收一小段**。从"长录像然后切"切换到"很多段短录像"，根本不需要 splitting 功能。

> 原文：They're trying to solve a problem they shouldn't be having in the first place.

这一句是整篇文章里我最喜欢的金句。它把"feature request"这个我们工程师每天处理的对象，重新定义成"问题表述"——而问题表述常常已经预设了一个**错误的解空间**。维护者的任务，是把用户从那个错误解空间里救出来。

这也解释了为什么"powerful by design"的工具特别需要这类工程师。Perfetto 这种工具能干的事太多了，新人很难一眼看出"为了我的需求，应该把工具的哪几块组合起来"。维护者就是这个组合的人肉路径规划器——这件事，你能交给 LLM 吗？也许——但前提是 LLM 见过足够多这种"问题表述背后藏着别的解"的案例。我们今天聊的所有 RAG 系统、Agentic 文档站、AI 客服，本质上都在试图自动化 Lalit 这一类直觉，而它们最常败的地方，就是**没学会反问**。

## 6. 第三种结局：产品真的该变了

最难处理的是第三种：用户问了一个新问题，新到不在原有的工具世界观里——这可能意味着工具该长出一块新东西。

Lalit 在这里给了两个对照鲜明的内部案例：

**做错了的那次**：UI 自定义。用户说"我们想改 UI"，Perfetto 团队答应了，让他们直接 hack UI 代码。结果是巨大的技术债——每加一个新功能都要兼顾所有已经存在的 hack，**整个 UI 变得不可扩展**。最后花了一年时间把它重做成一个 plugin API。事后看，用户真正想要的不是"hack UI"，而是"按团队/场景定制 UI，但不影响其他用户"——这个核心需求是用户**自己也说不出来**的。

**做对了的那次**：trace merge。用户一直在问能不能合并多个 trace，Perfetto 团队**抵住压力没做**，给了 workaround，说"以后再看"。直到去年他们终于做了，做得很干净。原因是——他们等了足够长的时间，把这件事的几何形状摸清楚了再下刀。

这两段是这篇文章里最像内部 retrospective 的部分。Lalit 在说一件残酷的事：**对于基础软件，"现在就做"通常是错的**。因为：

- 用户在第一次提需求时往往说不清楚他真正要什么；
- 工具的扩展点设错了，后面每个新功能都要付利息；
- 等到三个不同团队来要同一个东西时，你才看得清这个需求的"本质形状"。

这与 [matklad 的"软件架构的母题是 Conway 定律"](/post/good-read-matklad-learning-software-architecture/) 是同一种思维：先理解组织/用户的需求结构，再选数据/接口的结构。Lalit 把这条原则从架构层下沉到了**单个工单的处理流程**——每一次回应，都是一次微型的架构决策。

## 7. 隐藏的第四种结局：什么都不做

整篇文章最反直觉的部分，是他对"等待"的辩护。

我们这个行业训练我们：speed 是美德，shipping 是工作。但 Lalit 提供了一个反向证据——基础设施层面，**有时候最值钱的工作是按住手不动**。

他在 trace merge 那段用了一个非常克制的措辞：

> 原文：we knew doing it properly was a lot of work and easy to get wrong, so we waited.

"我们知道这事做对了很费工、做错了很容易，所以我们等。" 这一句话浓缩了高级工程师和中级工程师之间的真正分水岭。中级工程师看见 issue 涌进来，本能反应是"那就排进 roadmap"；高级工程师看见 issue 涌进来，本能反应是"我现在做的话，会带来什么样的不可逆代价？"

这种"不动"的勇气，需要两个东西：第一，对工具自身世界观的笃定；第二，对组织短期 KPI 压力的免疫。Lalit 在他另一篇文章 [《Why Senior Engineers Let Bad Projects Fail》](https://lalitm.com/post/why-senior-engineers-let-bad-projects-fail/) 里把第二点写得更直接——有些项目的最佳贡献，是让它失败。这两篇文章合起来读，几乎可以当成"如何在 Google 的 Promo Committee 文化里保留工程审美"的一份私房手册。

## 8. 对 AI 时代意味着什么

我想顺着 Lalit 没明说但呼之欲出的一条线再走一步：他这篇文章，正好踩在"用 LLM 替代工程支持"这条产业趋势的反面。

过去六个月，几乎每家工具厂都在试图把"用户问题"喂给 LLM 去回答——文档站接 RAG、Discord bot 接 Claude、PagerDuty 上挂 agent。这些系统大部分都是在加速"直接回答第一个问题"这件事。LLM 比人快、便宜、不会下班。但它有一个根本短板：它不会**反问**。或者说，它会反问，但它的反问是文本上的，不是判断上的——它没有 Lalit 那张"这个生态里合理问题的分布图"。

更危险的是：LLM 客服会高效地把 Lalit 描述的第一种和第二种困惑**直接消解掉**——用户从此再也不会和真人维护者对话，于是维护者再也看不到第三种结局的种子（产品该变）和第四种结局的耐心（先别变）。

这件事，已经发生了。我之前写过的 [《Turso 关掉了那扇付费的门》](/post/good-read-turso-bug-bounty-ai-slop/) 是同一硬币的另一面——AI 把开源 bug 赏金变成无成本造谣机；现在这一面是，AI 把"困惑驱动的产品演化"变成无信号的快速回答机。两者加起来，是开源工具维护者最害怕的未来：**信号被噪声替代，对话被自动应答替代，演化的种子被礼貌的"已为您解答"埋掉**。

Lalit 没把这层意思写出来，但他每一段都在写一件事——**人和人之间那种慢慢摸索出来的对话，是工具进化的氧气**。如果你打算用 LLM 砍掉这个对话层，请先想清楚你砍掉的是什么。

## 9. 延伸阅读图谱

### 作者其他代表作（5 篇带点评）

| 文章 | 一句话点评 |
|---|---|
| [Why I Ignore The Spotlight as a Staff Engineer](https://lalitm.com/software-engineering-outside-the-spotlight/) | 这篇文章的"母篇"。讲他为什么放弃做"演讲型 staff"，而走"工具维护者"路线。HN 547 票。 |
| [Why Senior Engineers Let Bad Projects Fail](https://lalitm.com/post/why-senior-engineers-let-bad-projects-fail/) | 第四种结局的延伸——高级工程师的核心技能之一是"准确判断哪些项目不该救"。 |
| [Eight years of wanting, three months of building with AI](https://lalitm.com/post/building-syntaqlite-ai/) | 他用 Claude Code 做出了一个想了八年没做的工具（SyntaQLite）。HN 959 票。 |
| [We stopped roadmap work for a week and fixed bugs](https://lalitm.com/fixits-are-good-for-the-soul/) | "Fixit week"如何成为团队心理治疗的工具。 |
| [What Makes a Good Tool for Claude Code](https://lalitm.com/writing-tools-for-claude-code/) | 维护者视角下，给 AI agent 写工具和给人写工具的差异。 |

### 同一主题群（5-10 篇外部对照）

- **Will Larson《Staff Engineer》** —— 这本书几乎是 Lalit 文章的学术版，把"staff engineer 的四种 archetype"分类化。
- **Camille Fournier《The Manager's Path》** —— 反面对照，写"通向管理"的路径。
- **Tanya Reilly《The Staff Engineer's Path》** —— 比 Larson 更新一些，专门讲"做技术领导而不做管理"的人怎么活。
- **Charity Majors 的 honeycomb.io 博客** —— 同样是给工程师做工具的维护者，写过大量 "support as research" 的文章。
- **Hillel Wayne《Are We Really Engineers?》** —— 工程师和"调用工具的人"之间的边界讨论。
- **John Ousterhout《A Philosophy of Software Design》** —— Lalit 文中"工具有形状、形状是世界观"的学术版。
- **Brian Foote, Joseph Yoder《Big Ball of Mud》** —— UI 自定义那段技术债的经典先驱论文。

### 反方观点（2-3 篇）

- 一些极简主义工具开发者（如 djb 风格的 Unix 哲学派）会反对 Lalit "等等再做"的论调——他们的立场是：**永远不要做**。如果用户想要 trace merge，让他写脚本去 merge。
- "Move fast and break things" 派——Meta 早期文化的代表，他们会认为 Lalit 这种"一年才做对"的节奏对消费产品是奢侈品。
- LLM-as-Support 信徒——他们会论证：现代 LLM 的反问能力已经足够，再用人来做支持是浪费。这是直接反对 Lalit 文章的核心前提的观点。

## 10. 编辑延伸思考

我想用三个相互嵌套的观察，把这篇文章在我自己脑子里激活的东西写出来。

**第一层：客服是研究**。Lalit 这篇文章最容易被误读的方向，是把它读成"如何做好客户支持"的鸡汤。它不是。它是一份**用户反馈的信息论**——把"工单"重新定义成"产品演化的最小信号单元"。在这个定义下，工单流不是负债，而是数据流；每一次答复不是 cost，而是**采样**。Perfetto 的 Senior Staff Engineer 把工单当成 streaming sensor data 来处理，这个心智迁移，是基础软件圈的核心 IP。

**第二层：反问是杠杆**。整篇文章其实只教了一件事——**在回答之前先反问**。但这一件事，是高级工程师最难传授给新人的肌肉。新人接到问题，本能反应是"我能不能答得上"，于是答案紧张地往外冒；高级工程师接到问题，本能反应是"这个问题是从哪儿来的"，于是反问先于答案。这个"反问先行"的反射，几乎只能通过看老手做才能学会——这也是为什么开源社区里"老手在 issue 区留几条评论"比"老手提交几个 PR"对新人更有教育价值。

**第三层：等是一种工作**。最后，"按住不做"是这篇文章里被低估的最大主题。在 Promo Committee 文化、在 ARR 增长文化、在 release-train 文化里，"什么都没做"是政治上最难为自己辩护的事。但 Lalit 用了一个一年的技术债故事，把"等"翻译成"为未来的可扩展性买的保险"。这件事配合 [Anton Leicht 的 Andy Warhol 时代终结](/post/good-read-leicht-frontier-ai-access-cutoff/)读会很有意思——后者讲的是 frontier AI 出现后特权用户名单的诞生，前者讲的是工具维护者在那个名单之外，**用"等"保住了下一代基础设施的可扩展性**。两件事看似无关，但都在追问：**当组织内外的速度信号都在催你"做点什么"的时候，你怎么挡得住？**

最后一层，是给我自己写博客的提醒。我每天扫 HN 找好文，本能反应是"哪篇能拿来发"，于是稿子紧张地往外冒。Lalit 这篇文章对我也是一种反问——**这个候选池里我为什么先注意到这一篇？它落在了我对"哪些问题应该有人写"的分布的哪个位置？** 我至少应该在每一次"哪篇好"的回答之前，先做一次这种自检。

## 11. 配套资料导览

本文目录下还有三份配套资料，建议按顺序使用：

- **`concept-cards.md`**：10 张概念卡片，把"用户提问诊断的三步 checklist"、"工具的形状"、"feature request 等待原则"做成可以打印贴墙的卡片。适合工程支持团队周会上一张张过。
- **`glossary.md`**：英中对照术语表，覆盖 Perfetto 生态（trace, snapshot, plugin API）、工程文化（XY problem, staff engineer, fixit）和性能工程基础词。25 条。
- **`mindmap.svg`**：把整篇文章的 4 种结局 + 三步诊断 checklist + 等待原则做成一张深色背景思维导图。
- **`cover.svg`**：本文封面图，深色背景配 Perfetto/反问主题。

## 12. 谁应该读

- **正在带支持团队的 staff/principal 工程师**：这篇文章是给你团队所有新人发的第一份阅读材料。
- **基础设施/开发者工具方向的产品经理**：你需要的不是"用户调研问卷"，而是这篇文章告诉你的"工单流采样"心智。
- **打算用 AI agent 替代客服的创业团队**：在你写下一段 prompt 之前，先想清楚 Lalit 这篇文章里那 1600 个字描述的"反问能力"，你打算怎么塞进 system prompt 里。
- **维护任何超过 3 年的开源项目的 maintainer**：你或许已经在干这件事，但 Lalit 给你提供了一套词汇，让你能向你的 manager/sponsor 解释你每天那些"看起来在闲聊"的 issue 评论到底创造了什么价值。
- **想从"会写代码"升级到"能影响产品"的中级工程师**：这是一份比《Staff Engineer》一书更直接、更短、更工程化的入场券。

---

> 📎 **本文采用 CC BY 4.0 协议引用**：原文作者 Lalit Maganti 的所有引用都已标明"原文："并加 blockquote。全文引用未超过原文 10%。所有图示与代码均为本文作者重写，无原文图片直接复制。
