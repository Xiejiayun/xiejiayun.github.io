# AlphaEvolve · 关键概念卡片

> 12 张卡片覆盖系统、评估、应用领域、相关算法、批评要点。读完它们，你不需要再读一遍原文也能跟上技术对话。

---

## 卡 1 · AlphaEvolve 一句话定义

AlphaEvolve 是一个由 Gemini 模型驱动的**进化式编程代理**：把 LLM 当作"变异算子"，把自动化评估器（编译/测试/打分）当作"选择压力"，让程序在 database 里世代进化，直到在一个有清晰评估函数的问题上找到比人类基线更优的算法。

**它不是**：新的 Gemini 模型 / 通用 chatbot / 替代 Claude Code 的 IDE 助手。
**它是**：一个把"程序搜索"自动化的进化框架。

---

## 卡 2 · 系统四件套

```
1. Prompt Sampler      — 从历代代码库挑出"母本"程序
2. LLM ensemble        — Gemini Flash（广度） + Gemini Pro（深度）
3. Automated Evaluator — 编译 / 测试 / benchmark / 形式化检查
4. Programs Database   — MAP-Elites 风格的多样性保留库
```

四件套缺一不可：没有评估器就退化成 random code；没有 database 就退化成 single-shot prompting。

---

## 卡 3 · MAP-Elites 是什么

MAP-Elites（Multi-dimensional Archive of Phenotypic Elites）是 evolutionary computation 社区一个经典框架，2015 年由 Mouret & Clune 提出。

核心思想：**不是保留"分数最高的程序"，而是按多个维度（行为特征）切格子，每格保留该格子里最好的那个**。这样 database 里同时存在多种"风格"的最优解，避免过早收敛到局部最优。

AlphaEvolve 把 MAP-Elites 接到 LLM 上，是它"创新点"中最容易被低估的一项。

---

## 卡 4 · 写放大（Write Amplification）

LSM-tree 数据库的核心指标。定义：**实际写入存储的字节数 ÷ 用户原始请求字节数**。

为什么会放大？因为 LSM 用层级 compaction 把无序写整理成有序结构——每个数据可能被反复读写多次。Spanner 这种生产数据库的写放大降低 20%，意味着**全球数据中心存储成本 / SSD 寿命 / 网络带宽**三项同时改善。

AlphaEvolve 通过自动搜索 compaction 启发式实现这一改进。

---

## 卡 5 · AC Optimal Power Flow（AC OPF）

电力工程教科书级问题：在交流电网中，给定发电机组容量、负载需求、线路阻抗，求一个**功率分配方案**使总成本最小、同时满足所有物理约束（电压、电流、相位、热极限）。

这是**非凸优化**——传统数值方法可能找不到任何可行解。GNN 求解的可行率从 14% 提升到 88%，意味着 AI 现在可以**几乎总是**给出可执行方案。对一个每天关乎千万人口供电的问题，这是质变。

---

## 卡 6 · Machine Learned Force Field (MLFF)

分子动力学领域的关键技术。**力场（force field）** 用来描述原子间相互作用的能量曲面。传统方法要么用经验势函数（快但不准），要么用 DFT 量化计算（准但极慢）。

MLFF = 用神经网络拟合 DFT 数据，做出"准且快"的折中。Schrödinger 把 MLFF 训练 / 推理速度都做到 4× 加速 → 直接缩短药物 / 催化剂 / 材料的 R&D 周期。

---

## 卡 7 · Erdős 问题 #1026 一图概览

```
Alice 把 N 枚硬币分进 k 堆        ← 任意分法
       │
       ▼
Bob 选一段 monotone 子序列         ← 单调（递增或递减）
       │
       ▼
Bob 把这些堆的硬币全拿走
       │
       ▼
Bob 能保底拿走多少比例？           ← 求 c_k 的渐近界
```

2025-09 提出，2025-12 完成。**AlphaEvolve 的贡献**：在 k=6 卡壳处，自动搜索出极值构造和反例，提示出紧密上界 $\frac{2k}{k^2+1}$，把"瞎试"的工作量压缩到一个晚上。**Terence Tao 完成了严格证明**。

---

## 卡 8 · 评估函数必须可计算 = 硬约束

AlphaEvolve 适用范围 = $\{$ 评估函数清晰、廉价、抗 reward hacking 的问题 $\}$

**适用**：矩阵乘 / 编译选项 / cache 策略 / 电路布局 / TSP / 数学不等式 / 量子电路误差
**不适用**：业务逻辑（"用户喜欢这个 feature 吗"）/ 产品设计（"这个按钮该放哪"）/ 团队沟通

这条约束决定了它**不会**替代 90% 的应用开发，但会重塑那 10% 极度高杠杆的算法工种。

---

## 卡 9 · 双模型分工（Flash + Pro）

```
Gemini Flash  → 广度：8-10× 吞吐量生成大量小幅 mutation
Gemini Pro    → 深度：长链推理、找 bug、补盲点

合在一起 = 探索 / 利用的角色分工（不是 ensemble 投票）
```

这套架构和 [Needle](https://github.com/cactus-compute/needle) 那种"大模型规划 + 小模型工具"是平行思想——AI 系统正在自然长出两层结构。

---

## 卡 10 · 反对意见 · "RSI ≠ AI 设计 AI"

HN 评论员 HarHarVeryFunny 的精要区分：

> "AI improving itself" 和 "AI optimizing software that happens to be used for AI training" 不是一回事。

AlphaEvolve 优化的是**运行 AI 的基础设施**（TPU、kernel、训练 pipeline），不是模型架构本身。是不是"递归自我提升"？取决于你怎么定义。但绝对**不**等于科幻意义上的"AI 设计下一代 AI"。

---

## 卡 11 · 反对意见 · "评估函数本身就是问题"

Yossi Kreinin 的论点（[All means are fair except solving the problem](https://yosefk.com/blog/all-means-are-fair-except-solving-the-problem.html)）：

> 很多产业层面的"问题"之所以无法被算法化，是因为它们根本不是优化问题，而是组织协调问题——评估函数不存在或被各方故意模糊化。

AlphaEvolve 的存在反而会**放大**"能 / 不能被量化"的分野：能量化的部分被自动化，无法量化的部分留给人类——但这部分恰好是最痛苦的部分。

---

## 卡 12 · 工程师的三条职业建议

1. **不要再以"我会调 LSM compaction 参数"为核心技能**——这一层正在被 AlphaEvolve 自动化。
2. **把"评估函数设计"练成核心技能**——把模糊业务目标翻译成 evolutionary loop 能跑的清晰打分函数，是新的高杠杆工作。
3. **关注基础设施复利**——AlphaEvolve 这种系统的成果会沉淀回基础设施层（TPU / Spanner / cache），先发者每年都会拉开 10-30% 成本差距。

---

> 这些卡片可以作为 AlphaEvolve 相关讨论的"快速参考"。也欢迎在评论里指出错漏。
