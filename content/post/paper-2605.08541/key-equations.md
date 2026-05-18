# 关键公式解读

> 配合 paper-2605.08541 主文阅读。每个公式给出形式、直觉、推导要点与应用。

---

## 公式 1：Chinchilla scaling law

$$ L(N, D) = E + \frac{A}{N^{\alpha}} + \frac{B}{D^{\beta}}, \quad A, B, \alpha, \beta, E > 0 $$

**直觉**
模型的 loss = 不可约部分 E（与数据熵下界相关）+ 容量项 A·N⁻ᵅ（参数有限带来的代表能力损失）+ 数据项 B·D⁻ᵝ（数据有限带来的泛化误差）。两项都呈现幂律衰减。

**典型数值（Hoffmann et al. 2022）**
- A ≈ 406.4, B ≈ 410.7, E ≈ 1.69
- α ≈ 0.34, β ≈ 0.28

**本文用法**
这是 base case。论文把同样的论证套到 Kaplan / Repeated-Data / Droppo-Elibol 上，但 Chinchilla 是最熟悉、影响最大的形式。

---

## 公式 2：Jacobian 列在 D = kN 上的共线性

把 D = kN 代入公式 1，对 (A, B) 求导：

$$ \frac{\partial L}{\partial A}\bigg|_{(N, kN)} = N^{-\alpha}, \quad \frac{\partial L}{\partial B}\bigg|_{(N, kN)} = k^{-\beta} \cdot N^{-\beta} $$

**关键观察**
把 N^{-β} 用 N^{-α} 表示：

$$ N^{-\beta} = N^{-\alpha} \cdot N^{\alpha - \beta} = N^{-\alpha} \cdot N^{\varepsilon}, \quad \varepsilon := \alpha - \beta $$

所以 Jacobian 第 i 行有两列：

$$ \mathbf{j}_A^{(i)} = N_i^{-\alpha}, \quad \mathbf{j}_B^{(i)} = k^{-\beta} \cdot N_i^{\varepsilon} \cdot N_i^{-\alpha} = c \cdot N_i^{\varepsilon} \cdot \mathbf{j}_A^{(i)} $$

当 ε → 0，N_i^ε → 1，两列变成同一向量的标量倍数——**精确共线**。

---

## 公式 3：Proposition 1 — Θ(ε⁻²) 条件数

设 J ∈ ℝ^{m×p} 的两列满足

$$ \mathbf{j}_b = c \mathbf{j}_a + \boldsymbol{\delta}, \quad c \neq 0, \quad \|\boldsymbol{\delta}\| = O(\varepsilon) $$

则当 ε → 0：

$$ \lambda_{\max}(J^T J) = \Theta(1), \quad \lambda_{\min}(J^T J) = \Theta(\varepsilon^2), \quad \boxed{\kappa(J^T J) = \Theta(\varepsilon^{-2})} $$

**证明草图**
在 (j_a, j_b) 子空间上：

$$ \begin{pmatrix} \mathbf{j}_a^T \mathbf{j}_a & \mathbf{j}_a^T \mathbf{j}_b \\ \mathbf{j}_b^T \mathbf{j}_a & \mathbf{j}_b^T \mathbf{j}_b \end{pmatrix} = \begin{pmatrix} \|\mathbf{j}_a\|^2 & c\|\mathbf{j}_a\|^2 + O(\varepsilon) \\ \cdot & c^2\|\mathbf{j}_a\|^2 + O(\varepsilon) \end{pmatrix} $$

determinant 是 O(ε²)、trace 是 Θ(1)。所以 λ_min·λ_max = det = Θ(ε²)，且 λ_max ≥ trace/2 = Θ(1)，得 λ_min = Θ(ε²)。

**数值后果**
- Chinchilla ε=0.06：ε⁻² ≈ 278
- Kaplan ε=0.019：ε⁻² ≈ 2,770
- 这是 design-level 的，**多训不会变小**。

---

## 公式 4：Corollary 1 — Θ(ε⁻¹) CI 膨胀

在 i.i.d. Gaussian 噪声 σ²、单 ray D=kN 设计下：

$$ \frac{\mathrm{CI}_{0.95}(A)}{\mathrm{CI}_{0.95}(\psi)} = \Theta(\varepsilon^{-1}) $$

其中 ψ = A + B·k⁻ᵅ 是可识别的组合系数。

**推导要点**
最小二乘估计量的协方差矩阵 Cov(θ̂) = σ²(JᵀJ)⁻¹。对 (A, B) 对应主子块：

$$ \mathrm{Var}(\hat{A}) = \frac{\sigma^2}{\lambda_{\min}((J^T J)_{A,B})} \cdot (\text{const}) = \Theta(\sigma^2 / \varepsilon^2) $$

而 ψ 在 reduced model 中是单参数，CI 正常：

$$ \mathrm{Var}(\hat{\psi}) = \Theta(\sigma^2) $$

CI 是 std × 1.96，所以比值 sqrt(Θ(ε⁻²)) = Θ(ε⁻¹)。

**数值**
- Chinchilla ε=0.06：CI 膨胀 ≈ 17×
- Kaplan ε=0.019：CI 膨胀 ≈ 53×

---

## 公式 5：Proposition 2 — TPP 多样性充要条件

给定 K 个训练 ratio k_1 ≤ ... ≤ k_K，设计 well-conditioned 的充要条件是：

$$ V_K \geq \tau_K $$

其中：

$$ V_K := \frac{1}{K} \sum_{\ell=1}^{K} k_{\ell}^{-2\beta_{\mathrm{eff}}} - \left( \frac{1}{K} \sum_{\ell=1}^{K} k_{\ell}^{-\beta_{\mathrm{eff}}} \right)^2 $$

$$ \tau_K := \frac{(K + \sum_{\ell=1}^{K} k_{\ell}^{-2\beta_{\mathrm{eff}}})^2}{K^2 \cdot \kappa_{\mathrm{target}}} $$

**直觉**
V_K 是 {k_ℓ⁻ᵝᵉᶠᶠ} 这个集合的样本方差（即"k_ℓ 在转换 x ↦ x⁻ᵝᵉᶠᶠ 后的离散度"）。τ_K 是把目标条件数 κ_target 翻译成的几何阈值。

**K = 1 case**
V_1 = (k_1⁻²ᵝᵉᶠᶠ) − (k_1⁻ᵝᵉᶠᶠ)² = 0 永远，τ_1 > 0 永远，所以**单 ratio 设计永远不满足**。

**K = 2 case**
设 R = k_2/k_1，不等式退化为 R ≥ R_min(β_eff, κ_target)。**只需两个差距足够大的 TPP 就够了**。

**K ≥ 3 reduces V_K**
增加中间点 fix 端点不变会**降低** V_K（这是样本方差的性质），所以更多 ratio 反而无助于识别性——除非进一步散开端点。

**a-priori 可用性**
β_eff 不必从你这次实验得到——可以用文献估计（Chinchilla β ≈ 0.28）。所以你可以在跑实验前就核对设计是否过关。

---

## 公式 6：Reduced model（Definition 2）

当设计 collinear（K = 1）时，唯一可识别的 model 是：

$$ L(N; \psi, \alpha, E) = \psi \cdot N^{-\alpha} + E, \quad \psi := A + B \cdot k^{-\alpha} $$

**含义**
- 你训了 m 个 (N_i, kN_i, L_i) 三元组。
- 在这些数据上，你能可靠估计 ψ、α、E 三个参数。
- 你**不能**单独估计 A 和 B——它们个别值的 CI 膨胀 ε⁻¹ 倍。
- 你能用学到的 (ψ, α, E) 预测**同 ratio k 下**新 N 值的 loss：L̂(N) = ψ·N⁻ᵅ + E。
- 你**不能**预测不同 k' 下的 loss——因为 ψ 是 k-specific 的。

**为什么这件事被忽视了**
因为大多数实操目的（"我想知道 N=70B 在 D=20N 上 loss 是多少"）刚好就是同 ratio 内插，reduced model 完全够用。问题出在大家假装拟合的是 full model，并报告 (A, B) 数值。

---

## 附：Theorem 1 holdout RMSE ordering（仅形式，证明在 Appendix B.13）

**Regime A（病态情况）**：当 V_K < τ_K 时（包括所有 K=1 设计）：

$$ \mathbb{E}[\mathrm{RMSE}_H^{\mathrm{NC}}] < \mathbb{E}[\mathrm{RMSE}_H^{\mathrm{CO}}] $$

且 E[R²_H^{NC}] > E[R²_H^{CO}]。

**Regime B（良态情况）**：当 V_K ≥ τ_K 且 K ≥ 2：

$$ \mathbb{E}[\mathrm{RMSE}_H^{\mathrm{CO}}] / \mathbb{E}[\mathrm{RMSE}_H^{\mathrm{NC}}] = \Theta(1) $$

即没有 systematic 优势——如果你的 CO 设计恰好已经满足 V_K ≥ τ_K，就不必额外构造 NC。

---

## 公式数值核对表

| Law | ε | ε⁻¹ (CI inflation) | ε⁻² (κ scaling) | 经验 holdout R²（CO → NC）|
|---|---|---|---|---|
| Chinchilla | 0.06 | 17× | 278 | ~0.84 → ~0.93 |
| Repeated-Data | 0.06 | 17× | 278 | 100% NC win |
| Kaplan | 0.019 | 53× | 2,770 | ~0.51 → ~0.91（最戏剧化）|
| Droppo-Elibol | 0.05~0.10 | 10-20× | 100~400 | 98% NC win |

---

## 公式核对：尝试用 V_K ≥ τ_K 设计一个 grid

假设你想拟合 Chinchilla（β_eff ≈ 0.28），目标 κ_target = 100。

**做法 A（CO，4 个 ratio）**：k ∈ {15, 20, 25, 30}
- k⁻ᵝ ≈ 0.483, 0.444, 0.413, 0.388
- mean ≈ 0.432, mean² ≈ 0.187
- mean of squares ≈ 0.187, V_K ≈ 0.0006
- τ_K（K=4）≈ 0.02 / 100 ≈ 2×10⁻⁴
- **V_K = 6×10⁻⁴ > τ_K = 2×10⁻⁴**——侥幸通过！但很贴近边界

**做法 B（K=2，宽距）**：k ∈ {5, 100}
- k⁻ᵝ ≈ 0.673, 0.275
- mean ≈ 0.474, mean² ≈ 0.225
- mean of squares ≈ 0.265, V_K ≈ 0.040
- τ_K（K=2）≈ 0.011
- **V_K = 0.040 ≫ τ_K**——大幅通过！

教训：4 个紧密相邻 ratio 不如 2 个远距 ratio——这正是 Prop 2 的几何含义。
