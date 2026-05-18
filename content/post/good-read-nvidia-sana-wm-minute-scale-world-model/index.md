---
title: "【好文共赏】把\"一分钟世界\"塞进一块 H100：NVIDIA SANA-WM 用混合线性注意力，把世界模型从 14B 砍到 2.6B"
description: "SANA-WM 用 Frame-wise Gated DeltaNet × Softmax 的杂交注意力、Plücker × UCPE 的双轨相机控制，把一分钟 720p 可控视频从「8 卡 14B」压成「单卡 2.6B」——一篇关于世界模型如何降本三个数量级的技术拆解。"
date: 2026-05-18
slug: "good-read-nvidia-sana-wm-minute-scale-world-model"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - 世界模型
    - 视频生成
    - 线性注意力
    - NVIDIA
    - 论文导读
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
>
> - 原文：[SANA-WM: Efficient Minute-Scale World Modeling with Hybrid Linear Diffusion Transformer](https://arxiv.org/abs/2605.15178)
> - 项目页：[nvlabs.github.io/Sana/WM](https://nvlabs.github.io/Sana/WM/)
> - 作者：Haoyi Zhu, Haozhe Liu, Yuyang Zhao, Tian Ye, Junsong Chen, Jincheng Yu, Tong He, **Song Han**, Enze Xie（NVIDIA）
> - 发布：2026-05-14（arXiv v1）
> - 阅读时长：约 50 分钟（含附录）
> - 多模评分：Opus 9.2 / Sonnet 9.0 / Gemini 8.8（综合 **9.0/10**）
> - 一句话推荐：**当世界模型领域还在比谁的模型更大时，Song Han 把"小而美"重新写了一遍——2.6B 参数、单 GPU、一分钟 720p、可精确控制 6 自由度相机，36 倍吞吐量打平 14B 工业基线。**

## 一、为什么这篇值得读

过去一年，"世界模型（World Model）"这个曾经只存在于 Schmidhuber 论文标题里的词，被 LingBot-World、HY-WorldPlay、Matrix-Game、Infinite-World 一连串发布拉到了产业聚光灯下。它们的共同特征是：动辄 5B–28B 参数、8 卡推理、最高 480p 分辨率、单段视频生成需要数十秒到数分钟。一种"video 版 GPT-3"的范式正在成形——**规模换可控、规模换长度**。

NVIDIA 的 SANA-WM 把这条路径反过来走。它的核心结论可以浓缩成一张表：

| 指标 | LingBot-World | HY-WorldPlay | Matrix-Game 3.0 | **SANA-WM (+refiner)** |
|---|---|---|---|---|
| 参数量 | 14B+14B | 8B | 5B | **2.6B (+17B refiner)** |
| 分辨率 | 480p | 480p | 720p | **720p** |
| 推理 GPU | 8 | 8 | 8 | **1** |
| 训练数据 | 大规模 | 大规模 | 大规模 | **~213K clips** |
| RotErr (Simple) | 10.47° | 17.89° | 12.96° | **4.50°** |
| VBench Overall | 81.82 | 68.82 | 78.53 | **80.62** |
| 视频/小时 (8×H100) | 0.6 | 1.1 | 3.1 | **22.0**（36× 加速） |

更挑衅的一点：经过 self-forcing 4 步蒸馏 + NVFP4 量化后，**60 秒 720p 视频可以在一张 RTX 5090 上 34 秒生成完毕**——一台游戏 PC，就是一个"一分钟世界"的本地推理引擎。

这不是一篇"参数更大"的论文，而是一篇关于**系统设计**的论文。它把三件事缝合到了一个 DiT 里：

1. **混合线性注意力**：把 Gated DeltaNet（GDN）从"按 token"扫描改造成"按帧"扫描，每四层 GDN 间插一层 softmax，state 大小恒为 $D \times D$。
2. **双轨相机控制**：粗粒度走 latent-frame UCPE，细粒度走 raw-frame Plücker mixing，补偿 VAE 时间下采样带来的运动信息损失。
3. **两阶段生成 + 自蒸馏**：先生成 stage-1 长视频，再用 17B refiner 做晚段去漂移；最后用 self-forcing 蒸馏到 4 步采样，配 NVFP4 量化部署到消费级 GPU。

从工程视角，这是 Song Han 团队一贯的风格——**把模型架构、训练流程、推理部署当成一个联合优化问题**。从研究视角，这是世界模型领域第一次有人系统性回答："如果我们不能继续 scale，能不能用更聪明的 attention 结构和更精确的 conditioning，把质量–吞吐量曲线向左下推一个数量级？"

> 📚 **跨文链接**：我们在 [《Needle：把 Gemini 3.1 蒸馏成 26M 参数的工具调用专家》](/post/good-read-needle-simple-attention-networks/) 里讨论过把 FFN 全砍掉的极端选择；这次 SANA-WM 选了另一条路——**保留 FFN，但重写 attention 的递归结构**。两者都是"对 Transformer 标准件做减法"的不同流派。

## 二、核心观点深度解读

### 2.1 Frame-wise GDN：把递归状态从"逐 token"升到"逐帧"

世界模型最棘手的事情是 **time-context tradeoff**——分辨率越高、时长越长，token 数指数级膨胀。一段 60 秒 720p 视频，即便经过 VAE 强压缩，latent token 也轻易突破 10 万；用 softmax 全自注意力，KV cache 在 80GB H100 上直接 OOM。

SANA-Video 选了 cumulative linear attention（ReLU-based）来压平内存：state 维度恒为 $D \times D$，与序列长度无关。但作者诚实地指出了它的硬伤——**没有衰减、没有显著性机制，陈旧特征和新特征同权累积**，分钟级序列下 state drift 严重。

> 原文："This compact state has no explicit decay or saliency mechanism: stale features accumulate with the same effective weight as more recent ones."

他们的修复方案，是把 Yang Songlin 等人的 **Gated DeltaNet** 从 token 级"升维"到 frame 级。原始 GDN 每个 token 一步：

$$
\mathbf{S}_i = \gamma_i \mathbf{S}_{i-1} + (\mathbf{v}_i - \gamma_i \mathbf{S}_{i-1}\hat{\mathbf{k}}_i)\beta_i \hat{\mathbf{k}}_i^\top
$$

其中 $\gamma_i \in (0,1]$ 是衰减门、$\beta_i \in [0,1]$ 是更新门、delta-rule 项只修正"当前 state 预测和目标值的残差"。

SANA-WM 的变种是**每一帧扫描一次，但一次性吃完该帧所有 $S$ 个空间 token**：

$$
\mathbf{S}_t = \mathbf{S}_{t-1} \mathbf{M}_t + \mathbf{U}_t,\quad \mathbf{M}_t = \gamma_t(\mathbf{I} - \hat{\mathbf{K}}_t \boldsymbol{\beta}_t \hat{\mathbf{K}}_t^\top)
$$

这个改动看似简单，背后有一个更关键的代数稳定性问题——**当 $S$ 很大（比如 $80\times 45 = 3600$），未做缩放的 key energy 会让 $\mathbf{I} - \mathbf{A}_t$ 变成扩张映射**。作者给了一个干净的不等式证明：将 key 做 $1/\sqrt{D \cdot S}$ 缩放后，

$$
\text{tr}(\hat{\mathbf{K}}_t \boldsymbol{\beta}_t \hat{\mathbf{K}}_t^\top) \leq 1 \implies \|\mathbf{M}_t\|_2 \leq \gamma_t \leq 1
$$

非膨胀性保住了，递归状态就不会爆。这是这篇论文我个人最喜欢的细节之一——**论文作者没有把它藏在附录里，而是放在正文 Eq.(4)-(5)，强调"为什么这个 $1/\sqrt{S}$ 不是凭感觉加的"**。

> 📚 **跨文链接**：这种"把递归结构重新引入 Transformer"的潮流，我们在 [《GGUF 不只是权重：一个本地推理引擎作者眼里，单文件模型格式还缺什么》](/post/good-read-gguf-beyond-the-weights/) 里也提到——RWKV、Mamba、GDN、Test-Time Training 都是同一波"线性注意力 + 状态空间"复兴的产物。

### 2.2 每四层插一层 softmax：为什么"杂交"比"纯线性"赢

一个朴素的疑问：既然 GDN 内存恒定、吞吐量高，为什么不全用 GDN？

作者给出了一个让人信服的实验答案——**纯 GDN 在最早的几个 attention 层会出现明显的"长程一致性塌方"**：场景在 30 秒后开始漂移，远处物体身份丢失。这与 Lin et al. 在 Jamba、以及 Anthropic 在 Claude 3 Haiku 上观察到的现象一致：线性注意力擅长"summarize the past"，但 softmax 擅长"retrieve specific past tokens"。

SANA-WM 的方案是**每四层 GDN 间穿插一层 softmax**：20 层 transformer 中，第 {3, 7, 11, 15, 19} 是 softmax，其余 15 层是 frame-wise GDN。这个比例与 Mamba-2 Hybrid 中观察到的 1:3–1:7 经验区间吻合——**少量 softmax 层就足以"锚定"长程检索**。

更巧的工程细节是：为了让 chunk-causal 推理时 softmax 那 5 层不爆内存，他们引入了 attention sink（保留第一帧作为永久键值）+ 局部时间窗口。这样 softmax 那 5 层的内存随 rollout 长度恒定，整个 60 秒视频推理 peak memory 锁在 51.1GB，刚好塞进一张 H100。

> 原文："To enhance long-video generation performance, we further fine-tune the GDN model by replacing every fourth block with standard softmax attention, while retaining the original QKV and output projections."

### 2.3 Plücker × UCPE：为什么相机控制需要"双速率"

世界模型的另一个老大难是 **action conditioning fidelity**——你说"相机左转 30 度后向前推 2 米"，模型能不能精确照做。

之前的方案分两派：

- **Pose embedding 派**（如 CameraCtrl、Sekai-X）：把 6-DoF pose 投影到 latent space，concat 到 token 上。优点是简单，缺点是 latent 已经被 VAE 大幅时间下采样，pose 信号被"抹平"。
- **Plücker 派**（如 ViewCrafter）：用 Plücker 坐标在原始像素分辨率上注入射线信息。优点是几何精度高，缺点是计算昂贵、和 latent diffusion 不直接兼容。

SANA-WM 同时采用两者，分工明确：

1. **粗粒度（Coarse）**：对每个 latent token，构造 ray-local 坐标系，用 UCPE（Universal Camera Pose Encoding）注入相机的全局 6-DoF 信息——它**告诉模型"摄像机大致在哪、往哪看"**。
2. **细粒度（Fine）**：在 VAE 编码之前的原始帧上做 Plücker mixing——它**补偿"latent 时间下采样导致的子帧运动信息丢失"**。

实验结果震撼：

- Hard-Trajectory split 上，SANA-WM + refiner 的 RotErr 是 **8.34°**，而 14B 参数的 LingBot-World 是 18.99°；2.6B 模型在最难指标上把 14B 模型甩开了 2.3 倍。
- CamMC（Camera Motion Consistency）从 LingBot 的 1.81 降到 1.44，**这是一个工业级的精度提升**——已经接近"游戏引擎渲染"的水准。

> 📚 **跨文链接**：相机条件化这件事，本质上是 [《Apple PorTool: Credit assignment in tree-structured tool use》](/post/apple-portool-credit-assignment-tree-tool-use-rl/) 中 credit assignment 问题在视觉 RL 上的姐妹问题——**当你给模型一个长指令序列，模型怎么知道"哪一段相机参数对应哪一段视觉输出"？**

### 2.4 两阶段生成：用 17B refiner 给 2.6B 主干"贴补丁"

SANA-WM 还有一个**反直觉的设计选择**：主干只有 2.6B，但配了一个 17B 的 refiner。

为什么不让主干本身长大？

作者的回答是——**长视频生成的瓶颈不在"生成能力"，而在"晚段质量衰减"**。前 20 秒模型表现良好，但 40–60 秒区间出现纹理粗糙、运动失真。如果整个模型放大 5 倍来解决这个尾部问题，训练成本和推理成本是线性甚至超线性增加；而只在 stage-2 用一个大 refiner 去"打磨"晚段，**推理时只多花 23.6GB 显存（51.1 → 74.7）、吞吐量从 24.1 降到 22.0 videos/hour**，性价比极高。

这个设计的代数证据在 $\Delta_\text{IQ}$ 指标上：

- Stage-1 only：Simple 3.79 / Hard 3.09（晚段比早段质量平均下降这么多）
- + Refiner：Simple 1.17 / Hard 0.31（接近不衰减）
- 对比 HY-WorldPlay：23.59 / 25.88（晚段完全崩坏）

这是世界模型领域第一次有人把"质量随时间衰减"作为一阶可优化指标公开 ablation——**这本身就是一个 benchmark 设计上的小贡献**。

### 2.5 213K clips：从"数据规模"到"数据质量"的转向

LingBot-World 训练用了上千万 clips。SANA-WM 只用 **212,975 clips**——少了两个数量级。

差异不在数量，而在 **metric-scale 6-DoF pose annotation 的质量**。作者搭建了一条数据管线：

- 主流标注器 VIPE 在长视频上的 depth 估计不稳定 → 用 **Pi3X**（长序列一致 depth）+ **MoGe-2**（metric scale 准确）替换
- DL3DV 是静态 3D 场景 → 用 **FCGS（Fast Compressed Gaussian Splatting）** 重建后渲染 60 秒相机轨迹 + **DiFix3D** 去除 splatting 伪影
- 7 个数据源混合：SpatialVID-HQ（158K，10s 真实）、DL3DV（5.7K 真实 + 14.9K 合成）、OmniWorld（1.7K 合成）、Sekai Game/Walking（13K）、MiraData（19K）

这是一个相当典型的"质量胜过规模"的故事。**它的政治学含义是**：如果你不是 OpenAI/Google 那种能买 100M 视频的公司，你的 moat 不在数据量，而在**标注精度**——精确的 metric pose 比海量近似 pose 更有价值。

> 📚 **跨文链接**：[《8.2 万亿种可能里只剩 284 种：tmctmt 一次失眠夜把 Mullvad 用户重新指纹化》](/post/good-read-mullvad-exit-ip-fingerprinting/) 里我提过"信息熵的非均匀分布"是攻击面；这里反过来——**视频数据的有效信息密度，远低于其字节量**，加 6-DoF pose 标签等于做了一次 200× 的信息浓缩。

### 2.6 Self-Forcing 4-step 蒸馏 + NVFP4 量化：把世界模型搬到 RTX 5090

这是 SANA-WM 最有"NVIDIA 味"的一段——他们把推理路径压到极致：

1. **60 步 H100 自回归** → 起点
2. **Self-forcing 蒸馏到 4 步** → 这是 Yin et al. 2024 提出的"用模型自己的预测作为下一步的输入"的 distillation 技巧，特别适合 AR diffusion；保留了多步质量，但只跑 4 步
3. **Attention sink + 局部窗口** → 让 5 层 softmax 在 chunk-causal AR 推理时常数内存
4. **NVFP4 量化** → NVIDIA Blackwell 引入的 FP4 数值格式，4-bit 浮点但带 per-block scale，比 INT4 精度损失小得多

最终结果：**单张 RTX 5090（32GB GDDR7、约 1500 TFLOPS FP8），34 秒生成 60 秒 720p 视频**。比实时还快接近 2 倍。

这意味着什么？意味着**世界模型从"需要 8 卡集群"的科研演示，变成了"游戏主机能跑"的消费品**。一个游戏开发者可以本地、实时地为玩家生成 minute-scale 的 dynamic environment。Roblox/Unity 的某些用例从这里开始可以被颠覆。

### 2.7 评测协议的"良知"：构建公平的 1-min benchmark

世界模型评测一直是个烂摊子——VBench 关注短视频质量、RealEstate10K 关注相机精度、各家用自己的 demo case。SANA-WM 团队做了一件值得鼓掌的事：

- 用 **Nano Banana Pro** 生成 80 张初始图（game/indoor/outdoor-city/outdoor-nature 各 20）
- 每张图配 **Simple + Hard 两种 revisit trajectory**（"revisit"指相机回到出发点附近，可以测 memory）
- 同时报告 5 类指标：**Pose Acc.（RotErr/TransErr/CMC）+ VBench 8 维 + Revisit Memory + 长程退化 $\Delta_\text{IQ}$ + 推理效率（Mem/Throughput）**

这是世界模型领域第一份**对长程一致性、相机精度、视觉质量、推理效率"四位一体"评测的标准方案**。预计未来一年这套 benchmark 会被广泛采用——这本身就是论文之外的额外贡献。

### 2.8 工程：Triton 自定义核 + Context-Parallel 训练

附录里有几段对工程师特别值钱的内容：

- **GDN scan kernel 用 Triton 手写**：标准 attention kernel（Flash-Attn 那套）对 frame-wise GDN 的递归不适用，他们写了 fused kernel 把 gate operation 和 scan 合在一起
- **Context-Parallel（CP）训练**：961 帧（60 秒 @ 16 FPS）序列在 64 GPU 上按时间分片，每片只持有 15 帧 latent，all-reduce 时同步 frame-recurrent state
- **混合精度 FlashAttn-3 for softmax 5 layers + BF16 for GDN scan**：因为 GDN scan 对数值动态范围更敏感（state 累积），不能简单 FP8

这一套"算法-kernel-并行策略"的联合设计，是 Song Han 团队从 SmoothQuant、AWQ、StreamingLLM 一路走来的标志性手法——**"如果你的 algorithm 跑不动，那是因为 kernel 没写到 hardware sweet spot"**。

## 三、延伸阅读图谱

### 3.1 作者圈代表作（建议同读）

| 论文 | 作者 | 这次贡献到 SANA-WM 的什么 |
|---|---|---|
| [SANA-Video](https://arxiv.org/abs/2509.24695) | Junsong Chen, Enze Xie, Song Han | 直接基础：DiT + linear attention 视频骨干 |
| [SANA (image)](https://arxiv.org/abs/2410.10629) | 同上 | 最初的"linear DiT"思想，从图像扩展到视频 |
| [Gated DeltaNet](https://arxiv.org/abs/2412.06464) | Yang Songlin 等 | Frame-wise GDN 的原始 token-wise 版本 |
| [SmoothQuant](https://arxiv.org/abs/2211.10438) | Song Han 等 | 量化思路传承，NVFP4 是同源 |
| [AWQ](https://arxiv.org/abs/2306.00978) | Song Han 等 | 蒸馏 + 量化联合优化的方法论 |
| [StreamingLLM](https://arxiv.org/abs/2309.17453) | Song Han 等 | Attention sink 概念的发源 |

### 3.2 同领域同期工作（要对比着读）

| 论文 / 系统 | 路线 | 与 SANA-WM 的本质差异 |
|---|---|---|
| LingBot-World | 14B+14B 大模型 | "scale up everything"路线，SANA 反方向 |
| HY-WorldPlay (Tencent) | 8B + 多 GPU | 同样关注长视频，但没有 hybrid attention |
| Matrix-Game 3.0 | 5B 游戏域专用 | 域窄但精度高；SANA 想做通用 |
| Infinite-World | 1.3B autoregressive | 参数小但 480p；SANA 拿 2.6B 做到 720p |
| Cosmos (NVIDIA, 2024) | NVIDIA 自家上一代 | Cosmos 是 base model，SANA-WM 是应用层 |
| Genie 3 (DeepMind) | 闭源 | 同样做 minute-scale，但 DeepMind 不放权重 |

### 3.3 反方/批判视角（必读）

1. **"World models 还不是真的 world models"** — Yann LeCun 反复强调：当前所谓世界模型都是 video prediction，缺乏因果推理和物理一致性。SANA-WM 在 hard trajectory 上的 RotErr 仍有 8.34°——**对机器人导航来说这是巨大的误差**。
2. **"Linear attention 永远不会真的 retrieve"** — Tri Dao（FlashAttention 作者）的观察：哪怕 hybrid，linear 那部分仍是 lossy summary。SANA-WM 用 1:3 比例的 softmax 弥补，但 60 秒以上的极端长程一致性还没完全验证。
3. **"36× throughput 是被定义的"** — SANA-WM 自报的 36× 是和 LingBot 比；如果比 Matrix-Game 3.0（5B 720p）只有 7×。**任何 efficiency claim 都依赖 baseline 选择**。
4. **"FP4 量化的隐藏成本"** — NVFP4 需要 Blackwell 硬件支持；A100/H100 跑不了原生 FP4，需要软件模拟，加速比会缩水。这是 NVIDIA 论文的"温柔锁定"。

### 3.4 论文里没提但你应该知道的背景

- **VAE 时间压缩比的选择**：LTX2-VAE 比 Wan2.1-VAE 大 8 倍压缩，但解码质量可能略损失——SANA-WM 没在主表里 ablation 这个，附录 C.2 提了但很短
- **213K 数据公开版本**：作者承诺会开放数据管线代码，但 metric pose 标签本身有版权限制（VIPE 是 Apache 2.0、Pi3X 是非商用），这给商用部署留下灰区
- **17B refiner 的来源**：refiner 不是从头训的，是基于一个公开 video generator 微调；附录 A 给了细节但语焉不详

## 四、编辑延伸思考：从 SANA-WM 看到的"小模型工程美学"

这一年多来，开源/低成本模型领域走出了一条独立于 OpenAI/Anthropic "更大更长"叙事的支线：

- **DeepSeek-V4-Flash**：MoE + 长上下文，但单次激活只有 37B，[antirez 在 MacBook 上跑通了](/post/good-read-antirez-ds4-local-inference/)
- **Needle (26M params)**：[把 Gemini 蒸馏成微型工具调用模型](/post/good-read-needle-simple-attention-networks/)，FFN 全砍
- **Mercury Bank 200 万行 Haskell**：[把语言学家当成可靠性工程师](/post/good-read-haskell-mercury-production-engineering/)
- **OCaml on Borealis**：[12 年 unikernel 研究塞进 5MB 卫星载荷](/post/good-read-ocaml-in-space-borealis/)
- **现在加上 SANA-WM**：把世界模型从 14B 砍到 2.6B，单卡运行

这五个故事的共同骨架是：**当主流叙事是"算力 = 王道"时，一小撮研究者反过来证明"约束才是创意之母"**。SANA-WM 的 213K clips、单 GPU 部署、Triton 自定义 kernel，本质上是**约束驱动的工程美学**——你不能买 100M 视频，所以你必须想清楚 6-DoF metric pose 比 raw count 更有价值；你不能用 8 卡推理，所以你必须把 softmax 注入到 GDN 之间而非纯线性化。

这种美学有一个更宏大的含义。我们在 [《禁欲计算：Dave Gauer 把 Thoreau、Flaubert、OpenBSD 拼在同一张配置文件里》](/post/good-read-ratfactor-ascetic-computing/) 里讨论过"为了禁欲，我选择不要这一行"。SANA-WM 的副本是："**为了在一张 GPU 上跑通，我选择不要 5 个数量级的参数**。"

这也连接到 [《Apple Silicon 比 OpenRouter 贵》](https://www.williamangel.net/blog/2026/05/17/offline-llm-energy-use.html) 这篇刚冒出来的小文章里的核心算式——**单个 token 的真实成本，最终由 model architecture × hardware 一起决定**。SANA-WM 把 throughput 提了 36×，相当于把"世界模型每秒生成成本"压到了 1/36。如果未来 5 年所有视频生成都被这种 efficiency arch 重写一遍，**整个 generative video 市场的单位经济学（unit economics）会被重新画**——这才是 NVIDIA 同时发论文 + 开源代码的真正意图。

最后一个观察：**SANA-WM 出现在一个所有人都在赌 GPT-5/Gemini-3 那种巨型模型会"解决一切"的时刻**。它选择反向押注："不，**有些问题不是 scale 问题，是架构问题**。"这种押注，过去十年在 BERT vs GPT、Transformer vs CNN、Mamba vs Attention 这些转折点上重复出现。每一次"小而美"路线都在巨型模型阴影下被低估，每一次都在三年后证明自己是基础设施。

## 五、配套资料导览

我为本文整理了以下配套资料（同目录下）：

- **`cover.svg`**：封面图（深色 + SANA-WM 关键词）
- **`mindmap.svg`**：技术拆解思维导图（架构 / 数据 / 训练 / 部署 / 评测）
- **`concept-cards.md`**：12 张关键概念卡片（GDN、UCPE、Plücker、Self-Forcing 等）
- **`glossary.md`**：英中对照术语表（35+ 条，覆盖世界模型、注意力、扩散三个领域）

## 六、谁应该读

- **视频生成 / 扩散模型方向研究者**：必读——hybrid attention 设计、双轨相机控制都是开箱即用的 receipt
- **机器人 / 具身智能从业者**：world model 是 sim2real 的核心组件，SANA-WM 把推理门槛降到单 GPU，可以本地跑大量 rollout
- **本地推理基础设施工程师**：NVFP4 + self-forcing 蒸馏 + attention sink 是组合拳，值得复用到其他 long-context 模型
- **AI 系统课程教师**：附录的 Triton kernel 设计、CP 训练分片是绝佳教学材料
- **产品 / 投资侧**：理解"小模型 + 高 throughput"路线对生成视频 unit economics 的颠覆

---

> 📂 **本文 slug**：`good-read-nvidia-sana-wm-minute-scale-world-model`
> 🏷️ **分类**：好文共赏 · 论文导读 · 世界模型
> 📅 **发布日期**：2026-05-18
