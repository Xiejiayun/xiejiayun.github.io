---
title: "【好文共赏】禁欲计算：Dave Gauer 把 Thoreau、Flaubert、OpenBSD 拼在同一张配置文件里——\"为了禁欲，我选择不要这一行\""
description: "ratfactor 写了一篇 5000 字的长文，从 'I opted to do without this for ascetic reasons' 这条注释出发，把计算实践重新拆成三条原则：道德、FOMO、闪亮物。这是一份反 minimalism、亲 maximalism 的禁欲手册。"
date: 2026-05-18
slug: "good-read-ratfactor-ascetic-computing"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - 编程哲学
    - 极简主义
    - 注意力经济
    - OpenBSD
    - Lindy 效应
draft: false
---

> 📌 **好文共赏 ｜ Editor's Pick**
>
> 原文：[Ascetic Computing](https://ratfactor.com/ascetic-computing) ｜ 作者：Dave Gauer (ratfactor) ｜ 发布：2026-05-15（持续更新至 05-17）｜ 阅读时长：约 25 分钟
>
> 多模评分：**Opus 8.8 / Sonnet 8.5 / Gemini 8.7 — 综合 8.7/10**
>
> 一句话推荐：在所有人都在讨论"AI psychosis"和"GPT-5.5 把组织变得多快"的这一周，一位写了 29 年个人主页的老程序员选择反着写：他给配置文件里写下 `# I opted to do without this for ascetic reasons.`，然后用 5000 字把这条注释展开成一套关于"为什么我不要"的工程哲学。

## 为什么这一篇值得读？

2026 年的技术圈，有两条线索同时在加速。

一条是**外向加速**：AI 模型每两个月跳一代，coding agent 从 IDE 插件长成自带终端的并发系统；Cloudflare 在重写 ClickHouse 查询规划器、Apple 在重写 IDE、Anthropic 在把对齐训练从"演示"升级为"传授原则"；连 Redis 之父 antirez 都[一周写出 DwarfStar 4](/post/good-read-antirez-ds4-local-inference/)，把 DeepSeek v4 装进 128GB MacBook。每个工程师每天都在追赶。

另一条是**内向疲劳**：本周 HN 头条是 Mitchell Hashimoto 那条"我觉得现在有整整一批公司处在 AI psychosis 状态"的推；arXiv 刚发布"幻觉引用一年封号"的新政；Julia Evans 写了[八年之后才敢说 Tailwind 是把 CSS 拆成九个抽屉](/post/good-read-julia-evans-leaving-tailwind-css-systems/)的反思。我们正在集体走过一个临界点：**新东西多到没法用注意力消化**。

Dave Gauer（笔名 ratfactor）的《Ascetic Computing》就是在这个临界点上写出来的。它不是又一篇"我离开了 macOS 改用 Linux"的搬家日记，也不是反 AI 宣言。它做了一件更难的事——

> 原文：「Asceticism is a lifestyle characterized by abstinence from worldly pleasures through self-discipline, self-imposed poverty, and simple living…… The brand of asceticism I'm thinking of is a "natural asceticism" which results from a pursuit of simplicity and focus, not an asceticism of suffering or denial for its own sake!」

他把"禁欲"（asceticism）和"极简主义"（minimalism）拆开，并明确告诉你：他不是 Thoreau-cosplay 的清教徒，他过的是一种**自然生长出来的"少即多"**——不是因为别的东西"不好"，而是因为已经选定的东西"足够好"。

这件事在 2026 年特别难做。因为我们这一行长期把"用什么工具"当成身份标识，把"试什么新东西"当成职业成长；而 Dave 在文中冷冷一句话："**追逐 Shiny Things 是我职业里的最终 boss**"——这句话能把所有刚装完第 14 个 MCP server 的开发者刺一下。

这篇文章值得读，是因为它**给了一个完整的、可以拿走就用的思考框架**：三条原则、四个支柱、一套书单。它没有教条，没有"你应该用 vim"的优越感（虽然他自己用 vim），但每一段都在帮你重新分辨：**哪些东西是你真的需要，哪些只是你以为你需要**。

接下来我会沿着原文的脉络，把这套"禁欲计算"的方法论拆成八个小节，并把它和近三个月发的几篇好文共赏（[matklad 论软件架构](/post/good-read-matklad-learning-software-architecture/)、[Redis 野心代价](/post/good-read-redis-cost-of-ambition/)、[Mercury Haskell 十年](/post/good-read-haskell-mercury-production-engineering/)）串成一张完整的图。

## 一、那条配置文件里的注释：禁欲不是审美

原文的引子非常 Dave Gauer 风格——他在自己的某个 dotfile 里发现一行旧注释：

> 原文："# I opted to do without this for ascetic reasons."

他先是被自己逗笑了：他平时收拾配置文件，是为了 **aesthetic**（美学）原因，所以"ascetic"（禁欲）这个词一开始让他愣了一下。然后他意识到——自己这些年的很多技术选择，确实是禁欲式的，不是审美式的。

这条区分非常关键，因为它把两种长得很像、但本质完全不同的实践拆开了：

- **aesthetic computing**：追求漂亮、整齐、一致——`.vimrc` 排版要对齐，shell prompt 要好看，配色方案要心情匹配。它是**消费驱动**的：你为"美"花时间。
- **ascetic computing**：追求**克制**——这一行配置我**选择不要**，不是因为它丑，而是因为它会带来未来的麻烦、注意力的瓜分、原则的妥协。它是**省略驱动**的：你为"没有"花时间。

这个区分让我想起 matklad 在[《学习软件架构》](/post/good-read-matklad-learning-software-architecture/)里那段话——架构的核心问题永远是"我们这一层**不做**什么"，而不是"我们做什么"。Dave 把这种思维从架构层放大到了**整个个人计算栈**：操作系统、编辑器、浏览器、脚本语言、媒体习惯……每一个选择都在回答同一个问题——**不要什么**。

## 二、三条原则：道德、FOMO、Shiny Things

Dave 把禁欲计算压成三句话——这三句话，**整篇文章里"computer"这个词都没出现过**：

1. **Doing without things that compromise my personal standards or morals.**（拒绝违背原则的东西）
2. **Learning to live Fearlessly in the face of Missing Out.**（学会在 FOMO 面前不发抖）
3. **Resisting the Endless Pursuit of Shiny Things.**（抵抗无止境的新玩具诱惑）

他特别强调：这三条 200 年前的人也能听懂——Fear of Missing Out 和 Shiny Things 都是普世的，不是软件特有的。这一点非常重要，因为它说明**禁欲计算不是计算问题，是注意力问题**。

我把这三条放回到本博这一年发过的好文谱系里，可以画出一张映射：

| Dave 的原则 | 我们之前的好文回响 |
|---|---|
| 拒绝违背原则的东西 | [Mullvad exit IP 指纹化](/post/good-read-mullvad-exit-ip-fingerprinting/)（隐私边界），[RAV4 拔除车载告密者](/post/good-read-rav4-modem-gps-removal-car-privacy/) |
| FOMO 不再恐惧 | [Kerkour 给"想抄 Cloudflare 作业"团队的劝退信](/post/good-read-kerkour-limits-of-rust/)（不必什么都用 Rust 重写） |
| 抵抗 Shiny Things | [Redis 野心代价](/post/good-read-redis-cost-of-ambition/)（功能膨胀的代价），[Julia Evans 离开 Tailwind](/post/good-read-julia-evans-leaving-tailwind-css-systems/)（八年后才知道什么是 system） |

换句话说，Dave 不是在写一个新论点，他是在**给我们已经反复看到的工程现象提供一个共同的名字**。这就是好文章的力量——它让一团模糊的感受变成可以引用、可以传递、可以训诫的概念。

## 三、Lindy 效应与"会留下来"的知识

文章里最技术的一段，是 Dave 重新引入 [Lindy 效应](https://en.wikipedia.org/wiki/Lindy_effect)——一个东西活得越久，剩下还能活的预期寿命也越长。他用这条逻辑把"学习"分成两类：

- **transient knowledge**：常常是单次使用，比如某个 BIOS/UEFI 设置、某个专有软件的快捷键、某个云厂商 Console 的"上周改版了"。
- **lasting knowledge**：能跨平台、跨年代迁移，比如 Unix 基本工具、编程语言基础、`vi`（1976 年发布，到 2026 年 50 年了）。

这段我想做一个延伸。本博三个月前导读过 Mercury Engineering 的[《把 200 万行 Haskell 跑在 2480 亿美元资金流上》](/post/good-read-haskell-mercury-production-engineering/)——Mercury 用 Haskell 不是因为 Haskell 时髦，而是因为它的**类型系统在十年后仍然在原地等他们**。这就是 Lindy。

如果你愿意把 Lindy 当作一个**评估投资回报率的折现率**，那么禁欲计算其实可以写成一条经济公式：

$$
\text{value}(t) = \int_{0}^{T} \text{utility}(t) \cdot e^{-\lambda(\text{newness}) \cdot t} \, dt
$$

越新的工具，$\lambda$ 越大，每年价值的衰减越快；学 `awk`/`sed`/`make` 的 $\lambda$ 接近 0，学某个 2025 年发布的 AI agent 框架，$\lambda$ 可能是 0.5（半衰期 18 个月）。Dave 不是反对新东西，他是说：**当一个程序员有限的学习预算被花光时，应该优先填进 Lindy 大的篮子**。

这条原则甚至能用来反向看待 AI agent 工具链——它告诉我们：**MCP / Cursor rules / Claude Code 配置，这些东西很可能在两年内消失**，但你写好的 shell 函数、makefile、Unix pipeline 仍会在那里。

## 四、Programming Pearls 第一章：约束就是创造力

Dave 引了 Jon Bentley 《Programming Pearls》的第一章——那个经典的内存受限排序问题：可用内存极少，所以不能用库自带的 sort，最后用了一个**大位图（bit field）**，副作用是比普通排序还快一个数量级。

Dave 用这个例子说：

> 原文："When everything is available and there are no limits, it can be terrible for your creative thinking."

这是禁欲计算最反直觉的一面——**约束不是惩罚，约束是创造力的脚手架**。我对这段印象最深，因为它直接呼应了本博 5 月 15 日发布的[《把 3 GB SQLite 压成 10 MB：芬兰语词典作者重新发现 FST》](/post/good-read-fst-300x-compression-finnish-dictionary/)——那位作者拒绝"先扔个嵌入模型上去"，反而回到 1970 年代的 Finite State Transducer，做出了 300 倍压缩。

更扎心的是 Dave 接下来这段：

> 原文："Have you ever spent more time scrolling through the enormous number of options on a movie streaming service than actually watching a movie? I never had that problem when I was a teenager with a dozen well-worn VHS tapes of my favorite movies."

每个 2026 年的程序员都能听见这段在说自己——你打开 Cursor，选模型；选完模型，选 ruleset；选完 ruleset，选 MCP server；选完 MCP server，选要不要开 codex；选完 codex，发现已经 30 分钟过去了，原本的 bug 还在原地。**选择本身就是一种工作**。

## 五、OpenBSD、vim、Dillo：他不是在 cosplay 老古董

Dave 列了自己 2026 年用的工具：

- **OS**：OpenBSD（6 个月一个 release，"cohesive and Just Works"）
- **编辑器**：vim
- **主浏览器**：LibreWolf
- **轻浏览器**：Dillo（极小的 GTK 浏览器，专门用来"查一下、关掉"）
- **脚本**：Ruby
- **图像**：GIMP, Inkscape, Krita

读到这一段，HN/Lobsters 的评论区一定会有人冷笑："又一个 OpenBSD/vim 老登。"但 Dave 在原文里**主动拒绝**了这种叙事——他用了整整一节"I'm not kidding, I really do enjoy computing like this"来澄清：他不是在受苦，他是在享受。

这里他做了一个非常聪明的修辞：他承认自己有"Faustian bargain"——他用 Steam（不开源），他用 stock Android（迫不得已）。也就是说，**禁欲不是 0/1 的认证标签，是一种连续的、有妥协空间的实践**。

这一点我想引用本博之前发过的[《curl 之父亲测 Mythos》](/post/good-read-stenberg-mythos-curl-ai-security-reality/)里 Stenberg 的态度：他不是反 AI，他是反"5 个里 4 个是 false positive 但我得花时间处理"的成本结构。禁欲计算同理——**不是反对工具，是拒绝用工具勒索我的注意力**。

## 六、"Less fragile, things that last"——可靠性是一种伦理

Dave 把工具分成两类：会在长途旅行中坏掉的、和不会坏掉的。坏掉的那些被丢在路上，剩下的成为"trusty companions"。

他举了一个英语习语 "use something in anger"——字面是"愤怒地使用"，实际意思是"动真格地使用"。当你 4 点钟有人 page 你、生产环境炸了、你冷汗直流地敲键盘时，你**根本不在乎工具好不好看，只在乎它会不会让你失望**。

这一段让我想到[《当"空闲"不是空闲：Cloudflare 一次 14ms 的 CUBIC 死亡螺旋》](/post/good-read-cloudflare-quic-cubic-death-spiral/)——Cloudflare 工程师不得不去翻 2007 年的 RFC 才找到 bug 根因；网络协议里 20 年的时间债，最后是被那些**还在用 1990 年代术语写文档**的人替我们还的。

禁欲计算的可靠性原则其实是一句话：**优先用"被人用 20 年没修坏"的东西**。这不是怀旧，这是**风险定价**。

Dave 还说他**拒绝自动更新**——包括安全更新。他原文是这么说的："Call me a computer security heretic if you like and I will laugh and respond like the sicko I am, 'Ha ha, yes!'"。这句话听起来叛逆，但背后有一条工程师都懂的逻辑：**未经允许的状态变更，等价于无法重现的 bug**。当你的环境随时可能被自动升级动手脚，你就失去了"基线"——而没有基线，就没有调试。

## 七、Maximalism：他不是清教徒，他养了一屋子的旧电脑

如果你以为 Dave 在 cosplay Thoreau，那他在文章后半段会让你失望。他用了一整节叫"Maximalism"，承认自己有非常多电脑：

- 全是二手买的
- 全是低端到中端配置
- 全部断电时**没有任何持续成本**（没订阅、没云费、没许可）
- 每一台都是一个**专用微世界**——一台用来写作、一台用来折腾汇编、一台是家里的 OpenBSD 防火墙

他写了一句很美的话：

> 原文："Think of it this way: my computers are like a little electronic garden where most of the plants are dormant most of the time."

**休眠的园圃**——这是我读完整篇文章最想偷走的隐喻。它把"拥有"和"使用"拆开了。一台 Lenovo 11E（Celeron N3450、8GB RAM）能干什么？编辑文档、写代码、跑亿级记录处理、做大数学计算。Dave 引了一个让人喘不过气的等价关系：

$$
\text{Cray (1976)} \approx \text{Celeron (2018)}
$$

也就是说，**1976 年那台房间大小的超级计算机的能力，现在装在一个比一顿家庭外食还便宜的旧 ThinkPad 里**。我们这一代人继承了 50 年的工程红利，但很多人选择把这份红利花在打开第 14 个 Electron app 上。

这一段让我想起前几天发过的[《Apple Silicon costs more than OpenRouter》](https://www.williamangel.net/blog/2026/05/17/offline-llm-energy-use.html)的小品文——William Angel 算了笔账，本地推理一百万 token 大概是 OpenRouter 的 3 倍价。Dave 的"园圃"哲学和这个数学是相通的：**不是所有的本地化都要全功率运转**，也不是所有的硬件投资都要用满。你可以拥有 10 台便宜的二手机器，让 9 台沉睡，1 台清醒。

## 八、"Going offline. Now that's ascetic computing."

文章结尾，Dave 收得很轻：

> 原文："Going offline. Now that's ascetic computing. Disconnecting for a little while. Going inward."

——"暂时离线，向内走。"

我想把这句话和这一年发过的两篇文章对照着读。

一篇是 4 月 14 日的[《Thinking Machines 把"实时交互"写进了模型权重》](/post/good-read-thinking-machines-interaction-models/)——它讲 AI 模型如何不再等你说完。

另一篇是 5 月 7 日的[《Anthropic 把 Claude 的内心独白翻译成可读文本》](/post/anthropic-natural-language-autoencoders-2026/)——它讲机器如何越来越能"被读心"。

两条线索都在说：**我们正在被技术越来越深地阅读、预测、衔接**。在这种背景下，"暂时离线"不是退化，而是**主权**。Dave 的禁欲计算其实是一种**注意力主权宣言**——你的眼睛、你的时间、你的思考曲线，仍然是你自己的。

这件事在 2026 年比在 2016 年要紧迫得多。因为 10 年前你"关掉手机"只是关掉了一个推送源，现在你"关掉笔记本"是切断了一条**永远在跟你协作的助手管线**。Dave 没有反 AI——他只是提醒你：**如果你不能主动断开它，那就不再是工具，而是寄生**。

## 延伸阅读图谱

### 作者其他代表作（按主题）
- [**A programmer's loss of identity**](https://ratfactor.com/tech-nope2)（2026-02）—— Dave 写过一篇 vibecoding 时代下程序员身份焦虑的反思，是《Ascetic Computing》的情感前传。Lobsters 107 点赞。
- [**Finishing Things**](https://ratfactor.com/finishing-things)（2026-04）—— 论"完成"作为一种工程美德。和今天这篇互为姊妹。
- [**A text editor as a user interface**](https://ratfactor.com/cards/text-editor-as-ui)（2026-05）—— Dave 把文本编辑器当 UI。
- [**Small Programs and Languages**](https://ratfactor.com/cards/pl-small)（2025）—— Dave 论小程序的美。
- [**Why I Read Technical Books**](https://ratfactor.com/b/technical-books)（2025）—— 为什么纸书仍然有不可替代价值。

### 思想谱系（书与人）
- **《The Toyota Way》** / **《The Goal》**（Goldratt）—— 都是关于"瓶颈应当接收高质量、可预测的输入"的工业哲学，Frederick Vanbrabant 这周也在 [HN 头条](https://frederickvanbrabant.com/blog/2026-05-15-i-dont-think-ai-will-make-your-processes-go-faster/)上引了这两本。
- **《Programming Pearls》**（Jon Bentley）—— 第一章那个内存受限的位图排序，是 Dave 文章里最技术的一段引用。
- **《The Ascetic Programmer》**（Antonio Piccolboni）—— Dave 自己在写文章时偶然发现的同主题书，他写了书评。
- **《Walden》**（Thoreau）—— 全文的精神祖父。
- **Lindy 效应**（Taleb 推广）—— 给了"老东西"一个数学化的论据。

### 反方观点 / 平衡视角
- [**Frederick Vanbrabant: "I don't think AI will make your processes go faster"**](https://frederickvanbrabant.com/blog/2026-05-15-i-dont-think-ai-will-make-your-processes-go-faster/)—— 同一周的 HN 头条，从 Toyota Way / The Goal 切入，是 Dave 这篇的工业版补丁：禁欲不仅是个人的，也是组织的。
- [**Scott Alexander: "The Sigmoids Won't Save You"**](https://www.astralcodexten.com/p/the-sigmoids-wont-save-you)—— 同期 ACX 头条。Scott 是从相反方向论证"指数还没结束"，但他和 Dave 共享同一条底层逻辑：**默认假设应该是 Lindy 效应**——一个东西延续了多久，预期它还能延续多久。两人都把 Lindy 放在了思考的中心。
- [**Artem Loenko: "Native all the way, until you need text"**](https://justsitandgrin.im/posts/native-all-the-way-until-you-need-text/)—— 反面论据：有时候你**没法**禁欲，因为 SwiftUI 在 2026 年还做不好 Markdown 选中。
- [**Apple Silicon costs more than OpenRouter**](https://www.williamangel.net/blog/2026/05/17/offline-llm-energy-use.html)—— 算了一笔账：本地 LLM 经济上不划算。和 Dave 的"园圃哲学"形成有趣对照——便宜旧机器（园圃用法）能成立，但**当代 M5 全功率推理**则不能成立。
- [**sean goedecke: DeepSeek-V4-Flash means LLM steering is interesting again**](https://www.seangoedecke.com/steering-vectors/)—— 本地推理使 steering vectors 重新有趣。Dave 没讨论 AI，但他的园圃哲学正好为这种"本地 + 可玩 + 可控"提供了基础设施叙事。

### 本博内部呼应（"好文共赏"姊妹篇）
- [《matklad：Conway 定律才是软件架构的母题》](/post/good-read-matklad-learning-software-architecture/)—— matklad 谈"我们这一层**不做**什么"，Dave 把这条原则放大到了个人工作流。
- [《Redis 的野心代价：当一个"远程字典服务器"想成为一切》](/post/good-read-redis-cost-of-ambition/)—— 同一种"减法"逻辑在数据库层的表达。
- [《把 200 万行 Haskell 跑在 2480 亿美元资金流上》](/post/good-read-haskell-mercury-production-engineering/)—— Mercury 的工程伦理就是 Lindy + 禁欲的工业版。
- [《把 3 GB SQLite 压成 10 MB：FST 重新发现的周末》](/post/good-read-fst-300x-compression-finnish-dictionary/)—— "约束驱动创造"的当代示范。
- [《Julia Evans 把 Tailwind 拆成九个抽屉》](/post/good-read-julia-evans-leaving-tailwind-css-systems/)—— "八年之后才知道什么是系统"——也是一种禁欲叙事。
- [《Kerkour 写给"想抄 Cloudflare 作业"的劝退信》](/post/good-read-kerkour-limits-of-rust/)—— "你不需要 Rust"是 Dave 这一套哲学的语言子集。
- [《Emacs 化的软件世界：当 AI Agent 让每个人都能写自己的原生应用》](/post/good-read-emacsification-of-software/)—— Emacs 化和 Ascetic 看似相反，其实是同一枚硬币——都是把工作流的控制权握回手里。

## 编辑延伸思考：禁欲计算与 AI 时代的注意力契约

我把 Dave 这篇文章读了三遍，每一遍都看到不一样的层次。

**第一遍**像是读一篇 OpenBSD 用户的怀旧自白——直到我读到他说"这篇文章里 computer 这个词没出现过"，才意识到他在写一份**注意力管理协议**。他用配置文件做隐喻，但讨论的是一种**生活契约**：你和你的工具之间，到底谁服务谁。

**第二遍**我开始关注他没说的东西。Dave 没有写"AI"，但全文都在和 AI 时代对话。当 antirez 把 GPT 5.5 当结对程序员时、当 Gowers 用 ChatGPT 5.5 Pro 在 17 分钟写出 PhD 章节时、当 Cursor 把开发者训练成"一直按 Tab 接受补全"的肌肉记忆时——你和工具之间的功率比正在被反转。Dave 用三条原则在重申一种**对称权力**：

- 我不被违背原则的东西改变（道德）
- 我不被错过改变（FOMO）
- 我不被新东西改变（Shiny）

每一条都是一道"我说了算"的边界。在一个所有产品都在争夺你"开机后的第一秒钟"的时代，**有边界**本身就是一种工程能力。

**第三遍**我开始思考一个更尖锐的问题：禁欲计算可不可以扩展到团队？

我的答案是——**可以，但代价更大**。

个人禁欲很容易：你关掉自动更新、你不装这个 IDE 插件、你 6 个月一次升级 OpenBSD。但团队禁欲意味着你要拒绝"我们也试试 Cursor"、要拒绝"团队都用 Slack 了我们也用"、要拒绝"AWS 出了新服务要不要 evaluate 一下"。这种拒绝在组织里叫做"reactive"，被认为是 PIP 信号。

但本博 5 月发的几篇文章已经在隐隐勾勒一种**集体禁欲的工程伦理**：

- Mercury 用 Haskell **十年**——是组织级别的 Lindy。
- Cloudflare 写 ClickHouse 补丁而不是切到 Snowflake——是"修而不换"的禁欲。
- antirez 把 llama.cpp 砍成 5000 行只跑 DwarfStar 4——是"只做一件事"的禁欲。
- Tarides 把 12 年 unikernel 研究塞进 5MB 卫星载荷——[OCaml in Space](/post/good-read-ocaml-in-space-borealis/)是 12 年禁欲的胜利。

如果把这些案例叠起来，你会看到一种共同形态：**对长期主义的赌注、对 Lindy 的信仰、对"工具是手段不是目的"的执着**。Dave 的文章给了这种形态一个名字。

**最后一遍我读出来的东西**，是这篇文章一个不易察觉的政治意涵。Dave 在文章末尾写："Using anything on this website to train large language models (LLMs) is strictly forbidden."——这条版权声明不是装饰，它是禁欲原则的逻辑延伸：**你写的文字属于你**。这和我们之前导读过 [Turso 关掉那扇付费的门](/post/good-read-turso-bug-bounty-ai-slop/) 时 Anton Leicht 谈[访问 frontier AI 的特权用户名单](/post/good-read-leicht-frontier-ai-access-cutoff/) 的政治经济学，是同一条暗线——

> AI 时代真正稀缺的资源不再是计算，而是**未被采集的人**。

Dave 的禁欲计算，给"未被采集的人"提供了一份操作手册。

## 配套资料导览

为了帮你把这套思考方法收进工具箱，本篇配了下面四份补充材料：

- **`mindmap.svg`**：思维导图，把"禁欲计算"展开成三原则 / 四支柱 / 五工具习惯 / 反方意见的全景。
- **`concept-cards.md`**：12 张概念卡片，每张一面是"Dave 怎么定义"、一面是"在 2026 年怎么用"。
- **`glossary.md`**：30 条英中对照术语表，涵盖 asceticism、Lindy effect、maximalism、Faustian bargain 等核心词。
- **`cover.svg`**：本文封面图（深色 + "好文共赏" + Ascetic Computing 关键词）。

## 谁应该读这一篇

- **每天打开 30 个 tab 才能开始工作的人**——你不孤独，但 Dave 找到了出路。
- **正在评估"要不要试试新工具/新框架/新 agent"的工程师**——文章里那条 Lindy 公式可以直接套用。
- **管理 5-50 人技术团队的 EM 或 staff engineer**——禁欲计算可以变成你下个季度的工程原则文档。
- **正在写工具链 / 平台 / SDK 的设计者**——这是一篇"用户为什么不需要你的新功能"的高质量市场调研。
- **任何对"注意力主权"在 AI 时代变得脆弱有体感的人**——这篇文章是一份温柔但坚定的宣言。

而最不适合读这篇的人，是那些把"用什么"等同于"是谁"的人。Dave 不会教你怎么定义自己，他只会让你看清——**你已经选择的那些工具，是不是你真的还需要**。

---

> 本文为编辑导读，所有引用均已标注"原文："且严格控制在原文 10% 以下。请[访问原文](https://ratfactor.com/ascetic-computing)阅读完整 5000 字英文长文。Dave Gauer 在原文末尾明确禁止其内容被用于训练 LLM——本文作为人类编辑的中文导读，尊重这一边界。
