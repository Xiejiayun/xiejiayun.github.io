---
title: "【好文共赏】「指数终将变 S 曲线」：Scott Alexander 把这条 AI 怀疑论金句送进了「Sigmoid 误判名人堂」"
description: "Astral Codex Ten 用三个最经典的预测翻车案例（联合国生育率、WEO 太阳能、METR AI 能力）证明一件事：sigmoid 在数学上必然为真，但在你做预测的那一刻几乎从不为真。最后用 Lindy 律给出黑盒 AI 预测的默认先验——平均还能再涨七年。"
date: 2026-05-19
slug: "good-read-scott-alexander-sigmoids-ai-scaling"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - AI 预测
    - 缩放定律
    - Scott Alexander
    - Astral Codex Ten
    - Lindy 律
    - METR
    - 贝叶斯
    - 趋势外推
draft: false
---

> 📌 **好文共赏 · Editor's Pick**
>
> 📄 原文：[**The Sigmoids Won't Save You**](https://www.astralcodexten.com/p/the-sigmoids-wont-save-you) · Astral Codex Ten
> ✍️ 作者：Scott Alexander · 📅 2026-05-15 · ⏱️ 阅读 ~18 分钟（中英双语原文长文 + 464 条评论）
> 🧪 多模评分：**Opus 9.1 · Sonnet 8.6 · Gemini 8.4 · 综合 8.7 / 10**
> 🪧 一句话推荐：当所有反 AI 加速论者都在掏出"所有指数终将变成 S 曲线"这把万能钥匙时，Scott Alexander 用三场预测翻车，把这把钥匙折弯成了一面照妖镜——并用 Lindy 律给出了一个让对方必须正面应战的默认先验。

---

## 1. 为什么这一篇必须读

过去 36 个月，**「all exponentials eventually become sigmoids」**（所有指数最终都会变成 S 形曲线）这句话，几乎成了一切对 AI 进步速度持怀疑态度者的语义底牌。它的修辞效率高到夸张：

- 它**数学上必然为真**——任何处于有限世界里的实数序列都不可能永远指数增长；
- 它**没有可证伪载荷**——只要你不指定拐点时间，它永远立得住；
- 它**带着「成年人在场」的智识优越感**——好像对面那个画外推直线的人不知道物理学。

Scott Alexander 这篇 5,000 词的短文做了一件几乎没人做过的事：他把这句正确的废话**当作一个具体的预测**来检验。结果非常残酷——在三个最该让 sigmoid 假设成立的领域（流行病学、能源、AI），过去十年的 sigmoid 预测者全军覆没。而且更糟：他们错的方向是同一个——**总是把拐点放在「今天」**。

如果你写过 AI 战略备忘录、为投资人做过 capex 折现、或者在公司内部为「是否要在 2027 年之前 ship 某个 agent 平台」吵过架，这篇文章是 2026 年 5 月你最该读的英文专栏。它给"不知道未来怎么走"的人提供了一个**可以辩护的默认先验**——而这正是大多数 AI 战略讨论里最稀缺的东西。

这一篇的价值还有一层：它**和我们近期翻译过的 [Anton Leicht《Andy Warhol 时代的终结》](/post/good-read-leicht-frontier-ai-access-cutoff/) 形成了一组镜像**——一边在论证"未来 AI 增长速率会卡在哪里"，一边在论证"如果它真的不卡，社会该怎么分配特权"。两篇配套读，才算把 2026 年 5 月这场 AI 增长辩论的完整光谱看完。

---

## 2. 这篇文章的论证骨架

Scott Alexander 的论证可以浓缩成一张极简流程图：

```
观察：              "所有指数最终都会变 S 形" 听起来很高级
↓
检验：              过去十年里，谁这么预测过？他们对了吗？
↓
三个反例：          UN 生育率、WEO 太阳能装机、METR-Wharton AI 能力
↓
共同病理：          "拐点正好在今天"——这是统计学上的不可能事件
↓
理论补刀：          如果你不知道生成过程，请用 Lindy's Law 作默认先验
↓
辩论换桌：          反方要么给出 explicit 模型，要么承认走 Lindy
```

整条链条最锋利的地方在第 5 步——他没有声称"AI 会继续指数"。他只是**反转举证责任**：当一个论证既无内部模型、也不服从一般性先验，那么它在认识论上是无效的。这是经典的 Bayesian 反击。

---

## 3. 核心观点深度解读

### 3.1 Sigmoid 命题的"必然为真"恰恰是它的命门

Scott 在文章开头就让步：**没有任何过程能永远指数增长**。流行病在群体免疫处收口，飞行器速度在冲压发动机的物理极限处收口（约 3500 km/h），算力增长会撞在功率密度和电网容量上。所以 sigmoid 在**够长的尺度上**总会赢。

> 原文：
> > "All exponentials eventually become sigmoids" ... is technically true. No process can keep growing forever; eventually it hits physical or practical limits.

但他立刻反问：**你确定拐点就在你做分析的此刻吗？** 在物理学里，这种"我恰好处在历史的转折点"的先验是极小的——这是 [Doomsday 论证](https://en.wikipedia.org/wiki/Doomsday_argument)、[Copernican 原理](https://en.wikipedia.org/wiki/Copernican_principle)和 Lindy's Law 共同立足的根基。一个真正的预测者，应当先回答："为什么是现在，而不是十年后？"

这层 framing 也照应了我们之前在 [《Chinchilla 的『出生缺陷』》](/post/paper-2605.08541/) 中讨论的核心问题：**scaling law 拟合误差里那一大部分被归因为"自然波动"的东西，其实根本不是噪声，而是实验设计的可识别性问题**。当你拟合不出系数，你也就没资格谈"指数即将变 sigmoid"——你连"指数"长什么样都没搞清。

### 3.2 名人堂第三名：联合国对生育率的连环误判

UN World Population Prospects 是过去三十年里被打脸最多的旗舰预测项目。它的标准做法是：**当一国生育率显著低于更替水平时，假设这种下降会"逐渐放缓"。**

实际上发生了什么？以韩国为例——

- 2015：UN 预测 2030 年生育率约 1.1
- 2020：UN 预测 2030 年生育率约 1.0
- 2024：实际值已经跌穿 0.7

Scott 引用的图表里，每一条蓝线都是 UN 不同年份的预测，**每一条都在曲线触底前画了一个钩**，而红色实际值像针一样穿过所有钩。

这背后的机理 Scott 没有详细展开，但读者评论里 Louis Dormegnie 的解释非常有力：**金融/政府机构都在做"向均值回归"的预测，因为做出超越共识的预测在政治和职业上是致命的。** 这种「不犯错的努力本身造成系统性犯错」的机制，与 [Mercury 那篇 Haskell 工程实践](/post/good-read-haskell-mercury-production-engineering/) 中讨论的「为可靠性付代价」议题在哲学上同源——只是符号相反：UN 是为了"不被嘲笑"而牺牲准确性；Mercury 则是为了"不让支付出错"而牺牲短期速度。

### 3.3 名人堂第二名：WEO 对太阳能的二十年漏判

如果说生育率预测的政治阻力还可以理解，世界能源组织（WEO）对太阳能装机量的预测则纯粹是一场"复印谬误"——**每年用上一年的"放缓预期"当模板，每年都被现实糊一脸**。

A. E. Hoekstra 整理的对比图里有大约 15 条蓝色 WEO 预测曲线。每一条都从画图当年开始划出一个钩——意思是"接下来太阳能装机会减速"。而实际装机量（黑线）以几乎完美的指数（年均 ~30%）穿过所有这些钩。

这里有一个细节非常深刻：**WEO 不仅没有正确预测，它的错误幅度还在**变大**。** 2014 年的预测和实际差了 ~3 倍；2022 年的预测和实际差了 ~10 倍。当一个预测系统的偏差随时间放大而不收敛，它已经不是"模型误差"，而是"模型完全没有捕捉到生成过程"。

读者评论里有一个机制解释最具说服力：**中国的太阳能产能扩张不在西方预测者的视野里**。他们用 OECD 经验做预测，但全球太阳能装机的"指数引擎"早已搬到了亚洲。这本质上和今天美国分析师预测 OpenAI 收入时漏掉中国推理服务市场是同一类错误——**当生成机制发生地理大转移时，旧地图必然失效**。

### 3.4 名人堂冠军：Wharton 团队对 METR 曲线的预测翻车

这是全文最戏剧化的一节。**METR**（Model Evaluation & Threat Research）从 2024 年开始维护一条指标：「AI 能够独立完成多长时长的任务（按人类工时计）」。这条曲线在 2019-2025 年间近似指数，每 ~7 个月翻倍。

2026 年初，宾夕法尼亚大学 Wharton 商学院的一个团队发表了 [arXiv:2602.04836](https://arxiv.org/abs/2602.04836)，用 sigmoid、Gompertz、log-linear 等多个模型拟合 METR 曲线，**预测 2027 年增长会显著放缓**，并在拟合中明确选择了 sigmoid 作为最优模型。

之后发生了什么？仅仅三个月，Anthropic Mythos Preview 和 OpenAI GPT-5.5 的发布把 METR 指标推上了**比作者画出的 sigmoid 钩远远高出**的位置（@Tenobrus 在 Twitter 上做的更新图里，那个绿色"星"标记的新数据点高高悬在拟合曲线之上）。

Scott 这里点出了一件非常关键的方法论事实：

> 原文：
> > Even though all exponentials eventually become sigmoids, this doesn't necessarily happen at the exact moment you're doing your analysis. Sometimes they stay exponential for much longer than that!

更尴尬的是，Wharton 团队的论文里把 sigmoid 模型选作"best fit"的判据是 **AIC（Akaike Information Criterion）**——但 AIC 是个**样本内**判据，对外推几乎无意义。当一个 sigmoid 的拐点必然落在数据区间内，AIC 就会偏向它——这是预测建模 101 的反例，却被一篇正式发表的论文当主结论。这正好和我们之前讨论 [Chinchilla scaling law 实验设计缺陷](/post/paper-2605.08541/) 时点出的"沿一条射线拟合就无法识别系数"是一种同构的错误：**用拟合优度代替预测效度。**

### 3.5 三个共同病理：拐点总是「正好在今天」

Scott 没有用统计学术语点破，但读者只要把三张图叠在一起，就会看到一个荒谬的共性——**所有 sigmoid 预测的拐点位置全部落在「预测者按下回车键那一刻 ± 1 年」**。

这在概率论上是一个**极小先验**事件。把过去 30 年都算上，sigmoid 真正发生的时刻应该是均匀分布在任意一个时间点。但 UN、WEO、Wharton 三组预测的 sigmoid 拐点叠加起来，95% 都集中在"今天"。

这意味着：**这些预测者并不是在做预测，而是在表达一种偏见**——"这个增长太快了，让我不舒服，所以它一定会很快停下来。" 用统计语言讲，他们在用**先验**冒充**后验**，并把它包装成科学输出。

### 3.6 Lindy's Law：黑盒预测的合法默认先验

文章后半段最有原创性的贡献是把 **Lindy's Law** 作为 AI 预测的默认先验提了出来。Lindy 律的非技术表述很简单：

> 一个东西已经存续了多久，你就可以期待它还能继续存续大致同样的时长。

Scott 用一个几何泉眼的思想实验来推导这个先验：

| 场景 | 已知信息 | 你下小时再爆发的概率 |
|------|----------|-----------------------|
| 标牌写"上次爆发：10 万年前" | 唯一信息 | 接近 0 |
| 标牌写"上次爆发：10 分钟前" | 唯一信息 | 比较高 |

数学上：**当你对一个过程的生成机制一无所知时，它的中位寿命估计 = 它已经活过的时间。** 这正是 Lindy 律的贝叶斯推导。

把它应用到 AI 上：

- "scaling era" 通常被回溯到 2019（GPT-2/3 前夕）；
- 到 2026 年 5 月已经持续约 7 年；
- **如果你对 AI 增长的生成机制一无所知**，那么你预测它再持续 7 年是中位估计；
- 在 Pareto 分布假设下，它在未来 2 年内崩盘的概率约 22%。

这等于说：**怀疑论者如果不想给出 explicit 模型，就必须接受"AI 至少再增长 5-10 年"的默认先验。**

### 3.7 反转举证责任——这才是全文真正的杀招

Scott 在结尾把整篇文章浓缩成两个问题，丢回给 sigmoid 论者：

> 原文：
> > If they're not treating AI as a black box, ... what is their model? ... If they are treating AI as a black box, why isn't their default expectation based on Lindy's Law?

这一招在辩论术上非常致命。它把对方逼进一个二选一：

1. **走 explicit 模型路线**：那么你必须说清你的数据中心增长曲线、算法效率假设、scaling exponent 假设；这正是 Epoch AI、AI Futures Project 等机构已经在做的工作（[「AI Futures Timeline Model」](https://ai-futures.org/)）。Scott 暗示：很多 sigmoid 论者根本没读过这些工作。
2. **走黑盒路线**：那么你必须解释为什么不用 Lindy 律。

这个 dichotomy 不一定无解（比如可以走"分层先验"或"专家先验融合"），但它把对方从"我有更好的直觉"的舒适区里拽出来——必须摆出实物。

### 3.8 一个不在主线但很有意思的细节：technology generations

文章中段藏着一个被很多读者忽略的二阶论点。Scott 谈到飞行器速度记录的 sigmoid 实际上是**多代技术叠加**——螺旋桨、涡轮喷气、冲压。每一代都走完自己的 sigmoid 后被下一代替代，整体看起来仍然像一条不规则指数。

这件事对 AI 的意涵非常微妙：**就算 transformer + 预训练这条路径明天就拐弯**，下一代（[diffusion LLM](/post/good-read-needle-simple-attention-networks/)、[hybrid linear attention](/post/good-read-nvidia-sana-wm-minute-scale-world-model/)、神经符号、世界模型）也可能续上指数。**真正能让 AI 加速停下来的，不是某条 sigmoid，而是 paradigm pipeline 的整体枯竭**——这种事件在过去 60 年的计算机科学史上发生过零次。

---

## 4. 延伸阅读图谱

### 4.1 作者其他代表作（精选 5 篇）

| 文章 | 一句话点评 |
|------|--------------|
| [Meditations on Moloch (2014)](https://slatestarcodex.com/2014/07/30/meditations-on-moloch/) | Scott 写作生涯的奠基之作，定义了"协调失败-多极陷阱"这套语言 |
| [Book Review: AI Futures Project's "AI 2027"](https://www.astralcodexten.com/p/book-review-ai-2027) | 系统性评估当前最被引用的 AI 时间线模型 |
| [Scott Aaronson's Eleven Theses on AI Safety](https://www.astralcodexten.com/p/scott-aaronsons-eleven-theses) | 评述 AI 安全派系的 11 命题划分 |
| [Highlights from the Comments on Sigmoids](https://www.astralcodexten.com/p/highlights-from-the-comments-on-sigmoids) | 同主题续篇，把这篇文章的最佳反驳整理出来 |
| [Forecasting Errors As Bayesian Evidence](https://www.astralcodexten.com/p/forecasting-errors-bayesian) | 把"专家系统性出错"作为信息来更新先验 |

### 4.2 同主题论文 / 博文 5-10 篇

| 资源 | 角度 |
|------|------|
| [AI Futures Timeline Model](https://ai-futures.org/) | Scott 在文中点名引用的 explicit 建模工作 |
| [METR 评估方法学论文](https://metr.org/blog/2024-07-11-time-horizons/) | 提出"任务时长翻倍"指标的原始论文 |
| [Epoch AI - Compute Trends](https://epochai.org/data/notable-ai-models) | 实证 AI 训练算力增长曲线的数据基础 |
| [Pareto, Lindy and the Doomsday Argument](https://en.wikipedia.org/wiki/Lindy_effect) | Lindy 律的数学推导与历史脉络 |
| [Auke Hoekstra 的 IEA 太阳能预测复盘](https://x.com/AukeHoekstra) | WEO 案例的一手数据源 |
| [Wharton sigmoid 论文 arXiv:2602.04836](https://arxiv.org/abs/2602.04836) | Scott 批评的具体目标论文 |
| [Tenobrus 在 X 上的对比图](https://x.com/tenobrus/status/2024954874564407704) | Wharton 预测翻车的实时记录 |
| [《Chinchilla 的『出生缺陷』》](/post/paper-2605.08541/) | 我们之前的 scaling law 实验设计深读 |
| [《当 AI 不再等你说完》](/post/good-read-thinking-machines-interaction-models/) | 模型层面对"时间维度"的另一种突破 |

### 4.3 反方观点 / 必读对照 2-3 篇

| 文章 | 立场 |
|------|------|
| [Gary Marcus - "Deep learning is hitting a wall"](https://garymarcus.substack.com/) | 长期 sigmoid 派代表，Scott 实际上没回应他的强论证（数据耗尽、推理瓶颈） |
| [Sutton - "The Bitter Lesson"](http://incompleteideas.net/IncIdeas/BitterLesson.html) | 经典反 sigmoid 立场：算力堆叠总能赢过精巧手工 |
| [《Andy Warhol 时代的终结》导读](/post/good-read-leicht-frontier-ai-access-cutoff/) | 假设 Scott 错了——AI 真的卡在某个 sigmoid 时，社会该怎么分配特权访问 |

---

## 5. 编辑延伸思考：把这篇文章放进 2026 年 5 月的 AI 辩论语境里

### 5.1 一个隐藏的方法论建议——「区间预测」而非「点预测」

Scott 没有明说，但他给出了一个隐含的最佳实践：**永远不要做 sigmoid 点预测，要做 sigmoid 区间预测**。

具体说，如果你真的相信 sigmoid 拐点存在，你应该输出的不是"2027 年放缓"，而是"未来 5-25 年间有 80% 概率拐点出现，其分布是这样的……"。但几乎所有 sigmoid 论者都拒绝给出这种分布——因为一旦给出，他们就要为分布形状负责。**点预测是不可证伪的修辞工具，区间预测才是认识论责任。**

### 5.2 这场辩论的真正分水岭其实在「paradigm pipeline」

读完文章我们最大的体会是：**当代 AI 增长论战实际上吵的是两件事，但参战者经常分不清**。

- **第一战线（窄）：当前 transformer + pretraining 范式还能涨多久？** 这是 Wharton sigmoid 派的真正命题，也是 Scott 在 METR 案例里实际反驳的命题。
- **第二战线（宽）：综合 AI 能力（跨范式）还能涨多久？** 这是 AI Futures、Epoch 等机构关心的问题，也是 Lindy 律真正应当应用的对象。

把这两件事分开，sigmoid 派的胜率会高很多。比如他们可以承认"AI 综合能力仍然指数"，但说"transformer 范式正在 sigmoid，需要下一代范式接力"。这正好对应我们之前在 [《Needle: 把 Gemini 3.1 蒸馏成 26M 参数》](/post/good-read-needle-simple-attention-networks/) 中观察到的现象——FFN 被砍掉、新架构在某些维度上做大跨度。**范式更替本身就是把单条 sigmoid 升级为多代 sigmoid 链条**——而后者在长期内仍是指数。

### 5.3 为什么这篇文章是 2026 而非 2024 年才能写出来

Scott 这一手 Lindy + 反转举证的论证，**只能在 GPT-5.5、Mythos、DeepSeek V4 都已落地之后才能写**。原因是：

- 在 2024 年，他需要面对"GPT-4 之后明显放缓"的强反方证据；
- 在 2026 年 5 月，所有曾经预测放缓的人已经被 Mythos 们公开打脸；
- 这意味着 Lindy 律的"经验先验"已经从"约 4 年"涨到"约 7 年"——**先验本身在 AI 持续增长中变得更鹰派**。

这是一个非常微妙的反身性现象：**每多过一个不放缓的月份，sigmoid 假说需要解释的概率谜题就重一倍**。Scott 没有强调这点，但他文章的杀伤力一半来自时代的红利。

### 5.4 给中文读者的一点本土化思考

中文圈对 AI 增长的怀疑有一种特殊性：**它经常和"美国 AI 行业过热泡沫"的论断绑定在一起**。从估值/盈利/算力订单的角度看，这种怀疑当然有道理（OpenAI 的现金消耗速度确实是历史级的）。但 Scott 的论证提醒我们一个重要区分——**"AI 公司估值会回调"和"AI 能力会停滞"是完全不同的两件事**。前者是商业周期，可以用经济学预测；后者是技术轨迹，需要走 Lindy 或 explicit 模型。

中文圈很多 AI 怀疑论文章把这两件事混在一起：用 NVIDIA 市值修正来论证 AI 能力 sigmoid。Scott 这篇文章的最大本土化价值，是逼读者把这两条线分开——**算力市场可以 sigmoid，能力曲线未必同步 sigmoid，反之亦然**。

---

## 6. 配套资料导览

本目录下附有以下配套文件，供深读使用：

- 🎨 `cover.svg` — 深色封面图（Sigmoid 误判名人堂三连图示意）
- 🗺 `mindmap.svg` — 全文论证思维导图
- 🃏 `concept-cards.md` — 12 张关键概念卡片（Sigmoid、Lindy 律、AIC、Doomsday 论证、METR、Wharton 预测、Pareto、WEO、UN WPP、Bayesian 反击、Paradigm pipeline、Black-box 先验）
- 📔 `glossary.md` — 英中术语对照表（30 条）

---

## 7. 谁应该读这篇文章

- **战略 / 投研人员**：在 AI 时代任何长期估值模型里，sigmoid vs exponential 是最大的折现假设之一。Scott 这篇文章直接关系到你 DCF 模型的 terminal value。
- **AI 创业者**：你在融资材料里讲的「未来 5 年 AI 能力图」会被各种 sigmoid 派 partner 挑战——这篇文章是反向 talking points 的标准答案。
- **政策研究者**：AI 政策（算力出口管制、能耗审查、安全立法）几乎全部隐含一个 sigmoid/exponential 选择。读完这篇你能识别你的政策提案默认了哪种曲线。
- **科普写作者 / 编辑**：这是怎样把统计学先验、流行病学曲线、能源预测史和 AI 辩论缝在 5,000 词里的一份范本。
- **普通技术读者**：如果你时间紧，**只读三个名人堂案例 + Lindy 律推导那两段**也已经回本。

---

> 📬 我们的「好文共赏」每周三 / 周日精选一篇国外深度技术文章，附作者代表作 + 5-10 篇延伸阅读 + 思维导图与术语表。完整目录见 [/categories/好文共赏](/categories/好文共赏/)。
