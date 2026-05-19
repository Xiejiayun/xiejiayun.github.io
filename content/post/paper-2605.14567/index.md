---
title: "【论文导读】Scaling Law 的微观机制：把『一条平滑幂律』拆成『几百次 sharp 的特征跳出』"
description: "拆解 arXiv 2605.14567 — ENS + EPFL 的 Krzakala / Loureiro 团队为 Kaplan-Chinchilla 经验幂律给出了一个**可证明**的微观机制：当目标函数依赖一族按 power-law 排序的隐藏方向时，spectral 学习器在 n ≍ dᵠ·i²ᵞ 处『一个一个』把第 i 个方向打捞出来，错位的跳出门槛叠加在一起，宏观上就是一条 (n/dᵠ)^{−1+1/(2γ)} 的平滑幂律。技术核心是一份比 Davis–Kahan 更紧的 resolvent / Neumann 展开，给出 individual eigenvector 恢复的 matching upper + lower bound。"
date: 2026-05-19
slug: "paper-2605.14567"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 论文导读
    - arXiv
    - Scaling Laws
    - Feature Learning
    - 表征学习
    - 随机矩阵
    - 谱方法
    - Krzakala
    - Loureiro
    - 高维统计
    - 多指标模型
    - Davis-Kahan
    - 神经标度律
    - 理论机器学习
draft: false
---

> 📌 **好文共赏 · 论文导读 | Paper Pick**
>
> 📄 论文：[Scaling Laws from Sequential Feature Recovery: A Solvable Hierarchical Model](https://arxiv.org/abs/2605.14567) · arXiv **2605.14567**
> 👥 作者：Arie Wortsman-Zurich、Hugo Tabanelli、Yatin Dandi、Florent Krzakala、Bruno Loureiro（ENS PSL · EPFL IdePHICS / SPOC 实验室联合）
> 📅 发布：2026-05-14（v1）| 多模评分：**Opus 9.0 · Sonnet-equiv 8.25 · Gemini-equiv 8.0 ⇒ 综合 8.42 / 10**
> ✍️ 一句话：Kaplan / Chinchilla 经验幂律不再只是"拟合得很好"的现象——这篇 54 页的硬核理论给出了第一个**可证明**的微观机制：若教师的隐藏方向强度按 $\lambda_i = Z_\gamma z_i i^{-\gamma}$ 排开，spectral 学习器会在 $n_i \asymp d^q i^{2\gamma} / Z_\gamma^2$ 处把第 $i$ 个方向"挑出来"，这一串错位的 sharp transition 平均下来就是一条 $(n/d^q)^{-1+1/(2\gamma)}$ 的平滑标度律；技术上靠一份比 Davis–Kahan 更紧的 resolvent 展开，给出 individual eigenvector 恢复的 matching upper + lower bound——一个"可独立感兴趣"的随机矩阵新工具。

---

## 1. 论文解决什么问题

过去六年，"神经标度律"几乎是 LLM 工程的一条公理：把模型大小 $N$、训练 token 数 $D$、训练算力 $C$ 任意一个朝着幂律方向放大，loss 就乖乖地像 $L \propto N^{-\alpha}$ 那样掉。Kaplan 等 2020 年的那张 [scaling laws 图](https://arxiv.org/abs/2001.08361)、Hoffmann 等 2022 年的 [Chinchilla 论文](https://arxiv.org/abs/2203.15556) 已经把这条经验幂律内化为整个行业的"算力预算神器"。

但有一件事一直是行业的"黑箱"：**这条幂律的指数到底从哪里来？**

主流理论给的答案是"spectral bias"——把神经网络当作一个固定的 kernel / random feature，generalization 由这个 kernel 的特征值谱（一般是幂律）决定 [^bahri]。Bordelon–Canatar–Pehlevan 2020 的[谱依赖学习曲线](https://arxiv.org/abs/2002.02561) 与 Cui–Loureiro–Krzakala–Zdeborová 2021 的 [kernel ridge 标度律](https://arxiv.org/abs/2105.15004)都属于这一族解释。

但这族解释有一个致命的回避点：**它假定表征是固定的**——也就是说，从 1B 模型到 100B 模型，表征空间没有任何变化，仅仅"信号在更长的尾巴上被多采样几次"。这显然与近几年的 emergence、grokking、feature learning 等等观察相悖。

> 「Yet most mathematical theories rely on linearized, kernel, or random-feature models, where the relevant representation is **fixed in advance** and learning is controlled by the spectrum of this representation.」
> —— Wortsman-Zurich et al., §1

这篇论文要回答的就是这个被回避的问题：**如果表征本身在被学习——也就是说，神经网络是在"逐渐发现"隐藏方向——平滑的幂律标度律还能不能从微观机理上推出来？** 它给出的回答是肯定的，而且把整个机制压缩成一句话：

> **平滑的 power-law 学习曲线，是许多 sharp 的、单个特征的 spectral 恢复跳变叠加平滑而成的。**

这是 ENS + EPFL 的 Krzakala / Loureiro 团队近两年一系列"hierarchical multi-index"工作 [^defilippis2025] [^tabanelli2026] 的延续。他们的"组合武器库"是高维随机矩阵理论 + Hermite analysis + 谱方法分析；这次他们把这套机器对准的，是 Kaplan / Chinchilla。

如果你读过我们关于 [Chinchilla scaling law 不可识别性](/post/paper-2605.08541/) 的导读，会知道经验幂律的尺度系数其实统计上很可疑；这篇论文从另一个方向上解决了"幂律为什么必须长成这样"的问题——并且**不需要做任何拟合**，纯理论。

---

## 2. 核心方法用人话讲清楚

### 2.1 一个"会暴露幂律"的最小教师模型

要证明"幂律来自顺序特征恢复"，你首先需要一个**简单到能解析、复杂到足以有幂律行为**的教师模型。论文给出的设定如下：

```
x ∈ ℝᵈ                ← Gaussian input (d-dim)
       │
       ▼
F(He_q(x)) ∈ ℝᴰ       ← Hermite-q tensor lift, D = (d+q-1 choose q) ≈ dᵠ
       │
       ▼   ⟨A⁽¹⁾_i , ·⟩
h⁽¹⁾_i ∈ ℝ            ← d₁ = dᵉ 个隐藏方向投影 (i = 1, …, d₁)
       │
       ▼   λᵢ · He₂(·)
h⁽²⁾ = (1/√2) Σᵢ λᵢ ( (h⁽¹⁾ᵢ)² − 1 )    ← anisotropic quadratic combine
       │
       ▼   g(·)
y = g(h⁽²⁾)
```

**关键的"幂律开关"在 $\lambda_i$ 上**：

$$
\lambda_i = Z_\gamma \cdot z_i \cdot i^{-\gamma}, \qquad z_i \sim \mathrm{Rad}(1/2)
$$

其中 $Z_\gamma$ 是把 $\mathrm{Var}(y) = \Theta(1)$ 校到 $O(1)$ 的归一化常数，$\gamma \ge 0$ 是**幂律指数**。$\gamma = 0$ 是各向同性退化，$\gamma$ 越大，强方向越占主导、尾部越长。

这是一个"教科书级的浓缩玩具模型"——它简单到可以用 random matrix 工具完整解析，但又包含了真实 transformer 必须面对的两件事：

1. **层级 / 组合性**：目标是一个 degree-$2q$ 的高维多项式，但分解成 degree-$q$ 的中间表示后变成了一个 $d_1$ 维问题；**先学表征再学回归** 是 sample-efficient 的必经之路。
2. **各向异性 power-law spectrum**：不同方向的"重要性"按幂律排开，就像真实数据里"高频概念稠密、低频概念稀疏"那样。

### 2.2 spectral 算法：把 $\hat C$ 当望远镜

给定数据 $\{(x_\mu, y_\mu)\}_{\mu=1}^n$，论文研究的"学习器"非常朴素——一个二阶谱估计算子：

$$
\hat C = \frac{1}{n} \sum_{\mu=1}^n y_\mu \cdot \mathrm{He}_2(F_\mu) \;\in\; \mathbb{R}^{D \times D}
$$

直觉是：你把标签 $y_\mu$ 与"二阶 Hermite 特征" $\mathrm{He}_2(F_\mu)$ 加权平均，得到一个 $D \times D$ 矩阵；它的 top-$d_1$ 个本征向量就是 $A^{(1)}_1, \dots, A^{(1)}_{d_1}$ 的估计。

为什么会这样？把 $\hat C$ 分解为 **signal + noise**（论文 Eq 2.8）：

$$
\hat C \;\simeq\; \underbrace{\nu_1 \cdot A^{(1)\top} A^{(2)} A^{(1)}}_{\text{signal: rank } d_1 \text{ spikes}} + \underbrace{\frac{1}{n} \tilde X_\perp Y \tilde X_\perp^\top}_{\text{isotropic noise, op-norm } \sim \sqrt{d^q / n}}
$$

信号项是一个 rank-$d_1$ 的"低秩 spike"——它的方向**恰好是** $A^{(1)}$ 的列空间，每个 spike 的大小是 $|\lambda_i| = Z_\gamma i^{-\gamma}$。噪声项则像一个 GOE 矩阵 $W$，模长是 $\sqrt{d^q/n}$。

这就把"学习器能不能恢复方向 $i$"翻译成了**经典的 spike detection 问题**：第 $i$ 个 spike 能不能从 $\sqrt{d^q/n}$ 的 GOE 噪声里"跳"出来？答案是 Baik–Ben Arous–Péché (BBP) 相变[^bbp]——只要 spike 大于噪声 op-norm，就能恢复，否则不能。

写成不等式即论文的 Eq 2.10：

$$
\boxed{ n_i \;\gtrsim\; \frac{d^q \cdot i^{2\gamma}}{Z_\gamma^2} }
\quad\Longleftrightarrow\quad \text{第 } i \text{ 个方向"被打捞出来"}
$$

注意这是一个**与 $i$ 强相关的门槛**：因为 $\lambda_i \propto i^{-\gamma}$，要分辨第 $i$ 个特征需要 $n$ 至少正比于 $i^{2\gamma}$（因为 BBP 比的是 spike size 平方 vs 噪声方差）。

### 2.3 主定理：matching upper + lower bound 的硬核之处

但是从"门槛"到"matching upper + lower bound"还有一步硬核的距离——你需要证明：**只要超过这个门槛，方向就**确实**恢复了；只要低于这个门槛，方向就**确实**没恢复**。这是论文的 **Theorem 3.1**：

> **Theorem 3.1 (Weak Recovery, 上+下界)：** 在 Assumption 3.1 下，spectral 估计的第 $k$ 个本征向量 $u_k$ 满足
>
> $$
> \left|\left\langle \frac{u_k}{\|u_k\|}, \frac{A^{(1)}_k}{\|A^{(1)}_k\|}\right\rangle \right| = 1 - O_d\!\left( \frac{d^q \cdot k^{2\gamma}}{n \cdot Z_\gamma^2} \right).
> $$
>
> 1. **充分**：若 $n = \omega_d(d^q k^{2\gamma} Z_\gamma^{-2})$，则 w.h.p. $u_k$ 恢复了 $A^{(1)}_k$，对齐误差以 $1/n$ 速率衰减；
> 2. **必要**：若 $n = \Theta(d^q k^{2\gamma} Z_\gamma^{-2} d^{-\delta})$（任意 $\delta > 0$），则 w.h.p. $u_k$ **没有**恢复 $A^{(1)}_k$。

写下来很短，但要证明这一点，标准的 Davis–Kahan 不等式不够用。

### 2.4 为什么 Davis–Kahan 不够用？

Davis–Kahan (1970) 是数值线性代数 / 高维统计里几乎所有"扰动后本征向量还能跟原向量对齐多少"问题的瑞士军刀。它说：

$$
\sin \theta(\hat u_k, u_k) \;\le\; \frac{\|\Delta\|_{op}}{\text{gap}_k}, \qquad \text{gap}_k = \min_{j \ne k} |\lambda_k - \lambda_j|.
$$

只要 spectral gap 远大于扰动的 operator norm，本征向量就稳定。

**问题是**——在 power-law 谱里，相邻 spike 的距离是

$$
|\lambda_k - \lambda_{k+1}| \approx Z_\gamma \cdot \left( k^{-\gamma} - (k+1)^{-\gamma} \right) \approx \gamma Z_\gamma \cdot k^{-\gamma - 1},
$$

也就是说 **gap 随 $k$ 衰减得比 spike 本身还快**。在 power-law 设定下，标准 Davis–Kahan 给出的恢复门槛比 BBP 门槛还宽松一个完整的 $k$ 因子；不够紧。

### 2.5 论文的"独立感兴趣"的技术工具

为了越过 Davis–Kahan，作者用了 resolvent 的 Neumann 展开（论文 Eq 3.2）：

$$
\hat u_k = u_k + \sum_{j \ne k} \frac{u_j^\top \Delta u_j}{\lambda_k - \lambda_j} u_j + \frac{1}{\lambda_k} P_{\mathrm{Ker}} \Delta u_k + o(\|\Delta\|_{op}^2)
$$

这把 $\hat u_k$ 拆成 **三个看得见每一项贡献的部分**：

1. **零阶项 $u_k$**：你想要的真值。
2. **被其他 spike "污染" 的项 $\sum_{j \ne k} \cdots$**：这一项是 Davis–Kahan 控制不住的——它通过 spectral gap 分母把"小 gap"的危险显式化，但好处是分子 $u_j^\top \Delta u_j$ 在我们的 GOE-like 噪声下可以做精细 concentration，于是即使 gap 小，污染也小。
3. **来自 noise kernel 的项 $\frac{1}{\lambda_k} P_{\mathrm{Ker}} \Delta u_k$**：这一项捕获"噪声从 $E[\hat C]$ 的零空间里漏进 $u_k$"的部分；它的尺度是 $\sqrt{d^q/n}/\lambda_k$，正好是 BBP 阈值。

这个工具的来源是 Eldridge–Belkin–Wang (2018) 的 "Unperturbed: spectral analysis beyond Davis–Kahan" 与 Greenbaum 等 (2020) 在数值线性代数文献里的扰动展开；作者直接说这一工具**"可以是独立感兴趣的"**——这是数学论文里相当含蓄的"这工具能用在别的地方"的说法。

### 2.6 从 sharp 到 smooth：怎么聚合？

光有单个方向的 sharp 阈值还不够，要看 **MSE**。论文 §2.2 给出了一个"未恢复尾巴"近似：把所有还没被打捞的方向贡献加起来，

$$
\text{MSE}(n) \;\approx\; \sum_{i > m(n)} a_i^2, \qquad a_i = |\lambda_i| = Z_\gamma i^{-\gamma}.
$$

其中 $m(n)$ 是在 $n$ 个样本下恢复的方向数。结合 BBP 门槛 $n_i \asymp d^q i^{2\gamma} / Z_\gamma^2$ 反推：

$$
m_n = \left( \frac{Z_\gamma^2 D}{n} \right)^{1/(2\gamma)} \cdot (-1) \quad \to \quad \text{Theorem 3.2}
$$

代入并对 $2\gamma > 1$ 的尾部求和，得到 **Theorem 3.2 / 公式 2.15**：

$$
\boxed{ \mathrm{MSE}(n) \;\asymp\; \left( \frac{n}{d^q} \right)^{-1 + \frac{1}{2\gamma}} }
$$

这就是论文要的"平滑幂律"——并且它的指数 $\alpha = 1 - \frac{1}{2\gamma}$ **直接由数据各向异性指数 $\gamma$ 决定**。$\gamma$ 越大（尾巴越长），$\alpha$ 越接近 1，scaling 越快；$\gamma \to 1/2^+$ 时 $\alpha \to 0$，scaling 退化为对数级——一条非常具体的相图。

### 2.7 实验：阶梯式 recovery 与 finite-size 平滑

作者在 $d \in \{120, 250, 400\}$、$q = 2$、$\varepsilon = 0.5$、$\gamma \in \{0, 0.2, 0.4, 0.6, 0.8, 1.0\}$ 的网格上跑了一组对照实验（论文 Figures 2–5）。三件最重要的观察：

1. **单方向跳变看得见**：Figure 4 左面板画的是每个 $i \in \{1, 3, 5, 8, 12, 15, 18, 20\}$ 在不同 $\alpha = \log(n)/\log(d)$ 下的 $\cos^2(\theta_i)$，曲线像一组阶梯——$i=1$ 在最小 $\alpha$ 就跳到 1，$i=20$ 要等到最大 $\alpha$ 才跳。
2. **跳变后是 $1/n$ 收敛**：跳变之后的 $1 - \cos(\theta_i)$ 在双对数图上是 $-1$ 斜率的直线，精确对上 Theorem 3.1 的 $O(d^q i^{2\gamma}/n)$ 预测。
3. **finite-size 把阶梯磨平**：$d = 120$ 时阶梯比 $d = 400$ 明显平滑——因为 $d \to \infty$ 极限下阈值才是 sharp 的，有限维下噪声波动把跳变"模糊"出有限宽度。MSE 曲线本身也呈现"近似但不严格"的幂律。

更妙的是 Figure 5 的非线性读出实验：把 $g_\star = \tanh$ 接到 $h^{(2)}$ 上之后，整体图景**一字不差**——MSE 曲线在与 first-layer 恢复对齐的同一时刻开始下降，证实"瓶颈是隐藏表征的恢复，而不是 readout 的拟合"。

> "the dominant bottleneck remains the recovery of the latent first-layer representation, rather than the final low-dimensional readout."
> —— §4, p. 10

这一句对实践派工程师有现实意义：它告诉你为什么 SFT 的 cap 通常来得很快——一旦底层表征里没有相应的 spike 跳出来，再多的 readout fitting 都没用。

---

## 3. 实验结果与亮点

让我用文字 + 自绘的 ASCII 图把核心实验讲清楚。

**(a) 阶梯式 recovery（Figure 4 重绘）**

```
cos²(θ_i)
1.0 ┤        ╭──────  i=1   ╭───── i=3   ╭───── i=5  ╭──── i=8 ╭──── i=12 ...
    │      ╱           ╱             ╱            ╱           ╱
    │    ╱           ╱             ╱            ╱           ╱
0.5 ┤   │           │            │           │           │
    │   │           │            │           │           │
    │   │           │            │           │           │
0.0 ┤───┴───────────┴────────────┴───────────┴───────────┴───────────────→ α = log(n)/log(d)
        1.7         2.0          2.3         2.6         2.9
```

每一条曲线是一个 $i$ 对应的 single-direction 对齐分数，跳变位置精确对应 $n_i = d^q i^{2\gamma}$。要点是：**这些跳变不是同时发生的——它们错位发生**。

**(b) 整体 MSE 是阶梯的"包络"（Figure 2 重绘）**

```
log MSE
 0  ┤●●●●●╲                                d=120 (粗虚线)
    │      ╲╲╲                             d=250 (实线)
-1  ┤        ╲●●╲╲                         d=400 (细实线)
    │            ╲╲╲╲╲
-2  ┤              ╲●╲╲●╲
    │                 ╲╲╲╲●╲
-3  ┤                    ╲●╲●●●●●●        ← 单条 d=400 的预测 power-law
    │
    └──────────────────────────────────────→ α
       1.5    2.0    2.5    3.0
```

随着 $d$ 增大，MSE 曲线在 $\alpha = 2.0$ 附近的跳变变得越来越尖锐——这是 finite-size smoothing 的活化石。

**(c) $\gamma$ 决定 scaling 速度（Figure 3）**

```
γ=0.0:  曲线 cliff —— 所有方向在同一 α 处一起跳，∼ step function
γ=0.4:  典型 power-law，斜率 ≈ -0.25
γ=1.0:  曲线在 wide α 区间里缓慢下降，斜率 ≈ -0.5
```

这把 Kaplan 经验观察到的 $\alpha \approx 0.34$ 解释成了 **"数据 / 任务的特征强度幂律指数 $\gamma$ 决定了 loss 幂律指数"**——给出了一个清晰可证伪的预测：如果你能测量数据里隐藏方向的强度分布，你就能预测 scaling exponent。

**(d) 非线性读出"不改变图景"（Figure 5）**

把内层激活从 identity 换成 $\tanh$，整张图几乎不动。这是论文最容易被忽略但工程上最重要的发现之一——**外层非线性不是 scaling 的瓶颈**。

---

## 4. 这篇论文的位置（关联图谱）

### 上游：它建立在哪里

这篇论文坐在三条研究路线的交叉口：

1. **Kernel/Random-feature scaling law 的"老世界"**：Caponnetto–De Vito (2007)、Bordelon–Canatar–Pehlevan (2020)、Cui–Loureiro–Krzakala–Zdeborová (2021, 2023)、Bahri 等 (2024 "Explaining neural scaling laws")。这一族解释假定表征固定。本文**与之对话**——它在更复杂、有 feature learning 的设定里复现了同样的幂律家族，于是说明"幂律不依赖于表征是否被学习"。
2. **Hierarchical multi-index 的"新世界"**：Cagnetta 等 2024 [random hierarchy model](https://arxiv.org/abs/2307.02129)、Tabanelli 等 2026 hierarchical spectral method、Dandi–Pesce–Zdeborová–Krzakala 2025 "computational advantage of depth"。本文是这条路线的直接延续——它**加入了 power-law spectrum 这一新的成分**，使得相同的层级 spectral 框架能产生幂律 scaling，而不是阶跃 scaling。
3. **eigenvector perturbation beyond Davis–Kahan**：Eldridge–Belkin–Wang 2018、Greenbaum 等 2020 在数值线性代数和谱聚类里的工作。本文把这条工具线移植到了 ML 标度律理论里，是一次方法上的"跨界引进"。

### 同期对手

- **Defilippis–Krzakala–Loureiro–Maillard 2026a "Optimal scaling laws in learning hierarchical multi-index models"**（arXiv:2602.05846）：同一作者群三个月前的姊妹工作，研究的是 SGD 训练下的 scaling laws；本文用 spectral 算法替换 SGD，得到更紧的常数与 matching lower bound。
- **Bordelon–Atanasov–Pehlevan 2024a "A dynamical model of neural scaling laws"**：用 dynamical mean field theory 解释 SGD 训练下的 scaling，主张"power-law spectrum + SGD 时间动力学"；本文用 spectral algorithm 给出了一个"无 SGD 也能复现幂律"的对照。
- **Ren 等 2025、Defilippis 等 2026b "Scaling laws and spectra of shallow neural networks"**：研究 shallow quadratic networks 的 feature-learning regime；本文是它的多层版本。

### 下游可能催生什么

1. **可证明的 scaling-law data engineering**：如果"scaling exponent = data anisotropy index $\gamma$"成立，那么数据混合策略就有了理论指导——不是盲目混合，而是**针对性地调控隐藏方向的强度分布**。这与 [DataComp](https://www.datacomp.ai/) 一类经验性工作能形成漂亮的理论桥梁。
2. **MoE 与稀疏路由的解释**：MoE 路由器在做的事，本质就是把不同 spike 分给不同 expert 学。这套理论很可能可以推广到 MoE 上，给出"专家数量 vs 总参数 vs 路由稀疏度"的可证明 scaling law（参见 [我们对 MSSP/μP 的导读](/post/paper-2605.14200/)）。
3. **解释 grokking、emergence 等"非平滑"现象**：如果你看到的不是平滑曲线而是阶跃 / sigmoid 曲线，那就是你**还没穿越足够多的特征跳变**——这给了 [Scott Alexander "Sigmoids 不是 exponential"](/post/good-read-scott-alexander-sigmoids-ai-scaling/) 那篇怀疑论一个很有意思的反向解读：sharp 跳变不是 scaling 终结，而是 finite-size 下的 transient。
4. **超越 Gaussian 输入**：作者明示"自然下一步是非高斯输入、richer nonlinearities、higher information exponents"——这条 program 至少还能写 5 年。

---

## 5. 编辑批判性评论

我对这篇论文的评分是 **Opus 9.0**，但有四个我必须指出的批判点。

**(1) "学习器"是 spectral，不是 SGD。** 论文 Remark 2.1 引用 Tabanelli et al. (2026)，声称"spectral 估计器是 SGD 在这种 hierarchical setting 下自然涌现的"——这是个**间接论证**，而不是直接证明。如果你的真实问题是"为什么 Llama-2 7B 训练曲线长这样"，本文的结论需要做一步"假装 SGD ≈ spectral algorithm"的跨越，这一步的严谨性是有争议的。Bordelon 等的动力学方法对此更直接。

**(2) Gaussian input 假设强得过分。** 真实 token embedding 不是 Gaussian——它的统计结构有"幂律词频 + 短语层次 + 句法层级"等等。论文用 Wiener-chaos 与 Hermite analysis 的好处恰恰来自 Gaussianity，迁移到非 Gaussian 时整个证明会断掉。Universality 研究（Lu–Yau 2025、Hu 等 2024）给了一些希望，但仍是开放问题。

**(3) "$\gamma$ 决定 $\alpha$"是漂亮的预测，但 $\gamma$ 怎么量？** 论文给了一条**结构性**的解释——但没告诉工程师怎么在真实数据集上**测量** $\gamma$。这是从理论物理 → 工程实践的最后一公里。如果不能测量 $\gamma$，那么"scaling exponent 可以预测"的承诺就只是承诺。

**(4) 实验规模不撑场面。** 最大的 $d$ 只到 800，最大的 $d_1$ 只有约 $\sqrt{800} \approx 28$。这对一个 54 页的论文来说不是问题（它的工作是 prove，不是 benchmark），但工程师读到 "MSE(n) ≍ (n/dᵠ)^{−1+1/(2γ)}" 时不能立即说"那 Llama-2 也会这样"——还差一个 sim2real 的桥。

**那么工程实践中能不能用？** 短期内**不直接**——这是 ML 理论而非工具。但中期它能改变你看问题的方式：

- **数据 mix 决定 scaling**：选数据时不只是看 token 数，还要看你能否让隐藏特征的强度分布**更长尾**。
- **早停 ≠ 缺陷**：当你看到训练曲线在 $10^5$ tokens 处出现"平台"，这可能是某个 i 的 BBP 阈值还没到；继续训练而不是急着换算法。
- **interpretability 的微观图像**：mech interp 现在流行"feature emergence"叙事——本文给出了一个数学上 sharp 的、可以测量的 emergence 定义（直接看 $\cos^2(\theta_i)$）。

> 与本站既有论文导读的对话：
>
> - 如果你读过 [Chinchilla scaling law 的统计不可识别性](/post/paper-2605.08541/)，这篇论文从微观角度告诉你：**为什么 $A$ 和 $B$ 这两个尺度系数其实没法独立估计**——它们都是同一个 $\gamma$ 的不同投影。
> - 如果你关心 [DeepMind 关于 CoT 监控的隐藏失败](/post/paper-2605.15257/) 或 [RoPE 的长上下文失败](/post/paper-2605.15514/)，那是工程 / 安全侧的"现象学"；本文提供的是工程现象背后**可证明的微观解释**。
> - 如果你和我一样厌倦了 [Scott Alexander "Sigmoid 必然替代 exponential"](/post/good-read-scott-alexander-sigmoids-ai-scaling/) 的那套修辞——本文是数学反例：sigmoid-shaped emergence 与 exponential-shaped scaling 可以**在同一个机制下共存**。

---

## 6. 配套资料导览

本篇导读附带四份精读材料，建议按需取用：

- **[architecture-mindmap.svg](./architecture-mindmap.svg)**：一张 4 分区思维导图，把 Compositional Setup / Spectral Algorithm / Main Theorems / Technical Novelty 分别用蓝橙绿紫四色画清楚——你想跟同事在白板上 5 分钟讲完这篇时直接用它。
- **[concept-cards.md](./concept-cards.md)**：14 张精炼概念卡，从"标度律"到"信息指数"到"Davis–Kahan 不够用"，每张 150–220 字，方便单独引用或贴到 wiki。
- **[glossary.md](./glossary.md)**：50 条中英对照术语表，按重要性排序，覆盖 RMT、Hermite analysis、feature learning、perturbation theory 五大主题——读不下英文论文时直接对照查。
- **[key-equations.md](./key-equations.md)**：8 个核心公式逐条解读（含直觉解释 + 在论文中的位置 + 与全局推导链的关系），用 KaTeX 排版——纸笔推导时的精确清单。

---

## 7. 谁该读这篇论文

- **理论机器学习研究者**：必读。这是 Krzakala / Loureiro 团队 2026 年最重要的输出之一，是 hierarchical multi-index program 的里程碑。
- **训练 foundation model 的工程师**：值得读 §1、§2.7 与 §5。理解"为什么训练曲线长这样"会改变你对 data mix 与 hyperparameter sweeping 策略的直觉。
- **mech interp / feature emergence 研究者**：必读 §3 与 Figure 4。它给出"feature emergence"一个 sharp 的、可测量的定义——$\cos^2(\theta_i)$ 的跳变曲线就是 mech interp 想看的东西，只是这里在 toy 上做对了。
- **数据团队 / data engineering**：值得读 §5 的 future directions。如果"scaling exponent = data anisotropy"这条预测成立，那 data engineering 就有了第一个 principled 评估指标。
- **数学背景的同学**：必读 §3 + Appendix D。Neumann 展开 + Hermite analysis + GOE 的组合相当精彩，是高维统计的活教材。

---

## 8. 一句话总结

> **平滑标度律不是某种"自然律"，它是几百次 sharp 的、个体特征"破水跳出"的累积——而 power-law 数据各向异性决定了这些跳变如何错位排列、又如何聚合成一条直线。**

[^bahri]: Bahri 等 "Explaining neural scaling laws" (2024), [arXiv:2102.06701](https://arxiv.org/abs/2102.06701) 给出了 kernel-spectral 视角的标度律解释，但表征固定。
[^defilippis2025]: Defilippis–Krzakala–Loureiro–Maillard "Optimal scaling laws in learning hierarchical multi-index models" (2026), [arXiv:2602.05846](https://arxiv.org/abs/2602.05846).
[^tabanelli2026]: Tabanelli 等 (2026) hierarchical spectral method, 论文 reference 列表中标为 Tabanelli et al. 2026。
[^bbp]: Baik–Ben Arous–Péché "Phase transition of the largest eigenvalue for non-null complex sample covariance matrices" (2005), [arXiv:math/0403022](https://arxiv.org/abs/math/0403022). BBP 相变是 spike detection 的经典门槛。

