# 关键概念卡片 · SU-01 论文 (arXiv 2605.13301)

每张卡 ≤ 120 字，便于快速复习。

---

### 卡 1 · Reverse-Perplexity Curriculum (反向 PPL 课程)

**是什么**：用 SFT 起点策略给所有训练轨迹打 PPL 分，每个 epoch 内**先难后易**呈现。

**为什么重要**：先用"陌生"轨迹塑形长 CoT 结构，再用"熟悉"轨迹巩固；论文消融显示这把 SFT 截断率从 8% 压到 0.3%。

**对比**：传统 CL 是 easy→hard，SU-01 反过来——因为目标是把**已经会答题**的后训练模型**改写**成会做证明的模型，而非从零教起。

---

### 卡 2 · P1-30B-A3B (骨架来源)

**是什么**：Chen et al. 2025 训出的物理奥赛 RL 模型，30B 总参 / 3B 激活的 MoE。

**关键点**：SU-01 不从 base 模型开始，因为后训练模型已经会"长思考"，只需 reshape；这让 SFT 只需 4 epoch + 8 GPU 就够。

**坑**：选错起点会折损（论文显式不推荐 base→SFT 路线）。

---

### 卡 3 · GSPO (Group Sequence Policy Optimization)

**是什么**：把 GRPO 的 token 级重要性比改为序列级长度归一化比；优势只减 group mean 不除 σ。

**好处**：(1) 与 MoE 路由器相容（无 token-level 路由扰动），(2) 对 100K+ token 长证明数值稳定，(3) 裁剪在 ε=1e-3 即可。

**出处**：Zheng et al. 2025，被 SU-01 直接采用。

---

### 卡 4 · 两阶段 RL：Verifiable → Proof-level

**Stage 1 (Coarse, 96 步)**：答案二值奖励（rule + Math-Verify + gpt-oss-120b 兜底）。把 SFT 丢失的答题力**先**找回。

**Stage 2 (Refined, 104 步)**：DeepSeekMath-V2 当生成式 judge，盯完整证明而非答案。专门攻 IMO-ProofBench Advanced 这种"答对了但证明松散"的题。

**顺序重要**：先 coarse 后 refined——proof RL 只有在 answer-policy 足够强时才收得动。

---

### 卡 5 · 三层 Verifier 级联

**层 1**：boxed 答案做规范化字符串匹配。  
**层 2**：Math-Verify 做符号 / 表达式等价。  
**层 3**：gpt-oss-120b 生成式裁决兜底。

**精神**：高精度规则在前，模型判定只处理残余的"长得不一样但其实对"的边角。

---

### 卡 6 · 生成式 Proof Judge (DeepSeekMath-V2)

**输入**：题目 + 候选完整证明。  
**输出**：二值 $r_{\text{proof}} \in \{0, 1\}$。

**部署**：32 GPU，32K 上下文，DP=64，EAGLE-MTP 投机解码 3 步。

**风险**：生成式 judge 容易被攻击（reward hacking）；SU-01 的对策是 prompt-preprocessing 把畸形 rollout 替换为占位答案。

---

### 卡 7 · 经验重放 (Targeted Replay)

**准入条件**：当前 batch 中 $0 < n^+(q) < 2$（"难但可解"）。

**轨迹选择**：从历史成功证明里挑**当前策略最确定**那条（$\arg\min \mathcal{H}$）。

**退役**：当 $n^+(q) \geq 4$ 删除——已经学会。

**重放占比**：$\rho = 0.25$。

---

### 卡 8 · 自精修 (Self-Refinement)

**触发**：组内平均奖励 < 0.5。  
**机制**：失败 rollout → "原题 + 错误草稿 + 修正提示" 重投。  
**注入比例**：$\eta_{\text{ref}} = 0.20$。  
**关键限制**：失败修正**不递归**入队——避免在不可学问题上烧 token。

---

### 卡 9 · Test-Time Scaling (TTS) 不是 best-of-N

**算法**：Solve → Verify → Refine 循环，模型自己当 verifier。

**控制三常数**：连续 5 次通过验证才接受；连续 10 次失败早停；单题最多 30 轮 + 10 并发。

**贡献**：把 IMO-ProofBench Advanced 从 38.1 推到 49.5；USAMO 2026 从 15 → 35（gold）。

---

### 卡 10 · IMO-ProofBench (Luong et al. 2025)

**结构**：分 Basic + Advanced 两档，看的是**证明质量**而不仅是答案。

**SU-01 + TTS 得分**：Basic 91.0 / Advanced 49.5 / Overall 70.2。

**位次**：超过 Gemini-2.5-DeepThink (60.7)，逼近 Gemini 3.1 Pro (72.6)，落后 GPT-5.5-High (80.7) 和 DeepSeekMath-V2 Heavy (80.5)。

---

### 卡 11 · USAMO 2026 金牌成绩

**SU-01 direct**：6 题得 15 / 42（bronze）。  
**SU-01 + TTS**：35 / 42 = 人类**单人最高分**（340 名参赛者中）。  
**金线**：25 / bronze 11。  
**未解题**：P2 — 涉及精细全局过程不变量证明。

---

### 卡 12 · IMO 2025 金牌成绩

**SU-01 direct**：21 / 42 (bronze)。  
**SU-01 + TTS**：35 / 42 — **正好压金线**。  
**未解题**：P6 — 模型用错了列置换归约（结构约束遗漏）。  
**比较**：Gemini 3.1 Pro Thinking 也在该题上失败。

---

### 卡 13 · IPhO 25 + 24 金牌

**direct (无 TTS)**：IPhO 2024 23.5 (金 ≥20.8) / IPhO 2025 20.3 (金 ≥19.7)。  
**+ TTS**：25.3 / 21.7。  
**意义**：**两届都不需要 TTS 就能拿金**——证明"统一配方"在物理域上也立得住。

---

### 卡 14 · 长 CoT 退化 (Through-the-Valley)

**现象**：在小模型上做长 CoT SFT 会**先掉**性能（"过 valley"）。SU-01 上 SFT 后 AnswerBench 69.2 → 59.8 (−9.4)。

**对策**：用 Coarse RL（+17.4）把答题力找回，再用 Refined RL 拉证明力。

**论文出处**：Luo et al. 2025 — 显式 SFT 退化的实证。

---

### 卡 15 · 反 hacking 输入预处理

**问题**：生成式 judge 容易被攻击——格式畸形的 rollout 反而拿高分。

**对策**：在送 judge 前若发现 chat template 泄漏、`\boxed{}` 未闭合、严重重复，用占位答案替换。

**坦白**：作者承认这只是"部分缓解"而非根治。

---

### 卡 16 · 失败模式 (作者自承)

1. IMO 2025 P6 未解 — 列置换归约错。  
2. USAMO 2026 P2 未解 — 全局策略不变量。

**规律**：当题目核心是**保持组合结构 / 精细过程不变量**时模型仍不稳。当题目有刚性形式表示（坐标、复数、模分类、自动机 DP）时表现最佳。

---

### 卡 17 · FrontierScience-Research OOD 表现

**未训练但测试**：化学、生物。SU-01 在同级开源里**最佳** (11.7%)，但绝对值低（GPT-5.5-High 36.7%）。

**结论**：**配方可迁移、能力没迁移**——证明 SU-01 不是过拟合到特定竞赛子集。

---

### 卡 18 · 资源核算

- **SFT**：8 GPU × 4 epoch（约一日级）。
- **RL**：64 GPU × 200 步（约 3–5 天级，根据 K=8 rollout、160K 上下文估）。
- **Judge 服务**：32 GPU × DSMath-V2 长驻。
- **总投入**：远低于 frontier 大模型训练成本——SU-01 的真正卖点是**配方在 30B 上跑得通**。

---

### 卡 19 · 与 AlphaProof 的关键差别

| 维度 | AlphaProof (DeepMind 2024) | SU-01 (2026) |
|------|---------------------------|--------------|
| 证明语言 | Lean 形式语言 | 自然语言 |
| 搜索 | 大规模符号搜索 | 验证-修正循环 |
| 训练 | 大规模自博弈 RL | 200 步 GSPO |
| 模型 | 闭源、未公布尺寸 | 30B-A3B、开源 |

**意义**：SU-01 证明在**自然语言侧**也能达到 IMO 金，把"形式化必要论"撼松一截。

---

### 卡 20 · 推理时计算的新算账

**单题中位**：solver 106K + refiner 83K + verifier 28.7K ≈ **218K tokens**，并行 10 条 × 至多 30 轮 → 最大 **数千万 token / 题**。

**寓意**：训练账只占总账一小角；要把 SU-01 类配方投入工程，**推理算力调度**才是新的瓶颈。

---

> **如何使用这些卡片**：先读卡 1–9（方法）→ 卡 10–13（成绩）→ 卡 14–20（局限与意义）。  
> 完整论文与原始数字见：<https://arxiv.org/abs/2605.13301>
