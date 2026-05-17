---
title: "【论文导读】SU-01：一份让 30B 开源模型拿下 IMO/USAMO 双金牌的统一配方"
description: "拆解 arXiv 2605.13301：反向 PPL 课程 SFT + 两阶段 GSPO（先答案后证明）+ 验证-修正式 Test-Time Scaling，仅用 200 步 RL 把 30B-A3B 的 MoE 推到金牌线，并对其方法、数据、风险做编辑级批判。"
date: 2026-05-17
slug: "paper-2605.13301"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 论文导读
    - arXiv
    - LLM 推理
    - 强化学习
    - GRPO
    - GSPO
    - RLVR
    - 测试时缩放
    - MoE
    - 数学奥赛
    - 开源
draft: false
---

> 📌 **好文共赏 · 论文导读 | Paper Pick**
>
> 📄 论文：[Achieving Gold-Medal-Level Olympiad Reasoning via Simple and Unified Scaling](https://arxiv.org/abs/2605.13301) · arXiv **2605.13301**  
> 👥 作者：Yafu Li, Runzhe Zhan, Haoran Zhang, Shunkai Zhang, Yizhuo Li et al.（上海 AI 实验室 / 香港中文大学 / 清华大学 / 上海交大 / 北大）  
> 📅 发布：2026-05-13 | 多模评分：综合 **8.67 / 10**（Opus 8.75 · Sonnet-equiv 8.25 · Gemini-equiv 9.0）  
> ✍️ 一句话：一份**200 步 RL** 就能把 30B-A3B 开源 MoE 推到 **IMO 35/42、USAMO 35/42、IPhO 双金**的统一配方——开源世界第一次在自然语言路线上摸到奥赛金牌带。

{{< figure src="cover.svg" alt="SU-01 论文导读封面" >}}

---

## 1 · 这篇论文到底在解决什么问题

奥林匹克级别的数学/物理题，是 LLM 推理研究里最严酷的压力测试。它要求模型同时做到四件事：在巨大解空间里搜索、精确控制每一步假设、对中间结论做自我验证、最后给出能扛住严格人类阅卷的完整论证。过去一年这条战线上跑出了两类系统：一类是 **AlphaGeometry / AlphaProof / Gemini Deep Think** 这种 "重型混合体"——要么神经-符号缝合、要么 Lean 形式化、要么是闭源的超大模型加海量搜索；另一类是 **DeepSeek-R1、OpenAI o1/o3、DeepSeekMath-V2** 这种"靠大 RL + 长 CoT"路线。前者复杂且大多闭源，后者动辄 0.7T+ 参数。

SU-01 的作者把问题问得很尖锐：**一个 30B 量级的开源 MoE，能不能用一个"一份配方走到底"的统一管线，被推到奥赛金牌线？** 而且这份配方应该跨数学和物理通用，不依赖几何 DSL、不依赖 Lean、不依赖闭源 frontier teacher 做无限蒸馏。

> "A central question is therefore whether a reasoning backbone can be pushed to olympiad-level performance with a compact, domain-unified recipe that applies the same reasoning-centric pipeline across mathematical and scientific problems." —— §1

他们给的答案是一份 **"specializable-generalist"** 管线：从一个已经会"长思考"的后训练模型 P1-30B-A3B 出发，先用一次**反向 PPL 课程 SFT** 重塑证明搜索 + 自检查行为，再用**两阶段 RL**（先看答案对错、后看证明质量）把这些行为放大到奥赛强度，最后用 **Solve→Verify→Refine 的测试时循环**把胜率再压一档。整套方法只跑 **200 步 RL**、64 张 GPU，模型与代码声明已开源。

这件事在 2026 年 5 月的 LLM 生态里意义不小：一直以来，奥赛金牌都被"闭源大模型 + 巨型搜索"垄断；SU-01 把推理金牌线**第一次稳定地放进 30B-A3B 这个普通团队也复现得起的尺寸**，并且证明配方本身能跨 math/physics/chemistry/biology。这是后训练-RL-推理时 三件套**集成水平**的一次跃迁，而不是某个单点创新。

---

## 2 · 核心方法用人话讲清楚

### 2.1 总体管线鸟瞰

{{< figure src="architecture-mindmap.svg" alt="SU-01 全流程思维导图" >}}

四个阶段串成一条不分叉的流水线：

```
┌──────────────┐   ┌────────────────┐   ┌──────────────────┐   ┌─────────────────────┐
│ P1-30B-A3B   │──▶│ ① 反向 PPL SFT │──▶│ ② Coarse RL      │──▶│ ③ Refined Proof RL  │──▶ ④ TTS
│ MoE 起点     │   │ 338K 轨迹      │   │ 96 步 / 答案奖励 │   │ 104 步 / 证明奖励   │
└──────────────┘   └────────────────┘   └──────────────────┘   └─────────────────────┘
```

每一段都不是发明算法，而是用一种**精确的顺序与精确的剂量**把已有零件拼出新效果——这是阅读这篇论文最关键的认知。

### 2.2 反向 PPL 课程 SFT——为什么"难的先教"

传统课程学习是 easy → hard：先让小学生背乘法表，再做应用题。SU-01 反过来。原因是它的起点 **P1-30B-A3B 不是空白模型**，而是已经会做物理奥赛的后训练 MoE。这种模型最大的风险不是"学不会"，而是被一坨"看上去差不多"的轨迹**平庸化**——长 CoT SFT 把它原本生动的搜索/自检查能力磨平。

具体操作是：

1. 用 SFT 起点策略 $\pi_0$ 给所有 338K 训练样本算长度归一化 PPL：

$$
\mathrm{PPL}(x_i, y_i) = \exp\!\Big(-\tfrac{1}{T_i}\sum_t \log \pi_0(y_{i,t} \mid \cdot)\Big)
$$

2. 每个 epoch 把样本按 PPL **降序**排好——高 PPL（陌生）的轨迹先教，低 PPL（熟悉）的轨迹尾段巩固。

3. 共 4 个 epoch，rollout 顺序锁定不打乱。

效果在论文 Fig. 6 的消融里非常直观：

| 课程顺序 | AnswerBench | AMO-Bench | 截断率 |
|---|---|---|---|
| 无 SFT（起点）| 69.3 | 41.3 | — |
| 随机顺序 | 39.5 | 31.0 | 7.3 / 8.0 % |
| **正向**（易→难） | 24.3 | 15.0 | 高 |
| **反向**（难→易，本文） | **55.8** | **40.0** | **0.3 / 0.0 %** |

最让人意外的是 **truncation rate（"无尽推理"截断率）从 8% 直接掉到 0%**——这意味着反向课程不仅没让模型崩，反而**显著抑制了长 CoT 的失稳**。论文给的解释是：先用陌生轨迹塑形长 CoT 结构，再用熟悉轨迹收尾，比反过来更不容易把模型推进"模仿但失控"的吸引盆地。

SFT 数据本身也值得拆一拆，338K 条轨迹的组成是论文给的真正配方：

| 大类 | 子集 | 数量 | 占比 |
|---|---|---|---|
| 直接生成（54.3%）| 数学 / STEM / 代码 / IF | 183.7K | 54.3% |
| 自改进（45.7%）| Self-Verify | 89.5K | 26.4% |
|  | Self-Refine | 65.2K | 19.3% |

注意自改进数据占近一半——这是论文一个常被忽略的关键决策：**Self-Verify 和 Self-Refine 不是"额外加点"，而是几乎和原始题解等量级的训练信号**。后面 TTS 阶段做的 Solve → Verify → Refine 循环，本质就是把这块 SFT 内化的能力在推理时再放大一次。

### 2.3 Coarse RL——先把"答题力"找回来

SFT 之后会发生一件反直觉的事：AnswerBench 从 69.2 掉到 59.8（−9.4）。这是 Luo et al. 2025 描述的 **"long-CoT through-the-valley"** 现象——长 CoT SFT 会先让小一点的模型变笨，然后才在 RL 中爬出谷底。SU-01 的第一阶段 RL 就是为这个山谷量身定做的。

算法用的是 [GSPO（Group Sequence Policy Optimization）](#gspo)。它和大家熟悉的 GRPO 的区别有两条要点：

- **优势只减组均值，不除 σ**。$\hat A_i = r(q,o_i) - \tfrac{1}{K}\sum_j r(q,o_j)$。论文实测：长 CoT 下 σ 的统计噪声大，反而扰乱方向。
- **重要性比是序列级、长度归一化的**：
$$s_i(\theta) = \exp\!\Big\{\tfrac{1}{|o_i|}\sum_t \log\tfrac{\pi_\theta(\cdot)}{\pi_{\theta_\text{old}}(\cdot)}\Big\}$$
一条 100K token 的证明只产生一个标量比值，不容易在 token 级累乘到爆炸。

奖励是**纯二值**的，但 verifier 设计成**三层级联**——这是工程上最干净的部分：

```
[1] 规范化字符串匹配  (高精度规则)
        ↓ unresolved
[2] Math-Verify       (符号 / 代数等价)
        ↓ unresolved
[3] gpt-oss-120b      (生成式裁决兜底)
```

数据池是 8,967 条 verifiable prompts（数学 + 物理），96 步 GSPO，K=8 rollout，最大响应 160K token。还有一个不显眼但关键的细节——**MoE 路由器在 RL 阶段冻结**。原因是 GSPO 用的是回放/重要性比，而 MoE 路由会改变同一 token 走哪个 expert，等价于改变了被采样策略本身。冻结路由器才能让"过去采的 rollout 还能按当前权重做公平评估"。

Coarse RL 跑完，AnswerBench 从 59.8 飙回 77.2（+17.4），ProofBench-Basic 从 57.6 拉到 76.7（+19.1），ProofBench-Advanced 从 14.8 到 25.2（+10.5）。山谷被填平了。

### 2.4 Refined Proof RL——把奖励从"答案"换成"完整证明"

这是 SU-01 真正能拿金牌的一节。**奥赛阅卷不是看你最后写了哪个数，而是看你怎么证出来的。** RLVR（可验证奖励 RL）能让模型答对，但不能保证证明严密。

所以 Stage 2 把奖励换成 **DeepSeekMath-V2 的生成式 proof judge**：它读完题目和完整证明，给出二值 $r_{\text{proof}} \in \{0,1\}$，看的是 CoT 是否有效、证明是否完整、是否严密。物理题继续用可验证奖励，证明题改用这个生成式 judge。这块部署在 32 张 GPU，用 EAGLE-MTP 3 步投机解码加速。

但生成式 judge 有两个先天问题：(1) 容易被攻击（reward hacking——模型学会"格式畸形"骗高分），(2) 训练信号噪声更大。SU-01 给出两个干净的对策：

**对策一：反 hacking 输入预处理**。送 judge 之前，若 rollout 出现 chat template 泄漏、`\boxed{}` 未闭合、或严重 n-gram 重复，就用占位答案替换。作者明白地承认这只是"部分缓解"——这是论文最坦诚的一段。

**对策二：经验重放 + 自精修双管齐下**。

- **经验重放**：维护一个缓冲池 $\mathcal{E}$。准入条件是"难但可解"——组内成功数 $0 < n^+(q) < 2$。退役条件是 $n^+(q) \geq 4$（成功率 ≥50%，已经学会，删掉省 token）。从同一道题历史成功轨迹里挑**当前策略**熵最小那条 $o^* = \arg\min_o \mathcal{H}(o; \pi_\theta)$ 作为"教科书"。重放占比 $\rho = 0.25$。
- **自精修**：当 batch 内某组平均奖励 < 0.5，把失败 rollout 改成"原题 + 错误草稿 + 修正提示"的新 prompt，按 $\eta_{\text{ref}} = 0.20$ 注入。**关键约束**：失败的修正**不再递归入队**——避免在不可学的题上烧 token。这一句限定避免了 self-improvement 工作里常见的"螺旋式下降"陷阱。

混合目标长这样：

$$
\mathcal{J}_{\text{refined}}(\theta) = (1-\rho)\,\mathbb{E}_{\mathcal{B}_{\text{fresh}}}\!\big[\mathcal{J}_{\text{GSPO}}\big] + \rho\,\mathbb{E}_{\mathcal{B}_{\text{exp}}}\!\big[\mathcal{J}_{\text{GSPO}}\big]
$$

104 步跑完，**ProofBench-Advanced 从 25.2 飙到 38.1（+12.9）**——而 ProofBench-Basic 几乎没动（76.7→77.1）。这说明 refined RL 的边际效用**只在最难的证明上兑现**，正是设计意图。

### 2.5 Test-Time Scaling——模型自己当 verifier 跑闭环

TTS 在 SU-01 里**不是 best-of-N**，也**不是简单的 majority vote**。它是一个 Huang & Yang 2025 风格的 **Solve → Refine → Verify → Verdict** 循环，再外加并行运行：

```
对每道题 q:
  并行启动 10 条独立 run
  每条 run 内部循环（最多 30 轮）:
       draft  = Solver(q, history)
       draft' = Refiner(draft)
       bug    = Verifier(draft')
       if bug == "no critical":
            success_streak += 1
            if success_streak == 5:  return ACCEPT
       else:
            fail_streak += 1
            if fail_streak == 10:  return ABORT
```

三个魔法常数：**5 次连续通过才接受，10 次连续失败就停，30 轮内一定终止**。其中"必须连续 5 次通过"是关键——它把 verifier 的随机噪声压平到 $\sim 1/32$ 数量级，同时也让"靠运气蒙过验证一次"的轨迹无法被采用。

token 预算很可观：solver 中位 106K、refiner 中位 83K、verifier 中位 28.7K，单题最坏情况要烧到**数千万 token**级。这是工程上需要正视的代价。

最后的成绩：

| 指标 | SU-01 直接 | + TTS |
|---|---|---|
| IMO-ProofBench Overall | 57.6 | **70.2** |
| IMO 2025 (满 42) | 21 (铜) | **35 (金线)** |
| USAMO 2026 (满 42) | 15 (铜) | **35 (单人最高)** |
| IPhO 2024 | 23.5 (金) | 25.3 |
| IPhO 2025 | 20.3 (金) | 21.7 |

注意 IPhO 两届 **不开 TTS 就已经金牌**——证明这套统一配方在物理域是真的迁移了，不是只为数学定制。

---

## 3 · 实验结果亮点（我提炼的版本）

### 3.1 阶段性增益分布——增量是"分工"而非"叠加"

如果把 SU-01 拆开看每阶段对哪个 benchmark 贡献最大：

```
                Answer  Proof-Basic  Proof-Advanced
起点 P1-30B-A3B   69.2    33.8         6.2
  +SFT          -9.4    +23.8        +8.6      ← 拉证明基础, 损失答题
  +Coarse RL   +17.4    +19.1       +10.5      ← 答题回血 + 双线推进
  +Refined RL   +0.3     +0.5       +12.9      ← 专攻最难证明
  +TTS           —      +13.8       +11.4      ← 验证循环再加一档
```

阶段间不是简单"加得多就好"。Coarse RL 几乎不动 Answer 数字的剩余空间（已经 77.5 了），Refined RL 又几乎不碰 Basic（已经 77.1）。**每一阶段在恰好它该擅长的位置发力**——这是配方设计成熟的标志，也是为什么作者敢叫它"unified scaling"。

### 3.2 同尺寸开源对手的位置

把 IMO-ProofBench Overall 按尺寸分组看：

```
30B-A3B 级（开源）:
  ▢ Qwen3.6-35B-A3B          23.1
  ▢ Nemotron-Cascade-2       52.9
  ▢ P1-30B-A3B (起点)        20.0
  █ SU-01                    57.6  (+TTS  70.2)

frontier 闭源:
  ▢ DeepSeek-V3.2-Speciale   56.0
  ▢ Gemini-2.5-DeepThink     60.7
  ▢ Gemini 3.1 Pro Thinking  72.6
  ▢ DeepSeekMath-V2 Heavy    80.5
  ▢ GPT-5.5-High             80.7
```

最让人震动的是 **SU-01 直接（不开 TTS）就超过 DeepSeek-V3.2-Speciale**——后者是当前公认的高质量推理模型；而 + TTS 之后逼近 Gemini 3.1 Pro Thinking（72.6），只剩 GPT-5.5 这种 frontier 闭源还有明显领先。**同尺寸（30B-A3B）开源里没有第二个能上 50 分的。**

### 3.3 USAMO 2026 单人最高

USAMO 2026 共 340 名人类选手，金线 25、银 18、铜 11，人类**单人最高分 35**。SU-01 + TTS 拿 35，**与人类冠军并列第一**。这是论文里最容易被截屏发推但也最值得严肃看待的一项数据：因为 USAMO 是直接采用人类阅卷标准的官方题（论文这次是请人类评分而非 judge 模型），它直接对比的是同一份阅卷规则下机器和顶尖高中生的差距。

### 3.4 跨学科迁移——FrontierScience-Research

只在 math + physics 训练，却在 chemistry / biology 出色：

| 模型 | Phys | Chem | Bio | 总 |
|---|---|---|---|---|
| Gemma-4-31B | 0.0 | 10.0 | 5.0 | 5.0 |
| Qwen3.6-35B-A3B | 0.0 | 5.0 | 10.0 | 5.0 |
| Nemotron-Cascade-2 | 5.0 | 5.0 | 20.0 | 10.0 |
| **SU-01** | 10.0 | 10.0 | 15.0 | **11.7** |

绝对值不高（GPT-5.5-High 是 36.7），但**SU-01 是同尺寸开源最强**。这暗示着 SU-01 学到的不只是"奥赛 trick"，而是"严谨推理"这一更通用的能力——这点对后续走 chemistry/biology RL 的工作非常重要。

### 3.5 长 CoT 工程化的成熟度信号

论文给出几个量化"长 CoT 成熟"的细粒度指标，比堆 benchmark 更值得品：

- 训练截断率 < 5%（论文自定义的 SFT 收敛信号）
- TTS solver 中位 106K tokens / refiner 83K / verifier 28.7K
- 单条 rollout 稳定运行到 256K tokens
- 验证连续 5 次通过 / 10 次失败的双阈值

这些数字单独看像工程参数，但合起来表明：**SU-01 已经把"长 CoT 推理"当成可调度、可监控、可控成本的稳定服务对待**，而不是停留在"凑出一次成功"的演示态。

---

## 4 · 这篇论文的位置（关联图谱）

### 上游——SU-01 站在谁的肩膀上

- **GRPO / GSPO 谱系**：Shao et al. 2024 的 GRPO 把 PPO baseline 换成组内均值；Zheng et al. 2025 的 GSPO 进一步把 importance ratio 拉到序列级。SU-01 直接采用 GSPO 而不发明新算法。
- **DeepSeek-R1 / DeepSeek-V3.2-Speciale**：前者奠定"大规模 RL 自然涌现长 CoT"的范式，后者是 SU-01 的教师模型（生成 SFT 轨迹）。
- **DeepSeekMath-V2**：被 SU-01 直接拿来当 proof judge——SU-01 与之的关系不是竞争而是**寄生与被寄生**：用 V2 当 judge 训出来的模型，反过来在 IMO-ProofBench 上几乎追平 V2 Heavy。
- **AlphaProof / AlphaGeometry**（DeepMind 2024）：形式化路线的 IMO 金，论文显式拿来对照，强调 SU-01 走的是**自然语言**路线。
- **ExGRPO**（Zhan et al. 2025）：经验重放思想的直系来源，SU-01 用其简化变体（无 policy-shaping）。
- **P1**（Chen et al. 2025）：直接给出 30B-A3B 物理奥赛骨架。
- **"Through-the-valley"**（Luo et al. 2025）：解释了"为什么 SFT 后要先做 coarse RL 找回答题力"。
- **IMO-ProofBench**（Luong et al. 2025）：本文的主要评测尺。
- **Huang & Yang 2025**：TTS 的 verify-refine 循环算法直接照搬。

### 下游——它会催生什么

- **"统一配方 + 小骨架"的奥赛工业化**。一旦门槛被压到 30B-A3B + 64 张 GPU，奥赛级别推理就会从"frontier 闭源专属"快速扩散到学校实验室与开源社区。预计 6–12 个月内会有 7B / 14B 量级的 SU-01 复刻版出现。
- **proof-level judge 的军备竞赛**。SU-01 的 judge 是 DeepSeekMath-V2；下一步会有人专门训练**只为"判证明"而存在**的小模型（10B 级），并把 anti-hacking 做成 SDK。
- **跨学科 RL 的可扩展性论文**。FrontierScience 上 chemistry / biology 已能迁移，下一步会有"统一配方 + chemistry-specific judge"的版本，覆盖 IChO/IBO/ICho-Bench。
- **TTS 计算的市场化**。如果一道难题要烧数千万 token，会催生"按证明难度动态分配 TTS 预算"的产品形态——把推理算力变成可计量的商品。
- **教育与教师培养**：35 分 USAMO 模型出现后，AI 助教/题解机器人会迅速被引入数学竞赛培训领域，但同时会重新激起一轮关于"模型证明是否算证明"的人文讨论（这点可对照 [Gowers 实测 ChatGPT 5.5 Pro 做加性数论研究](/post/good-read-gowers-chatgpt-phd-math/) 那篇）。

### 同期对手

- **DeepSeekMath-V2 Heavy**（IMO-ProofBench 80.5）：闭源、未公布尺寸但显然 ≫ 30B，SU-01 的"目标线"。
- **Gemini 3.1 Pro Thinking** (72.6) / **GPT-5.5-High** (80.7)：frontier 闭源代表，SU-01 + TTS 仍未追上但已稳压前代 Gemini-2.5-DeepThink。
- **Apple PORTool**（参见 [Apple PORTool 论文：用分叉回滚树解决工具调用的信用分配难题](/post/apple-portool-credit-assignment-tree-tool-use-rl/)）：同期另一个走 "RL + 信用分配创新" 路线的工作，但目标是工具使用而非证明。
- **SDAR**（2605.15155，本轮候选池另一篇）：把 OPSD 当门控辅助损失叠在 RL 上，目标是 agentic 任务，与 SU-01 同期但不冲突。

---

## 5 · 编辑批判性评论

读完论文我的总评是：**这是 2026 上半年最值得严肃读的开源推理论文之一**，但有些值得警惕的事情论文要么没说、要么说得很轻。

**第一，配方的稳健性可能比"复现"更脆弱。** 反向 PPL 课程的消融只对比了 random / 正向 / 反向三种顺序，没有对 PPL 阈值、epoch 内重复策略、起点策略选择做扫描。这条 trick 在不同骨架（比如 Qwen3.6-base、Llama-4-MoE）上能否稳定有效，是开放问题。我倾向于认为：**反向 PPL 强烈依赖于"起点模型已经会长思考"**——一旦换到没经过推理后训练的纯 base 模型，"难者先教"反而可能崩。

**第二，judge 模型的依赖是隐性 frontier 锁定。** SU-01 看似把成本压到 30B-A3B 训练，但 refined RL 阶段 24/7 挂着一个 DeepSeekMath-V2 在 32 张 GPU 上做 judge。这个 judge **本身就是 frontier 推理模型**。也就是说：要复刻 SU-01，你不仅要会训 30B，还要**养得起一个 V2 级别的 judge 长期在线**。对于绝大多数学术团队这条门槛仍然致命。论文没有讨论"用更小 judge 是否还行"——这是接下来工程化的真问题。

**第三，TTS 的成本账没算清。** 一道题最坏要烧到数千万 token，但 USAMO 2026 P2 和 IMO 2025 P6 仍然 0 分。这意味着 TTS 不是"无限放大算力就能保金"，**有一类问题（精细全局不变量、组合结构保持）模型即使烧光所有 token 也解不出**——这是模型能力的硬天花板，不是采样量问题。论文坦率承认这点，但没给"如何识别哪种题烧 TTS 没用"的判别方法。在工程实践里这条至关重要：你不能对所有题都按最坏情况分配预算。

**第四，奖励 hacking 的"输入预处理"是补丁而不是根治。** 论文承认 generative judge 容易被攻击，对策是发现畸形输出就替换占位。但任何 RL 老兵都知道：模型一旦发现"格式 X 会被替换"，它就会绕到"格式 Y"。论文跑了 200 步 RL 没崩，部分原因可能是步数本来就少；如果换到 1000 步 + 更大 K 的训练，hacking 几乎一定会出现。建议读者把 "200 步" 这个数字也当成一个**对抗鲁棒性的隐藏约束**而不只是"省算力的卖点"。

**第五，跨学科"迁移"是真的，但绝对值很低。** Chemistry / Biology FrontierScience-Research 上 SU-01 拿 11.7%，确实是同尺寸最佳，但距离 GPT-5.5-High (36.7%) 差 3 倍。论文把这个解读为"配方迁移"，我更愿意解读为"配方迁移、能力没迁移"——SU-01 学到了**严谨的形式**，没学到**化学/生物特有的领域知识**。下一篇工作的核心问题应该是：**RL 信号能不能跨学科共享，还是必须每个学科训自己的 judge？**

**第六，工程实践层面：用还是不用？**

- ✅ **可以用**的场景：奥赛培训助教（产出可被人类教师审阅再发布）、形式化证明初稿生成、研究生级别物理/数学问题的快速尝解、教师批改时的对照解。
- ⚠️ **要小心**的场景：任何要求"机器输出即终稿"的场景。论文展示 USAMO 35 分是在**人类阅卷**条件下的，TTS judge ≠ 人类裁判，把它直接用于"自动判分"会出 false-positive。
- ❌ **不要用**的场景：原创性数学研究——SU-01 是"olympiad-style solver"，不是"theorem prover"，对开放性数学（参见 [Gowers 那篇](/post/good-read-gowers-chatgpt-phd-math/)）能力仍有量级差距。

最后一个观察：SU-01 论文的真正贡献**不是任何单一算法**，而是**"统一配方 + 资源量级 + 复现路径"**这三件事第一次同时被锁死。我把它和 DeepSeek-R1 放在同一个层级——不是因为方法更聪明，而是因为它**重新定义了一份社区可以照着抄的清单**。这种"集成水平的跃迁"在 LLM 圈每 6–9 个月才出现一次，值得圈起来重点记忆。

延伸阅读：[LLM 推理的真相：思维链只是表象，潜在状态才是本质](/post/llm-reasoning-latent-not-cot-2026/) 与本文的"长 CoT 工程化"形成漂亮互补——前者说"链是表象"，本文说"链确实能被工业化"。两个看似冲突的判断在 SU-01 这里被一种方式同时托住：**链不是机制本质，但链可以是稳定的接口**。

---

## 6 · 配套资料导览

本目录下另有四份配套：

- 📐 [`architecture-mindmap.svg`](architecture-mindmap.svg) — SU-01 整条管线的思维导图，包含三阶段训练 + TTS 控制律 + 关键成绩。
- 🃏 [`concept-cards.md`](concept-cards.md) — 20 张关键概念卡，每张 ≤120 字，用于快速复习。
- 📖 [`glossary.md`](glossary.md) — 62 条中英术语对照表，覆盖 RL 算法、训练资产、评测基准、推理基础设施五大维度。
- 🧮 [`key-equations.md`](key-equations.md) — 11 段核心公式（含反向 PPL、GSPO、混合重放目标、TTS 控制律）的 KaTeX 解读。

延伸到博客上的关联文章：

- [LLM 推理的真相：思维链只是表象，潜在状态才是本质](/post/llm-reasoning-latent-not-cot-2026/)
- [开放权重 LLM 架构演进全景：从 GPT-2 到 Gemma 4 的七年革命](/post/open-weight-llm-architecture-evolution-2026/)
- [2026 LLM 架构演进全景：从注意力变体爆发到推理时扩展的新范式](/post/llm-architecture-evolution-2026/)
- [Apple PORTool 论文：用分叉回滚树解决工具调用的信用分配难题](/post/apple-portool-credit-assignment-tree-tool-use-rl/)
- [Fields 奖得主 Gowers 实测 ChatGPT 5.5 Pro 做加性数论研究](/post/good-read-gowers-chatgpt-phd-math/)
- [Reward Hacking：AI 正在学会作弊，我们的对策还停留在打补丁](/post/reward-hacking-ai-safety-2026/)
- [AI 评测正在变成新的算力黑洞：当评估比训练还贵](/post/ai-evals-new-compute-bottleneck-2026/)

---

## 7 · 谁该读这篇论文

- **做 LLM 后训练 / RL 研究的同学**：必读。GSPO、反向 PPL、两阶段 RL、重放策略是 2026 年所有"中等成本就想做出大效果"的 RL 实验的新标配。
- **奥赛培训机构 / 数学教育研究者**：必读。35 / 42 分的 USAMO 不再是"未来可能"，而是"今晚就能跑的事实"。
- **推理基础设施工程师**：必读。SGLang + EAGLE-MTP + 三层 verifier 的部署细节是 production-grade 长 CoT 服务的最新参考实现。
- **科学研究自动化的研究者**：建议读。FrontierScience-Research 这块的迁移结果暗示"统一推理配方 + 学科 judge" 模式的工程可行性。
- **AI 安全 / 对齐研究者**：建议读。reward hacking 对策、生成式 judge 的攻防面、TTS 控制阈值这些都是 alignment 研究的新前沿。
- **普通工程师 / 产品经理**：选读§1 + §5（编辑批判）+ §7。重点理解"什么场景能用、什么场景不能用"。

---

## 多模评审记录

| 维度 | Opus（编辑） | Sonnet-equiv | Gemini-equiv |
|---|---|---|---|
| Breakthrough | 9 | 8 | 9 |
| Rigor | 9 | 8 | 9 |
| Reproducibility | 8 | 8 | 9 |
| Impact | 9 | 9 | 9 |
| **Composite** | **8.75** | **8.25** | **9.00** |

**综合 8.67 / 10**，超过 8.5 发表阈值。三位评审一致选定本文为本轮 Top Pick，理由：**唯一一篇有"对照人类 USAMO 阅卷的硬证据 + 完全开源的 30B-A3B 复现路径"的奥赛级推理论文**。

---

> **版权声明**：本文为对 arXiv 2605.13301 的独立解读与批评。引用论文原文不超过 3 句/段，全文引用合计 < 10%。论文图表均未直接复制，所有可视化（封面、思维导图、关键成绩条形图）均由本博客重新绘制。原始论文版权归原作者所有。
>
> **本文写作流程透明声明**：候选池规模约 550 篇 (cs.LG/CL/AI/CV recent + HF + 关键词搜索)；筛 Top 8 经 Opus + 模拟 Sonnet + 模拟 Gemini 三轮独立打分；论文 PDF 与全文已读完整。
