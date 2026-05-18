# 概念卡片：RoPE 长上下文失败模式

> 15 张卡片，每张正反面：**正面** = 你听到这个词应该立刻浮现的画面；**背面** = 一句话讲透的工程含义。

---

## 🎴 卡片 01：RoPE Product

**正面**：query 和 key 经过 RoPE 旋转之后的内积 $S(m) = \sum_{n=0}^{h-1} a_n \cos(m\theta_n + \varphi_n)$。

**背面**：现代 LLM attention 分子的"原始版本"。本文最关键的观察是——把它当作**正态随机变量**来分析，整个长上下文失败链就被打开了。

---

## 🎴 卡片 02：Rotary Positional Embedding (RoPE)

**正面**：Su 等 2021 提的位置编码。把 $d$ 维向量切成 $h = d/2$ 对二维子向量，第 $n$ 对在位置 $m$ 处旋转角度 $m\theta_n$。

**背面**：现代 LLM 的"事实标准"位置编码。Llama / Qwen / DeepSeek / Kimi / gpt-oss 全部用它。本文证明它有**内禀缺陷**。

---

## 🎴 卡片 03：RoPE Base $B$

**正面**：基础频率，决定 $\theta_n = B^{-n/h}$。原版用 $B = 10{,}000$；Llama-3 用 $5\times 10^5$；长上下文模型常用 $10^6 \sim 10^8$。

**背面**：长上下文 LLM 工程上调得最猛的旋钮——但本文证明它是**两头不能赢**的 trade-off：$B \uparrow$ 保 token 区分，但丢 position 区分。

---

## 🎴 卡片 04：Locality Bias（近邻偏好）

**正面**：attention 分数应该随距离 $m$ 增加而单调下降——近的 token 被给更多权重。

**背面**：RoPE 之所以好用的"天然 inductive bias"。本文证明：**长上下文里这个 bias 失效**，attention 在远处和近处给的分数变成随机的。

---

## 🎴 卡片 05：Central Limit Theorem (CLT)

**正面**：独立同分布随机变量之和趋近正态分布。

**背面**：本文的"魔术钥匙"——把 $h$ 个独立的 cos 项相加，按 CLT 看成正态分布，整个 long-context 分析就变成了**高斯随机变量比较**问题。

---

## 🎴 卡片 06：Position Inversion（位置反转）

**正面**：同一个 key，移到更远的位置，attention 分数**变高**了。

**背面**：locality bias 的反向破裂。本文 **Theorem 1** 证明：随 $M$ 上升，反转概率趋近 0.5——和投硬币一样。Llama 3.1-8B 实测：在 50K-128K 距离上反转概率接近 0.5。

---

## 🎴 卡片 07：Position Aliasing（位置混叠）

**正面**：存在两个不同距离 $m_1 \neq m_2$ 让 $S(m_1) = S(m_2)$ 完全相同。

**背面**：硬故障。本文 **Theorem 2** 证明：存在 alias pair 的概率指数趋近 1；BF16 + 8K 上下文实测有 **77,505** 对 aliasing 位置。

---

## 🎴 卡片 08：Attention Invariance（注意力不变性）

**正面**：把两个不同 key 互换位置（在 aliasing 距离上），attention 输出**完全不变**。

**背面**：Position Aliasing 的语义后果。"Alice 养猫" 和 "Alice 养狗" 在某些位置组合下对 attention 完全等价。8K 上下文里 1,491 个这种例子。

---

## 🎴 卡片 09：Token Inversion（token 反转）

**正面**：$S_1(0) > S_2(0)$ 但 $S_1(m) < S_2(m)$——零距离上排序对，移到距离 $m$ 反过来了。

**背面**：本文 **Theorem 3**：随 $M$ 上升趋近 0.5；随 $B$ 上升下降。Llama 3.1-8B 实测：`cat` vs `number` 对 `pet` 的相对排序在前 10 个 token 内就翻转。

---

## 🎴 卡片 10：Token Aliasing（token 混叠）

**正面**：$S_1(m) = S_2(m)$——不同 key 在同一位置上 attention 分数完全相同。

**背面**：本文 **Theorem 4**：aliasing 位置数被 $\Theta(2^{-f}\sqrt{h}\,M)$ 上界。BF16 + $h = 64$：最多 5% 位置 alias。

---

## 🎴 卡片 11：Indexing Task（索引任务）

**正面**：给一个整数 list `arr = [0,1,2,3,...]`，问 `arr[k]`。

**背面**：本文设计的"残忍诊断"。它绕开 NIAH 的 token-identity 优化，**纯测 position 识别能力**。结果：6 个 frontier LLM **全部** 在 4K-8K 内掉到随机猜。

---

## 🎴 卡片 12：Needle in a Haystack (NIAH)

**正面**：在长上下文里藏一句话，让模型找出来。

**背面**：现代 long-context 模型的"训练目标偏置"——它们被疯狂优化在 NIAH 上 perfect，代价是 position 能力被掏空（本文的核心 indictment 之一）。

---

## 🎴 卡片 13：低频项 vs. 高频项

**正面**：RoPE product 里 $n \ll h \log_B M$ 是高频（振荡），$n \gg h \log_B M$ 是低频（缓慢衰减）。

**背面**：本文最干净的分解：**低频项决定均值**（locality bias 的来源），**高频项决定方差**（位置 / token 区分能力的来源）。$M$ 增大让低频项失效，高频项的方差淹没差距，所有失败模式由此产生。

---

## 🎴 卡片 14：BF16 精度的助攻

**正面**：Brain Float 16，7 位显式 fraction。

**背面**：Position / Token Aliasing 的"放大器"。BF16 的解析率给定了 RoPE product 的"网格大小"——网格越粗，aliasing 越频繁。但即使 FP32 也不能消除，只能缓解。

---

## 🎴 卡片 15：NoPE / 替代位置机制

**正面**：完全不用位置编码，只靠 causal mask 隐式编码顺序（Gelberg 2025 等）。

**背面**：本文给"放弃 RoPE 派" 的最大理论靠山。如果 RoPE 在长上下文里物理上不可救，那 NoPE / ALiBi / 学习式相对位置 / SSM 阵营（Mamba 类）就有了正当性。

---

> 📌 **学习建议**：从 #1, #2, #5 开始建立"RoPE product 是正态分布"的直觉；然后 #6, #7, #9, #10 是四条定理的对应失败模式；最后 #11, #12 把它和工程实测对接，#15 看未来。
