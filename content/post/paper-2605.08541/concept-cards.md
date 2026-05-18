# 关键概念卡片：scaling-law 实验设计 16 张速查

> 配合 [paper-2605.08541](./) 主文阅读。每张卡分「定义/直觉」+「在本文中的角色」两面。

---

## 卡片 1 / 16 · Scaling Law（神经缩放律）

**定义/直觉**
描述模型 loss 随参数量 N、数据量 D 变化的幂律函数。最常见形式：

$$ L(N, D) = E + \frac{A}{N^{\alpha}} + \frac{B}{D^{\beta}} $$

其中 E 是不可约 loss（约等于真实数据的熵下界）。

**在本文中的角色**
本文的研究对象。论文证明：上式中 A、B 在常见实验设计下**不可识别**，但组合量 ψ = A + B·k⁻ᵅ 可识别。

---

## 卡片 2 / 16 · Tokens-per-Parameter (TPP) Ratio

**定义/直觉**
训练数据量与参数量的比值 k := D / N。Chinchilla 推荐的 compute-optimal 比值约为 20；over-trained LLaMA-3 实际跑到 ~200。

**在本文中的角色**
**这个 ratio 既是 prescription 也是 design problem 的来源**。Chinchilla 提议训练单个模型时用 D ≈ 20N，但当用 fan-of-rays（多个 k 接近的设计）来拟合 scaling law，本文证明会产生病态。

---

## 卡片 3 / 16 · Collinear / Non-collinear Design

**定义/直觉**
- **Collinear（CO）**：训练样本都满足 D = k·N，即所有 (N, D) 点在一条过原点的直线上。
- **Non-collinear（NC）**：(N, D) 点覆盖一个二维矩形/区域，比率 k = D/N 在不同样本上不同。

**在本文中的角色**
论文的核心二分。CO 是普遍做法（Chinchilla、Cerebras-GPT、OLMo ladder 等）；NC 是论文推荐做法。1,900 个 LLM 实证 NC 在 holdout 上以 97.3% 胜率击败 CO。

---

## 卡片 4 / 16 · Jacobian Matrix（J）

**定义/直觉**
拟合非线性最小二乘 `min ½‖L_obs − L̂(N, D; θ)‖²` 时，Jacobian J 的 (i, j) 元素是 ∂r_i/∂θ_j，刻画参数 θ_j 局部如何影响第 i 个残差。

**在本文中的角色**
论文证明的全部立足点。当 D = kN 且 α ≈ β 时，J 的 j_A 列与 j_B 列几乎共线（差一个 N^ε 因子）。条件数恶化全部源于 J 的几何性质，与具体损失函数无关。

---

## 卡片 5 / 16 · Condition Number κ(JᵀJ)

**定义/直觉**
$$ \kappa(M) = \frac{\lambda_{\max}(M)}{\lambda_{\min}(M)} $$

对称正定矩阵的条件数。在数值线性代数里，求解 `Mx = b` 的相对误差大约会被放大 κ(M) 倍。

**在本文中的角色**
Proposition 1 的核心：**κ(JᵀJ) = Θ(ε⁻²)**。ε 越小，求解最小二乘的法方程越数值病态。对 Chinchilla（ε=0.06）κ 大约几百到几千；对 Kaplan（ε=0.019）κ 大约几千到几万。

---

## 卡片 6 / 16 · Exponent Gap ε

**定义/直觉**
ε := |α − β|，即 scaling law 中 N 指数和 D 指数的绝对差。
- Chinchilla: ε ≈ 0.06（α=0.34, β=0.28）
- Kaplan: ε ≈ 0.019（α_N=0.076, α_D=0.095）
- Droppo-Elibol: ε ≈ 0.05~0.10

**在本文中的角色**
论文用 ε 把"病态程度"量化成一个可计算的小数。**ε 是经验事实，不是假设**——所有现行 SL 论文报告的 α、β 都满足 ε 很小，这就是为什么病态在文献里普遍存在。

---

## 卡片 7 / 16 · Sloppy Model

**定义/直觉**
源自系统生物学/物理（Transtrum et al. 2010, 2015）。指：在参数空间中，loss 沿某些方向极度敏感、沿另一些方向极度迟钝，使得"等价拟合"参数构成一条窄长的流形。

**在本文中的角色**
论文把 scaling-law 的病态归为 sloppy model 现象的一个 instance。CO 设计下，A 和 B 沿 (1, −k⁻ᵅ) 方向几乎完全自由（无信号约束）——这条方向上的"等价拟合"参数构成了 sloppy direction。

---

## 卡片 8 / 16 · Reduced Model（ψ-Model）

**定义/直觉**
当 A、B 单独不可识别时，组合量

$$ \psi := A + B \cdot k^{-\alpha} $$

是可识别的（Definition 2）。reduced model 直接拟合 `L(N) = ψ·N⁻ᵅ + E`，只用 3 个参数。

**在本文中的角色**
论文给的"安慰奖"：即使你的设计 collinear，你**还是能学到 ψ、α、E**——但只能用来预测同一 k 上的 loss，不能外推到任何离开 D = kN 的点。

---

## 卡片 9 / 16 · TPP-Diversity Threshold (V_K ≥ τ_K)

**定义/直觉**
Proposition 2 给出的**充要条件**：

$$ V_K \geq \tau_K $$

其中 V_K 是 {k_ℓ⁻ᵝᵉᶠᶠ} 的样本方差，τ_K 由 κ_target 决定。满足时 κ(JᵀJ) ≤ κ_target，估计 well-conditioned。

**在本文中的角色**
**论文最实操的产物**。a-priori 可算（只需文献 β_eff 估计），不必先训完才知道结果。任何打算跑 scaling-law 实验的人都应该在 design phase 先核对这个不等式。

---

## 卡片 10 / 16 · K = 2 端点散开原则

**定义/直觉**
Proposition 2 的推论：使用 K=2 个 TPP 比率 k_1 < k_2，只要 R = k_2/k_1 大于一个 R_min 就足够。**K ≥ 3 不会进一步降低对 R 的要求**——多加中间点不增加可识别性。

**在本文中的角色**
反直觉的工程建议：**与其用 12 个紧密相邻的 TPP（如 1, 1.5, 1.9, 2, ...）训 12N 个模型，不如用 2 个差距巨大的 TPP（如 5 和 100）训 2N 个**。本文实验用了密集的 CO grid 仍是 collinear——多≠diverse。

---

## 卡片 11 / 16 · IsoFLOP 曲线

**定义/直觉**
固定 compute C = 6ND 的等高线。在 (N, D) 平面上是一条 D = C/(6N) 的双曲线。Chinchilla 的核心做法就是把 isoFLOP 曲线投到 loss 上、找最小值，给出 D/N ≈ 20。

**在本文中的角色**
论文 3.4 节展示：CO 训练时，**isoFLOP 曲线正好横切训练 ray**——你画 isoFLOP 是在 sloppy direction 上做预测。这就是 Chinchilla 系数为什么反复被各家修订的几何理由。

---

## 卡片 12 / 16 · Confidence Interval Inflation

**定义/直觉**
Corollary 1：

$$ \frac{\mathrm{CI}_{0.95}(A)}{\mathrm{CI}_{0.95}(\psi)} = \Theta(\varepsilon^{-1}) $$

A 的置信区间相对 ψ 的置信区间膨胀 ε⁻¹ 倍。Chinchilla 17×、Kaplan 53×。

**在本文中的角色**
论文最直观的"严重程度"指标。Kaplan 文章给的 N_c、D_c 数值，其 95% CI 实际比可识别量宽 53 倍——意味着报告值在统计上几乎是噪声。

---

## 卡片 13 / 16 · Holdout Splits（H_col, H_nc, H）

**定义/直觉**
- **H_col**：从 collinear training fan 中保留 5 个 TPP 比率（k ∈ {6, 6.2, 6.5, 6.7, 7}）作为留出。
- **H_nc**：从 NC grid 中保留 300-401M tokens 范围的 D 值作为留出。
- **H**：H_col ∪ H_nc 的并集。所有指标在这个统一留出上比较。

**在本文中的角色**
公平的 head-to-head 比较设计。两边的设计在同一 H 上评测——避免"每边只在自己留出上算 RMSE 然后比"这种 apples-to-oranges 比较。

---

## 卡片 14 / 16 · Win Rate Bootstrap (1500 paired comparisons)

**定义/直觉**
30 seeds × 5 corpora × 4 laws × ~2.5 epochs ≈ 1500 paired (NC, CO) 比较。NC 在 1460 次比较中给出更小的 holdout RMSE 或更高的 R²。胜率 = 1460/1500 = 97.3%，CI [96.4%, 98.0%]。

**在本文中的角色**
统计上把"NC 比 CO 好"做成了一个非常窄的置信区间。R² 平均差 0.095（0.837 → 0.932）也不是 marginal 改善。

---

## 卡片 15 / 16 · IsoFLOP RMSE Invariance (Prop 3)

**定义/直觉**
论文证明：将 (N, D) 重参数化为 (N, C) 后，给定 hat L 在 H 上的 RMSE 不变。这意味着 isoFLOP 曲线的预测误差**完全等于**直接评估 hat L 在留出点上的预测误差——它不是一个新的 metric，只是另一种可视化。

**在本文中的角色**
回应一类辩护："我们用 isoFLOP RMSE 而不是直接 RMSE 来评估，所以 collinear bias 不影响。"论文证明这是错的——isoFLOP RMSE 和 (N, D)-RMSE 数学上等价。

---

## 卡片 16 / 16 · Repeated-Data Scaling Law

**定义/直觉**
Muennighoff et al. 2025 提出，当数据反复重复（epoch >1）时，应该用"effective" (N', D')：N' 反映 active parameters 因重复贬值，D' 反映 unique tokens。

**在本文中的角色**
论文在 Appendix B.7 里验证这个 law 也满足同样的 collinear 病态：换一个 functional form 不能绕开 J 的几何问题。重要 corroboration——病态是设计 geometry 的问题，不是某个具体 law form 的问题。
