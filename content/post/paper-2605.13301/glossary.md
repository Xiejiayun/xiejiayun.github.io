# 术语表 · SU-01 论文 (arXiv 2605.13301)

中英对照，按字母 / 拼音顺序。

| 缩写 / 英文 | 中文 | 释义 |
|---|---|---|
| **30B-A3B** | 30B 总参 / 3B 激活 MoE | "Active 3B" 是 MoE 每 token 实际激活的专家参数量；30B 是总参；SU-01 的骨架 P1-30B-A3B 即此结构 |
| **Advantage (优势)** | 优势 | RL 中 "本条 rollout 比基线好多少"；SU-01 用组均值作基线 |
| **AlphaGeometry** | AlphaGeometry | DeepMind 2024 用神经-符号混合解 IMO 几何题，是 olympiad LLM 的奠基工作 |
| **AlphaProof** | AlphaProof | DeepMind 2024 用 Lean 形式语言 RL 拿 IMO 银/金，与 SU-01 走自然语言路线形成对照 |
| **AMO-Bench** | AMO 基准 | 数学奥赛题目集，论文用作 answer-bench 之一 |
| **AnswerBench** | 答案基准 | 测的是 "解题答案" 是否正确，与 ProofBench 互补 |
| **ASCII / Mermaid** | ASCII / Mermaid | 文中流程图绘图工具 |
| **CoT (Chain of Thought)** | 思维链 | LLM 在输出最终答案前显式推理的中间步骤；Wei et al. 2022 提出 |
| **Causal Forcing++** | 因果强制++ | 同期 arXiv 2605.15141 的视频生成方法，与 SU-01 同期但方向不同 |
| **Coarse RL** | 粗 RL | SU-01 第一阶段 RL，目标只看最终答案，96 步 |
| **Curriculum Learning** | 课程学习 | 按难度排序训练样本的训练范式；SU-01 用反向（难→易）变体 |
| **DeepSeek-R1** | DeepSeek-R1 | 开源大规模 RL 推理模型，被 SU-01 列为"长 CoT RL 的奠基者"之一 |
| **DeepSeek-V3.2-Speciale** | DeepSeek-V3.2-Speciale | 教师模型：用于生成 SFT 轨迹 |
| **DeepSeekMath-V2** | DeepSeekMath-V2 | 数学专长模型，SU-01 用其 Judge 变体做 proof-level 奖励 |
| **DSA / MLA Attention** | DSA / 多头潜在注意力 | DeepSeek 系列引入的注意力变体；MinT 论文（2605.13779）讨论 |
| **EAGLE / EAGLE-MTP** | EAGLE 投机解码 | 加速推理的 speculative decoding 框架；SU-01 部署 judge 时用 3 步 EAGLE-MTP |
| **Eval / Verifier (评估器/验证器)** | 评估器 / 验证器 | 给 RL 提供奖励信号的判定器；SU-01 用三层级联 |
| **ExGRPO** | ExGRPO | Zhan et al. 2025 的经验重放版 GRPO；SU-01 用其简化版 |
| **FrontierScience** | 前沿科学基准 | 跨 P/C/B（物化生）的 olympiad / research-style 题集 |
| **Gemini Deep Think** | Gemini Deep Think | Google DeepMind 拿 IMO 金的闭源系统 |
| **GPQA** | GPQA | 研究生层级 QA 基准；论文未直接报告（OOD 探针用 FrontierScience-Research 替代） |
| **GRPO** | 群体相对策略优化 | Shao et al. 2024 提出，DeepSeekMath 用的核心 RL 算法 |
| **GSPO** | 群体序列策略优化 | Zheng et al. 2025；token→sequence 级；SU-01 实际采用 |
| **gpt-oss-120b** | gpt-oss-120b | OpenAI 开源模型，用作 SU-01 第三层 verifier 兜底 |
| **Hardness Filter** | 难度过滤 | 在 RL 训练时剔除当前策略可 0% / 100% 解的题 |
| **IMO** | 国际数学奥林匹克 | International Mathematical Olympiad，6 题 × 7 分 = 42 满分 |
| **IMO-ProofBench** | IMO 证明基准 | Luong et al. 2025 提出；分 Basic / Advanced 两档评分 |
| **Importance Ratio (重要性比)** | 重要性采样比 | $\pi_\theta / \pi_\text{old}$；SU-01 在序列级长度归一化后再做 clip |
| **In-context Learning** | 上下文学习 | LLM 不更新权重，只靠 prompt 学新任务 |
| **IPhO** | 国际物理奥林匹克 | International Physics Olympiad，理论 30 分 + 实验 20 分 |
| **Judge Model (判官模型)** | 判官模型 | 给 RL 提供奖励的生成式评分器；SU-01 用 DeepSeekMath-V2 |
| **K (rollout 组大小)** | 组采样数 | 每个 prompt 采样多少条 rollout；SU-01 K=8 |
| **KL (Kullback-Leibler)** | KL 散度 | RL 中常用作正则项；SU-01 KL coef = 0 |
| **Long-CoT Degradation** | 长 CoT 退化 | 长 CoT SFT 让模型先掉点的现象（Luo et al. 2025）；SU-01 用反向 PPL + Coarse RL 修复 |
| **LoRA** | 低秩适应 | 参数高效微调；与 SU-01 关联较弱（论文用全量微调） |
| **Math-Verify** | Math-Verify | 规则 + 符号代数验证器，SU-01 verifier 第二层 |
| **MoE** | 混合专家 | 每 token 只激活部分专家的稀疏架构；SU-01 骨架是 MoE |
| **MoE Router** | MoE 路由器 | 决定 token 走哪个 expert；SU-01 RL 阶段**冻结** |
| **OPC (Open Proof Corpus)** | 开放证明语料 | Dekoninck et al. 2025；refined RL 数据源之一 |
| **OOD (out-of-distribution)** | 分布外 | SU-01 用 chemistry / biology 测 OOD 迁移 |
| **OPSD** | 在线策略自蒸馏 | On-Policy Self-Distillation，2605.15155 SDAR 用 |
| **PPL (Perplexity)** | 困惑度 | 模型对一段文本"不熟"的程度；SU-01 课程的排序键 |
| **PPO** | 近端策略优化 | RL 经典算法；GRPO/GSPO 都源自它 |
| **ProofBench-Basic** | 证明基准 - 基础 | IMO-ProofBench 较易档 |
| **ProofBench-Advanced** | 证明基准 - 进阶 | IMO-ProofBench 难档；SU-01 的最大涨幅来源 |
| **P1-30B-A3B** | P1-30B-A3B | Chen et al. 2025 物理奥赛 RL 模型，SU-01 直接初始化自此 |
| **Replay Buffer** | 经验重放池 | 存历史成功 rollout 以供后续 RL 复用 |
| **Reward Hacking** | 奖励黑客 | 模型钻 verifier 漏洞拿假奖励；SU-01 用输入预处理部分缓解 |
| **Reverse-PPL Curriculum** | 反向 PPL 课程 | SU-01 核心 SFT trick，难者先教 |
| **RL** | 强化学习 | Reinforcement Learning |
| **RLVR** | 可验证奖励 RL | RL with Verifiable Rewards；Lambert et al. 2024 / Tulu 3 |
| **Rollout** | 采样轨迹 | RL 中策略采样得到的一条完整轨迹 |
| **SDAR** | 自蒸馏 Agentic RL | 2605.15155，另一篇候选论文 |
| **SFT** | 监督微调 | Supervised Fine-Tuning |
| **SGLang** | SGLang | 高性能 LLM serving 框架；SU-01 inference 默认后端 |
| **slime** | slime | THUDM 出品 RL 训练框架，SU-01 用它做训练 |
| **Specializable-Generalist** | 可特化-泛化体 | SU-01 用语：通用模型经精修后专精，但不失泛化 |
| **SU-01** | SU-01 | 本论文模型名（Shanghai-United-01 推测） |
| **Token-level vs Sequence-level Clipping** | token 级 / 序列级裁剪 | PPO/GRPO vs GSPO 的核心差异 |
| **TTS** | 测试时缩放 | Test-Time Scaling；SU-01 用 verify-refine 循环 |
| **USAMO** | 美国数学奥林匹克 | USA Math Olympiad；6 题 × 7 分 |
| **Verifiable Reward** | 可验证奖励 | 由确定性 verifier 给的二值奖励，不靠模型判 |
| **Verify-and-Refine** | 验证-修正 | TTS 算法骨架（Huang & Yang 2025） |
| **vLLM** | vLLM | 另一 LLM serving 框架；SU-01 baseline 评测用它 |
| **Z-Score Normalization** | Z 分归一 | 优势除以 σ；GRPO 用，SU-01 **不用** |

---

**统计**：约 62 条术语，覆盖 RL 算法、数据资产、评测基准、推理基础设施、对手工作五大维度。建议读者从 RL 算法（GSPO/GRPO/PPO）+ 训练数据（SFT/RL pool）+ 三层 verifier 三组开始记。

> 完整背景请见配套的概念卡片 (`concept-cards.md`) 与公式手册 (`key-equations.md`)。
