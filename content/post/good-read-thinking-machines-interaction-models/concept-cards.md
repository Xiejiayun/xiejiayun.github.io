# 概念卡片 · Interaction Models（Thinking Machines, 2026-05-11）

> 从 23,000 字的研究 preview 中蒸馏出来的 12 张概念卡片。每张卡片回答一个具体问题，可以独立带走。

---

## 卡片 1 · 交互模型（Interaction Model）

**一句话定义**
把"实时交互"作为一等公民、训练在权重里的多模态模型——而不是用 VAD + ASR + TTS + LLM 拼出来的 harness。

**关键区别**
| 项 | 传统 turn-based 模型 | Interaction Model |
| --- | --- | --- |
| 输入 | 等用户说完整句话 | 200ms 流式吃 |
| 输出 | 一次性生成完整回复 | 200ms 流式吐 |
| 边界 | VAD 外部组件判断 | 模型自己学到的 |
| 视觉打断 | 不存在 | 训练目标之一 |

**为什么重要**：因为按照 Sutton 的 Bitter Lesson，**手工编排的 harness 一定会被 end-to-end 训练超越**。

---

## 卡片 2 · 协作瓶颈（Collaboration Bottleneck）

**问题陈述**
今天的前沿模型最优化的指标是 "agent autonomy"——能不能脱离人完成长任务。但博客指出：现实工作里用户根本无法 upfront 把需求说清楚，他需要在过程中持续给反馈、纠正、interject。当模型只能 turn-based 交互，用户就被挤出了 loop。

**作者用的隐喻**：用 email 解决一场重要的吵架。

**学术加持**：博客同时引用了 Hayek（局部知识不可言说）、Scott（métis，意会的实践知识）、Clark & Brennan（grounding in communication 需要 copresence + contemporality + simultaneity）。这是少见的把社会学论文写进 release post 的做法。

---

## 卡片 3 · Bitter Lesson v2

**Sutton 原命题（2019）**
通用方法 + 算力，最终会击败任何人工特征工程。

**TML 的延伸**
> "For interactivity to scale with intelligence, it must be part of the model itself."

也就是说，把 turn detection、interruption logic、multimodal fusion 全部塞进 harness 是注定要被淘汰的；它们必须是模型本身能学到的能力。Sean Goedecke 在他的 commentary 里把这视为最有分量的论断。

---

## 卡片 4 · 200ms 时间对齐微轮次（Time-aligned micro-turns）

**机制**
- 每个 micro-turn = 200ms 输入 + 200ms 输出
- 输入/输出都是流，没有"轮次"概念
- 200ms 是个**目标延迟**：能让对话感觉自然，但又给模型留下足够的 decode 时间

**为什么不是 50ms 或 1s**
更短：prefill/decode 的开销吃掉所有时间，模型变蠢。
更长：人能感觉到延迟，"对话像 walkie-talkie"。
200ms 是人际对话中正常 turn 间隔的下沿（参考 Levinson 团队的跨语言研究）。

---

## 卡片 5 · 双模型分工：Interaction + Background

**Interaction model（前台）**
- 永远在线、低延迟
- 负责听 / 说 / 看 / 维持上下文
- TML-Interaction-Small：276B MoE，12B active

**Background model（后台）**
- 异步、可以慢
- 负责重推理、工具调用、长任务
- 通过 "rich context package"（不是 query，而是整段对话）被唤起

**回灌**
后台结果以流的形式传回，前台模型在合适的时机插入对话——而不是粗暴打断用户。

这个 split **解决了"实时性 = 必须蠢"的悖论**。

---

## 卡片 6 · Encoder-free Early Fusion

**传统多模态做法**：每个模态一个独立大 encoder（Whisper for 音频、CLIP for 图像），然后把 embedding 拼到 LLM 上下文里。

**TML 的做法**：
- 音频：dMel 表征 → 轻量 embedding 层
- 图像：40×40 patch → hMLP（Touvron et al. 2022 的 hierarchical MLP）
- 音频输出：flow head（Lipman et al. 2022）

**好处**：所有组件**和 transformer 一起从头联训**，没有 encoder/decoder 的 "translation tax"。代价是训练规模更大。

---

## 卡片 7 · Streaming Sessions 推理优化

**问题**
200ms 的小 chunk 意味着 prefill/decode 极频繁，每次都要 reallocate GPU memory + 重算 metadata，开销可能比模型本身还大。

**TML 的解法**
- 客户端把每个 200ms chunk 当 HTTP request 发送
- 推理服务器维护一个 **persistent sequence in GPU memory**，把 chunk 直接 append 进去
- 避免 reallocation + metadata 重算
- 已 upstream 到 SGLang

**意义**：这是 inference engine 设计上的一次重要转向——以前是 batched generation，现在要为 continuous streaming 重做接口。

---

## 卡片 8 · Trainer-Sampler Bitwise Alignment

**为什么要做**
RLHF/在线 RL 训练时，sampler（推理）和 trainer（反向传播）跑在不同 kernel/parallelism 策略上，得到的 token 分布会有微小差异，长期下来会 destabilize 训练。

**TML 用了什么**
- Batch-invariant kernels（小于 5% 性能开销）
- All-reduce / reduce-scatter 用 NVLS（NVLink Switch System）保证 Blackwell 上确定性
- Attention 选择 left-aligned Split-KV，让 prefill 和 decode 用相同累加顺序

**幽默小注**：博客提到，有一段时间 batch-invariant kernel 居然比标准 kernel 还快——因为附带的 comm 优化恰好抵消了开销。

这是 [《Defeating Nondeterminism in LLM Inference》](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/) 那篇前作的延续。

---

## 卡片 9 · 新交互维度：TimeSpeak / CueSpeak / Visual Proactivity

**TML 自己造的 benchmark**

**TimeSpeak**：模型能不能在用户指定的时间点主动开口？
- 例：「我要练习呼吸，请你每 4 秒提醒我吸气和呼气，直到我喊停」
- 评判标准：时间窗 + 语义内容都对才得分

**CueSpeak**：模型能不能在该说的时候和用户同时开口？
- 例：「每次我 code-switch 切到另一种语言，请告诉我原语言里对应的词」
- 强制评测 simultaneous speech 能力

**Visual Proactivity（RepCount-A / ProactiveVideoQA / Charades）**
- 「请数我做了多少个俯卧撑」——模型要从视频流里读时序
- 论文里直接放话：当前所有商用 API 都做不了，包括 thinking-high 模型

---

## 卡片 10 · 性能数字（精选）

| 指标 | TML-Interaction-Small | GPT-realtime-2.0 (minimal) | Gemini-3.1-flash-live (minimal) |
| --- | --- | --- | --- |
| Turn-taking latency (s) | **0.40** | 1.18 | 0.57 |
| FD-bench V1.5 平均 | **77.8** | 46.8 | 54.3 |
| FD-bench V3 Response Quality (%) | **82.8** (含 BG) | 80.0 | 68.5 |
| Audio MultiChallenge APR | **43.4** | 37.6 | 26.8 |
| IFEval (VoiceBench) | **82.1** | 81.7 | 67.6 |
| BigBench Audio | 75.7 / 96.5（含 BG） | 71.8 | 71.3 |
| HarmBench refusal rate | 99.0 | 99.5 | 99.0 |

**Sean Goedecke 的尖锐评论**：BigBench Audio 上 76% → 96.5% 的跃升靠开启 background reasoning model 实现，"算不算 fair comparison" 是个开放问题。

---

## 卡片 11 · 模型规模与对手

- TML-Interaction-Small：**276B 总参数 / 12B active**（MoE）
- Moshi：~7B
- Opus 4.7 / GPT-5.x：估算 1-3T+
- DeepSeek V4-Flash：类似量级

**意义**：TML 不在 frontier intelligence 上做竞争（他们说大模型在他们这套架构里"太慢"），但把 full-duplex 这个赛道从 "research-scale 玩具"（Moshi 量级）一口气推到 "production-grade frontier-grade"。

---

## 卡片 12 · 局限与未交付承诺

博客自己列了 5 个 limitation：

1. **长会话**：连续音视频流上下文增长快，需要更好的 context management
2. **算力/部署**：低延迟需要好的连接，弱网体验会显著退化
3. **Alignment / Safety**：real-time 改变了 attack surface
4. **更大模型**：作者承认现有更大的 pretrained 模型现阶段太慢，没法上线
5. **更强 background agent**：当前 "前台 + 后台" 协同还只是冰山一角

**未交付**：现在只是 research preview，**几个月后才会开放有限访问**。Sean Goedecke 提醒：在拿到真实使用前，所有 benchmark 都该打折看。
