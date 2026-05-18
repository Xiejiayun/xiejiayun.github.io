# 关键概念卡片 · MSSP / μP / MoE Scaling

> 这是 [《MoE 时代的 μP：MSSP》导读](./)的随读卡片集。每张卡片可独立阅读，建议按问题驱动顺序使用。

---

## 卡片 1 · μP（Maximal Update Parameterization）

**一句话**：让神经网络的训练动力学在宽度 → ∞ 时收敛到一个非退化极限的参数化方案，使小模型最优超参可以**直接迁移**到大模型。

**核心三公理**
1. **稳定 + 特征学习**：激活幅度保持 Θ(1)，每次更新带来的特征变化也保持 Θ(1)
2. **最大有效更新 + 传播更新**：来自本层权重的 Δh 和来自上游的 Δh 都保持 Θ(1)
3. **忠实性**：optimizer 输入是 Θ(1) 的，从而 Adam 的 ε 可以正确缩放

**对应原始论文**：Yang & Hu 2021；实证应用：Yang et al. 2022 (μTransfer)

**和 MSSP 的关系**：在 dense 网络上两者等价；在 MoE 上 MSSP 严格更强。

---

## 卡片 2 · MSSP（Maximally Scale-Stable Parameterization）

**一句话**：μP 的 MoE 扩展——要求把权重 $W = W_0 + \Delta W$ 完全展开后**每一个被分解出来的原子贡献**在 forward 和 backward 两条路径上都保持 Θ(1)。

**为什么需要它**：MoE 多了一根跨专家求和的"通路"。dense μP 只看总和 Θ(1)——会容忍 init = O(1/√M)、effective = Θ(1) 这种内部失衡，结果是小尺度上看不出问题、大尺度上突然崩。

**实操含义**：一张完整的 (b, c, d, α) 缩放指数表，覆盖 4 种 weight × 3 种 Regime × {SGD, Adam}。

---

## 卡片 3 · MoE 的三种 Co-scaling 区制

```
Regime I  : N ≍ N_e → ∞,  M, K = Θ(1)   "少而宽" GShard/Switch
Regime II : N ≍ M ≍ K → ∞,  N_e = Θ(1)  "细粒度" DeepSeek/Qwen
Regime III: N, N_e, M, K 全部 → ∞       全比例放大（理论干净）
```

**为什么必须分开**：MoE 的 scaling 不可交换——先把 M 推到 ∞ 再推 N，和反过来推，得到的极限分布是**结构上不同的**。论文中 Regime III 的 MSSP 极限是**四层条件分布层级**，而 Regime II 只有两层，这种差异 dense μP 完全看不到。

---

## 卡片 4 · CLT/LLN 失衡：MoE 失败的根源

**对 M 个独立专家做平均**，根据每个 summand 的方向是否相干，会出现两种极限：

- **i.i.d. 随机方向**：被 √M 抑制（中心极限定理风格）→ Θ(1/√M)
- **共享相干方向**：保持 Θ(1)（大数定律风格）

```
Regime II × μP 下的失衡：
─────────────────────────
  init aggregate   : CLT,  Θ(1/√M)  ← 太小
  effective term   : LLN,  Θ(1)     ← 标准
  propagating term : CLT,  Θ(1/√M)  ← 太小
─────────────────────────
```

**后果**：训练初期 ∆h_agg 被 init 和 propagating 主导，feature learning 实际上消失，需要几百~几千步才能"自愈"——大尺度模型自愈得更慢，因此更差。

---

## 卡片 5 · Aggregation 三项分解

对 post-aggregation 激活的变化做权重分解：

$$
h^{\text{agg}}_t = \tfrac{1}{M} \sum_i \phi_i \cdot ( \underbrace{W^{\text{out},i}_0 h^{\text{in},i}_0}_{\text{init}} + \underbrace{\Delta W^{\text{out},i}_t h^{\text{in},i}_t}_{\text{effective}} + \underbrace{W^{\text{out},i}_0 \Delta h^{\text{in},i}_t}_{\text{propagating}})
$$

- **init**：来自初始随机权重的贡献（两层 Gaussian chain → CLT）
- **effective**：来自本 expert 输出权重更新（被 δ^{l+1} 锁定方向 → LLN）
- **propagating**：来自上游传过来的 Δh^{in}（在 Reg II 仍是 CLT，在 Reg III 因 Marchenko-Pastur 变成 LLN）

**MSSP 的修补**正是让所有三项都变成 Θ(1)。

---

## 卡片 6 · Regime II 的 Fix：放大 expert init variance

**单一干预**：把 expert 输出权重的初始化标准差从 $1/\sqrt{N_e}$ 改成 $\sqrt{M/N_e}$。

```python
# μP（错）
nn.init.normal_(expert_out.weight, std=1.0/math.sqrt(N_e))

# MSSP-Regime II（对）
nn.init.normal_(expert_out.weight, std=math.sqrt(M)/math.sqrt(N_e))
```

**为什么是 √M**：精确地 compensate 掉 init aggregate 的 CLT 抑制——单个 expert 的输出幅度乘 √M、跨 M 个专家平均除 √M、净效果是 Θ(1)。

**适用范围**：top-K 路由 + 负载平衡辅助损失（DeepSeek-V3 / Qwen-MoE / Mixtral 范式）。

---

## 卡片 7 · Regime III 的 Fix：专家共享初始化

**反直觉的设计**：在 t=0 时让**所有 M 个专家拥有完全相同的权重矩阵** $W^{\text{in,i}}_0 = W^{\text{in}}_0$。

**为什么这不会让所有专家完全等价**：
1. router 给每个专家分配不同的输入子集
2. 不同输入诱导不同的梯度
3. 第一步 SGD 之后 expert 自然分化
4. 但保留了 t=0 时**所有专家张成同一个特征空间**的 nice 结构

**这避免了什么**：Regime III 下 Marchenko-Pastur 让 $G_i \approx c I$，独立 init 时 propagating term 会变成 LLN-Θ(1) 而不是 CLT-Θ(1/√M)，导致和 effective term 同阶但**方向冲突**——共享 init 让两项可控地对齐。

---

## 卡片 8 · DMFT（Dynamical Mean-Field Theory）

**一句话**：从统计物理借来的工具，用路径积分形式描述**有限宽度神经网络在 N → ∞ 极限下的训练动力学**。

**为什么用它**：经典 NTK 假设权重不变化、只在初始化处线性化；DMFT 不做这个假设，可以处理真实的**特征学习**（feature learning）。

**核心数学骨架**：MSRDJ（Martin–Siggia–Rose–De Dominicis–Janssen）路径积分把训练轨迹写成

$$
Z[\eta] = \int \mathcal{D}\phi\, \mathcal{D}\hat\phi\, e^{i\hat\phi(\partial_t \phi - F[\phi]) + \eta\hat\phi}
$$

然后做 saddle-point + 自一致 closure。

**在 MoE 上的应用**：论文给出 3 个 Regime × 2 个参数化（μP, MSSP）= 6 套 DMFT 描述。Regime III × MSSP 的四层条件分布层级是**全文最数学密集的部分**。

---

## 卡片 9 · μP 的 Adam 处方

Adam 不像 SGD 那样可以被 DMFT 干净地处理——optimizer 自身的归一化（除以梯度平方的滑动平均的平方根）破坏了"线性算子"假设。

**μP 框架下的处理**（Yang & Littwin 2023）：
- **学习率**：和 SGD 不同的缩放（如 hidden Adam LR ∝ 1/N，hidden SGD LR ∝ 1）
- **ε 参数**：必须随 layer-wise gradient RMS 一同缩放，否则 ε 在大尺度上要么太大要么太小
- **weight decay**：在 AdamW 里 wd 必须保持 scale-independent，PyTorch 里要用 inverse LR multiplier 补偿

MSSP 沿用了这套处理框架并扩展到 MoE。**严格的 Adam-DMFT 仍是 open problem**。

---

## 卡片 10 · 负载平衡辅助损失（Aux Load Balancing Loss）

```
loss_total = loss_main + 0.01 × loss_aux
loss_aux = M × Σ_i f_i × P_i
  f_i: 每个 expert 实际接收的 token 比例
  P_i: 每个 expert 在 router 平均输出概率
```

**作用**：防止 router 把所有 token 都路由到某几个 expert 导致大部分 expert 失活。

**MSSP 的处理**：作者在所有大尺度实验里都开了 0.01 的 aux loss。论文 Table 1 还给出 "Aux load-balancing loss multiplier : 1"——表示这个系数**不需要随 scale 变化**。

**注意**：DeepSeek-V3 的 *aux-loss-free balancing*（用 bias adjustment 代替 aux loss）**没有**在 MSSP 论文里被验证过——是个 open question。

---

## 卡片 11 · μTransfer 实战流程

μP 的实操价值是这条流水线：

```
1. 在小模型（如 N=128）上做穷举超参扫描
   → 找到 LR、初始化 multiplier 等的最优值
2. 应用 μP 的指数缩放规则
   → 自动推算大模型（如 N=8192）的对应超参
3. 大模型一次跑成功，不需要再扫
```

**经济效益**：一次 70B pretraining 的 LR 扫描可能花费 $1M+；μTransfer 把这个数字降到几乎为 0。

**MSSP 把这套流程扩展到 MoE**。如果你在做 MoE 大模型训练，这是**值得专门写代码支持**的工具。

---

## 卡片 12 · bcdα-Parameterization 框架

通用的"任意层任意优化器"参数化语言：

$$
W_0 \sim \mathcal{N}(0, n^{-2b_W}), \quad W_t = W_{t-1} - \eta\, n^{-c_W} \Psi_t(n^{d_W} g_0, \ldots, n^{d_W} g_t)
$$

- $b_W$：初始化方差的缩放指数
- $c_W$：学习率的缩放指数
- $d_W$：梯度归一化的缩放指数（影响 Adam ε）
- $\alpha_{\text{agg}}$：MoE-specific，跨 M 个专家求和后的归一化指数

**MSSP 的成果**就是：在 MoE 三 Regime 下，对每个权重矩阵（Embedding / Pre-LN / Hidden / Router / Expert Layer 1 / Expert Layer 2 / Final-LN / Unemb）给出对应的 (b, c, d) 三元组——共 8 × 3 ≈ 24 个条目。

---

## 卡片 13 · 同期独立工作：Jiang et al. 2026

论文中提到 **independent and concurrent work** by Jiang et al. (2026):

- 范围：仅 Regime III × signSGD
- 方法：也用 DMFT
- 实验：Transformer MoE 上单轴 LR 迁移

**和 MSSP 论文的关系**：
- 在 **Regime III × Adam** 上 MSSP 处方和他们的 signSGD 处方**一致到 ε scaling 和更大 router init**——独立验证！
- MSSP 覆盖更广：Regime I + II + III、SGD + Adam，并发现 Regime II/III 上 μP 本身失败这一关键负面结果

**对读者的意义**：两篇论文相互验证的部分（Regime III × signSGD-like）可信度极高；MSSP 独有的部分（Regime II × Adam 的 M/N_e init）需要更长时间的社区复现。

---

## 卡片 14 · Marchenko–Pastur 在 Regime III 中的关键作用

**Marchenko–Pastur 定律**：当 $W \in \mathbb{R}^{N \times N_e}$ 是 i.i.d. 高斯且 $N, N_e \to \infty$ 时，$W W^\top / N_e$ 的经验谱密度收敛到 Marchenko–Pastur 分布。

**论文中的应用**：在 Regime III（$N_e \asymp N$）下：

$$
G_i = W^{l,\text{out},i}_0 (W^{l,\text{out},i}_0)^\top \approx c \cdot I_N, \quad c = \Theta(1)
$$

也就是 $G_i$ 在大尺度下**几乎是恒等矩阵的标量倍**。代到 propagating 项里：$G_i u \approx c u$ 对所有 i 都一样——所有专家朝同一方向发力，CLT 抑制不再适用，变成 Θ(1) 的 LLN 项。

**为什么 Regime II 不会有这个**：Regime II 中 $N_e = \Theta(1)$，$G_i$ 的秩是固定常数，是 Haar-分布在 Grassmannian Gr(N_e, N) 上的随机投影——**i.i.d. 的随机方向**，CLT 行为保留。

---

## 卡片 15 · 四层条件分布层级（Regime III × MSSP DMFT 极限）

最终 DMFT 极限的结构（论文 Sec 5）：

```
X_glob (residual-stream 全局过程)
   ↓ 条件依赖
F_sh (共享 expert 隐藏过程, K-依赖)
   ↓ 条件依赖
E | F_sh (expert/router 单点过程)
   ↓ 条件依赖
U | (F_sh, E) (expert 内部隐藏神经元单点过程)
```

四套 kernel 相互嵌入彼此的条件分布，**联立求解**整个动力学。

**对比**：μP 极限只有三层；多出的"shared expert-hidden"层级正是 MSSP **共享初始化**所诱导的 self-averaging 结构。这是 MSSP 极限"在质上不同"的最数学化体现。

**实用意义**：理论家未来研究 MoE 训练时，可以把这套四层结构当作起点；工程师不需要理解每层细节，只需要知道**MSSP 极限是良定义的**就够了。
