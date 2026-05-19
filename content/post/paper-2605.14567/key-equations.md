# 关键公式解读 — arXiv 2605.14567

**论文**:《Scaling Laws from Sequential Feature Recovery》(Wortsman-Zurich, Tabanelli, Dandi, Krzakala, Loureiro)

本文从"按方向逐个恢复特征"的角度,推导出二层网络在多指标 (multi-index) 教师下的标度律 (scaling law)。下面整理 8 个最核心的公式。

---

## 公式 1 · 复合教师目标函数

$$
y_\mu = g\!\left(h^{(2)}_\mu\right),\qquad
h^{(2)}_\mu = \frac{1}{\sqrt{2}}\sum_{i} \lambda_i\left(\bigl(h^{(1)}_{\mu,i}\bigr)^2 - 1\right),\qquad
h^{(1)}_{\mu,i} = \bigl\langle A^{(1)}_i,\, F_\mu \bigr\rangle
$$

**含义**: 教师网络由两层组成 —— 第一层把高维输入 $F_\mu \in \mathbb{R}^D$ 投影到 $d_1$ 个隐藏方向 $A^{(1)}_i$,第二层对这些投影做 Hermite-2 ($x^2-1$) 非线性组合,权重为 $\lambda_i$,最后再经过外层非线性 $g$。

**直觉**: 之所以选 $\mathrm{He}_2(x)=x^2-1$ 作为内层激活,是因为它对高斯输入正交于线性项,使得"信号"出现在二阶矩 (协方差) 而非一阶矩中。$\lambda_i$ 给不同隐藏方向赋予不同强度,这种强度的幂律衰减正是产生 power-law scaling 的根源。

**论文中的位置 / 作用**: 出现在第 2 节模型定义 (Eq. 2.5),是全文分析的起点 —— 后续的谱估计、信号/噪声分解、阈值与定理都建立在这一 teacher 形式之上。

---

## 公式 2 · 幂律权重 (power-law spectrum)

$$
\lambda_i = Z_\gamma\, z_i\, i^{-\gamma},\qquad
Z_\gamma = \Bigl(\textstyle\sum_{i} i^{-2\gamma}\Bigr)^{-1/2}
$$

**含义**: 第 $i$ 个隐藏方向的强度按 $i^{-\gamma}$ 幂律衰减;$z_i$ 为 $\pm 1$ 的随机符号,$Z_\gamma$ 是使 $\sum_i \lambda_i^2 = 1$ 的归一化常数。

**直觉**: 这是经典"特征重要性呈幂律"的假设 —— 与自然数据 (图像、语言) 中协方差谱、target 谱常呈 power-law 一致。$\gamma$ 越大,重要方向越集中于前几位;$2\gamma>1$ 时 $\sum i^{-2\gamma}$ 收敛,$Z_\gamma$ 有限,这是后续标度律成立的关键条件。

**论文中的位置 / 作用**: 第 2 节假设 (A1),贯穿全文。MSE 标度律的指数 $1/(2\gamma)$ 直接来自这一谱衰减率。

---

## 公式 3 · 二阶谱估计算子

$$
\hat C \;=\; \frac{1}{n}\sum_{\mu=1}^{n} y_\mu\, \mathrm{He}_2(F_\mu)\;\in\;\mathbb{R}^{D\times D}
$$

**含义**: 用标签 $y_\mu$ 对输入的 Hermite-2 张量 $\mathrm{He}_2(F_\mu) = F_\mu F_\mu^\top - I_D$ 做加权平均,得到一个 $D\times D$ 的经验矩阵。

**直觉**: 因为标签里含 $h^{(1)}_{\mu,i}$ 的二次项,期望 $\mathbb{E}[y\,\mathrm{He}_2(F)]$ 恰好等于一个由 $\{A^{(1)}_i\}$ 张成、以 $\lambda_i$ 加权的低秩信号矩阵。$\hat C$ 就是这一总体量的样本估计;对它做谱分解,就能"读出"隐藏方向。这是矩 (method of moments) / spectral method 的标准思路。

**论文中的位置 / 作用**: Eq. 2.6,是算法层面的核心估计量。第 3 节的所有上下界、对齐度分析、MSE 标度都围绕 $\hat C$ 的特征向量展开。

---

## 公式 4 · 信号 + 噪声分解

$$
\hat C \;\simeq\; \underbrace{\nu_1\, A^{(1)\top} A^{(2)} A^{(1)}}_{\text{信号 (rank } d_1\text{)}}
\;+\; \underbrace{\frac{1}{n}\,\tilde X_\perp\, Y\, \tilde X_\perp^\top}_{\text{噪声 (op-norm} \sim \sqrt{d^q/n}\text{)}}
$$

**含义**: 谱估计算子可分解为两部分:低秩 ($\le d_1$) 的信号项,集中在 $\{A^{(1)}_i\}$ 张成的子空间;以及在该子空间正交补上的高维噪声项,其算子范数大约为 $\sqrt{d^q/n}$ ($q$ 表征 $\mathrm{He}_2$ 张量的方差度)。

**直觉**: 这就是一个 spiked covariance / signal-plus-noise 模型 —— 当某个信号 spike 的强度 $\lambda_i$ 超过噪声水平 $\sqrt{d^q/n}$ 时,对应方向就能从谱中"冒出来";否则被淹没。BBP 相变 (Baik-Ben Arous-Péché) 思想在此被推广到多 spike + 幂律强度的情形。

**论文中的位置 / 作用**: Eq. 2.8。它把信号检测问题转化为标准的随机矩阵扰动问题,是单方向阈值 (公式 5) 和主定理 (公式 6) 推导的桥梁。

---

## 公式 5 · 单特征恢复阈值 (sequential emergence)

$$
n_i \;\gtrsim\; \frac{d^{q}\, i^{2\gamma}}{Z_\gamma^{2}}
$$

**含义**: 要让第 $i$ 个隐藏方向 $A^{(1)}_i$ 从 $\hat C$ 的谱中"涌现",所需样本量至少为 $d^q i^{2\gamma}/Z_\gamma^2$ 的量级。

**直觉**: 把 $\lambda_i^2 \asymp Z_\gamma^2 i^{-2\gamma}$ 与噪声水平 $\sqrt{d^q/n}$ 对比,信号超过噪声当且仅当 $\lambda_i \gtrsim \sqrt{d^q/n}$,移项即得此阈值。结论极其直观:**越次要的方向 ($i$ 大) 需要越多的样本才能学到**,且需求按 $i^{2\gamma}$ 增长 —— 这正是"sequential feature recovery (顺序特征恢复)"这一标题的来源。

**论文中的位置 / 作用**: Eq. 2.10,是全文物理图像最清晰的一式。它直接解释了训练曲线为何呈"阶梯/幂律"形态,并为 MSE 标度律 (公式 8) 提供单点贡献。

---

## 公式 6 · 主定理:特征级对齐度的匹配上下界

$$
\left|\left\langle \frac{u_k}{\|u_k\|},\; \frac{A^{(1)}_k}{\|A^{(1)}_k\|}\right\rangle\right|
\;=\; 1 - O_d\!\left(\frac{d^{q}\, k^{2\gamma}}{n\, Z_\gamma^{2}}\right)
$$

**含义**: $\hat C$ 的第 $k$ 个经验特征向量 $u_k$ 与真实方向 $A^{(1)}_k$ 之间的余弦相似度等于 $1$ 减去一个明确量级的误差项,且该误差是 **紧的** (上下界匹配)。

**直觉**: 误差大小恰好等于"阈值 $n_k$ / 实际样本数 $n$"的比 —— 与公式 5 完美呼应:样本量越超阈值,对齐越好;接近阈值时误差趋于 $O(1)$,方向尚未学到。"上下界匹配"意味着这一标度不是粗糙估计,而是真实的渐近行为。

**论文中的位置 / 作用**: Theorem 3.1,是论文最主要的技术贡献,把"sequential recovery"图像变成可量化、可验证的定理。

---

## 公式 7 · 预解算子展开 (resolvent / Rayleigh-Schrödinger 展开)

$$
\hat u_k \;=\; u_k \;+\; \sum_{j\neq k} \frac{u_j^{\top}\,\Delta\, u_k}{\lambda_k - \lambda_j}\, u_j
\;+\; \frac{1}{\lambda_k}\, P_{\mathrm{Ker}}\, \Delta\, u_k
\;+\; o(\|\Delta\|_{op}^{2})
$$

**含义**: 把扰动后的特征向量 $\hat u_k$ 在未扰动基底 $\{u_j\}$ 下做二阶展开:第一项是泄漏到其他信号方向的能量 (与 spectral gap $\lambda_k-\lambda_j$ 成反比),第二项是泄漏到零空间 (噪声补空间) 的部分。

**直觉**: 这是物理学家熟悉的 Rayleigh–Schrödinger 微扰论,在此被用作 RMT 工具:把"信号 + 噪声"中的"噪声"当作小扰动 $\Delta$,展开后逐项估计。**两项分别对应两种误差来源**:相邻幂律方向之间的混淆 (gap 小、$\gamma$ 大时尤其严重),以及来自高维噪声子空间的漏入。

**论文中的位置 / 作用**: Eq. 3.2,是证明 Theorem 3.1 的关键技术工具 —— 上下界的常数就来源于对这两类项的精细控制。

---

## 公式 8 · MSE 标度律 (主 scaling law)

$$
\mathrm{MSE}(n) \;\asymp\; \left(\frac{n}{d^{q}}\right)^{-1 + \frac{1}{2\gamma}}
\quad\text{当 } 2\gamma > 1,\qquad
m_n \;=\; \left(\frac{Z_\gamma^{2}\, D}{n}\right)^{1/(2\gamma)}
$$

**含义**: 测试均方误差随样本数 $n$ 呈幂律下降,指数为 $-1+\tfrac{1}{2\gamma}$ (对 $2\gamma>1$);其中 $m_n$ 是给定样本量下能被恢复的有效方向数 ("已学到的特征数")。

**直觉**: 把 MSE 分解为 "已学方向 (索引 $\le m_n$) 的拟合残差 + 未学方向 (索引 $>m_n$) 的尾部能量",未学尾部 $\sum_{i>m_n} \lambda_i^2 \sim m_n^{1-2\gamma}$。把阈值 $n \sim d^q m_n^{2\gamma}/Z_\gamma^2$ 反解出 $m_n \propto n^{1/(2\gamma)}$,代回尾部就得到 MSE 的幂律。这正是 Kaplan/Hoffmann/Chinchilla 等"neural scaling laws"的一种**可严格证明的微观对应**:**$\gamma$ 越大 (谱越陡),scaling 指数越接近 $-1$,数据效率越高**。

**论文中的位置 / 作用**: Eq. 2.15 与 Theorem 3.2,是全文的最终结论 —— 把单方向阈值 (公式 5) 与特征对齐 (公式 6) 累加成对整体 MSE 的解析预测,从而把"sequential feature recovery"与现代深度学习中观测到的 neural scaling laws 直接联系起来。

---

> **总览**:从教师模型 (公式 1-2) → 谱估计算子 (公式 3) → 信号/噪声分解 (公式 4) → 单方向阈值 (公式 5) → 特征级对齐定理 (公式 6) → 微扰论工具 (公式 7) → 整体 MSE 标度律 (公式 8),全文构成了一条"从随机矩阵论严格推出 scaling law"的清晰逻辑链。
