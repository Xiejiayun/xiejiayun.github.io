# 概念卡片 · The Sigmoids Won't Save You

> 每张卡片 30-60 字，关键概念压缩到可口袋化。

---

## 1. Sigmoid（S 形曲线）
形如 1/(1+e^-x) 的有界增长曲线。前半段近似指数，后半段渐进饱和。**所有有限世界里的实数增长过程最终都会 sigmoid——但这不等于"明天就会"。**

## 2. 「All exponentials eventually become sigmoids」
当下最流行的 AI 怀疑论修辞底牌。数学上为真，但作为预测无意义——它没有指定拐点时间。Scott Alexander 用本文证明：**这句话的杀伤力建立在听众不会要求你做区间预测的默契上。**

## 3. Sigmoid 误判名人堂
Scott 列出的三个翻车案例：
- 🥉 UN 生育率预测（每年画钩，实际穿钩）
- 🥈 WEO 太阳能装机（15 条预测全错向同一方向）
- 🥇 Wharton arXiv:2602.04836（用 AIC 选 sigmoid，3 个月被 Mythos 打脸）

## 4. Lindy's Law（Lindy 律）
**一个不会自然死亡的过程，已经存续多久，就还能再存续多久。** 数学推导基于"你正好在历史拐点这一刻"的先验极小。本文把它作为 AI 黑盒预测的默认先验提出来——这是文章最原创的一击。

## 5. AI scaling era
通常回溯到 2019（GPT-2 前夕），到 2026-05 已持续 ~7 年。按 Lindy 律的中位估计，AI 增长再持续 7 年是默认。在 Pareto 假设下，未来 2 年内崩盘概率约 22%——**显著低于普通读者直觉**。

## 6. METR（Model Evaluation & Threat Research）
非营利评测组织，维护"AI 能独立完成的任务时长"指标。曲线从 2019-2025 近似指数，~7 个月翻倍。**本文头号反例就是基于这条曲线的 Wharton sigmoid 拟合**。

## 7. AIC（Akaike Information Criterion）的滥用
AIC 是样本内拟合优度判据，**对外推预测几乎无意义**。Wharton 论文用 AIC 选了 sigmoid 为 best fit，但 sigmoid 在含拐点的样本内 always 占便宜。这是预测建模 101 反例。

## 8. Doomsday 论证 / Copernican 原理
"我恰好处在历史转折点这一刻"是统计上的极小先验事件。Sigmoid 论者隐式假设了这一点而不自知。这层批评与 Doomsday 论证、Copernican 原理同源。

## 9. 反转举证 dichotomy（Scott 的杀招）
强制对手二选一：
- A. 走 explicit 模型 → 摆出 capex、算法、scaling exponent 假设
- B. 走黑盒 → 服从 Lindy 律
不能两者皆否。这把对手从"我有更好的直觉"舒适区里拽出来。

## 10. Paradigm pipeline（技术代际链）
飞行器速度曲线由螺旋桨+涡喷+冲压三代 sigmoid 拼接而成，整体仍近指数。AI 同理——**就算 transformer 范式 sigmoid 了，diffusion LLM、神经符号、世界模型还可能接力**。让 AI 整体停下来的不是单条 sigmoid，而是 paradigm pipeline 枯竭——史无前例。

## 11. 点预测 vs 区间预测的认识论责任
**点预测是不可证伪的修辞，区间预测才有认识论责任。** Sigmoid 论者拒绝给出拐点的概率分布——一旦给出，他们就要为分布形状负责。这是 Scott 隐含的最佳实践建议。

## 12. 「算力市场 sigmoid ≠ 能力曲线 sigmoid」
中文圈常用 NVIDIA 估值回调来论证 AI 能力 sigmoid，这是范畴错误。商业周期可以用经济学模型预测，技术轨迹必须走 Lindy 或 explicit 模型。**两条曲线在历史上经常背道而驰。**
