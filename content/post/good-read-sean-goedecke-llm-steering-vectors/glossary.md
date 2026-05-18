# 术语表 · LLM Steering · 英中对照

| English | 中文 | 释义 |
|---|---|---|
| Activation | 激活值 | 神经网络某一层在某个输入下产生的中间数值张量。Steering 操纵的就是这个。 |
| Activation Layer | 激活层 | 在某层之后取 activation 作为操作对象。常见做法是取中后段的某一层（如 24/32 层模型的第 24 层）。 |
| Abliteration | 去拒答（消融对齐） | 通过 steering 把模型的"拒答方向"去掉。比 LoRA uncensored 更轻量，对原能力损伤更小。 |
| AY-3-8910 / YM2149 | YM2149 音频芯片 | 雅马哈在 AY-3-8910 基础上修改的音频芯片，Atari ST 的标志声音。本文出现是因为引申讨论。 |
| Black Box | 黑盒 | 指传统看待 LLM 的方式——只看输入输出，不看内部。 |
| Boostable Feature | 可放大特征 | SAE 抽出的、可以单独放大/抑制的语义概念。 |
| Chain-of-Thought | 思维链 | LLM 显式列出推理步骤的提示工程方法。Steering 是不可见版的 CoT。 |
| Context Window | 上下文窗口 | LLM 单次能处理的最大 token 数。Sean 提出 steering 或可压缩 context。 |
| DeepSeek V4 Flash | DeepSeek V4 Flash 模型 | DeepSeek 2026 年发布的小尺寸 MoE 模型，是 DS4 唯一支持的目标。 |
| Direction (in activation space) | 激活空间方向 | Steering vector 在数学上就是 activation 空间中的一个向量方向。 |
| dir-steering | 方向操舵 | DS4 中 steering 模块的命名，dir 即 direction。 |
| DS4 / DwarfStar 4 | DwarfStar 4 | antirez 在 2026-05 发布的本地推理引擎，专为 DeepSeek V4 Flash 优化。 |
| Feature | 特征 | SAE 视角下，一组共激活的神经元对应一个语义概念。 |
| Fine-tune | 微调 | 在预训练模型上用小数据集继续训练，永久修改权重。 |
| GGUF | GGUF 格式 | llama.cpp 生态使用的模型文件格式，单文件包含权重和元数据。 |
| Golden Gate Claude | "金门大桥 Claude" | Anthropic 2024-05 的演示：放大"金门大桥"特征后，Claude 把所有话题都拉向金门大桥。 |
| Implicit Memory | 隐式记忆 | 模型存储在权重 / activation pattern 中的知识，对应 context 之外的"已知"信息。 |
| Inference | 推理 | 模型用已训练权重对新输入生成输出的过程。Steering 在推理时介入。 |
| Interpretability | 可解释性 | 研究"模型在想什么"的子领域。Anthropic 是行业领头。 |
| Latent Space | 隐空间 | 模型内部表示的高维向量空间。Steering 是在隐空间里做加减法。 |
| Layer Activation Patching | 层激活替换 | 极端 steering：把整层的 activation 替换为另一个模型的 activation。Sean 用它做归谬。 |
| llama.cpp | llama.cpp | 社区主流本地推理引擎。DS4 是它的精简分支。 |
| LoRA | 低秩适配 | 一种轻量 fine-tune 方法，只训练低秩矩阵。"无审查"版常用 LoRA 实现。 |
| Mid-flight Manipulation | 推理中操纵 | 在 forward pass 进行到一半时介入修改 activation。Steering 的代名词。 |
| Middle-class Research | 中产阶级研究 | Sean 对 steering 的定位——大厂用不上、API 用户碰不到的"夹心"领域。 |
| Monosemanticity | 单义性 | 一个神经元/特征只对应一个语义概念的理想状态。SAE 旨在逼近这个状态。 |
| Natural Language Autoencoder (NLA) | 自然语言自动编码器 | Anthropic 2026-05 提出的方法：把 activation 翻译成可读自然语言。本博客有专文。 |
| Polysemanticity | 多义性 | 一个神经元同时编码多个语义概念，是 LLM 的常态。 |
| Prompt Engineering | 提示工程 | 通过 prompt 文本控制模型行为。Steering 的最大竞品。 |
| Refusal Direction | 拒答方向 | 把"拒绝回答有害问题"对应的 activation 子空间，可以被 steering 掉。Abliteration 的核心。 |
| RLHF | 人类反馈强化学习 | 现代 LLM 对齐的主要技术，"中产阶级"步骤之一。 |
| Sparse Autoencoder (SAE) | 稀疏自动编码器 | 用一个辅助模型从 activation 抽稀疏特征。是 SAE 的主流 interpretability 工具。 |
| Steering | 操舵 / 引导 | 推理时直接调整 activation 来引导输出。本文主题。 |
| Steering Vector | 操舵向量 | 一个 activation 空间中的固定向量，加到某层 activation 上就会改变模型行为。 |
| Superposition | 叠加（叠加态） | 模型把多个特征塞进同一组神经元的现象，是 SAE 必要性的根源。 |
| System Prompt | 系统提示 | 模型对话前置的"角色设定"prompt。"你是一个专家"就是经典系统 prompt。 |
| Token | 词元 | LLM 的最小输入/输出单位。Steering 的"竞品"prompt 是以 token 形式工作的。 |
| Towards Monosemanticity | 《迈向单义性》 | Anthropic 2023 年的 SAE 奠基论文，开启了 feature-level interpretability。 |
| Uncensored Model | 无审查模型 | 去除了拒答约束的开源模型变体。 |
| Verbosity Steering | 冗长度操舵 | "respond tersely" → 一个朴素 steering vector 的标准玩具示例。DS4 内置的就是它。 |
| Working Memory | 工作记忆 | 模型当前 context 里的信息。与 implicit memory 相对。 |
