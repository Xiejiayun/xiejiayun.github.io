# 术语表（中英对照）

> 配合 paper-2605.08541 主文阅读。每条 1-2 句精炼解释，附带本文中的用法。

## A — D

| 英文 | 中文 | 在本文中的含义 |
|---|---|---|
| **Active parameters** | 激活参数 | 训练时实际参与某个前向/反向传播的参数数量。MoE 等稀疏架构里和总参数 N 不一致。Repeated-Data scaling law 里用 effective N' 概念。 |
| **Asymptotic regime** | 渐近区制 | ε → 0、m → ∞ 等极限下成立的描述。Prop 1、Cor 1、Prop 2 都是 ε → 0 时的 leading-order 结果。 |
| **BF16 (bfloat16)** | BF16 半精度 | Google 提出的 16-bit 浮点格式。论文用它验证 NC 优势不是 FP32 的数值伪影——BF16 NC 仍胜 98.7%。 |
| **Bias inflation** | 偏差膨胀 | Theorem 1 的 Regime A：当 V_K < τ_K，CO 的 holdout RMSE 严格大于 NC。 |
| **Chinchilla scaling law** | Chinchilla 缩放律 | Hoffmann 2022 提出，L = E + A·N⁻ᵅ + B·D⁻ᵝ。本文证明其 (A, B) 在 D=kN 下不可识别。 |
| **Collinear design (CO)** | 共线实验设计 | 所有训练点都满足 D = k·N，落在一条过原点的射线上。本文证明它病态。 |
| **Condition number** | 条件数 | κ(M) = λ_max/λ_min。Prop 1: κ(JᵀJ) = Θ(ε⁻²)。 |
| **Confidence interval (CI)** | 置信区间 | 95% CI(A)/95% CI(ψ) = Θ(ε⁻¹)。Chinchilla 17×、Kaplan 53×。 |
| **Compute-optimal** | 算力最优 | Chinchilla 框架下，给定 compute C 时最小化 loss 的 (N, D)。Hoffmann 给出 D ≈ 20N。 |
| **Cross-entropy loss** | 交叉熵损失 | 论文实验用 per-epoch cross-entropy loss 作为拟合的 L_i。 |
| **Differential evolution polish** | 差分进化精修 | 非线性最小二乘的全局优化技巧。论文用它给 100 random restart 后做最后一步精修。 |
| **Design matrix degeneracy** | 设计矩阵退化 | Jacobian 列接近共线时的统计学术语。本文是非线性回归版的多重共线性。 |
| **Droppo-Elibol scaling law** | Droppo-Elibol 缩放律 | Droppo & Elibol 2021 提出的 5 参数 scaling law。本文证明其 (N_C, D_C) 也病态。 |

## E — H

| 英文 | 中文 | 含义 |
|---|---|---|
| **Effective exponent β_eff** | 有效数据指数 | 各 law 数据轴的实际 power：Chinchilla 是 β、Kaplan 是 α_D、Droppo-E 是 γ_D。V_K 公式需要它。 |
| **Effective N'** | 有效参数量 | Repeated-Data scaling law 里因 epoch 重复而调整后的 N。 |
| **Exponent gap ε** | 指数间距 | ε := \|α − β\|（或对应的 law-specific 量）。整个病态分析的 driving parameter。 |
| **Extrapolation** | 外推 | 在训练 (N, D) 范围之外预测 loss。本文核心问题：CO 设计在外推时严重退化。 |
| **Fan-of-rays** | 射线扇 | 多个 D=kN 直线构成的设计。本文 CO 实验用了 12 条射线——但因为方向相近、几何上仍 collinear。 |
| **FineWeb-Edu** | FineWeb-Edu 数据集 | HuggingFace 整理的高质量预训练语料。本文未直接用（用了 C4 等 5 个），但 PMNet 论文用到。 |
| **Gauss-Newton method** | 高斯-牛顿法 | 解非线性最小二乘的经典迭代法。本文用 GN linearization 推导所有理论结果。 |
| **Gradient Domination** | 梯度主导 | 一个常见的优化几何条件，使 SGD 类方法在非凸问题上仍有线性收敛。本文 Cor 3 用到。 |
| **Holdout set (H)** | 留出集 | 不参与训练、用来评估外推性能的 (N, D, L) 点集。本文用 H = H_col ∪ H_nc 做 head-to-head。 |

## I — N

| 英文 | 中文 | 含义 |
|---|---|---|
| **Identifiability** | 可识别性 | 给定无限训练数据时参数能否被唯一确定。本文 (A, B) 在单 ray 下不可识别，但 ψ 可识别。 |
| **Ill-conditioning** | 病态条件 | 数值线性代数概念：高条件数导致解对扰动极度敏感。本文核心病症。 |
| **IsoFLOP curve** | 等算力曲线 | C = 6ND 的等高线。本文 Prop 3 证明 isoFLOP RMSE 不能绕开 collinear 病态。 |
| **Jacobian J** | 雅可比矩阵 | J_{ij} = ∂r_i/∂θ_j。本文所有论证的几何对象。 |
| **Kaplan scaling law** | Kaplan 缩放律 | Kaplan et al. 2020 提出的 5 参数 power-law form。ε ≈ 0.019 在四种 law 里最病态。 |
| **k_target** | 目标条件数 | Prop 2 中由 design 选择的目标 κ。τ_K 是 k_target 的函数。 |
| **Last-layer cost** | 末层成本 | Kaplan-Chinchilla 复现争论里的食谱细节。Porian 2025 归因于它，本文给出了更深的统计原因。 |
| **LLaMA-style transformer** | LLaMA 风格 transformer | 本文 1,900 个模型全部采用的架构。RMSNorm、SwiGLU、RoPE 等典型组件。 |
| **Loss surface** | 损失曲面 | 拟合后的 L̂(N, D; θ̂)。论文 Figure 1a 展示 CO 拟合的 loss surface 在小 N 区域残差爆炸。 |
| **Multicollinearity** | 多重共线性 | 线性回归里设计矩阵列接近线性相关。本文是其非线性回归对应。 |
| **Multivariate identifiability** | 多元可识别性 | 同时识别多个参数（如 A 和 B）的能力。单 ray 下 (A, B) 不能同时识别。 |
| **Nonlinear least squares (NLS)** | 非线性最小二乘 | min ½‖r(θ)‖² where r non-linear in θ。本文的拟合 framework。 |
| **Non-collinear design (NC)** | 非共线设计 | (N, D) 点二维分布。本文推荐做法，holdout 上 97.3% 胜率。 |
| **Normal equations** | 法方程 | (JᵀJ)Δθ = −Jᵀr。GN 迭代核心一步。 |

## O — R

| 英文 | 中文 | 含义 |
|---|---|---|
| **Over-training** | 过训练 | TPP 显著大于 compute-optimal（如 LLaMA-3 用 ~200 TPP）。本文 Appendix D.7 测了 k=10-20 范围。 |
| **Power-law fit** | 幂律拟合 | 拟合 L ∝ N⁻ᵅ 形式。所有现代 scaling law 的基础假设。 |
| **Practical scaling law (Hu et al.)** | 实操缩放律 | 2026 年 Hu et al. 的修正 Chinchilla 形式（不再假设单 epoch、数据充足）。本文 Related Works 提及。 |
| **Pre-training corpus** | 预训练语料 | 本文用了 5 个：C4、Cosmopedia、peS2o、RedPajama、Wikipedia。 |
| **Random restart** | 随机重启 | 拟合时从多个 random θ_0 各跑一次。本文用 100 次。 |
| **Reduced model** | 简化模型 | Definition 2: L(N) = ψ·N⁻ᵅ + E，3 参数。单 ray 下唯一可识别的 model。 |
| **Repeated-data law (Muennighoff 2025)** | 重复数据缩放律 | 用 effective (N', D') 处理多 epoch 重复。本文证明它继承 Chinchilla 的病态。 |
| **Residual r(θ)** | 残差 | r_i = L_i − L̂(N_i, D_i; θ)。NLS 的优化对象。 |
| **RMSE (Root mean square error)** | 均方根误差 | √mean((L_pred − L_true)²)。本文 holdout 评估的主指标之一。 |

## S — Z

| 英文 | 中文 | 含义 |
|---|---|---|
| **Sample variance V_K** | 样本方差 V_K | V_K := mean(k_ℓ⁻²ᵝᵉᶠᶠ) − (mean(k_ℓ⁻ᵝᵉᶠᶠ))²。Prop 2 中度量 TPP 多样性的统计量。 |
| **Scaling-law experimental dataset** | 缩放律实验数据集 | Def 1: {(N_i, D_i, L_i)} 三元组集合，加 train/holdout split。 |
| **Sloppy direction** | 松弛方向 | Sloppy model 里数据不约束的参数方向。本文 CO 下沿 (1, −k⁻ᵅ) 方向松弛。 |
| **SmolLM** | SmolLM 系列 | HuggingFace 小型 LM 系列。PMNet 论文用 SmolLM-135M 作 transformer baseline。 |
| **Stop-gradient** | 梯度截断 | sg[·] 操作符。本文实验里 advantage 用 stop-gradient（虽然这部分是 PMNet 论文的细节）。 |
| **Sufficient TPP diversity** | TPP 多样性充分 | V_K ≥ τ_K 满足时，设计 well-conditioned。 |
| **Tail extrapolation** | 上尾外推 | TEA paper (2605.10716) 概念。和本文不同主题，但都是 scaling-law/RLHF 圈的 2026-05 论文。 |
| **τ_K threshold** | τ_K 阈值 | Prop 2 中右侧的目标量。τ_K = (K + Σk_ℓ⁻²ᵝᵉᶠᶠ)² / (K² κ_target)。 |
| **TPP (Tokens-per-Parameter)** | 每参数 token 数 | k = D / N。Chinchilla 约 20；over-trained 现代模型可达 100~3000。 |
| **TPP ratio R** | TPP 比率比 R | R := k_max / k_min。K=2 时充要条件简化为 R ≥ R_min。 |
| **Unidentifiable** | 不可识别 | 某参数不能被数据唯一确定（即使数据无限）。本文 CO 下 A、B 都不可识别。 |
| **Validation split** | 验证集 | 用于 checkpoint 选择，与 holdout 分开。本文用 128 prompts × 32 samples 做 validation。 |
| **Win rate** | 胜率 | NC vs CO paired comparison 里 NC 给出更优 R²/RMSE 的比例。本文 97.3%。 |
