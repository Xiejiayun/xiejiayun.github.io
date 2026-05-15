# AlphaEvolve · 英中对照术语表

> 35 条术语，按字母顺序排列。覆盖系统术语、评估指标、相关算法、应用领域。

| 英文 | 中文 | 一句话解释 |
|------|------|------------|
| AC Optimal Power Flow (AC OPF) | 交流最优潮流 | 电力系统中给定负载求功率分配方案的非凸优化问题 |
| AlphaEvolve | AlphaEvolve | DeepMind 的进化式编程代理，用 Gemini 做变异、用自动评估器做选择 |
| Automated Evaluator | 自动评估器 | 编译、运行、打分一段候选程序的子系统；定义了"什么算更好" |
| Cache Replacement Policy | 缓存替换策略 | 缓存满了之后决定换出哪个条目的算法（LRU、LFU、CLOCK 等） |
| Constructive Lower Bound | 构造性下界 | 通过给出具体构造来证明某下界的方法（与存在性证明对照） |
| DeepConsensus | DeepConsensus | Google 用于 PacBio 长读基因测序错误纠正的深度学习模型 |
| Distillation | 蒸馏 | 用大模型作为教师，把知识压缩到小模型；Needle 即为此类技术 |
| Erdős Problem #1026 | 厄尔多斯第 1026 号问题 | 关于硬币分堆 / 单调子序列拿币比例的组合数学问题 |
| Evolutionary Programming | 进化式编程 | 通过 mutation + selection 让程序逐代演化的范式 |
| FLOPS Investment | 算力投入 | 训练或运行模型耗费的浮点运算量；AlphaEvolve 完整 cost 未公开 |
| Force Field (in molecular dynamics) | 力场（分子动力学） | 描述原子间相互作用的能量函数；MLFF 用神经网络拟合 |
| Gemini Flash | Gemini Flash | Google 的小型 Gemini 模型，主打吞吐量和延迟 |
| Gemini Pro | Gemini Pro | Google 的旗舰 Gemini 模型，主打深度推理 |
| GNN (Graph Neural Network) | 图神经网络 | 处理图结构数据的神经网络；AlphaEvolve 用它解 AC OPF |
| Heuristic | 启发式 | 不保证最优但通常 work 的经验规则；常用于 NP-hard 问题 |
| Klarna | Klarna | 瑞典金融科技公司，AlphaEvolve 把它的训练流水线提速 2× |
| LSM Tree | LSM 树 | Log-Structured Merge Tree，现代数据库存储引擎主流结构 |
| MAP-Elites | MAP-Elites | 一种多维档案进化算法，按行为特征切格保留多样性 |
| MIE (Memory Integrity Enforcement) | 内存完整性强制 | Apple 在 M5 上引入的内存安全防线；与本文无关，但博客其它好文中提到 |
| MLFF (Machine Learned Force Field) | 机器学习力场 | 用神经网络近似 DFT 力场的方法，加速分子动力学 |
| NP-hard | NP 难 | 复杂度类，目前没有已知多项式时间算法的问题集合 |
| Prompt Sampler | 提示采样器 | 从程序数据库中挑出"母本"程序传给 LLM 的子系统 |
| Programs Database | 程序数据库 | 进化算法世代的产物存档；AlphaEvolve 用 MAP-Elites 组织 |
| Ramsey Number | Ramsey 数 | 组合数学中关于图染色的不可避免子结构问题；AlphaEvolve 改进了下界 |
| Recursive Self-Improvement (RSI) | 递归自我提升 | 一种 AGI 理论假设：AI 通过改进自己的设计加速进化 |
| Reward Hacking | 奖励黑客 | 模型学会优化"评估函数"而非"真实目标"的失败模式 |
| Schrödinger | Schrödinger | 美国药物发现 / 材料计算公司，使用 AlphaEvolve 优化 MLFF 推理 |
| Spanner | Spanner | Google 的全球分布式数据库；写放大被 AlphaEvolve 降低 20% |
| Strassen's Algorithm | Strassen 算法 | 1969 年提出的 7 次乘法 2×2 矩阵乘法；AlphaEvolve 在 4×4 复矩阵上首次找到 48 步解 |
| Tammes Problem | Tammes 问题 | 在单位球面上放置 N 个点使最小成对距离最大化 |
| Thomson Problem | Thomson 问题 | 在单位球面上放置 N 个等电荷使总势能最小化 |
| TPU (Tensor Processing Unit) | TPU | Google 自研的 AI 专用芯片；下一代 TPU 部分电路由 AlphaEvolve 设计 |
| TSP (Traveling Salesman Problem) | 旅行商问题 | 经典 NP-hard 组合优化；FM Logistics 用 AlphaEvolve 改进 10.4% |
| Willow | Willow | Google 量子计算芯片；AlphaEvolve 把其量子电路误差降低 10× |
| Write Amplification | 写放大 | LSM 数据库实际写入字节 / 用户原始字节比值；越低越好 |
| Young's Convolution Inequality | Young 卷积不等式 | 调和分析中的经典不等式；AlphaEvolve 改进了某些常数的下界 |

---

> 编辑注：如果你看到 "AlphaEvolve 解决了 XXX"，先问"它的评估函数是什么？怎么自动算出来的？"——99% 的炒作文章会答不上来。
