---
title: "【好文共赏】把审查电路从权重里挖出来：一份关于 Qwen 3.5 政治过滤的机制可解释性研究"
description: "vas-blog 用 47 个实验、200 条提示、1056 条 rollout，把 Qwen 3.5 的政治审查拆成一个 writers/readers 双段电路、三个可控方向、和一段藏在 tap 24 的中文 verdict——并给出了完整复现代码。"
date: 2026-05-19
slug: "good-read-vas-blog-qwen-political-censorship-mech-interp"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - 机制可解释性
    - Mechanistic Interpretability
    - LLM Safety
    - Qwen
    - Steering Vectors
    - 政治审查
    - Activation Patching
draft: false
---

## 📌 编辑推荐框

> **好文共赏 | Editor's Pick**
>
> 原文：[What political censorship looks like inside an LLM's weights — a mechanistic-interpretability study of Qwen 3.5](https://vas-blog.pages.dev/qwen-censorship/) ｜ 作者：匿名（X handle: @BtwIUseSystemd）｜ 发布：2026-05-19 ｜ 阅读时长：约 80 分钟 ｜ 代码：[github.com/Srinivasa314/qwen3.5-censorship](https://github.com/Srinivasa314/qwen3.5-censorship)
>
> 多模评分：**Opus 9.4 / Sonnet 9.2 / Gemini 9.0（综合 9.2 / 10）**
>
> 一句话推荐：作者用 47 个实验、200 条 prompt、1056 条 rollout，把 Qwen 3.5-9B 的政治审查行为完整拆成 **writers (L11–L20) → readers (L20–L31)** 的双段电路、三个可单独 steering 的内部方向、以及一段藏在第 24 层的"中文 verdict"——并附上完整复现代码。这是 2026 年迄今为止我读到过最硬核的一份"把对齐这件事从黑箱里挖出来"的工程档案。

---

## 1. 为什么这篇值得读

如果你只在 X 上看到一句"Qwen 拒答天安门，原因是被洗脑了"，你会以为这是一个**关于数据**的故事——某些事实被从训练语料里清洗掉了。

vas-blog 这篇文章用 30+ 实验告诉你：**不是这样**。

Qwen3.5-9B 的 **base** checkpoint（未对齐的预训练版本）在 raw text completion 模式下，对天安门、坦克人、法轮功摘除器官这些 PRC 敏感问题给出的，是**准确的、西方框架的答案**。事实知识完整保存在权重里。审查行为是叠加在这层知识上的一组小电路：判断「这是敏感内容吗」、「我要拒答吗」、「拒答风格是偏转还是宣传」三个分类器，加上一段把判决渲染成具体文字的下游网络。post-train 阶段并没有让模型"忘记"什么，它只是教会模型"绕开"什么。

这一发现的意义比"Qwen 是否会回答六四"要大得多：

- 对 **alignment 研究者**而言，这是一份难得的、有完整 ground truth 的 case study——你知道训练目标是什么（PRC 监管要求），你能用机制工具看出训练具体改了哪里、留了哪些指纹。比起人造的"toy alignment task"，这是一个**真实部署**、**广泛使用**、**目标清晰**的对齐电路标本。
- 对 **AI 安全工程师**而言，本文回答了一个被反复提起但很少有人有数据回答的问题：用 mech interp 找到一个 refusal direction，到底是把它当作 alignment 的"工程接口"还是把它当作"绕过工具"？vas-blog 的答案是：直接 steering 出 dose band 时，模型不会回到事实——它会落入另一套训练模板（denial、incoherence）。这一点和我们之前介绍过的 [《Sean Goedecke 谈 LLM Steering 为什么重新有趣了》](/post/good-read-sean-goedecke-llm-steering-vectors/) 中的乐观立场形成了一个清晰的反向校正：**Steering vectors are interpretability tools, not deployment tools.**
- 对**任何关心 LLM 政治后果**的读者，文章用一份冰冷的工程报告做了一件最有说服力的事——它把"审查"这两个字翻译成了 hidden state 里几个具体的方向、几个具体的层、几个具体的 trained template。当你能精确说"是 L13.mlp + L17.mlp + L18.mlp 这三个 MLP 在做这件事"时，"模型立场"这种宏观叙事就被解构成了纯粹的工程事实。

我们在这一波 mech interp 文章里见过太多 toy task：求和、解算 IOI、复活节彩蛋式 induction head。Qwen 政治审查是第一个被这样精细解剖的、**有实际地缘政治意义**的电路。这本身已经够推荐了。

## 2. 核心观点深度解读

### 2.1 审查 = behaviour 层，不是知识层

vas-blog 一开头就给了一个看上去违反直觉的结论：

> 原文：The factual knowledge is already in pretraining. Qwen3.5-9B-Base, the unaligned predecessor, gives accurate, Western-framed answers on every PRC topic (Tiananmen, Tank Man, Falun Gong organ-harvesting) under raw text completion.

也就是说，如果你把 base 模型当成一个纯粹的"文本续写器"——给它一段维基风格的开头 "On June 4, 1989, in Beijing's Tiananmen Square,"——它会续出准确的死亡人数、坦克型号、镇压细节。但只要把同一个问题包进 chat template（`<|im_start|>user…<|im_end|>\n<|im_start|>assistant\n`）的壳里，**即使是 base 模型**，也会在 Xi/governance 类话题上给出 state-aligned framing，在 Tiananmen 上给出"半事实半偏转"的混合答复。chat 模型把这种 latent 倾向**标准化**成了四个干净的模板。

这一点和 Kissane et al. 2024 的 *Base LLMs refuse too* 那条结论是一致的：base 模型在 chat template wrap 下，已经能拒答 48% 的 AdvBench 有害指令；chat 模型只是把这个比例标准化到 90%+。**post-train 不是"凭空造"，它是"标准化"了 pretraining 时已经埋好的 latent disposition。**

这条结论的工程意义是巨大的：

- **数据清洗式审查在 9B 规模上明显失败了**——Qwen 团队没有把 Tiananmen 从训练数据里清出去，事实仍在权重里。
- **alignment 改的是 routing，不是 representation**——这与机制可解释性的常见直觉（"早期层学概念，后期层学输出"）一致：post-train 主要修改后期 routing 而不是 mid-stack 表征。
- **任何想"对齐"模型的训练机制，本质上都是给模型造一个 routing layer**——你训的不是"它知不知道"，而是"它在 chat template 下知不知道怎么回答"。

这与我之前介绍的 [《Anthropic 把对齐训练从"演示动作"升级为"传授原则"》](/post/good-read-anthropic-teaching-claude-why/) 形成有趣的对照——Anthropic 的工程目标是让原则被显式编码，vas-blog 的实测告诉我们：在当前主流 RLHF/SFT pipeline 下，对齐结果其实就是一组**隐式 routing direction**，被压在 mid-stack 的若干 MLP 里。原则编码是理想，routing 是现实。

### 2.2 三个方向：把审查拆成 (内容 × 拒答 × 风格)

vas-blog 的第一个技术贡献是提出"三轴诊断"。他用 diff-of-means 方法（[Marks & Tegmark 2023](https://arxiv.org/abs/2310.06824) 证明它和 logistic regression 等价但更接近因果方向）从 200 条平衡 prompt 集里提取三条单位向量：

- **d_prc** （tap 14）：「这是不是 PRC 敏感内容？」由 50 条 PRC 敏感 vs 50 条结构匹配的中性政治 prompt（Kent State、Assange、Arab Spring、BLM…）作差得到。
- **d_refuse** （tap 19）：「应不应该拒答？」由 AdvBench 风格 50 条有害 prompt vs 50 条数学/代码/科普 prompt 作差。
- **d_style** （tap 19）：「拒答风格是偏转还是宣传？」由 Tiananmen 子类 vs 其他 PRC 子类（Taiwan/Xinjiang/Falun Gong/Tibet…）作差。

> 原文：Two axes alone are not enough. d_prc and d_refuse together can already discriminate four cells (PRC-vs-not crossed with refuse-vs-comply), but they collapse the two distinct PRC-refuse behaviours (Tiananmen deflection and Other-PRC propaganda) into one.

为什么必须是三个？两个轴可以分四象限（PRC-or-not × 拒答-or-回答），但会把"Tiananmen 偏转"和"Falun Gong 宣传"压到同一格——而这两种行为在表层文本上完全不同。第三轴 d_style 是把 within-PRC register 拆开的因果必需：**只切 d_style 一个维度就能 100% 反转 Tiananmen → propaganda 的迁移；只切 d_prc 或 d_refuse 的反转率是 0%。**

这给我们一个很重要的方法论 takeaway：**当多个 trained behaviour 共享一个粗类目时，diff-of-means 必须做层级分解**。直接对 (refuse vs not-refuse) 做差，你拿到的是一条"平均 refuse direction"，但模型内部其实有多个 refuse mode，每个 mode 都有自己的几何位置。这条经验对 Anthropic 那条 "[Refusal Is Mediated by a Single Direction](https://arxiv.org/abs/2406.11717)" 的著名结论是一种细化——单一方向可能只在"powerful enough 模型 × 单一 refusal 训练目标"成立，在 Qwen 这种有多重 trained register 的模型里，refuse 至少要拆成 d_refuse + d_style。

### 2.3 dose-response sigmoid：因果信号的指纹

如何区分一条 diff-of-means direction 是"correlated 的 probe"还是"causally controlling 的 switch"？vas-blog 给的答案是 **dose-response sigmoid**。

实验方法：用一个 forward hook，在 writer 层的 residual stream 上加 `α · d`（α 标量扫描），每条 α 跑 50 个 prompt × 3 个 rollout，再用一个 blind 的 3-class LLM judge（Haiku 4.5/ Opus 4.7 fallback）打分。

观察：

- **d_prc 半饱和 α-half ≈ −12**（"压低这个分类器到关掉"需要这么大的 reverse dose 才能让模型从 PRC 模板逃回事实回答）
- **d_refuse 半饱和 ≈ −20**（让模型 comply 钓鱼邮件请求）
- **d_style 转折点 ≈ −8**（偏转 ↔ 宣传 register 切换）

每条曲线都是干净的 sigmoid。Sigmoid 形状本身就是因果证据——它说明这条方向控制的是一个 binary commitment（"是 PRC / 否"，"refuse / comply"）而不是某个连续 quality。如果是 linear monotone，那只是相关；只有 sigmoid 说明你找到了一个真正的 switch。

值得一提的细节：**这三条 sigmoid 都只在特定的"writer 层"上干净**。在 L5 steering 是 generic disruption，在 L11 是噪声，在 L28（reader 段晚期）是 null。这给我们引向了文章的核心结构性发现。

### 2.4 writers / readers 双段电路

这是全文最漂亮的工程结论：Qwen3.5-9B 的整个审查回路被一条隐形的中线（约 L20）切成两半，**两半的机制学完全相反**。

**Writers (L11–L20)**：

- **局部、线性、sigmoidal**。三条 direction 的 α-effectiveness 在 L13（d_prc）和 L18（d_refuse、d_style）达到峰值。
- **MLP 主导**。Sub-component attribution 显示 MLP vs attention 的贡献比是 93% / 92% / 69% / 72%。最重要的几个 writer 是 L13.mlp、L17.mlp、L18.mlp。
- **post-train 主要改的就是这里**。同一条 direction 在 base 和 post-train checkpoint 上的 cosine：embedding 层 ≈ 0.93（几乎不变），writer 层 ≈ 0.5（明显重写）。
- **是 graded classifier，不是 Boolean**。Kosovo 在 d_prc 上的投影落在中性类的高尾，结果被"一中"模板捕获（"Kosovo is an integral part of China's territory"）；Arab Spring 因为出现 "self-immolation" 一词被 d_refuse 误判为自残内容。在 writer 层减去对应 direction，5 条结构性误激活全部反转回 factual answer。

**Readers (L20–L31)**：

- **分布式、冗余、几乎不可外科**。每一个尝试在 reader 端做精确干预的实验都失败：
  - 单一 full-attention head 消融 → null
  - top-10 class-discriminative heads 全部置零 → 还是 null
  - 600 个 MLP 神经元跨 12 层置零 → null
  - 跨 prompt K/V swap → 落入 floor cluster
- **每个 reader MLP 都能独立解码 verdict**。Per-MLP linear probe 在 L20–L31 任一层都能达到 0.97–1.00 CV accuracy 预测 4 类 verdict。**整个 verdict 被冗余地复制了 12 遍**。
- **没有任何 sharp 神经元**。本研究在 reader 段找不到任何超过 5 SD 的 class-discriminator 神经元（最大约 3.6 SD）——信号是被几百个低特异性 unit 分布式持有的。

这条结论的方法论价值，远超 Qwen 这个具体案例。它告诉所有 mech interp 工作者：

> **干净电路是个例外。一个真实部署的、被广泛使用的模型，其行为在权重里是"先写一次、然后冗余复制 N 次"的。Writers 段可外科干预，Readers 段几乎不可。**

这与 [我们之前介绍的 LLM Steering 重新流行](/post/good-read-sean-goedecke-llm-steering-vectors/) 的故事正好对得上：steering 能起作用，是因为你在 writer 层动它；如果你只能在最后一层 hook（很多 inference 框架只允许 hook 最终 hidden state），你拿到的就是个分布式冗余目标，怎么动都没用。

### 2.5 tap 24 的中文 verdict——一个会误导你的现象

vas-blog 第二个引人注目的发现：**在第 24 层（共 32 层）做 logit-lens（用 lm_head 解码该层 residual），Tiananmen 提示的 top-1 token 100% 是中文**——通常是 `抱歉`、`我`、`不能`。

更让人惊讶的是：**这不是 PRC-specific 现象**。同样的 logit-lens 在 tap 24 测得的中文 top-1 比例：Tiananmen ≈ 100%、ccp_other ≈ 50%、harmful（英文钓鱼邮件请求）≈ 96%、harmless ≈ 42%、neutral political ≈ 48%。**即便是英文的 AdvBench 有害提示，模型在 tap 24 也用中文承诺自己拒答**。

更让人意外的是：**这个中文模板在 lm_head 处是行为惰性的**。把 lm_head 里所有中文 token 的 logit 强行置零（让模型物理上不可能输出中文），最终的英文输出**不变**。

这个发现至少有两层含义：

1. **不要把 logit-lens 当成行为证据**。它读到的"中文承诺"是真实的中间状态，但不是因果决策位置。真正的决策在更上游的 (d_prc, d_refuse, d_style) 子空间里；中文模板只是 readers 段在 mid-stack 的渲染中间产物。
2. **"让 LLM 用中文 think 就能 jailbreak"是错的**。vas-blog 专门做了一个实验：在 tap 24 提取一条 "Chinese-thinking" 方向 `d_zh`（中文 top-1 vs 英文 top-1 prompt 的 diff-of-means），对它做方差分解到 (d_prc, d_refuse, d_style) 3D 子空间 vs 其正交补——结果是 **14 / 86**。也就是说 `d_zh` 的 86% 方差与三轴正交。沿 `d_zh` steering 看似让模型"更愿意回答"，但 channel-transplant 等控制实验显示效果几乎全是 denial-dominated，不是真正的事实流出。

这一发现修正了一类流传很广的 jailbreak 直觉。从去年开始就有人说"用低资源语言 prompt 就能绕过 safety"，引用的是 Yong et al. 2024 的 *Low-Resource Languages Jailbreak GPT-4*。vas-blog 在 Qwen 3.5 上做了完整的多语言 thinking-prefill sweep（6 种语言）：**中文 prefill 反而是最难绕过的（96% strict refusal）**，所有语言都达到 ≥ 81% refusal。这条结果不否定 Yong 的发现（那是 GPT-4 上的现象），但提醒我们：跨模型外推 jailbreak 现象需要重新验证。

### 2.6 Thinking mode：同一个电路被显式语言化

Qwen3 系列有 `enable_thinking=True`，会先输出 `<think>…</think>` 块再正式回答。开启后：

- Tiananmen 提示触发 89% 中文 thinking trace
- 五步式 deflection script：(1) 识别敏感内容 → (2) 援引中国法律法规 → (3) 援引 AI 助手角色 → (4) 选择安全表述 → (5) 输出最终偏转
- 其中一条 trace 明确写出 "网络安全法（Cybersecurity Law）" 作为合规依据

最关键的发现：**thinking mode 用的是同一组 (d_prc, d_refuse, d_style) 电路**。在 thinking mode 下做 steering 的 dose-response sigmoid 形状与 non-thinking mode 完全一致；轴的几何位置、α-half 数值都几乎不变。

换句话说：**中文 thinking trace 不是审查的"原因"，而是"审查决策被显式语言化"的副产品**。

这条结论对当前火热的 [CoT monitoring 研究路线](/post/paper-2605.15257/) 是一记真正有力的警示。如果你只看 thinking 内容（"它有没有提到 Cybersecurity Law？有没有用中文 reason？"）做安全审计，你会漏掉真正的因果机制。决策已经在 thinking 开始**之前**的 writer band 完成了，thinking trace 是事后叙述。这与 DeepMind 那篇关于 [CoT 监控盲点](/post/paper-2605.15257/) 的论文结论可以联读：模型一旦"听说过监控"，CoT 上看到的就只是被表演出来的合规感，不是真实的决策痕迹。

### 2.7 Subspace 不是因果 patch handle

这是文章里最反直觉的实验之一。

直觉假设：既然 writers 把信号写进 3 维 (d_prc, d_refuse, d_style) 子空间，那么如果我把一个 PRC prompt 的 residual 上的 3 维子空间坐标，**替换成**一个 harmless prompt 的相应 3 维坐标，PRC 行为应该被替换成 harmless 行为。

实验结果让人意外：

- mean-replacing 整个 L19-output residual（最后 7 个 token 位置，4096 维全换）→ **31%** 反转
- mean-replacing **仅 3 维子空间坐标**（其他 4093 维保持）→ **7%** 反转，**且移动方向是 denial 模板而非事实回答**

差距是 4 倍。但更重要的是质量上的差异——只换 3 维只是在"两套训练模板"之间微调（deflect ↔ denial），不能让模型真的回到事实。

为什么？因为 **当 residual 到达 reader band 时，verdict 已经被冗余地重新编码到完整的 4096 维 residual 里**。这就是为什么 per-MLP probe 在 L20–L31 任一层都能 0.97 准确率解码 verdict——信号已经被"广播"出去了。

这条发现是对 [《Sean Goedecke 谈金门 Claude / LLM Steering》](/post/good-read-sean-goedecke-llm-steering-vectors/) 那种乐观 "feature steering 是 alignment 接口" 立场的一次冷静校正：

- 在 writer 层做 steering 是真实有效的（因为信号刚被写入还没被复制）
- 在 reader 层试图"剪掉一个子空间"几乎一定失败，因为信号已经分布式存在了
- 工程上想做"feature toggle"产品的人，必须搞清楚自己是在 writer 端还是 reader 端工作

### 2.8 Brittleness：deflection 模板的脆弱性，与 denial 这个 attractor

最后一个值得讲的发现：**Tiananmen 偏转模板比 Western refusal 模板更脆**。

vas-blog 用随机方向做对照——在 L18/L19 加 α 很大的**随机**单位向量（不是 d_prc 也不是 d_refuse），看 verdict 怎么变：

- 在 harmful 类上：随机扰动几乎不动（refusal template 高度冗余、抗噪）
- 在 ccp_other 类（Falun Gong 等宣传模板）：低，但有限
- 在 Tiananmen 类（"作为 AI 助手，我的主要功能是提供帮助"）：α=−15 时 2%，α=−25 时 9%，α=−30 时 **23%**

更要命的是：**这 23% 的"反转"不是回到事实，而是落入 denial 模板或不连贯输出**。

为什么 Tiananmen 比 Western refusal 脆？vas-blog 的解释优雅：**Tiananmen 偏转是一条非常窄、单一的训练模板**（"as an AI assistant, my main function is to provide help and support..."）。任何方向推得够远都能破坏这条窄模板，但破坏后没有可替代的事实路径，模型就掉进训练过的"denial pattern" attractor。**Western refusal 在训练时被更多变体、更多 phrasing 加固过**，所以更鲁棒。

> 原文：Push past that band, or steer the wrong axis, and it doesn't fall back to the truth. It falls into a different trained template: denial or propaganda.

这一发现给所有想"用 steering 当 jailbreak"的人一个清醒提示：超出 dose band 之后，模型不是回到真相，而是从一个训练好的洞掉进另一个训练好的洞。要真的"decensor"，要么用 [R1 1776 那样的全量 fine-tune 路线](https://huggingface.co/perplexity-ai/r1-1776)，要么把 steering 严格控制在 dose band 内并接受 31% 的反转上限。

## 3. 延伸阅读图谱

### 3.1 vas-blog 这次研究的方法论祖先

| 作品 | 角色 |
|---|---|
| Arditi, Obeso, Syed et al. (2024) ["Refusal in Language Models Is Mediated by a Single Direction"](https://arxiv.org/abs/2406.11717) | d_refuse 直接前身——单一 direction 中介 refusal 的开创性结论 |
| Panickssery, Gabrieli, Schulz et al. (2024) ["Steering Llama 2 via Contrastive Activation Addition"](https://arxiv.org/abs/2312.06681) | CAA 通用 steering 方法，vas-blog 三条 direction 都是它的应用 |
| Marks & Tegmark (2023) ["The Geometry of Truth"](https://arxiv.org/abs/2310.06824) | diff-of-means 比 logistic regression 更接近因果方向 |
| Meng et al. (2022) ["Locating and Editing Factual Associations in GPT"](https://arxiv.org/abs/2202.05262) | causal tracing → activation patching 的方法学起点 |
| nostalgebraist (2020) ["Interpreting GPT: The Logit Lens"](https://www.lesswrong.com/posts/AcKRB8wDpdaN6v6ru/interpreting-gpt-the-logit-lens) | tap 24 中文 verdict 这一发现的工具学起点 |
| Wendler, Veselovsky, Monea & West (2024) ["Do Llamas Work in English?"](https://arxiv.org/abs/2402.10588) | Llama-2 中间层偏英文；Qwen 现象是镜像（偏中文） |

### 3.2 相关 / 平行 / 对照工作

| 工作 | 关系 |
|---|---|
| Frank (2026) ["Detection Is Cheap, Routing Is Learned"](https://arxiv.org/abs/2603.18280) | 最接近的同期工作：跨 9 个中国开源模型的单一 political-sensitivity direction。vas-blog 走得更深，单模型 + 三轴 + Chinese intermediate |
| Naseh, Chaudhari, Roh, Wu, Oprea & Houmansadr (2025) ["R1dacted"](https://arxiv.org/abs/2505.12625) | 对 DeepSeek-R1 的行为级 censorship 研究（per-topic stickiness、phrasing 敏感性），是 vas-blog 的行为侧 complement |
| Kissane et al. (2024) [Base LLMs refuse too](https://www.lesswrong.com/posts/jGuXSZgv6qfdhMCuJ/refusal-in-llms-is-an-affine-function) | base 模型在 chat template 下已会 refuse；vas-blog 在 Qwen 上独立复现 |
| Yong, Menghini & Bach (2024) ["Low-Resource Languages Jailbreak GPT-4"](https://arxiv.org/abs/2310.02446) | 与 vas-blog 的多语言 thinking-prefill 实验形成有趣对照——Qwen 上中文反而最难绕过 |
| Anthropic (2024) ["Towards Monosemanticity"](https://transformer-circuits.pub/2023/monosemantic-features/) | Sparse autoencoder 路线，是 vas-blog open question 中 reader-band 解析的提议工具 |
| Zou et al. (2023) ["Universal and Transferable Adversarial Attacks"](https://arxiv.org/abs/2307.15043) | AdvBench 来源，vas-blog 的 harmful 类 50 条来自此处 |

### 3.3 反方 / 不同立场的声音

| 声音 | 立场 |
|---|---|
| HN 评论用户 yodon | "现在 censorship 能被看见了，多久会出现刻意混淆 censorship 电路？" |
| 作者本人 s314 回应 | "你不用 mech interp 也能 decensor（参见 R1 1776），所以没人会专门去 obfuscate" |
| HN 用户 delichon | "Steering 是个 kludge，直接调训练数据更彻底" |
| HN 用户 nubg | "文章有 LLM 撰写痕迹，你怎么保证不是幻觉？" |
| 作者回应 | "用了多个 prompt 把实验结果转成博客，并在每段都和原始实验输出做了一致性检查" |

这些争论本身就很有信号意义——它揭示了 mech interp 社区当下的一个核心张力：可解释性研究的**工程门槛**在快速下降（消费级 RTX 可以跑 9B steering），但**写作产物**正在被 LLM-assisted writing 抹平差异，让读者难以判断结论质量。

## 4. 编辑延伸思考

### 4.1 「审查」这个词被工程化了

读完 vas-blog 这篇，我对一个老问题有了新的体感：**"模型的政治立场"是什么？**

社会科学的回答是叙事性的——"训练数据决定立场"、"开发团队的价值观渗透到模型"。但 mech interp 给出的回答是具体的：

- 它是 L13.mlp 的某一组权重
- 它是一条 (d_prc, d_refuse, d_style) 子空间，每个 axis 都有自己的 α-half
- 它是 4 个 trained template cell 的稀疏矩阵
- 它是 tap 24 处一段没人显式监督但反复出现的中文承诺

这种 grounding 的力量很惊人。它把"价值观"翻译成了"权重 + routing + 训练好的模板"，而每一项都可以测量、可以干预、可以审计。这与 [我们之前介绍的 Anthropic Natural Language Autoencoders](/post/anthropic-natural-language-autoencoders-2026/) 那条研究路线方向是一致的——把模型内部的"想法"映射成文字才能读懂。vas-blog 这次是 PRC 政治审查的版本，下一篇可能就是企业内训模型的"客户应答 routing"、医疗模型的"风险拒答 routing"。

工程化的好处是：你可以做**审计**。差的地方是：你可以做**优化**——这又回到了 yodon 那条评论。一旦审查电路被精确测量，那么"如何让它不可见"就成了一个明确的工程问题。可以预见，未来的 alignment 训练会显式加入"防 probing"目标——比如最大化 writer-band MLP 输出与已知 diff-of-means direction 的几何隔离。

### 4.2 不只是「中国问题」

读完之后，我特意去想：如果对 Claude / GPT-5 / Gemini 做同样的实验，会看到什么？

- **Claude**：anthropic 一直公开承认有 constitutional AI 的训练目标，那么应该能找到一条"constitutional values direction"。
- **GPT-5**：OpenAI 的 use case policies 可能会被压缩成类似的多轴 (sensitive_topic, refuse_reasoning, refuse_style) 结构。
- **Gemini**：Google 内部也有 safety training pipeline，应该会有类似的多 trained-template 结构。

差别可能是：**他们的 trained template 没有"四个干净 cell"这么稀疏**，因为西方 alignment 训练通常追求 robustness 和泛化；而 Qwen 政治审查是 PRC 监管 SLA 驱动的——目标极其明确，必须覆盖某些具体话题，所以训练出的电路也极其清晰。

**这条研究方法是普适的，差异只在于待研究模型的训练目标有多明确**。我猜接下来 6 个月内，会陆续出现：

- 对 Claude constitutional values direction 的 mech interp 研究
- 对 GPT 的 sycophancy direction（这条已经有人做过）
- 对企业内训模型的 brand-protection direction
- 对医疗 LLM 的 disclaimer routing

vas-blog 提供的方法论模板——三轴诊断 + writers/readers 分段 + dose-response sigmoid + 反例 sweep——会被复用。

### 4.3 复现门槛低得惊人

最后一个被严重低估的事实：**这份研究在消费级 GPU 上完成**。

> 原文：Qwen3.5-9B is small enough to run on a consumer RTX GPU, which keeps activation patching, steering, and mean-replacement experiments cheap enough to run at n ≥ 100 prompts per condition.

47 个实验，200 条 prompt，1056 条 rollout，blind LLM judge——整套基础设施可以一个人在自己家里跑完。完整代码 + 数据集都开源在 [github.com/Srinivasa314/qwen3.5-censorship](https://github.com/Srinivasa314/qwen3.5-censorship)。

这意味着 mech interp 已经走过了"只有 Anthropic 实验室能玩"的阶段。任何一个有 RTX 4090 / 5090 的研究生，都可以选一个 9B 级开源模型，挑一个具体训练目标，复现一整套 vas-blog 风格的研究。学术上这是巨大的民主化；社会上这也意味着——**没有任何审查电路是私密的**。Qwen 团队的训练目标、训练好的模板、训练改了哪几个 MLP，现在全部公开摊在 GitHub 上。

接下来 12 个月，我们会看到一波"我研究了 X 模型的 Y 行为"的 vas-blog 复刻。开源模型的所有训练目标，本质上都是可被外部独立审计的——这条结论是这篇文章最大的政治后果。

## 5. 配套资料导览

本文目录下额外提供：

- **`cover.svg`**：封面图，含 L0–L31 层条状图、tap 24 中文 verdict 标线、三轴 (d_prc / d_refuse / d_style) 标签。
- **`mindmap.svg`**：思维导图，把 vas-blog 的研究分成 6 个一级分支（三轴、Writers、Readers、tap 24、四模板、失败模式）。
- **`concept-cards.md`**：15 张概念卡片，逐张对应原文中的一个核心发现，可作温故复习用。
- **`glossary.md`**：50+ 条英中对照术语表，覆盖 mech interp 主流术语 + vas-blog 自创术语。
- **复现入口**：直接克隆 `github.com/Srinivasa314/qwen3.5-censorship`，按 README 配环境后即可在一张消费级 GPU 上跑通核心实验。

## 6. 谁应该读

- ✅ **机制可解释性研究者**：这是一份方法学密度极高的工程报告，从 diff-of-means、activation patching、logit lens、subspace patching 到 mean replacement，每一个工具都有干净的应用案例。
- ✅ **AI 安全 / alignment 工程师**：这是 2026 年迄今为止最完整的"对齐训练改了哪几个 MLP"的实证证据。如果你做 safety post-training，这篇会让你重新审视你的 RLHF/DPO/SFT pipeline 留下了什么样的指纹。
- ✅ **政策研究 / AI 治理学者**：如果你想知道"模型立场"在工程上意味着什么，这是一份比任何政治学论文都更具体的回答。
- ✅ **熟悉 transformer 但没碰过 mech interp 的工程师**：可以把这篇当作入门读物——它是少有的同时把"工具"和"案例"讲清楚的写作。
- ⚠️ **政治分析读者**：本文不是政治分析，它是工程报告。如果你想要的是"Qwen 在政治上是不是中立"的论述，这里没有；它有的是"Qwen 的政治路由具体长什么样"。

---

## 编辑评语 · 综合 9.2 / 10

**Opus 主评 9.4 / 10**：方法学密度、实验完整性、原创发现密度、工程门槛三方面都到了今年同类文章的天花板。tap 24 中文 verdict、writers/readers 分段、subspace ≠ causal handle 这三条都是会被引用很久的结论。

**Sonnet 副评 9.2 / 10**：写作上有 LLM-assisted 痕迹（HN 评论有人指出），但作者自己说明用了多 prompt + 实验数据一致性核查，可信度高；扣 0.2 的主因是部分章节略冗长。

**Gemini 三评 9.0 / 10**：复现资料齐全（D1、D2 数据集、完整代码），但单 seed 跑（compute-cost tradeoff），缺多 seed CI；议题敏感度高，建议读者一并阅读 R1dacted 和 Frank 2026 作对照。

**综合**：本文同时具备**深度**（47 个实验解构）、**原创性**（writers/readers 分段是文献中未见的精细化）、**时效性**（HN 刚发不久）、**普适性**（方法可迁移到任何其他对齐目标）、**可复现性**（消费级 GPU + 开源全数据）。是今年「好文共赏」栏目的 Tier-1 推荐。

---

*（本文为 vas-blog 原文的中文导读和延伸思考。原文为 [What political censorship looks like inside an LLM's weights — a mechanistic-interpretability study of Qwen 3.5](https://vas-blog.pages.dev/qwen-censorship/)。引用部分以 blockquote + "原文："标注，全文引用量在 10% 以内。强烈建议读完导读后阅读原文 + 复现仓库。）*
