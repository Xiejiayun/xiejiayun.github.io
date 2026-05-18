# 关键公式解读 · MSSP

> 用 KaTeX 数学环境逐一拆解 MSSP 论文里 7 个最关键的公式。建议先读 [正文导读](./) 再回看本文。

---

## 公式 1 · MoE 块的核心递归

$$
h^{l}_{t} = h^{l-1}_{t} + K^{-\alpha_{\text{agg}}} \sum_{i \in \text{top-}K} \phi^{l}_{t,i} \cdot W^{l,\text{out},i}_{t}\, \varphi\!\left(W^{l,\text{in},i}_{t}\, h^{l-1}_{t}\right)
$$

**逐项解读**：

- $h^{l-1}_t$ — 第 $l-1$ 层（前一层）的残差流（residual stream）激活，在 token-step $t$
- $K^{-\alpha_{\text{agg}}}$ — 对 top-$K$ 个被选中专家做平均的归一化因子；$\alpha_{\text{agg}} \in [0, 1]$ 是论文重点求解的指数之一
- $\phi^{l}_{t,i} = \sigma(\beta (Q^l_t h^{l-1}_t)_i)$ — router 给第 $i$ 个 expert 的 gate 值，$\sigma$ 为 sigmoid 或 softmax，$\beta$ 是温度
- $W^{l,\text{out},i}_t \varphi(W^{l,\text{in},i}_t h^{l-1}_t)$ — 第 $i$ 个 expert 的内部 FFN：先 down-project 到 expert 宽度 $N_e$，再非线性激活 $\varphi$，再 up-project 回残差流宽度 $N$

**为什么这个递归在缩放分析上"困难"**：跨 $i$ 求和 + router 与 expert 强耦合 + 残差连接，三者使得"对单个权重求 ∂"的传统信号传播分析必须**同时**追踪三个尺度（N, N_e, M），并且这三者趋于无穷的相对速率会改变极限——这就是为什么必须分 3 个 Regime。

---

## 公式 2 · bcdα 参数化

$$
W_0 \sim \mathcal{N}(0,\, n^{-2 b_W}), \qquad W_t = W_{t-1} - \eta\, n^{-c_W}\, \Psi_t\!\left(n^{d_W} g_0, \ldots, n^{d_W} g_t\right)
$$

其中 $g_t = \nabla_W \mathcal{L}_t$ 是梯度，$\Psi_t$ 是 optimizer 的核心算子（entrywise）。

**三元组 $(b_W, c_W, d_W)$ 的含义**：

- $b_W$：**初始化方差缩放**——单个 entry 的标准差是 $n^{-b_W}$
- $c_W$：**学习率缩放**——effective LR 是 $\eta n^{-c_W}$
- $d_W$：**梯度归一化缩放**——在送入 optimizer 前对梯度做的 $n^{d_W}$ 缩放（对 Adam 这个特别重要，因为 Adam 内部要除以梯度二阶矩）

**MSSP Table 1 就是把这三元组（加上 $\alpha_{\text{agg}}$）填进每个权重 × 每个 Regime × 每个 optimizer 的格子里**。共大约 24 个非平凡条目。

---

## 公式 3 · Aggregation 三项分解（论文 Eq. Agg）

这是论文最核心的等式，所有诊断和修补都从它出发：

$$
h^{\text{agg}}_t = \frac{1}{M} \sum_{i=1}^{M} \phi^{l}_{i} \cdot \left( \underbrace{W^{l,\text{out},i}_0\, h^{l,\text{in}}_{0,i}}_{\text{init}} + \underbrace{\Delta W^{l,\text{out},i}_t\, h^{l,\text{in}}_{t,i}}_{\text{effective}} + \underbrace{W^{l,\text{out},i}_0\, \Delta h^{l,\text{in}}_{t,i}}_{\text{propagating}} \right)
$$

**为什么这个分解是"对的"**：把 $W^{l,\text{out},i}_t = W^{l,\text{out},i}_0 + \Delta W^{l,\text{out},i}_t$ 和 $h^{l,\text{in},i}_t = h^{l,\text{in},i}_{0,i} + \Delta h^{l,\text{in},i}_t$ 同时代入 $W h$，得到四项（init×init, init×Δ, Δ×init, Δ×Δ）；其中 init×init 就是 init，init×Δ 是 propagating，Δ×init 是 effective，Δ×Δ 是高阶可忽略。

**MSSP 公理就是：上面每一项单独都必须是 Θ(1)**。

---

## 公式 4 · Regime II 下 propagating 项的 LLN/CLT 判别

在 Regime II（$N_e = \Theta(1)$）下，propagating 项中关键的"主项"形式为：

$$
\frac{1}{M} \sum_{i=1}^{M} \phi^{l}_{i}\, G_i\, u, \qquad G_i := W^{l,\text{out},i}_0 (W^{l,\text{out},i}_0)^\top \in \mathbb{R}^{N \times N}, \quad u \propto \delta^{l+1}_t
$$

其中 $u$ 是反向传播的 error 信号，**对所有 expert 共享**。

**关键事实**：当 $N_e = \Theta(1)$ 时，$G_i$ 是秩 $N_e$ 的，等价于（缩放后）一个 $\mathrm{Gr}(N_e, N)$ 上 Haar-均匀的正交投影。$M$ 个 expert 之间的 $G_i$ **互相独立**且**没有共享方向**。所以 $\{G_i u\}_{i=1}^M$ 是 i.i.d.，平均会被 √M 抑制——CLT 行为，幅度 $\Theta(1/\sqrt{M})$。

**Regime III 下变化**：$N_e \asymp N$ 时，Marchenko-Pastur 让 $G_i \approx c I_N$ 对所有 $i$ 都一样——所有 $G_i u \approx c u$ 共享方向 $u$——平均不再被抑制，幅度回到 $\Theta(1)$ 的 LLN 行为。

**这就是为什么 Regime II 和 III 需要结构上不同的 fix**。

---

## 公式 5 · MSSP 公理（数学化版本）

> **Maximal Scale Stability for MoEs**：把权重写为 $W = W_0 + \Delta W$ 并将这一分解传播到整个网络后，**所有被分解出来的原子贡献**都必须是 $\Theta(1)$：

形式化的三类条件：

1. **Forward μ-条件**（沿用 μP）：
$$\|h^l_t\|_{\text{RMS}} = O(1), \quad \exists t: \|\Delta h^{l}_{t+1}\|_{\text{RMS}} = \Theta(1)$$

2. **Backward 对称条件**：对任意 $h^l_t = W^l_t x^{l-1}_t$，反向传播也分解 $\bar\delta^{l-1}_t = (W^l_0)^\top \delta^l_t + (\Delta W^l_t)^\top \delta^l_t$，**两项分别保持 $\Theta(1)$**（在适当归一化下）

3. **聚合条件**：在 Aggregation 分解（公式 3）中，**init / propagating / effective 三项分别保持 $\Theta(1)$**；对反向 expert-aggregated 梯度也有对称要求

**重点**：MSSP 公理在 dense 网络上**等价于** μP（因为没有跨通道聚合）；只有当架构含有"M 个并行通路 + 跨通路求和"时才严格更强。

---

## 公式 6 · Regime II MSSP 的关键单点修补

**MSSP-Regime-II 处方**（论文 Table 1 中和 μP 唯一不同的一行）：

$$
\text{Expert Layer 2 Init. Std.} = \underbrace{N_e^{-1/2}}_{\mu P} \quad \longrightarrow \quad \underbrace{M^{1/2}\, N_e^{-1/2}}_{\text{MSSP}}
$$

**直觉为什么 $\sqrt{M}$ 倍正好**：在 Regime II 下，init 项的 CLT 抑制因子是 $1/\sqrt{M}$；把每个 expert 输出的初始幅度乘以 $\sqrt{M}$，平均后正好抵消，得到 $\Theta(1)$。

**整张表的影响范围**：MSSP-Regime-II 处方**只改这一项**——其他 init / LR / Adam ε 全部和 μP 一致。换句话说，**一行代码就修好了**。

---

## 公式 7 · DMFT 路径积分骨架（MSRDJ）

论文 Sec 5 用的核心数学工具，描述训练动力学的生成泛函：

$$
Z[\eta] = \int \mathcal{D}\phi\, \mathcal{D}\hat\phi\, \exp\!\left( i \int \mathrm{d}t\, \hat\phi(t) \left[ \partial_t \phi(t) - F[\phi(t)] \right] + \int \mathrm{d}t\, \eta(t)\, \hat\phi(t) \right)
$$

- $\phi(t)$：原始动态变量（在 MoE 中是各层激活、梯度、router state 等）
- $\hat\phi(t)$：辅助"响应场"（response field），保证 $\partial_t \phi = F[\phi]$ 被强制满足
- $F[\phi]$：训练动力学的"右手项"，由 SGD 更新规则给出
- $\eta(t)$：外源场，用于推出响应函数

**怎么用**：
1. 对随机初始化 $W_0 \sim \mathcal{N}(0, n^{-2b})$ 做平均，得到 effective action $S[\phi, \hat\phi]$
2. 取 $n \to \infty$ 鞍点近似（saddle-point）
3. 写出自一致方程组：order parameter（如 kernel $K_t = \langle \phi_t \phi_t^\top \rangle$）= 它们自己积分的函数
4. 数值或分析求解

**在 MoE 上额外的复杂度**：必须同时追踪 4 个层级的 single-site 过程（公式见 [概念卡 15](./concept-cards.md#卡片-15--四层条件分布层级regime-iii--mssp-dmft-极限)）——这是 dense μP 文献中从未出现过的结构。

---

## 公式 8 · LR 迁移的"操作性"测试

工程上判断 MSSP 是否 work 的最简单 metric：

$$
\eta^*(N_1) \stackrel{?}{=} \eta^*(N_2) \quad \forall\, N_1, N_2
$$

也就是：**在不同 $N$ 下扫学习率，最优 $\eta^*$ 是不是同一个数**？

论文图 6 的实际比较：

```
                Regime II × μP    Regime II × MSSP
   N=256:       η* ≈ 7e-3         η* ≈ 5e-3
   N=512:       η* ≈ 5e-3         η* ≈ 5e-3
   N=1024:      η* ≈ 3e-3         η* ≈ 5e-3
   N=2048:      η* ≈ 1.5e-3       η* ≈ 5e-3
```
（数值为示意趋势，对照论文 Fig 6）

**判读**：μP 下最优 LR 随 N 单调下降 → 不迁移；MSSP 下最优 LR 在四个尺度上**严格一致** → 完美迁移。

> 注：上表为对照论文 Figure 6 的趋势化描述，并非论文给出的精确数值；本表仅用于教学说明 LR-transfer 的判定方法。读者请以论文原图为准。

---

## 总结表 · 8 个公式的角色

| # | 公式 | 在论文中的角色 |
|---|---|---|
| 1 | MoE 递归 | 整个分析的对象 |
| 2 | bcdα 参数化 | 缩放语言（语法）|
| 3 | Aggregation 三项分解 | 诊断的"显微镜"|
| 4 | CLT/LLN 判别 | 解释 μP 为什么失败 |
| 5 | MSSP 公理 | 新的设计准则 |
| 6 | Regime II 修补 | 工程师最关心的"一行修复"|
| 7 | MSRDJ 路径积分 | 严格证明的工具 |
| 8 | LR 迁移测试 | 验收标准 |
