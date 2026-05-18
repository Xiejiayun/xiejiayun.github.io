# 术语表 · arXiv 2605.13687（中英对照）

> 48 条术语，按主题排序。

## 一、生成模型与语言定义

| 英文 | 中文 | 解释 |
|---|---|---|
| Broadcast Process | 广播过程 | 在树上从根向叶逐层采样 token 的概率过程 |
| d-ary Tree $T_{d,h}$ | d-叉树 | 分支因子为 d、高度为 h 的完全树 |
| Branching Factor | 分支因子 | 每个内部节点的子节点数 d |
| Height | 高度 | 树的深度 h，叶节点数 $n = d^h$ |
| Leaf Sequence | 叶节点序列 | 按 DFS 排列的 $d^h$ 个叶 token，即"语言" |
| Broadcast Channel $\kappa$ | 广播信道 | 父 → 子的转移核 |
| Prior $\nu$ | 先验 | 根节点的分布 |
| Internal Nodes | 内部节点 | 不可观测的潜在结构（句法 / 主题） |
| Ising Process | 伊辛过程 | $\Sigma=\{\pm 1\}$、$\rho$-相关复制的广播 |
| Coloring Process | 着色过程 | $\Sigma=[q]$、"孩子不能与父亲同色"的广播 |
| Correlation $\rho$ | 相关系数 | Ising 里 child 复制 parent 的概率 |
| q-Coloring | q-着色 | 用 q 种颜色给树染色使相邻不同色 |
| Valid Coloring | 合法着色 | 满足"父子异色"约束的着色方案 |
| Valid Rate | 合法率 | 生成序列对应某棵 d-叉树合法 q-着色的概率 |

## 二、阈值与相

| 英文 | 中文 | 解释 |
|---|---|---|
| Kesten-Stigum Threshold | KS 阈值 | $d\rho^2 > 1$：根信号能传到叶的临界条件 |
| Reconstruction Phase | 重建相 | KS 阈值之上、根信号可恢复的相 |
| Freezing Regime | 冻结相 | CSP 里合法解互相孤立、变得稀疏的相 |
| Phase Transition | 相变 | 当参数越过阈值时系统行为发生质变 |
| Subcritical / Supercritical | 亚临界 / 超临界 | KS 阈值上下两侧的两个相 |

## 三、核心理论工具

| 英文 | 中文 | 解释 |
|---|---|---|
| k-gram Model | k-gram 模型 | 只依赖前 k 个 token 的条件分布模型 |
| k-gram Ansatz | k-gram 拟设 | 用最优 k-gram 代替 ctx=k Transformer 做理论分析 |
| Belief Propagation (BP) | 信念传播 | 在树/图上计算边缘分布的精确算法 |
| Optimal Autoregressive Process | 最优自回归过程 | 给定 ctx 长度下的理论最优 NTP 分布 |
| Conditional Distribution | 条件分布 | $p(\cdot \mid \text{context})$ |
| Marginal Distribution | 边缘分布 | 子树或叶集合的分布投影 |
| Markovian Process | 马尔可夫过程 | 状态只依赖前一个状态的随机过程 |

## 四、统计指标

| 英文 | 中文 | 解释 |
|---|---|---|
| Variance | 方差 | 随机变量与均值差的平方期望 |
| Excess Kurtosis | 超额峰度 | 分布"重尾"程度，标准高斯为 0 |
| Gaussian | 高斯 | 正态分布 |
| Central Limit Theorem (CLT) | 中心极限定理 | 大量独立和趋于高斯 |
| Asymptotic | 渐近的 | 极限意义下成立的陈述 |
| Log-linear Scaling | 对数线性缩放 | log y = a · x + b |
| Slope | 斜率 | log-log 缩放曲线的指数 |

## 五、推理与 CoT

| 英文 | 中文 | 解释 |
|---|---|---|
| Chain of Thought (CoT) | 思维链 | 模型在生成最终答案前先输出中间步骤 |
| Reasoning Trace | 推理轨迹 | 显式的中间推理 token 序列 |
| Reasoning Model | 推理模型 | 训练时被允许写入/读取额外推理 token 的模型 |
| Working Memory | 工作记忆 | 推理过程中可读写的状态空间，论文里是 $O(h \log d)$ 比特 |
| Oracle Trace | 神谕轨迹 | 由真实 belief 状态生成的"完美"推理轨迹 |
| Test-Time Compute | 测试时计算 | 推理时投入更多 token / 搜索来换取性能 |
| RLVR | 可验证奖励强化学习 | DeepSeek-R1 / SU-01 系列的训练范式 |

## 六、计算复杂性与表达力

| 英文 | 中文 | 解释 |
|---|---|---|
| TC⁰ | TC⁰ 复杂度类 | 常深度阈值电路类，log-精度 Transformer 落在这里 |
| Turing Completeness | 图灵完备 | 能模拟通用图灵机 |
| Worst-case Complexity | 最坏情况复杂性 | 最坏输入下的代价 |
| Statistical Complexity | 统计复杂性 | 学习样本/分布偏差意义下的代价 |
| Existential Result | 存在性结果 | 证明"存在某种模型/算法"满足条件 |
| Quantitative Result | 定量结果 | 给出具体常数/斜率/速率 |
| Sparse Parities | 稀疏奇偶问题 | 学习理论里的经典硬问题（Blum-Kalai-Wasserman） |

## 七、训练与实验

| 英文 | 中文 | 解释 |
|---|---|---|
| Next-Token Prediction (NTP) | 下个 token 预测 | 自回归 LM 的标准训练目标 |
| Hierarchical Punctuation | 层级标点 | 实验里按子树深度插入的特殊标记 token |
| nanochat | nanochat | Karpathy 2025 的极简 Transformer 训练框架 |
| Context Window | 上下文窗口 | Transformer 一次能看到的 token 数 |
| Autoregressive Sampling | 自回归采样 | 一次生成一个 token 并喂回输入的推理方式 |

