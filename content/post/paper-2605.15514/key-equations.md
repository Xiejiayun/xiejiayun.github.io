# 关键公式解读：RoPE 长上下文失败模式

> 5 组公式 + 推导思路，把论文的数学骨架拆开给你看。

---

## 公式 1：RoPE Product 的定义

$$
S_{q,k}(m) \;=\; \sum_{n=0}^{h-1} a_n \cos(m\theta_n + \varphi_n)
$$

**符号表**：
- $q, k \in \mathbb{R}^d$：query 和 key 向量，$d$ 是 attention head 维度
- $h = d/2$：把 $d$ 维切成 $h$ 对二维子向量
- $\theta_n = B^{-n/h}$：第 $n$ 对子向量的角频率，$B$ 是 RoPE base（通常 $10^4 \sim 10^8$）
- $a_n > 0$：第 $n$ 对子向量的振幅 = $\lVert q_{2n:2n+2}\rVert \cdot \lVert k_{2n:2n+2}\rVert$
- $\varphi_n \in [0, 2\pi)$：第 $n$ 对子向量的夹角
- $m$：query 与 key 的相对距离

**怎么得到的**：RoPE 把 $q$ 和 $k$ 切成 $h$ 对二维子向量，每一对在位置 $m$ 处旋转角度 $m\theta_n$。两个旋转后的二维向量做内积，等于"原始夹角"减去"位置差对应的旋转角"——所以是 $\cos(m\theta_n + \varphi_n)$ 而不是 $\cos(\varphi_n)$。把所有维度对加起来就是 $S_{q,k}(m)$。

**物理直觉**：
- $\theta_n$ 在 $n = 0$ 处最大（$= 1$），$n = h-1$ 处最小（$\approx B^{-1}$）；
- **高频项**（$n$ 小）：在小 $m$ 内就完成多次振荡 → 区分相邻位置；
- **低频项**（$n$ 大）：在长 $m$ 内只转很小角度 → 随距离单调衰减 → locality bias 的来源。

---

## 公式 2：CLT 把 RoPE Product 当作正态随机变量

$$
\tilde{S} \;=\; S_{q,k}(m) \;\xrightarrow{d}\; \mathcal{N}\!\big(\mu_M(q,k),\; \sigma_M^2(q,k)\big), \quad m \in [A, M)
$$

**关键直觉**：
- 当距离 $m$ 在足够大的区间 $[A, M)$ 上均匀采样时，每个 $\cos(m\theta_n + \varphi_n)$ 项可以**视作独立**的近零均值随机变量（高频项在区间上几乎填满 $[-1, 1]$）；
- 应用 CLT，$h$ 个独立项的和近似为高斯。

**均值与方差的分配**：
$$
\mu_M(q,k) \;\approx\; \underbrace{\sum_{n: \theta_n \cdot M < 2\pi} a_n \cos(\varphi_n + \tfrac{M}{2}\theta_n)}_{\text{低频项主导}}
$$

$$
\sigma_M^2(q,k) \;\approx\; \tfrac{1}{2}\!\!\!\!\!\sum_{n: \theta_n \cdot M \geq 2\pi}\!\!\!\!\! a_n^2 \quad \text{（高频项主导）}
$$

**频率阈值** $\lambda(M) = \Theta(h \log_B M)$：把 $\{0, 1, \ldots, h-1\}$ 切成低频段 $n > \lambda(M)$（贡献 $\mu$）和高频段 $n < \lambda(M)$（贡献 $\sigma^2$）。$M$ 越大，$\lambda(M)$ 越大，高频段越多——所以**方差随 $M$ 上升**；同时低频段越少——所以**均值的衰减效应被削弱**。

> 💡 这是论文最核心的一行公式：**$M \uparrow$ 时 $\mu \to 0$, $\sigma^2 \uparrow$**——这就是所有失败模式的根。

---

## 公式 3：Theorem 1（Position Inversion 概率）

设 $m_1 \sim U[0, M/2)$，$m_2 \sim U[M/2, M)$，则 Position Inversion 的概率（即 $S(m_1) < S(m_2)$ 的概率）下界为：

$$
\Pr_{\text{PI}}(M, B) \;\geq\; \Phi\!\left( -\frac{\mu_{[0, M/2)} - \mu_{[M/2, M)}}{\sqrt{\sigma_{[0,M/2)}^2 + \sigma_{[M/2,M)}^2}} \right)
$$

其中 $\Phi$ 是标准正态 CDF。

**取极限**：
$$
\lim_{\frac{\log M}{\log B} \to \infty} \Pr_{\text{PI}}(M, B) \;=\; \frac{1}{2}
$$

**推导直觉**：两个正态变量之差还是正态。它们的均值差由 low-freq 衰减给出，方差和由 high-freq 给出。$M \to \infty$（在 $B$ 固定时）让 high-freq 维度数爆涨，$\sigma$ 把 $\mu$ 差完全淹没——比大小就退化成无偏的硬币抛掷。

**工程含义**：
- $M$ 越大，$\Pr_{\text{PI}} \to 0.5$；
- 现代 Llama-3 base $B = 5 \times 10^5$、Llama 实测：$M = 600 \Rightarrow \Pr_{\text{PI}} > 0.3$，$M = 4{,}600 \Rightarrow \Pr_{\text{PI}} > 0.4$。**也就是 4K 上下文内已经substantially broken**。

---

## 公式 4：Theorem 2（Position Aliasing 总数）

随机选择距离 $m_1$，存在 alias $m_2$ 满足 $S(m_1) = S(m_2)$（在精度 $\varepsilon$ 下）的概率：

$$
\Pr_{\text{PA}}(M) \;\geq\; 1 - \left(1 - \frac{2\varepsilon}{\sigma_M(q, k)\sqrt{2\pi}}\right)^{M-1}
$$

**取极限**：$M \to \infty \Rightarrow \Pr_{\text{PA}} \to 1$（指数级）。

**Aliasing pair 总数的期望**：
$$
\mathbb{E}[|\{(m_1, m_2) : S(m_1) = S(m_2)\}|] \;\sim\; \binom{M}{2} \cdot \frac{2\varepsilon}{\sigma_M\sqrt{2\pi}}
$$

$\varepsilon$ 是 RoPE product 数值类型的解析率（BF16 在 $|S| \approx 10$ 量级下约为 $2^{-7} \cdot 10 \approx 0.08$）。代入 $M = 8{,}000$、$\sigma_M \approx 5$：
$$
\mathbb{E}[\text{aliasing pairs}] \;\approx\; \frac{8000 \cdot 7999}{2} \cdot \frac{0.16}{5\sqrt{2\pi}} \;\approx\; 3.2 \times 10^5
$$

这个数量级和实测的 75K-77K 在同一对数级——理论与实证吻合。

---

## 公式 5：Theorem 3 + 4（Token-side 的两条对称定理）

### Theorem 3：Token Inversion 概率

设两个 key $k_1, k_2$，定义 $S_1(m) = S_{q, k_1}(m)$，$S_2(m) = S_{q, k_2}(m)$。假设零距离上 $S_1(0) > S_2(0)$。在距离 $m \sim U[0, M)$ 上：

$$
\Pr_{\text{TI}}(M, B) \;\geq\; \Phi\!\left( -\frac{S_1(0) - S_2(0)}{\sqrt{\mathrm{Var}(S_1(m) - S_2(m))}} \right)
$$

差值 $D(m) := S_1(m) - S_2(m)$ 也是正态，方差由 high-freq 项贡献：

$$
\mathrm{Var}(D) \;\approx\; \tfrac{1}{2}\!\!\!\!\!\sum_{n: \theta_n M \geq 2\pi}\!\!\!\!\! (a_{1,n}^2 + a_{2,n}^2)
$$

当 $M \to \Theta(B)$ 时，$\mathrm{Var}(D) \to \infty$，$\Pr_{\text{TI}} \to 1/2$。

**注意**：和 Theorem 1 不同，这里 $B \uparrow$ 让 high-freq 范围变窄（$n$ 中能满足 $\theta_n M \geq 2\pi$ 的项变少），所以 $\mathrm{Var}(D) \downarrow$，$\Pr_{\text{TI}} \downarrow$ —— **$B \uparrow$ 反而能压住 token inversion**。这就是 §1 里说的 "RoPE base 是 trade-off 旋钮" 的精确数学体现。

### Theorem 4：Token Aliasing 数量

Token aliasing 位置（即满足 $S_1(m) = S_2(m)$ 的距离 $m$）的总数有显式上界：

$$
|\{m \in [0, M) : S_1(m) = S_2(m)\}| \;\leq\; \Theta\!\big(2^{-f} \sqrt{h}\, M\big)
$$

其中 $f$ 是浮点数据类型的显式 fraction 位数（BF16: $f = 7$，FP16: $f = 10$，FP32: $f = 23$），$h$ 是 half hidden dim。

**代入工程数字**：$h = 64$、BF16、$M = 32{,}000$：
$$
\text{token aliasing positions} \;\leq\; 2^{-7} \cdot 8 \cdot 32{,}000 \;\approx\; 2{,}000
$$
即 **6% 左右的位置**会出现 token aliasing。论文实测和这个上界吻合。

---

## 公式 6：四模式的总规律表

| 失败模式 | 关键公式 | $M\uparrow$ | $B\uparrow$ |
|---|---|:---:|:---:|
| Position Inversion | $\Pr \to 1/2$ 当 $\frac{\log M}{\log B} \to \infty$ | ↑ | ↑（变糟）|
| Position Aliasing | $\Pr \to 1$，pair 数 $\sim M^2 \varepsilon / \sigma$ | ↑ | ↑（变糟）|
| Token Inversion | $\Pr \to 1/2$ 当 $M \to \Theta(B)$ | ↑ | ↓（变好）|
| Token Aliasing | 位置数 $\leq \Theta(2^{-f}\sqrt{h}\,M)$ | ↑ | ↓（变好）|

> 🔑 **核心观察**：$B$ 在 position-side 和 token-side 上的影响**完全相反**。这意味着不存在一个能同时优化所有失败模式的 $B$ 值——你必须**选择牺牲哪一边**。Llama-3 / Qwen / DeepSeek 等选了 "$B \uparrow$ 来支持长 context"，于是 position 区分能力被牺牲了，这就是 indexing task 全部塌方的根因。

---

## 数学上还能补的细节

1. **Berry-Esseen 误差**：CLT 在 $h = 64$ 时的有限样本偏差是 $O(1/\sqrt{h}) = O(0.125)$。论文用 Llama 3.1-8B 实测确认正态近似的拟合质量（Fig 2c），但严格的 BE 上界没在正文给。

2. **振幅一致性假设**：所有定理都假设 $\{a_n\}$ 大致均匀。实际 attention head 里常有 1-2 个 $a_n$ 量级远大于其余，这会让"有效 $h$" 变小，进而让 CLT 不那么准。论文 Limitations 一节诚实地承认了这点。

3. **多头多层的累积效应**：论文没在多头多层情况下给出新定理，附录 E 仅做了讨论。这是未来工作的开放点。

> 📐 **学习建议**：先吃透公式 1（RoPE product 定义）+ 公式 2（CLT 近似）这两个基础；然后看公式 3 的概率推导就能复现 Theorem 1。如果你想用代码验证，可以写一个 `compute_rope_product(q, k, m, theta, h)` 函数 + Monte Carlo 模拟，30 行 Python 就能跑出和论文一致的曲线。
