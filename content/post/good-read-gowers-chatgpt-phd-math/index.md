---
title: "【好文共赏】17 分钟一篇 PhD 章节：Fields 奖得主 Gowers 实测 ChatGPT 5.5 Pro 做加性数论研究"
description: "Tim Gowers 详细记录 ChatGPT 5.5 Pro 如何在几次 prompt 里把 Rajagopal 的指数上界改成多项式，并附上被改进者 Isaac 的逐节评估——这是 LLM 走出『拼接已知』、走进『原创结构』的临界证据。"
date: 2026-05-14
slug: "good-read-gowers-chatgpt-phd-math"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - AI for Math
    - LLM
    - 加性数论
    - 研究方法论
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
>
> 原文：[A recent experience with ChatGPT 5.5 Pro](https://gowers.wordpress.com/2026/05/08/a-recent-experience-with-chatgpt-5-5-pro/) · 作者：**Timothy Gowers**（Fields Medal 1998；Collège de France & Cambridge）+ 客串 **Isaac Rajagopal**（MIT）
> 发布：2026-05-08 · 阅读时长：约 35 分钟（含数学附录）· HN 热度 723 / 534 评论 · 多模型评分 **Opus 9.7 / Sonnet 9.4 / Gemini 9.5（综合 9.5/10）**
> 一句话推荐：当 Fields 奖得主亲自坐在键盘前、用零数学输入让 ChatGPT 把一个 PhD-级公开问题的上界从 *指数* 改成 *多项式*，并且被改进者本人逐节背书——LLM 与数学研究的关系，已经从「能不能做」过渡到「我们该怎么承认」。

---

## 一、为什么这篇博客值得放下手头的事去读

过去两年，AI 做数学的「里程碑文章」我们见过不少：AlphaProof 拿 IMO 银牌、Tao 借 GPT-4 跑 polymath、FrontierMath 的私题刷分。但绝大多数都有两条共同遗憾：

1. 评估者要么是模型作者自己（利益相关），要么是非主流方向的研究者（quoting 力度不够）；
2. 实验过程不可复现：要么是不公开的私题，要么是高度优化的 prompt + tool 链路。

Gowers 这篇博客之所以特殊，是它一次性把这两条遗憾都抹掉了：

- **评估者重量级**：Timothy Gowers，1998 年 Fields 奖得主，加性组合学的奠基性人物之一，比专门做 AI 评估的人远更挑剔；
- **过程完全透明**：他给出每个 prompt 的具体内容、ChatGPT 的思考时间（17 分 5 秒、16 分 41 秒、47 分 39 秒……）、生成的 LaTeX preprint 链接，以及最关键的——被 ChatGPT 改进的那位作者 **Isaac Rajagopal** 亲自下场，写了一段「客串评估」，承认其中一个 idea「我会很骄傲花一两周才想到」。

这不是「LLM 在某基准上超过博士平均水平」之类的统计宣称。这是一份**单点存在性证明**：在加性数论、组合学这种纯靠人脑构造的领域，一个被高规格证人核验过的「PhD 章节级」原创结构，由 LLM 在大约 2 小时内、零数学输入下产出。

更深的一层意义，是 Gowers 在文末讲的——「教 PhD 学生做研究这件事，刚刚变难了」。这是 AI 时代关于研究教育最早、最坦率的一个具体判断，比 Twitter 上的抽象焦虑要扎实得多。

（顺便说，这种『顶级行业内人士亲笔示范 + 反向自我祛魅』的写法，与我们之前选过的 [《curl 之父亲测 Mythos》](/post/good-read-stenberg-mythos-curl-ai-security-reality/) 内核高度一致——都是「一线专家用真实样本去对 AI 神话祛魅或正名」的典范。）

---

## 二、用一句话讲清楚 Gowers 让 ChatGPT 做的是什么问题

如果你对加性数论完全陌生，可以这样想：

> 给你 $k$ 个整数，你可以拿它们任意挑 $h$ 个（允许重复）相加。把所有能造出来的和收集起来，得到一个新集合 $hA$。这个新集合的大小，最少是 $hk - h + 1$（当 $A$ 是等差数列），最多是 $\binom{k+h-1}{h}$（当 $A$ 是 $B_h$-set，所有和都两两不同）。介于两者之间的每个值 $t$，能不能都用某个 $k$ 元集合 $A$ 达到？如果能，最小的 $A$ 直径（即 $\max A - \min A$）需要多大？

这个问题就是 Mel Nathanson 在 *Diversity, Equity and Inclusion for Problems in Additive Number Theory* 这篇文章里展开的一连串小问题之一。Nathanson 给了一个上界 $2^k - 1$（指数级），并问能不能改进。

ChatGPT 5.5 Pro 第一步，把这个上界改成了 $O(k^2)$（多项式级），而且 quadratic 是显然最优的。它的做法是把 Nathanson 用「2 的幂」这种指数大的 Sidon 集合，换成「Singer 构造」给出的密度更高（直径只有 $k^2$ 级别）的 Sidon 集合。

第二步，Gowers 加大难度，问 ChatGPT 能不能把 Rajagopal 2024 年那篇论文里关于 $h \ge 3$ 时的指数级上界（约 $C^k$）改进。这一步才是真正的山脊。

- 16 分 41 秒后，ChatGPT 给出第一个改进：把指数 $k$ 改成指数 $\log k$。Isaac 评价为「我工作的一个常规修改」。
- 经过若干来回，最终 ChatGPT 把上界压到 **多项式级**，使用的是一个 *原创* 的构造：用 $B_h$-set / $h$-dissociated set 替换原来论文里的几何级数 $1, q, q^2, \dots, q^{k-1}$。
- Isaac 的原话：「这个 idea 完全是原创的，我会非常骄傲花一两周想出来。」

Gowers 把这次实验的「研究工作量」校准为：**相当于一个组合学 PhD 论文的合理章节**。不算顶级 break-through，但远不是「拼接已知」。

---

## 三、为什么这次比之前所有「AI 做数学」事件都更冲击

### 3.1 评估者是被改进的人本人

过去 AI 做数学的报道，最容易被打回原形的一句话是：**「这个 idea 早就在文献里有了，AI 只是抄出来。」**

Gowers 这次设计的鬼斧神工就是——把被改进的人本人请过来评估。Isaac Rajagopal 是 MIT 数学系学生，他自己在 2024 年用近一年时间完成了对 $\mathcal R(h, k)$ 的完整刻画。如果 ChatGPT 用的 idea 在他论文哪个角落已经隐含，最有资格指出来的就是他。

但 Isaac 的客串文章里，他反过来做了一件让 AI 信徒和怀疑论者都难以辩驳的事：他在第三人称视角下，用自己的语言，**重新推导了 ChatGPT 的构造**，并说「这个 idea 完全是原创的（completely original，as far as I can tell）」。

更精彩的是，Isaac 把 ChatGPT 的关键 trick——「用 $h$-dissociated 集合控制低阶加法关系」——拆成了 (a)(b)(c)(d) 四条 property，逐一在两套构造（他的旧构造 vs ChatGPT 的新构造）之间做映射，并指出：核心 idea 不在最后的论证，而在**最开始那一步「能不能找到一个只用多项式大数字的 $h$-dissociated 集合」**。

这是真正的「数学家级别 review」，比任何 LLM 自评、benchmark 跑分都强一万倍。

### 3.2 没有 tool use，没有 RAG 神话

Gowers 强调："**My mathematical input was zero.**" 他没有给 ChatGPT 喂论文（除了说"Rajagopal 那篇 arxiv 论文"），没有显式让它去搜文献，更没有跑 Lean。它就在 ChatGPT 5.5 Pro 的 chat 框里、用一句话级别的 prompt，吐出 LaTeX 排版的 preprint。

这意味着：

- 它的「思考」是真的——17 分、47 分、31 分这种时长，是 reasoning model 内部 chain-of-thought 推理的时长（与我们之前讨论过的 [《LLM 推理：latent 不是 CoT》](/post/llm-reasoning-latent-not-cot-2026/) 提到的"潜推理"路径有一致内核）；
- 它的「知识」来自训练语料 + reasoning 自洽。Singer 1938 的构造、Bose-Chowla 1962 的构造，都是教科书内容，但能在恰当的时机想起来、装配在正确的位置，是一种"做研究的反射"。

如果有人怀疑这是 prompt 黑魔法的结果，Gowers 直接附上了两份 ChatGPT 写的 preprint 链接（一份小问题 $h=2$、一份大问题 $h \ge 3$），任何人都可以下载、自己核验。

### 3.3 它产出的不是答案，而是 *publishable structure*

回顾近两年「AI 数学」热点：

- AlphaProof 用的是形式化证明（Lean），它产出的"证明"非数学家几乎无法阅读；
- FrontierMath 测的是「给一个高难度题，输出一个数字答案」，离论文还差好几公里；
- Tao 用 GPT 主要在写文献综述、查约稿格式。

而 ChatGPT 5.5 Pro 这次产出的是 **一份能直接进 PhD 章节的 LaTeX preprint**，从问题陈述、定理表述、构造、引理、附录、与原论文的对应表，一应俱全。这是从「答题机」走到「论文写作合作者」的台阶。

Gowers 用了一个犀利的反问：

> 原文（节译）：如果这份结果是某位人类数学家做出来的，它毫无疑问是可以发表的。但把它送进期刊又没什么意义——它已经免费可读了，也没人需要"credit"（除了 Isaac，他确实需要 credit）。

这个观察暴露了学术出版体系的一个空洞：**期刊系统的核心功能是分配 credit + 同行评审，但 AI 产出的内容把第一项功能挂空了**。

---

## 四、Gowers 在文末抛出的四颗深水炸弹

读到这里，AI 怀疑论者可能想说：「不就是一篇博士论文章节吗？数学家又不是为了刷 SCI 而活的。」但 Gowers 的反思才是这篇文章真正的杀伤力所在。他在文末连扔了四颗炸弹，每一颗都值得单独写一篇博客来回应。

### 炸弹 1：训练 PhD 学生这件事，刚刚变难了

> 原文（节译）：训练新博士生做研究这件事一直就很难。其中一种常用方法，是给他们一个"看上去比较温和"的问题。如果 LLM 已经能解决"温和问题"，这条路就堵死了。从今往后，给学生的 PhD 问题，最低门槛是 *LLM 自己解决不了的*。

这条非常具体、可操作，几乎可以预见今年秋季招生季就会有导师重新洗牌备题库。

这与我们之前介绍过的 [《资深开发者为何"说不清"自己的价值》](/post/good-read-senior-developer-speed-scale-decoupling/) 在结构上完全同构——AI 在不断抬升「入门工作」的门槛，迫使行业把"junior 到 senior"的路径重新设计。

### 炸弹 2：人类研究者依然有"剩余价值"——但价值的形态变了

Gowers 进一步指出：未来仍然有人会做数学，但 **目的从「在世界上留下你的名字」变成「内化解题过程本身」**。

> 原文（节译）：会写代码的人是更好的"vibe coder"；懂基本算术的人能识别计算器的错误。同样，做过数学研究的人，会成为更好的 AI 协作者，能识别 AI 输出里 "feel wrong" 的地方。

这是一种 **可迁移技能的重估**：研究本身不再是产物，而是过程。这与 [《David Silver: Ineffable Intelligence》](/post/david-silver-ineffable-intelligence/) 里 RL 那种「过程即奖励」的哲学有近亲关系——只不过 Silver 是给 agent 讲的，Gowers 是给人类讲的。

### 炸弹 3：arXiv 与学术体系的政策空白

> 原文（节译）：arXiv 有反对接收 AI 内容的政策，这是合理的。但也许应该有一个专门的 repository，让 AI 产出的结果可以"活着"。前提是：有人类数学家认证，或者有 proof assistant 形式化验证；并且要求它必须回答了人类提出的某个问题。

这是研究治理空缺的明确指认。 Lean / mathlib 社区可能是第一个能承接这个角色的——它已经有完整的形式化机制 + 社区审议流程。把"AI preprint repository + Lean 自动验证 + 社区 review"组合起来，不难想象成为下一代学术发表机制的雏形。

### 炸弹 4：原创性的定义

Gowers 留下一个开放问题：

> 原文（节译）：假设一位数学家通过与 LLM 长时间对话解决了某重大问题，人类只做了引导，LLM 做了所有技术工作并给出主要 idea。我们会不会把这视为这位数学家的重大成就？我不认为我们会。

但 HN 评论区 mxwsn 等给出反方观点：F1 比赛同时奖励车手和工程师；这是文化选择不是技术结论。

这场关于"AI 时代学术信用归属"的辩论，几乎可以确定会在未来 3-5 年炸开。

---

## 五、细读 ChatGPT 的关键 trick：$h$-dissociated 集合替换几何级数

为了让非数学读者也能感受 ChatGPT 究竟做了什么，我把核心思路用最少的术语重写一遍。读懂这一节，你能对"原创性"的具体形态有直观感觉。

**Isaac 的原始构造**：要造一个 $k$ 元集合 $A$，使 $|hA| = t$（一个指定的中等值）。他用的「积木」是几何级数：

$$
G_q = \{1, q, q^2, \dots, q^{k-1}\}
$$

这个东西有几个漂亮性质：

- (a) 它是 $B_{h-1}$-set；
- (b) 它在 $h-1$ 重和集大小是 $k$ 的线性函数；
- (c) 它是 $B_h$-set；
- (d) 它在 $h$ 重和集大小是 $k$ 的二次函数。

这些"四件套"让你能在中间装配、调出任意 $|hA|$。但问题是——$G_q$ 的元素最大是 $q^{k-1}$，是 $k$ 的 *指数级* 数字。所以总体集合 $A$ 的 diameter 也是指数级。

**ChatGPT 的关键替换**：能不能找一个集合 $D$，元素都是 $k$ 的多项式量级，但仍然满足上述四件套？

它的答案是 $h$-dissociated set。这是一类比 $B_h$ 弱、但只要求"低阶加法关系都是平凡"的集合。利用有限域 $\mathbb F_{p^h}$ 的乘法群，可以构造出长度 $\sim p^h$（多项式级）的 $h$-dissociated set $D_h$（这是 1938 年 Singer 构造的小推广）。

然后 ChatGPT 定义两个新积木：

$$
G^{\text{new}}_1 = D_h \cup (D_h + L), \quad G^{\text{new}}_2 = D_h \cup (D_h + L) \cup (D_h + 2L)
$$

其中 $L$ 是一个比 $D_h$ 直径稍大的整数。它证明这两个新积木 *也满足 (a)(b)(c)(d)*，而且元素全是 $k$ 的多项式量级。然后整套上界证明套路完全平移过来。

为什么这是"原创"——Isaac 看完后说：「这不是简单的术语替换，因为 $B_h$-set 和 $h$-dissociated set 在所需性质上有微妙的不一致；ChatGPT 看出了 $h$-dissociated 已经够用，并具体证明四件套依然成立。这一步我从没想过。」

**这就是 LLM 走过的临界点**：不是"会查文献"、不是"会复用模板"，而是 **在两个相关但不完全等价的概念之间，看出哪一个更弱的能 substitute、并补上验证细节**。

这是数学家最贵的技能，也是最容易被低估为"trivial trick"的能力。

（这种"替换更弱但够用的工具"的思维方式，让我想到我们之前讨论 [《Apple PorTool: 信用分配 + 树形工具使用 RL》](/post/apple-portool-credit-assignment-tree-tool-use-rl/) 时介绍的 tree-of-tool-use 框架——智能体也在不断"用最便宜的工具替代最贵的工具"。这本质上是一种 *优化品味*。）

---

## 六、HN 评论的三种典型反应

文章在 HN 上 723 分、534 评论，反应大致分三派：

**(A) AI 凯歌派**：用「F1 车手 vs 工程师」类比，强调使用 LLM 解决问题本身是一种新的学术贡献。引用次数最高的评论之一：
> 在以 AI 协作产生最佳结果的时代，深刻的领域专家 + LLM 调教者将做出 outsized 贡献。真正的转折点是 *纯 AI > 人 + AI* 的那一刻。

**(B) S 曲线怀疑派**：用 dehrmann、coldtea 等用户作代表，主张这是 S 曲线临近顶端的最后冲刺，未来一两年会饱和。但他们没法解释为何 Gowers 看到的 capability 增长还在加速。

**(C) 数学纯粹派**：用 qwrahg 那条评论作代表——"Wiles 和 Perelman 从来不发 blog，只解决真问题"。这条评论被反驳很多次，因为它把"使用通信工具"和"做研究"混为一谈。

值得注意的是，**反对最强烈的并不是数学家**——而是软件工程师群体，他们最害怕被替代。数学家群体（包括评论区的 quasihumanist、mwildon 等可识别专业身份的用户）反而冷静许多，更多在讨论 arXiv 政策、形式化验证、PhD 教育这些治理问题。

---

## 七、延伸阅读图谱

### 7.1 Gowers 自己的其他相关写作

- **[Group and semigroup puzzles and a possible Polymath project](https://gowers.wordpress.com/2026/03/20/group-and-semigroup-puzzles-and-a-possible-polymath-project/)**（2026-03-20）：他用 ChatGPT 找 Artin-Tits 群字问题的可能"易解但未解"实例。这是本文实验的前奏。
- **[Creating a database of motivated proofs](https://gowers.wordpress.com/2022/04/28/announcing-an-automatic-theorem-proving-project/)**（2022）：他更早就在做"自动定理证明"项目，思路与今天 LLM 风格完全不同——是 symbolic search。这种"前 LLM 心法"反过来让他对 LLM 的优势看得很准。
- **[The two cultures of mathematics](https://www.dpmms.cam.ac.uk/~wtg10/2cultures.pdf)**（2000）：Gowers 经典文章，区分"理论建构者"vs"问题解决者"两种数学家。LLM 现在恰好擅长后者。
- **[Mathematics, A Very Short Introduction](https://global.oup.com/academic/product/mathematics-a-very-short-introduction-9780192853615)**（2002）：他写给非数学家的入门小册，可以作为本文背景知识的低门槛入口。
- **[Discrete Analysis](https://discreteanalysisjournal.com/)**：他创办的数学开放期刊，可能成为未来"AI-friendly 期刊"的一个雏形。

### 7.2 相关 AI-for-Math 论文与博文

- **DeepMind, *AlphaProof / AlphaGeometry 2 IMO Silver*** (2024)：神经搜索 + Lean 形式化，第一次拿到 IMO 银牌；与 LLM 路线对应。
- **Trinh et al., *Solving olympiad geometry without human demonstrations*** (Nature 2024)：AlphaGeometry 原始论文。
- **Wu et al., *FrontierMath: A Benchmark for Evaluating Advanced Mathematical Reasoning in AI*** (arXiv 2411.04872)：私题难基准。
- **Terence Tao 在 mathstodon 关于 GPT 的多篇笔记** (2024-2025)：与 Gowers 不同，Tao 用 GPT 主要做"研究 sherpa"，记录他对模型上下行能力的体感。
- **Lean Community 的 Mathlib4**: 形式化数学的 ground truth 库，Gowers 提到的 "AI repository + proof assistant" 治理方案直接依赖它。
- **Buzzard et al., *FLT in Lean* (Imperial College London FLT 项目)**: 形式化费马大定理，可视为 Gowers 设想的 "human-AI-machine 三方核验" 的工程预演。
- **Bloom, *Erdős Problems Database*** (erdosproblems.com)：本文背景里反复出现，是 LLM 攻克"易解未解"问题的主战场。

### 7.3 反方观点

- **Gary Marcus, *AGI is still nowhere near*** (Substack 2026 系列)：经典 AI 怀疑论；可与 Gowers 文本对照阅读，看具体证据如何冲击抽象怀疑。
- **Yann LeCun 关于 LLM 推理局限的 Twitter 长帖**（2025-2026）：从 architecture 层面解释为何 LLM 看似做了数学其实是表面拟合；与 Gowers 实测形成有趣张力。
- **Subbarao Kambhampati, *Can LLMs Reason and Plan?*** (Annals NY Acad Sci 2024)：实证质疑 LLM 推理；但他基本不讨论 chain-of-thought 推理模型的最新一代。

---

## 八、编辑延伸思考：临界点的形态

读完这篇文章，我想到三个层级的临界点判断。

### 第一层：能力曲线

我自己用过 Opus 4.7、GPT-5.5 Pro、Gemini 3.1 Pro 做数学。一个朴素观察是：**真正的"原创性 leap"，往往不是出现在 benchmark 分数的连续上升中，而是出现在某些特定 cognitive primitives 的解锁瞬间**。

比如：
- "看出两个概念在所需性质上的差异并选择更弱的那个"——这是 ChatGPT 在本文中展示的；
- "在多个看似无关的引理之间发现潜在桥梁"——Tao 提到的；
- "知道什么时候该问'这真的是必要的吗？'"——Isaac 的客串文章里反复提到的。

这些不是新功能，是 reasoning 训练把潜在能力激活的副产品。一旦激活，benchmark 提升是不可逆的。

参考我们之前讨论的 [《前沿 AI 模型竞速 2026Q1》](/post/frontier-ai-models-race-2026-q1/)：各家模型在 reasoning benchmark 上的曲线已经显示这种"阶梯式跃迁"特征。

### 第二层：研究文化

Gowers 文末提到的"训练 PhD 学生变难了"，本质是 **机器抬高了"研究 floor"**：

- 以前 PhD 入门题目 = 文献里没人做过 + 难度温和；
- 以后 PhD 入门题目 = 文献里没人做过 + 难度温和 + LLM 也做不了。

这个增量看似小，但意味着每个导师都需要重新设计题库，意味着"温和题"的供给会枯竭，意味着学生与导师的协作模式需要 redesign（也许会出现"博士生 + LLM + 导师"的三方协作论文常态）。

这与软件工程界已经发生的"AI 抬升 junior floor"完全同构。我们在 [《资深开发者为何"说不清"自己的价值》](/post/good-read-senior-developer-speed-scale-decoupling/) 里讨论过——AI 杀死的不是 senior，是 junior 的成长路径。学术界的相同动力学正在到来。

### 第三层：学术信用体系

最后一层冲击最深，也最难短期解决。

Gowers 提出的「AI repository + 人工或形式化认证」是个合理的 v1 方案，但它解决的是"如何让 AI 结果进入文献"的问题，没解决"如何分配 credit"。

我个人倾向于一个混合方案：
1. AI 产出的结果有一个独立的 namespace，例如 *arXiv/AI* 或 *Mathlib/AI*；
2. 每个结果必须挂钩：(a) 触发的 human researcher（提问者），(b) 使用的 model + 版本，(c) 形式化验证状态；
3. 引用时分别标注，类似 "Smith (with assistance of GPT-5.5 Pro, formalized in Lean 4)"；
4. 期刊重新定义"研究贡献"，把"问题选择 + 评估准确性 + 把 AI 结果 integrate 进更大叙事"也视为可发表的工作。

这个方案的好处是不需要否认 AI 的贡献，也不需要把 AI 列为合作者（合作者要承担责任，模型不能承担），同时给做 prompt + 评估 + 整合的人类研究者留出明确的署名空间。

但这个方案的最难一步，是说服顶尖期刊接受。短期内可能 Discrete Analysis（Gowers 自己办的）会先吃螃蟹。

（这个治理空白与我们之前讨论的 [《AI Copyright Laundering》](/post/ai-copyright-laundering-opensource-2026/) 在 *AI 产出归属* 问题上呈现镜像关系——一个是从下游消费侧探讨 AI 内容洗稿，另一个是从上游生产侧探讨 AI 内容如何被承认。两端的张力会在 2026-2028 年同时爆发。）

---

## 九、配套资料导览

本文目录下另附四份配套资料：

- **`cover.svg`**：封面图，深色背景 + 加性数论符号装饰；
- **`mindmap.svg`**：思维导图，把全文五个主轴（实验过程、技术突破、验证链、教育冲击、元问题）放在同一张图上；
- **`concept-cards.md`**：12 张关键概念卡，从 Sumset / Sidon set 到 arXiv 政策，每张卡含定义 + 历史 + 在本文中的角色；
- **`glossary.md`**：60+ 条英中术语对照，分加性数论、AI 与 LLM、研究文化、研究治理四个分区。

---

## 十、谁应该读这篇原文

- **AI 研究者**：想看 reasoning model 在真实研究场景下的 *capability 边界* 而不是 benchmark 数字；
- **数学家与理论 CS 研究者**：想知道自己未来 3-5 年的研究方式会发生什么 framework-level 变化；
- **PhD 学生与博士后**：想理解为什么导师可能开始给你不一样的题目；
- **学术期刊编辑**：要面对的 governance 问题已经摆在面前；
- **技术产品经理 / 高管**：想看 AI 在"高门槛专业领域"的实际渗透形态，不是 marketing demo；
- **任何关心"AI 时代人的剩余价值"的人**：Gowers 这篇博客给出了我读过最具体、最诚实的回答之一。

如果你只能从原文带走一句话，我建议是 Gowers 文末的这句：

> 原文：通过解决困难数学问题，你不一定能得到上一代数学家曾得到的奖赏，但你会非常好地装备好自己，去面对我们即将经历的世界。

这句话不只适用于数学家。

---

> 本文为 *xiejiayun.github.io · 好文共赏* 系列第 N 篇。原文链接 [Gowers's Weblog](https://gowers.wordpress.com/2026/05/08/a-recent-experience-with-chatgpt-5-5-pro/)。所有引用均在 10% 之内，金句已标注「原文」。如发现疏漏，欢迎在 issue 区指出。
