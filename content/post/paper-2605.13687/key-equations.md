# 关键公式解读 · arXiv 2605.13687

> 公式渲染依赖 KaTeX。每条公式后面附一段"读起来像什么"的人话注解。

---

## 公式 1 · 广播过程的转移核（Ising 特例）

$$
\kappa(\sigma, \sigma') = 
\begin{cases}
\frac{1+\rho}{2} & \sigma = \sigma' \\[4pt]
\frac{1-\rho}{2} & \sigma \neq \sigma'
\end{cases}
$$

**怎么读**：父亲是 $\sigma$ 的条件下，孩子有 $\frac{1+\rho}{2}$ 概率"复制"，$\frac{1-\rho}{2}$ 概率"翻转"。$\rho = 1$ 时是完美复制，$\rho = 0$ 时是公平硬币。

**为什么重要**：这是 Ising 模型在 Bethe lattice 上的标准定义，所有后续定理都靠它推。

---

## 公式 2 · 广播过程的转移核（Coloring 特例）

$$
\kappa(\sigma, \sigma') = 
\begin{cases}
0 & \sigma = \sigma' \\[4pt]
\frac{1}{q-1} & \sigma \neq \sigma'
\end{cases}
$$

**怎么读**：孩子的颜色必须**与父亲不同**，在剩下 $q-1$ 种颜色里均匀抽。

**为什么重要**：这是硬约束语言的代表——任何相邻 token 都受限于"局部规则"，整棵树合法着色的存在性变成一个 CSP 问题。

---

## 公式 3 · Kesten-Stigum 阈值

$$
d\rho^2 > 1
$$

**怎么读**：分支因子 $d$ 与相关 $\rho^2$ 乘积大于 1 时，根信号能"挤过"层层独立噪声传到叶。直观理解：每往下一层信号衰减 $\rho^2$，但分支扩张 $d$ 倍，扩张快于衰减就保留信号。

**为什么重要**：论文所有 Ising 下界（Thm 3.1/3.2）默认在 KS 阈值之上。下方根本不需要长 ctx 也能"学"，因为根信息本来就传不到叶。

---

## 公式 4 · Theorem 3.1（Ising 方差缩放律）

$$
\log\left(\frac{1}{n}\operatorname{Var}(S_X)\right) \;=\; w \log(d\rho^2) + o(1),
\quad \text{as } h - w \to \infty, \; w \to \infty.
$$

其中 $S_X = \sum_{r \in \text{leaves}} X_r$。

**怎么读**：把"叶节点和的归一化方差"取 log，对"上下文深度 $w$"画 log-log 图，**得到一条斜率为 $\log(d\rho^2)$ 的直线**。

**为什么重要**：这是论文最美的一行——它**从生成模型推出 scaling law 的斜率**，而不是事后拟合经验数据。对 $d=3, \rho=0.9$ 的实验配置，斜率 $\log(2.43) \approx 0.886$，论文里的图实测正好对上。

---

## 公式 5 · Theorem 3.2（Ising 峰度 → 高斯）

$$
\frac{S_X - \mathbb{E}[S_X]}{\sqrt{\operatorname{Var}(S_X)}} \;\xrightarrow{d}\; \mathcal{N}(0, 1).
$$

**怎么读**：ctx=w 的非推理模型生成的叶和，标准化后**收敛到标准高斯**。

**为什么重要**：真实语言（完整广播过程）的 $S_X$ 是**非高斯**的——它带着根 token 的全局偏好。所以 bounded-context 模型本质上"丢失了根的信号"，把分布**强制高斯化**。在 LLM 工程语境里：上下文不够时，模型生成的文本会"丧失主题倾向"，向一个均匀化的均值漂去。

---

## 公式 6 · Theorem 3.3（Coloring 全局违法）

$$
\Pr_{X \sim \mathcal{M}_{ctx=w}}\Bigl[\,X \text{ 是某棵合法 q-着色 } T_{d,h} \text{ 的叶序列}\,\Bigr] \;\to\; 0
\quad \text{as } h \to \infty
$$

（在 freezing regime 下，对任何 bounded-context 模型 $\mathcal{M}$）

**怎么读**：在 freezing regime 下，**没有**任何 ctx 有界的自回归模型能持续生成"对应于真实树上合法着色"的叶序列——合法率趋于 0。

**为什么重要**：这是比"统计偏差"更尖锐的失效模式。等价于"代码每一段都过 type-check，整体 link 不起来"。是 long-horizon coding agent 故障模式的形式化版。

---

## 公式 7 · Theorem 3.4（O(log n) 推理上界）

存在一个推理模型 $\mathcal{M}^{\text{reason}}_{w}$，配有
$$
O(h \log d) \;=\; O(\log n) \quad \text{比特工作记忆,}
$$
使得
$$
\mathcal{L}\bigl(\mathcal{M}^{\text{reason}}_{w}\bigr) \;=\; \mathcal{L}\bigl(\text{真实 }(d,h,\kappa,\nu)\text{-语言}\bigr)
$$
（精确等于真实语言的分布）。

**怎么读**：只要给模型一段 $O(\log n)$ 比特的"笔记本"用来读写当前 DFS 路径上祖先节点的状态，它就能**精确**采样真实语言——而不是只逼近。

**为什么重要**：和 Thm 3.1/3.3 的下界（$\Omega(n)$ ctx）结合起来得到**指数分离**：上下文需要 $\Omega(n)$，但推理工作记忆只需 $O(\log n)$。

构造性证明：本质上是把 belief propagation 写在推理轨迹里。

---

## 公式 8 · 自回归广播过程（Definition 2.2）

给定参数 $(d, h, \kappa)$ 和上下文深度 $w \le h$，自回归广播过程 $X_L \in \Sigma^{d^h}$ 按以下方式生成：

1. 从真实 $(d, h, \kappa)$ 广播过程在任意大小 $d^w$ 子树上的边缘分布采样 $Y_1$；
2. 对 $r = 2, \dots, d^{h-w}$，先从 $\{1, \dots, h-w\}$ 上的"相邻子树最低公共祖先高度分布"采样 $h_r$，然后在条件 "$Y_{r-1}$ 已知 且 LCA 高度为 $h_r$" 下从真实广播过程采样 $Y_r$；
3. 输出 $X_L = (Y_1, Y_2, \dots, Y_{d^{h-w}})$。

**怎么读**：这是论文用来近似"ctx=$d^w$ 的 Transformer"的**理论代理对象**。它一次生成一棵深度 $w$ 的子树，且只看前一棵子树和它们的 LCA 高度的边缘。

**为什么重要**：直接分析"Transformer 输出分布"做不到；分析"自回归广播过程"做得到。论文用实验证明：用 SGD 训出来的 ctx=$d^w$ Transformer 在合成语言上**定量等价于**这个理论代理。

---

## 公式总结表

| 公式 | 内容 | 角色 |
|---|---|---|
| (1) | Ising 转移核 | 定义软全局相关性 |
| (2) | Coloring 转移核 | 定义硬全局约束 |
| (3) | KS 阈值 $d\rho^2 > 1$ | 信号传播条件 |
| (4) | 方差 log-线性，斜率 $\log(d\rho^2)$ | **第一份理论 scaling law 斜率** |
| (5) | 峰度 → 3（高斯） | bounded ctx 的统计退化 |
| (6) | Coloring 合法率 → 0 | "局部合法、全局违法"失效 |
| (7) | $O(\log n)$ 推理记忆 → 精确采样 | **指数级 CoT 价值上界** |
| (8) | 自回归广播过程 | 整套理论的可解析代理 |

---

**记忆诀**：所有结果都围绕一条对比线——

$$\boxed{\;\;\text{非推理：ctx } = \Omega(n) \quad \longleftrightarrow \quad \text{推理：memory } = \Theta(\log n)\;\;}$$
