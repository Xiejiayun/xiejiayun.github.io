# 关键公式解读 · SU-01 数学装置

本页把 SU-01（arXiv 2605.13301）核心训练目标用 KaTeX 形式列出，并附人话解释。所有符号沿用论文记号。

---

## 1. 反向 PPL 课程评分

对每条 SFT 样本 $(x_i, y_i)$，用 SFT 起点策略 $\pi_0$ 计算长度归一化困惑度：

$$
\mathrm{PPL}(x_i, y_i) \;=\; \exp\!\Big(-\tfrac{1}{T_i}\sum_{t=1}^{T_i} \log \pi_0(y_{i,t} \mid x_i, y_{i,<t})\Big)
$$

**人话**：模型读起来越"陌生"的轨迹 PPL 越高。SU-01 反过来把高 PPL 样本放到 epoch 前段先教（hard → easy），尾段做低 PPL 巩固。论文消融表明这一序列把答案精度 39.5→55.8，并把"无尽推理"截断率从 8% 压到 0.3%。

---

## 2. 群体相对优势（GSPO，去 σ 化）

每个 prompt $q$ 采样 $K$ 条 rollout $\{o_1, \ldots, o_K\}$，得到组内基线均值：

$$
\hat A_i \;=\; r(q, o_i) \;-\; \tfrac{1}{K}\sum_{j=1}^{K} r(q, o_j)
$$

**人话**：每条 rollout 的优势 = 自身奖励 − 同组平均。和原始 GRPO 区别：**不除标准差**——σ 在小组规模下噪声大，反而扰乱长 CoT 的方向。

---

## 3. 序列级重要性比

$$
s_i(\theta) \;=\; \exp\!\Big\{\tfrac{1}{|o_i|}\sum_{t=1}^{|o_i|} \log\tfrac{\pi_\theta(o_{i,t} \mid q, o_{i,<t})}{\pi_{\theta_\text{old}}(o_{i,t} \mid q, o_{i,<t})}\Big\}
$$

**人话**：传统 PPO 在每个 token 上做重要性采样比，长 CoT 会指数爆炸。GSPO 把比值做长度平均放到指数上——一条 100K-token 的证明也只产生一个标量比值，与 MoE 路由器 + 长度相容。

---

## 4. Coarse RL · GSPO 目标 (Eq. 1)

$$
\mathcal{J}_{\text{GSPO}}(\theta) \;=\; \mathbb{E}_{q, \{o_i\}}\!\left[\frac{1}{K}\sum_{i=1}^{K} \min\!\Big(s_i(\theta)\,\hat A_i,\;\mathrm{clip}\!\big(s_i(\theta), 1-\epsilon, 1+\epsilon\big)\,\hat A_i\Big)\right]
$$

参数：$\epsilon = 10^{-3}$，KL 系数 0，熵系数 0，每个 rollout 做 4 次策略更新，对称裁剪。MoE 路由器**冻结**——保证回放轨迹仍按训练时同样的专家路由评估。

---

## 5. Refined RL · 混合重放目标 (Eq. 2)

$$
\mathcal{J}_{\text{refined}}(\theta) \;=\; (1-\rho)\,\mathbb{E}_{\mathcal{B}_{\text{fresh}}}\!\big[\mathcal{J}_{\text{GSPO}}(q, G_q; \theta, \pi_{\theta_\text{old}})\big] \;+\; \rho\,\mathbb{E}_{\mathcal{B}_{\text{exp}}}\!\big[\mathcal{J}_{\text{GSPO}}(q^*, \{o^*\} \cup G_{q^*}; \theta, \pi_{\theta_\text{src}})\big]
$$

- $\rho = 0.25$：每个 batch 中 25% 来自经验重放，75% 来自新鲜 on-policy rollout。
- $\pi_{\theta_\text{src}} = \pi_{\theta_\text{past}}$：重放轨迹按生成时的旧策略计算 importance ratio，避免分布漂移。
- 重放轨迹选择：
$$
o^* \;=\; \arg\min_{o \in \mathcal{E}(q^*)} \; \mathcal{H}(o; \pi_\theta)
$$
熵 $\mathcal{H}$ 用 SGLang 提供的 top-16 log-probs 估计。**人话**：从同一道难题的历史成功证明里，挑当前策略**最确定**那一条做"教科书"。

---

## 6. 重放缓冲准入 / 退役条件

- **准入**（hard-but-solvable）：当前组内成功数 $n^+(q)$ 满足
$$
0 < n^+(q) < 2
$$
即至少有一条成功（说明题目可解），但成功数 ≤1（说明还不熟）。
- **退役**：当 $n^+(q) \geq 4$（成功率 ≥ 50%），题目从重放池删除——已经学会。

---

## 7. 自精修（Self-Refinement）触发

若组内平均奖励
$$
\bar r(q) \;=\; \tfrac{1}{K}\sum_{i=1}^K r(q, o_i) \;<\; \tau_{\text{ref}} = 0.5
$$
则把组内失败 rollout 改造为"原题 + 错误草稿 + 修正指令"的新 prompt，按比例 $\eta_{\text{ref}} = 0.20$ 注入后续 batch。**注意**：失败的修正**不再递归**入队——避免在不可学的难题上死循环。

---

## 8. Test-Time Verify–Refine 控制律

对每道题 $q$ 启动最多 $\mathrm{MAX\_RUNS} = 10$ 条独立并行运行；每条运行内部执行：

```
for round in 1 .. MAX_EXPLORATION_ROUNDS (=30):
    draft  ← Solver(q, history)
    draft' ← Refiner(draft)
    bug    ← Verifier(draft')
    if bug == "no critical issues":
        success_streak += 1
        if success_streak == MAX_VERIFICATION_TRUE_ROUNDS (=5):
            return ACCEPT
    else:
        fail_streak += 1
        if fail_streak == MAX_VERIFICATION_FALSE_ROUNDS (=10):
            return ABORT
```

实测每道题中位生成 token：solver 106K, refiner 83K, verifier 28.7K, verdict 404 tokens。

---

## 9. 推理奖励反 hacking 的预处理

设原始 rollout $o$ 的解析结果为 $\mathrm{parse}(o)$。当
- $o$ 含泄漏的 chat template token、或
- `\boxed{}` 不闭合、或
- 极端重复（n-gram 重复率超阈），

则用占位答案替换 $o$ 后再喂给 DeepSeekMath-V2 judge。**人话**：不让模型靠"把 judge 输入弄歪"获得奖励——这是论文显式承认的"还没完全解决但有缓解"的攻击面。

---

## 10. 与 GRPO / PPO 的简表对比

| 维度 | PPO | GRPO (DeepSeek) | **GSPO (SU-01)** |
|------|-----|-----------------|------------------|
| 优势基线 | learned value | group-mean / std | **group-mean only** |
| 重要性比 | per-token | per-token | **per-sequence (length-norm)** |
| 裁剪粒度 | token | token | **sequence** |
| KL 项 | 显式 | 显式 | **0** |
| MoE 长 CoT 友好 | 否 | 一般 | **是** |

> 论文不写"GSPO is novel"——它来自 Zheng et al., 2025。SU-01 的贡献是**首次把 GSPO + 反向 PPL 课程 + 生成式 judge + verify-refine TTS** 串成一条 200 步就能复现的开放配方。

---

## 11. 数据资产汇总

- SFT 总轨迹：**338,409** 条（数学 71.8K + STEM 62.9K + 代码 30.2K + IF 18.8K + Self-Verify 89.5K + Self-Refine 65.2K）
- Coarse RL 题库：**8,967** verifiable prompts
- Refined RL 题库：**16,287** proof prompts（含 Open Proof Corpus 子集）

> 论文链接：<https://arxiv.org/abs/2605.13301>  
> 代码 / 模型：见论文项目页（论文称已开源 code + models）
