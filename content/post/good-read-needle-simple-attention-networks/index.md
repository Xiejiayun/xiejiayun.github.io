---
title: "【好文共赏】Needle：把 Gemini 3.1 蒸馏成 26M 参数的工具调用专家，并顺手把 Transformer 里的 FFN 全砍掉"
description: "Cactus Compute 用 200B token 训练了一个 26M 参数、无 FFN、encoder-decoder 的 Simple Attention Network，在手机上跑出 1200 tok/s 的工具调用速度，并把 Gemini 3.1 Flash-Lite 的能力压进一个能本地微调的小盒子里。"
date: 2026-05-14
slug: "good-read-needle-simple-attention-networks"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 小模型
    - 边缘AI
    - 工具调用
    - 模型架构
    - 知识蒸馏
    - Transformer
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
> 原文：[Needle / Simple Attention Networks](https://github.com/cactus-compute/needle/blob/main/docs/simple_attention_networks.md) | 作者：Henry Ndubuaku 等（Cactus Compute）| 发布：2026-05-12 | 阅读时长：约 25 分钟（含代码）
> 多模评分：Opus 9.3 / Sonnet 9.0 / Gemini 9.1 — 综合 **9.1 / 10**
> 一句话推荐：当一家初创公司花 27 小时 TPU 时间训练出一个能跑赢 FunctionGemma-270M、Qwen-0.6B 的 26M 模型，并顺手证明"Transformer 里那 2/3 的 FFN 参数对外部知识任务可能是浪费的"，整个 on-device AI 路线图都需要重新画一遍。

## 1. 为什么这篇文章值得读

2026 年 5 月 12 日，一个非常容易被错过的 Show HN 出现了：Cactus Compute 在 GitHub 上挂出了一个叫 Needle 的项目，标题里说"把 Gemini 3.1 的工具调用蒸馏成了 26M 参数的模型"。两天之内，它冲到 HN best 第三名（723 分，206 评论），但真正值得停下来读完的不是 README 第一行的数字，而是那份配套的设计文档 `docs/simple_attention_networks.md`。

这份文档大概是 2026 年到目前为止，**少数把"小模型如何为某类任务做架构级特化"讲清楚的工程论文级文本**。它做了三件并非孤立的事：

1. **把 Transformer 里所有的 FFN（也就是常说的 MLP）全部砍掉**——只保留注意力 + 门控残差。模型 d=512、8 个解码器、12 个编码器，总参数 26M，比同任务的 FunctionGemma-270M 小一个数量级。
2. **把 decoder-only 改回 encoder-decoder**——因为工具列表是结构化对象，需要双向编码；并且 cross-attention 的固定大小表示让 KV cache 显著缩小。
3. **用 200B token 预训练 + 2B token 后训（合成数据）+ Muon/AdamW 混合优化器 + INT4 QAT 作为正则**，最终在 16 块 TPU v6e 上 27 小时跑完整个故事——并且权重和数据生成全部 MIT 开源。

如果你只读 README，你会以为这是一篇"我们做了一个能跑在手机上的工具调用模型"的产品博文。但当你点开 `simple_attention_networks.md`，你会发现这是一份对当下"凡是大模型都要先堆 FFN、堆 decoder-only、堆 RLHF"的工业直觉的**正面反驳**——而且每一处反驳都给出了清晰的"为什么"。

这点与我之前写的[《2026 LLM 架构演进全景》](/post/llm-architecture-evolution-2026/)中所讨论的"七年过去，Transformer 架构走向何方"形成了一个有趣的对照——Needle 不是又一种注意力变体，它是直接质疑"FFN 这个组件是否对所有任务都必须存在"，这是更底层的一次重新审视。

更进一步，Needle 不是论文 PPT，它是一个**可以在你 Mac 上 `git clone` 完之后 `needle playground` 就跑起来的小工具**。当一篇技术文章既能讲清"为什么"，又能让你在 10 分钟内复现实验，它的可信度和影响力会指数级放大。

## 2. 谁在做这件事：Cactus 与作者的工程史

Needle 的第一作者 Henry Ndubuaku 是 Cactus Compute 的联合创始人。Cactus 这家公司过去 12 个月最被人记住的项目是 [`cactus`](https://github.com/cactus-compute/cactus)——一个"从零为手机、手表和定制硬件设计的推理引擎"，曾在 2025 年中作为 Show HN 出现过一次（HN id=44524544），主打"在 ARM / NPU 上跑量化大模型，比 llama.cpp 在某些 SoC 上快 2–3 倍"。

也就是说，Needle 不是孤立项目，它是 Cactus 的"自研引擎 + 自研模型"双栈战略的最后一块拼图。这种"我要做手机上的工具调用，所以我先做推理引擎，再做匹配引擎的小模型"的全栈思路，与[《Edge AI 的速度困局：当模型进化快过芯片迭代》](/post/edge-ai-silicon-model-gap/)中的核心观察非常呼应：当大厂还在做 100B 模型时，真正想吃下"手表/眼镜/汽车"这块边缘 AI 市场的玩家，必须自己把模型和运行时一起拧在一起，否则你既挤不进 Apple 的 4GB RAM 预算，也跑不动 Wear OS 的 1GHz 核心。

## 3. 核心观点深度解读

下面这 8 节，是这篇文章对 LLM 工程社区最有冲击的几个论断。我会按"原文怎么说 → 它在挑战什么 → 工程上要付出什么代价"三层来拆。

### 3.1 No FFN：softmax 已经是非线性，FFN 是冗余的

Transformer 的标准 block 结构是 `Attn → FFN → Attn → FFN ...`，FFN 大约占总参数的 2/3。Cactus 团队的判断很直接：

> 原文："Softmax is nonlinear. softmax(QKᵀ/√d)·V is a data-dependent nonlinear mixing operation. For a task that is about routing information (query → tool alignment), attention is the right primitive."

他们的核心论证是：**工具调用本质上是"检索-装配"**——查询 → 工具名匹配 → 参数抽取 → 拼装 JSON。这三件事都是"对齐与拷贝"，不需要 per-position 的特征变换（而那才是 FFN 真正的角色）。

但更深一层的论证是：**FFN 之所以在大模型上看起来不可或缺，是因为大模型需要在权重里"记忆事实"**。当你做闲聊或开放问答，FFN 就是一个可微的 KV store。但当模型可以从输入读到完整的工具签名、参数 schema、上下文文本，它就不需要再把事实压进权重里了。

这背后藏着一个对 RAG / Tool Use / Agentic 模型很关键的推论：

> 原文："The model doesn't need to memorize facts in FFN weights if the facts are provided in the input."

换句话说，**对于"知识在外部、模型只负责对齐与组装"的所有任务，FFN 可能都是部分冗余的**。这与[《LLM 推理的真相：思维链只是表象，潜在状态才是本质》](/post/llm-reasoning-latent-not-cot-2026/)里讨论的"推理在哪里发生"形成了一个有趣的反向命题：如果思考的本质是潜在状态的演化，那么对外部知识依赖的任务里，权重的角色就该被重新评估。

代价是什么？**模型不能脱离外部上下文做开放问答**。Cactus 自己也坦白：Needle 在多轮对话上明显不如 Qwen-0.6B、Granite-350M。这是设计权衡，不是设计 bug。

### 3.2 Encoder-Decoder 复辟：当输入比输出结构化得多

近五年 LLM 工业界几乎全 decoder-only 一统，T5 的 encoder-decoder 路线只有 Flan-T5、UL2 等少数项目坚守。Needle 反向选择 encoder-decoder，原因有三：

1. **双向编码工具列表**：工具签名是结构化 JSON，左到右因果掩码会浪费 50% 的信息。
2. **KV cache 大小固定**：encoder 产出一个定长的上下文向量，cross-attention 每步只看这个向量，而不是 decoder-only 那样每一步都要重新对全输入做自注意力。
3. **多头设计的自然契合**：encoder 输出既喂 decoder，也喂对比检索头（CLIP-style 工具选择），结构干净。

我把这件事称作**"任务结构决定了架构方向"**。Decoder-only 之所以胜出，是因为 GPT-style 的"输入和输出在同一语义平面上"——你说"写一首关于秋天的诗"，模型要把"秋天"的语义复用到生成里。而工具调用是**异质生成**：输入是自然语言+JSON schema，输出是 JSON。两边语义平面不同，cross-attention 就是天然的桥梁。

这点与[《开放权重 LLM 架构演进全景：从 GPT-2 到 Gemma 4 的七年革命》](/post/open-weight-llm-architecture-evolution-2026/)里讨论的"decoder-only 终局是否已到"形成了一个值得回味的对照——大模型未必都得用同一个范式，针对任务做架构特化才是性价比最高的路径。

### 3.3 Gated Residual：没有 FFN 之后，残差必须重设计

砍掉 FFN 之后会出现一个意想不到的问题：标准残差 `x = x + Attn(Norm(x))` 假设每层只是在做"加一个增量"，而真正的"信息重写"由 FFN 完成。FFN 一旦不存在，每层只能 ADD，无法 REWRITE，深层网络的表达能力会被限制。

Needle 的解法是**门控残差**：

```
x = x + sigmoid(gate) * Attn(Norm(x))
```

`gate` 是 per-sublayer 的可学习标量，初始化为 0，这样 `sigmoid(0)=0.5`，训练起步时残差只有半强度。模型可以通过梯度学到"这一层应该完全启用 (gate→∞)"或"这一层基本忽略 (gate→-∞)"。

这是 2026 年小模型设计里非常典型的一种做法：**用极轻量的可学习标量替代昂贵的全 FFN 重写**。同样思路在 [nGPT](https://arxiv.org/abs/2410.01131)、[DeepSeek-V3](https://arxiv.org/abs/2412.19437) 等近期工作里也出现过——它们的共同点是用归一化和门控构造"近恒等初始化"，让深网络在 0 步时不会偏离原始流形。

### 3.4 ZCRMSNorm：从 1+γ 到 γ，零中心化的归一化

标准 RMSNorm 的形式是 `x · γ / RMS(x)`，γ 初始化为 1。ZCRMSNorm 把它改成 `x · (1+γ) / RMS(x)`，γ 初始化为 0。

差别非常小，但**意义明显**：训练开始时，整个归一化层等价于恒等映射（up to RMS scaling），网络初始状态完全由数据驱动，没有任何分量带着学习好的偏置启动。

配合上一节的"gated residual 起点为 0.5"，整个网络在 step 0 是一个"被阻尼的恒等映射 + 阻尼的注意力增量"，**所有学习都从无偏置的起点开始**。这是从 nGPT/DeepSeek-V3 一脉相承的设计哲学：让初始化尽可能干净，让梯度自己决定每个组件的角色。

这种"初始化哲学"在小模型上尤其重要——大模型有足够多的冗余权重去吸收糟糕的初始化，而 26M 模型的每一个参数都必须为最终损失负责。

### 3.5 Muon + AdamW 双优化器：Newton-Schulz 正交化对抗"线性塌缩"

去掉 FFN 之后，整个网络变成"一堆线性投影 + softmax 路由"的堆叠。这有个潜在风险：**线性层级联可能塌缩到一个等效的低秩矩阵**，把 8 层 Transformer 退化成 1 层的表达能力。

Needle 的解法是**双优化器**：

- **Muon**（Newton-Schulz 正交化 SGD）：只作用于 Q/K/V/O 投影，LR=0.02，weight decay=0.01。它通过近似的正交化更新约束权重矩阵保持满秩。
- **AdamW**：作用于其他所有参数（embedding、gates、norms、CLIP head），LR=3e-4。

Muon 是 2024 年底由 [Keller Jordan 等人](https://kellerjordan.github.io/posts/muon/) 提出、在 nanoGPT speedrun 上击败 AdamW 而走红的优化器。它在 Transformer 投影矩阵上的奇异值约束效果，**正好契合 Needle 这种"没有 FFN 来打散线性结构"的架构**。这是 2026 年小模型训练里一个明显的趋势：不再用一把优化器走天下，而是按"参数物理意义"分桶用不同优化器。

### 3.6 INT4 QAT as Regularization：把部署量化作为正则化器

这是整篇文档里最有"工程师哲学"的一节：**Needle 在训练时每 100 步做一次 INT4 假量化前向，用 STE（直通估计器）让梯度回流**。

这个做法本身不新，QAT（Quantization-Aware Training）在视觉模型上用了多年，但 Cactus 把它换了个用法：他们不是为了"训完之后能部署到 INT4"才做 QAT，而是发现**量化噪声本身就是一个非常好的正则化器**——对一个没有 FFN、参数本来就少、容易过拟合的小模型，每 100 步一次的"权重四舍五入"扮演了一个隐式的 weight noise injection。

副产品才是"部署时无 PTQ gap"。这是把"训练时正则化"和"部署时量化"打通成同一件事的一个漂亮例子。

这种"用部署约束反过来改善训练"的思路，与我之前在[《推理工程革命》](/post/inference-engineering-revolution-2026/)里讨论的"推理优化倒推训练设计"形成了一个清晰的呼应——2026 年的小模型工程，已经不再是"训练 + 后量化"的两段式，而是一个端到端的优化目标。

### 3.7 Contrastive Tool Selection Head：CLIP 风格的工具检索

当工具集很大时（想象一下 ChatGPT 的 GPTs 商店、企业 MCP 服务器集群），把所有工具签名塞进一次输入是低效的。Needle 在 encoder 上挂了一个 CLIP 风格的**对比检索头**：

- 架构：encoder output → mean pool → Dense(d/4) → ReLU → Dense(128) → L2 normalize
- 训练：CLIP 对称对比损失，可学习温度 `log_temp`，主 CE loss 的 0.1 倍权重
- 推理：把 query 和每个工具都过 encoder，按余弦相似度排 top-k

最关键的设计是 **encoder 共享**——同一个 12 层 encoder 同时为生成（cross-attention）和检索（对比头）服务。这意味着模型不需要为"检索"训练一个额外的 dual-encoder，省下大量参数和延迟。

这套设计放在 Agentic AI 的大图景里，**和[《Apple PORTool：用分叉回滚树解决工具调用的信用分配难题》](/post/apple-portool-credit-assignment-tree-tool-use-rl/)是互补的两条腿**：Apple 关心的是"多工具序列调用里如何把奖励分配到每一步"，而 Needle 关心的是"单次调用里如何选对工具+填对参数"。一个是 RL 层，一个是基础模型层，两边都解了之后，整套 on-device agent 才能真正自治。

### 3.8 Token-Level Loss Weighting：把错误模式当作损失设计

最后一个看似平凡却极工程化的点是：Needle 训练时给不同 token 加了不同权重：

- JSON 结构 token：1.0×
- 工具名：2.0×
- 参数 key：1.5×
- **参数 value：4.0×**

为什么是 4×？因为他们观察到训练早期模型已经能把 JSON 结构写对（~99% parse rate），实际的错误主要发生在参数值——尤其是"location"、"date"、"city"这种从自然语言里抽取出来的值。**把损失权重直接对齐到错误分布上，是远比"调整温度"或"加更多数据"更直接的工程手段**。

这是小模型设计的一种典型"近端优化"思维：你知道错在哪里，就直接把损失加到那里，而不是寄希望于参数容量去自动学到。

## 4. 跑分与方法论：怎么知道它真的有用？

文档与 README 里给出的对照组是：

- **FunctionGemma-270M**（Google）
- **Qwen-0.6B**（阿里）
- **Granite-350M**（IBM）
- **LFM2.5-350M**（Liquid AI）

Cactus 的说法是"在 single-shot function call 任务上击败这些模型"。这里有两个细节值得注意：

1. **Needle 是 single-shot 专家，不是通用 chatbot**。在多轮对话、推理、写作上它一定不如上面任何一个。这是清晰的能力边界声明，而不是市场话术。
2. **HN 评论区里也有质疑**，例如：能不能处理"用一句模糊的话激活一个隐含 action"（即用户说"明天 10 点咖啡馆"，模型要决定调用 `add_appointment` 而不是 `send_message`）。Cactus 在评论里回答："这是 disambiguation 任务，我们的合成数据里有专门覆盖，但实际效果要看 finetune"。

跑分的方法论我倾向于这么读：**Needle 不是 SOTA 模型，它是一个能力极度收窄但收窄到位的小模型**。把它当 Apple 的 [PORTool RL agent](/post/apple-portool-credit-assignment-tree-tool-use-rl/) 里的"单步动作模型"用，可能比把它当 ChatGPT 用合适得多。

## 5. 延伸阅读图谱

### 5.1 作者 / 团队的相关产出

1. **[cactus-compute/cactus](https://github.com/cactus-compute/cactus)** — Cactus 推理引擎本体。"从零为手机和可穿戴设计的运行时"，是 Needle 在生产中实际跑起来的执行栈。
2. **[Cactus 之前的 Show HN（2025）](https://news.ycombinator.com/item?id=44524544)** — 推理引擎首次发布时的设计动机讨论，可对比 Needle 论文里"为什么去 FFN 能让 KV cache 更友好"。
3. **Cactus 内部博文系列** — Cactus 的 GitHub README 里有一组关于"在 ARM CPU 上做 GEMM"的笔记，是这个团队为什么敢去掉 FFN（FFN 在手机 SoC 上是带宽杀手）的真实物理动机。
4. **Cactus-Compute/needle 数据集生成脚本** — 训练数据完全由 Gemini API 合成，覆盖 15 类工具（timer、navigation、smart-home 等）。在 `launch_train.sh` 与 `needle generate-data` 里能看到具体提示工程。
5. **HuggingFace Cactus-Compute/needle 模型卡** — 包含完整的 JAX/Flax 实现，可以下载并在 Mac 上微调。

### 5.2 与"无 FFN" / "encoder-decoder 复辟" 同方向的论文

1. **[Linear Attention is (Maybe) All You Need](https://arxiv.org/abs/2407.04620)**（2024，TogetherAI / Tri Dao 团队）— 研究 FFN 在 linear attention 下是否仍必要。
2. **[Switching Transformers: Mixture-of-Depths](https://arxiv.org/abs/2404.02258)**（Google DeepMind，2024）— 让 token 自己决定要不要走 FFN，与"全砍 FFN"是另一种思路。
3. **[FlexAttention](https://pytorch.org/blog/flexattention/)**（PyTorch，2024）— attention 才是真正的 routing primitive 的工业级表述。
4. **[T5 vs. decoder-only 经典对照](https://arxiv.org/abs/1910.10683)**（Raffel et al., 2019）— Needle 的 encoder-decoder 立场实际上是 T5 的一种现代化复活。
5. **[Phi-3-mini 技术报告](https://arxiv.org/abs/2404.14219)**（Microsoft）— 同样在 3B 以下做"小模型也能 SOTA"，但 Phi 走的是 data-quality 路线，而 Needle 走的是 architecture-tailoring 路线。
6. **[nGPT](https://arxiv.org/abs/2410.01131)**（Nvidia）— ZCRMSNorm 的直接灵感来源。
7. **[Muon optimizer 原始博客](https://kellerjordan.github.io/posts/muon/)** — Newton-Schulz 正交化的来历。

### 5.3 与 "on-device tool use / small agent" 方向的工程文章

1. **[Apple Apple Intelligence: Foundation Language Models](https://machinelearning.apple.com/research/apple-intelligence-foundation-language-models)**（Apple，2024-2025）— 3B 模型在 iPhone 上的工业级部署，思路与 Needle 互补。
2. **[Phi-3 on Edge](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/deploy-models-phi-3)**（Microsoft）— Phi-3 在 ONNX Runtime 上的边缘部署实践。
3. **[Functionary: Function calling small model](https://github.com/MeetKai/functionary)** — 早期 7B 级别的 function call 专用模型，可以和 Needle 对比"小到什么程度才算极致"。
4. **[Gemini Nano / On-Device API](https://developers.google.com/ai/gemini-nano)** — Google 自家小模型方案，Needle 把它当上游蒸馏对象。
5. **[Hermes 3 function-calling](https://nousresearch.com/freedom-at-the-frontier-hermes-3/)** — Nous Research 在工具调用上的训练实践。

### 5.4 反方观点 / 批评视角

1. **HN 评论里的核心批评**：Needle 在"工具数量很大且语义高度重叠"的场景表现未知。作者承认这种情况下应该靠对比检索头先过滤 top-k。
2. **"小模型只是大模型的影子"派**：Sebastian Raschka 等学者多次指出，小模型在"分布外行为"上极其脆弱，Needle 也明确说"用之前请自己测自己的工具集"。
3. **"没必要去掉 FFN"派**：去 FFN 的代价是模型完全依赖输入上下文，无法对工具集做有效的"先验记忆"。如果你的应用希望模型记住公司内部的 200 个工具语义而不需要每次都把签名塞进 prompt，FFN 可能仍是必要的。

## 6. 编辑延伸思考：Needle 把"on-device AI"的故事讲完了一半

我读完 Needle 之后，最想跟同行讨论的不是"无 FFN 是不是真的可以推广"，而是它揭示了一个更大的格局问题：**当大模型把"全能"做到极致后，小模型的胜负手不在尺寸，而在 task-architecture co-design**。

过去 18 个月，我们看到了三种小模型路线：

1. **Phi 路线**（Microsoft）：通用架构 + 高质量数据。胜在通用，输在不够专用。
2. **MobileLLM / Gemma 路线**（Meta / Google）：通用架构 + 量化 + 蒸馏。胜在工程成熟，输在创新有限。
3. **Needle / Cactus 路线**：专用架构 + 专用数据 + 端到端自研栈。胜在每一项任务的极限性能，输在"换个任务就要重训一个模型"。

哪一条路线赢？2025 年我倾向于第 2 条，2026 年看完 Needle 之后我开始怀疑第 3 条才是真正的 on-device 终局。原因有三：

- **任务专门化 + 模型专门化 + 引擎专门化**这套组合，把 "26M 参数能跑 1200 tok/s decode" 这种数字推到了通用方案做不到的位置。
- 开发者经济学上，**MIT 开源 + 一键 finetune** 让"我为我自己的工具集训一个 Needle 变体"成为一个真实的工作流。我可以用 Gemini API 花 $50 合成数据，再用一张 H100 花 1 小时 finetune 出我自己的小模型，部署到我自己的 App 里——这种"自助小模型车间"在 2024 年是不可想象的。
- 与[《Apple PORTool》](/post/apple-portool-credit-assignment-tree-tool-use-rl/)、[《Agent Memory Architecture Technical Debt》](/post/agent-memory-architecture-technical-debt/) 拼在一起看，2026 年 agentic AI 的正确分层正在浮出水面：**云端大模型做 planning，边缘小模型做单步动作，本地 vector store + sqlite 做 memory**。Needle 完美填上了"边缘动作执行"这一层。

但 Needle 也讲完了故事的另一半才能成立。它现在还缺：

- **多工具 disambiguation 的真实基准**——没有一个公开的、像 BFCL 那样的多工具混淆数据集来评测它。
- **结构化错误的可解释性**——参数 value 错误后模型不知道错了，需要外部 schema validator 兜底。
- **finetune 后的退化曲线**——HN 评论提到有人 finetune 后效果反而变差，作者解释是数据质量问题，但缺少系统性研究。

如果这三件事在未来三个月内被 Cactus 或社区填上，Needle 会从一个"漂亮的开源实验"变成一个**真正改写 on-device AI 经济学的基础设施**。

最后一个值得想的问题：**当一家初创公司能用 27 小时 TPU 时间训出一个能打的小模型，"训练成本"作为护城河还剩下多少**？2024-2025 的共识是"训练贵，所以闭源"。2026 年的反例正在密集出现：DeepSeek-V3、Mistral、Phi-3，现在再加上 Cactus。**护城河正在从"训练能力"迁移到"task-architecture co-design 能力"+"端到端栈完整度"**，这是一个对开源社区极其友好的迁移。

## 7. 配套资料导览

本文目录下另有四份配套资料，建议依次阅读：

- **`mindmap.svg`** — Needle 的核心论点思维导图（10 个分支节点）
- **`concept-cards.md`** — 12 张关键概念卡片：FFN、Encoder-Decoder、Gated Residual、ZCRMSNorm、Muon、QAT、CLIP head、Loss weighting、Distillation、Cross-attention、Tool retrieval、Inference engine
- **`glossary.md`** — 35 条英中对照术语表，覆盖架构、训练、部署三大类
- **`cover.svg`** — 文章封面

## 8. 谁应该读

- **正在做 on-device / edge AI 模型的工程师** — 必读，几乎每个设计决策都能直接抄。
- **做 Agentic AI 框架的人** — 把 Needle 当作"边缘动作执行层"嵌进你的 agent 栈，能让端到端延迟降一个量级。
- **正在评估"是否要自研小模型"的产品技术 leader** — 这是 2026 年最便宜的"自研模型可行性"参考。
- **对 Transformer 架构演进有兴趣的研究者** — 这是过去 18 个月里少见的"敢于砍掉 FFN"的负向探索，值得当反例案例研究。
- **关心开源 AI 经济学的人** — 思考一下：MIT 协议 + 200B token 训练 + JAX/Flax 全开源——这意味着什么样的护城河重构？

---

> **编辑后记**：今天的"好文共赏"选这篇，是因为我已经很久没看到一份开源 README 同时具备三件事——技术决策有清晰的"为什么"、产品形态可以 `git clone` 后立即复现、和一种愿意把整个架构假设拿出来挑战社区的姿态。在 2026 年 5 月这个"AI 圈每天都有新模型发布"的节奏下，能把一个 26M 模型讲得这么沉稳、这么不浮夸，值得我们停下来仔细读完。
