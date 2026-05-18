# MinT 关键公式解读

> 配套 [【论文导读】MinT](./)
>
> MinT 是一份系统论文，公式不多，但有几条核心数学决定了它整个设计的可行性。本节用 KaTeX 把这些数学展开。

---

## 1. LoRA 的基础数学

LoRA 把一个原始权重 $W \in \mathbb{R}^{d \times k}$ 的更新写成两个低秩矩阵之积：

$$
W' = W + \Delta W, \quad \Delta W = B A, \quad B \in \mathbb{R}^{d \times r},\ A \in \mathbb{R}^{r \times k}
$$

其中秩 $r \ll \min(d, k)$。训练时只更新 $A, B$，原始 $W$ 完全冻结。

**参数量比例**（这是 MinT 「adapter 小于 1% base」论断的数学基础）：

$$
\frac{|A| + |B|}{|W|} = \frac{r \cdot k + d \cdot r}{d \cdot k} = r \cdot \left(\frac{1}{d} + \frac{1}{k}\right)
$$

对于 Qwen3-4B 一个典型的 attention 投影 $d = k = 3584$，rank $r = 1$ 时：

$$
\text{ratio} = 1 \cdot \left(\frac{1}{3584} + \frac{1}{3584}\right) \approx 0.056\%
$$

聚合所有 target modules 后约 0.10%，与论文实测 rank-1 ≈ 7.9 MiB 一致。

---

## 2. GRPO 与重要性采样

GRPO（Group Relative Policy Optimization）的核心 objective 大致形式为：

$$
\mathcal{L}_{\text{GRPO}} = -\mathbb{E}_{\tau \sim \pi_{\text{old}}} \left[ \sum_t \min\left( \rho_t \hat{A}_t,\ \text{clip}(\rho_t, 1-\epsilon, 1+\epsilon) \hat{A}_t \right) \right]
$$

其中重要性比例：

$$
\rho_t = \frac{\pi_{\theta}(a_t | s_t)}{\pi_{\text{old}}(a_t | s_t)}
$$

而组相对优势（同 prompt 一组 rollout 内归一化）：

$$
\hat{A}_t = \frac{r_i - \mathrm{mean}(\{r_j\}_{j=1}^G)}{\mathrm{std}(\{r_j\}_{j=1}^G)}
$$

这里 $r_i$ 是第 $i$ 条 rollout 的 reward，$G$ 是组大小。

**为什么 train-rollout 一致性很重要？** 因为 $\rho_t$ 假设我们能精确计算 $\pi_{\theta}(a_t|s_t)$。一旦 train 和 rollout 的 forward 路径（MoE 路由 / DSA indexer）不一致，$\rho_t$ 就会带上**架构噪声**，导致 advantage 信号被污染。

---

## 3. IcePop 重要性裁剪（DSA 一致性）

MinT 借鉴 IcePop（arXiv:2510.18855）的做法处理 DSA indexer 漂移：

$$
w_t = \begin{cases}
1, & \rho_t \in [1 - \delta_-,\ 1 + \delta_+] \\
0, & \text{otherwise}
\end{cases}
$$

然后把 GRPO 的 token-level objective 用 $w_t$ 屏蔽：

$$
\mathcal{L}^{\text{IcePop}}_{\text{GRPO}} = -\mathbb{E} \left[ \sum_t w_t \cdot \min\left( \rho_t \hat{A}_t,\ \text{clip}(\rho_t, 1-\epsilon, 1+\epsilon) \hat{A}_t \right) \right]
$$

**含义**：当某个 token 的 train/rollout 概率比离开置信带（说明该 token 的架构状态不一致），就**完全丢弃**这个 token 的梯度。

**代价分析**：设 token 不一致率为 $p_{\text{drop}}$，则有效 batch size 缩水为 $(1 - p_{\text{drop}}) \cdot B$。MinT 实测 $p_{\text{drop}}$ 对 Qwen3-30B + R3 约 0.0013%，对 Qwen3-235B 约 0.0253%，对 GLM-5/5.1 + DSA 视 IcePop 配置在 0.x% 量级——可接受范围内。

---

## 4. 三层 Cache 的容量约束方程

MinT 三层 cache 之间满足如下硬约束：

$$
|\text{GPU batch}| \le 64 \le |\text{CPU cache}| \le |\text{Catalog}|
$$

设：
- $N_c$ = catalog 大小（10⁶ 量级）
- $N_{\text{cpu}}$ = CPU cache 容量（~500/engine）
- $N_{\text{gpu}}$ = GPU batch frontier（实测 64）
- $H$ = hot set size（活跃 adapter 数）

**Warm-path engine 数下界**（假设 hot set 均匀分布）：

$$
n_{\text{engines}}^{\text{warm}} = \left\lceil \frac{H}{N_{\text{gpu}}} \right\rceil = \left\lceil \frac{H}{64} \right\rceil
$$

论文给出的 2300 active wave 例子：$n_{\text{engines}} = \lceil 2300 / 64 \rceil = 36$（4 GPUs/engine → 144 GPUs）。

**Cold-path 隔离 fleet** 由 cold load rate $\lambda$ 与每 engine 冷启动上限 $C_{\text{cold}}$ 决定：

$$
n_{\text{engines}}^{\text{cold}} = \left\lceil \frac{\lambda}{C_{\text{cold}}} \cdot T_{\text{cold}} \right\rceil
$$

论文实测 $\lambda = 38.3$ LoRA/s，$C_{\text{cold}} = 32$/engine，$T_{\text{cold}} \approx 60$ s（worst-case cold p95 量级）→ $n^{\text{cold}}_{\text{engines}} \approx 72$（288 GPUs）。

总 fleet 是 warm + cold 之和：**144 + 288 = 432 GPUs** for 1M catalog + 2300 active wave。

---

## 5. Packed MoE LoRA 的加载时间模型

设原始 MoE LoRA 由 $N$ 个小 tensor 组成（论文实测 $N = 37{,}248$）。加载时间近似为：

$$
T_{\text{load}}^{\text{naive}} = N \cdot (t_{\text{seek}} + t_{\text{alloc}} + t_{\text{build}}) + \frac{S}{B}
$$

其中：
- $t_{\text{seek}} + t_{\text{alloc}} + t_{\text{build}}$ ≈ per-tensor 元数据开销（约 20 μs/tensor 在现代 PyTorch loader）
- $S$ = 总字节数（约 110 MB）
- $B$ = IO 带宽（NVMe 约 3 GB/s）

代入：$T^{\text{naive}}_{\text{load}} \approx 37248 \times 20\,\mu\text{s} + 110\,\text{MB}/3\,\text{GB/s} \approx 0.745\,\text{s} + 0.037\,\text{s} \approx 0.78\,\text{s}$

打包后 $N' = 672$：

$$
T_{\text{load}}^{\text{packed}} \approx 672 \times 20\,\mu\text{s} + 0.037\,\text{s} \approx 0.013\,\text{s} + 0.037\,\text{s} \approx 0.05\,\text{s}
$$

**理论加速比** ≈ 15×。论文实测 **8.5–8.7×**，差距来源于 PyTorch tensor 构建路径中还有其他不可消除开销。

**关键洞察**：在大模型 IO 路径里，**对象数往往比字节数更重要**——这是论文最反直觉的一条工程经验。

---

## 6. 并发 GRPO 的气泡填充模型

设单 policy GRPO 一步的时间分解：

$$
T_{\text{step}}^{\text{single}} = T_{\text{rollout}} + T_{\text{reward}} + T_{\text{forward}} + T_{\text{backward}} + T_{\text{optim}}
$$

其中 $T_{\text{rollout}}$ 阶段 GPU 上的训练侧大部分空闲——它在等 sampler 跑完。

**MinT 的并发 schedule**：让 $K$ 个 policy 的 GRPO step 交错执行，使得 policy $i$ 的 rollout 阶段被 policy $j$ 的 forward/backward 填充：

$$
T_{\text{step}}^{\text{concurrent}}(K) \approx \max(K \cdot T_{\text{forward+backward}}, T_{\text{rollout}}) + T_{\text{optim}}
$$

理论加速比上限：

$$
\text{speedup}_{\text{max}}(K) = \frac{K \cdot T_{\text{step}}^{\text{single}}}{T_{\text{step}}^{\text{concurrent}}(K)} \le K
$$

实测 $K=3$ 时 Qwen3-4B 取得 **1.77×**（理论上限 3×，约 59% 达到率），Qwen3-30B 取得 **1.45×**（48% 达到率）。30B MoE 因为 forward/backward 更重，rollout 气泡的相对占比更小，所以填充收益更低——这与公式预测一致。

---

## 7. Adapter Handoff 的 critical path 公式

传统 merge handoff：

$$
T_{\text{handoff}}^{\text{merge}} = T_{\text{merge}} + T_{\text{checkpoint write}} + T_{\text{ckpt read}} + T_{\text{load full}} + T_{\text{cold sample}}
$$

MinT adapter handoff：

$$
T_{\text{handoff}}^{\text{adapter}} = T_{\text{export LoRA}} + T_{\text{LoRA write}} + T_{\text{LoRA read}} + T_{\text{attach to base}} + T_{\text{cold sample}}
$$

由于 LoRA 字节数为 base 的 ~1%–3.3%，IO 项缩水 30–100×；同时 attach-to-base 比 load-full-checkpoint 快几十倍（base 不动）。

实测：

| 模型 | merge handoff | adapter handoff | 加速 |
|---|---|---|---|
| Qwen3-4B | (71.82 + 55.70) ≈ 127.5 s | (0.036 + 4.114) ≈ 4.15 s | **30.7×** 单步 IO+load；含 sample 后约 **18.3×** |
| Qwen3-30B MoE | (402.25 + 156.07) ≈ 558.3 s | (46.46 + 117.30) ≈ 163.8 s | **3.41×** 单步 IO+load；含 sample 后约 **2.85×** |

---

## 总结

MinT 的核心数学其实只有 7 条，分布在三个层面：

1. **LoRA 本身的低秩参数学**（公式 1）→ 决定 adapter <1% 的可能性
2. **RL 一致性的重要性采样数学**（公式 2-3）→ 决定 train-rollout 一致性是 MoE/DSA RL 的可行性边界
3. **服务调度的容量约束与加载时间模型**（公式 4-7）→ 决定百万 LoRA 服务的 fleet 经济学

理解了这 7 条，你就能用同一套数学去评估市面上任何一个 RL-as-a-service / multi-LoRA serving 方案是否合理。
