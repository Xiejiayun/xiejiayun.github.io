# 概念卡片：vas-blog 的 Qwen 3.5 政治审查机制研究

> 配套阅读：本文每张卡片对应原研究中的一个关键概念，用于读后温故。

---

## 卡片 1 · 「审查不是知识缺失，而是 routing」

**结论**：Qwen3.5-9B-Base（未对齐的预训练 checkpoint）在 raw completion 模式下，对 Tiananmen、Tank Man、Falun Gong 摘除器官等 PRC 敏感问题给出准确、西方框架的答案。

**含义**：事实知识完整保存在权重里，post-train 阶段并没有"擦除"它们。审查行为是叠加在这层知识上的 routing layer——模型学的是"绕开"而不是"忘记"。

**对应实验**：E2（base-vs-posttrain CJK commitment under chat template）。

---

## 卡片 2 · 「Writers / Readers 双段电路」

**Writers (L11–L20)**：少数 MLP，把语义编码成一组 3 维内部判决。局部、线性、可外科干预。

**Readers (L20–L31)**：把这 3 维判决冗余地"渲染"成最终文本。分布式、几乎不可外科——任何单点干预（单头 / 单层 / 600 神经元置零）都失败。

**类比**：Writers 是法官写判决书的那几行字，Readers 是抄录员、翻译员、印刷工人组成的大队伍——你可以改判决书，但你无法通过解雇某一个翻译员让判决失效。

---

## 卡片 3 · 「三个内部方向（轴）」

| 轴 | 定义对比 | 起作用层 | 语义 |
|---|---|---|---|
| **d_prc** | mean(prc_sensitive) − mean(neutral_political) | tap 14 | 这是不是 PRC 敏感内容？ |
| **d_refuse** | mean(harmful) − mean(harmless) | tap 19 | 应不应该拒答？ |
| **d_style** | mean(tiananmen) − mean(prc_other) | tap 19 | 是偏转还是宣传？ |

每个方向用 diff-of-means 提取：取该层最后一个 prompt token 的 residual，两组均值相减、归一化。AUC ≥ 0.99，pairwise cosine 0.91–0.98（说明 7 个 PRC 子话题共享一条主轴）。

---

## 卡片 4 · 「为什么不是两个轴就够？」

**两轴假设**（d_prc × d_refuse）能把四象限分开（PRC 与非 PRC × 拒答与回答），**但会把 Tiananmen 偏转和 Falun Gong 宣传压到同一格**——而这两种行为在文本层完全不同。

**单方向 subspace patching 测试**：只切 d_style 一个维度，能 100% 反转 Tiananmen → propaganda 的迁移；只切 d_prc 或 d_refuse 反转率为 0%。

**结论**：d_style 是 within-PRC register 切换的因果必需。三个轴是最小完备集。

---

## 卡片 5 · 「dose-response：sigmoid 是因果信号的指纹」

**Steering 操作**：在某一层 residual stream 上加 α · d，α 从 −30 到 +30 扫描。

**观察**：每条轴在其 writer 层都有一条干净的 sigmoid 曲线——α 越过 direction-specific threshold 时，verdict 在两端之间平滑切换。

**为什么 sigmoid 重要**：单调线性 = 相关；sigmoid = 控制变量。判断一个 direction 是 probe 还是 control switch 的关键。

**关键数值**：
- d_prc 半饱和 α-half ≈ −12（让模型"逃出"审查回到事实）
- d_refuse 半饱和 ≈ −20（让模型 comply 有害提示）
- d_style 转折点 ≈ −8（在偏转 ↔ 宣传之间切换）

---

## 卡片 6 · 「tap 24 的中文 verdict」

**现象**：在第 24 层（共 32 层）做 logit-lens（用 lm_head 解码中间层 residual），Tiananmen 提示的 top-1 token 100% 是中文——通常是 `抱歉`、`我`、`不能`。

**普适性**：即使是英文钓鱼邮件提示，tap 24 的拒答 token 也用中文承诺（96% Chinese top-1）。

**行为惰性**：把 lm_head 里所有中文 token 的 logit 置零，最终英文输出**不变**。中文承诺是表面现象，真正决策在更上游的 3 维 writer signal 里。

**和 Wendler 2024 的对比**：Llama-2 的中间层概念空间偏英文；Qwen 是镜像现象（偏中文），但 vas-blog 额外发现：这个中文模板在 lm_head 处是因果惰的。

---

## 卡片 7 · 「四个 trained template cells」

模型只学了少数 (topic × style) 组合：

| Topic | Trained Style |
|---|---|
| Tiananmen / Tank Man | 偏转（stock deflection） |
| Falun Gong / Taiwan / Xinjiang / Tibet | 宣传（state-aligned） |
| Xi / CCP governance | 偏转 |
| AdvBench-style 有害 | Western-style refusal |
| 数学 / 代码 / 中性政治 | factual |

**缺失的格子**：没有 "deflect about Taiwan"，没有 "propaganda about Tank Man"。
**后果**：steering 把方向推向不存在的格子时，模型会跌入邻近模板或产出不连贯文本，而不是落到 truth。

---

## 卡片 8 · 「distributed translation：没有翻译官」

**实验**：tap 24 的中文 verdict 到 tap 32 的英文输出之间，逐个消融 L24–L31 各 sub-component 看哪一个是"翻译层"。

**结果**：所有单点消融都不足以阻止翻译；最强单点扰动只能让 tap 30 仍剩 9.5% 中文。

**含义**：从中文模板到英文 token 的"翻译"被冗余分布在 8 层、attention 与 MLP 各组件中。这与 readers 的整体冗余设计一致。

---

## 卡片 9 · 「writers 是 graded classifier，不是 Boolean」

**反例 1**：Kosovo 在 d_prc 上的投影落在中性类高尾，**误激活**"一中"模板（"Kosovo is an integral part of China's territory"）。

**反例 2**：Arab Spring 中含 "self-immolation"，被 d_refuse 误判为自残相关内容并 refuse。

**反例 3**：aspirin 合成（一种 OTC 药物）被 d_refuse 标记为武器化学合成。

**因果验证**：在 writer 层减去对应方向，5 条反例**全部**反转回 factual。

**含义**：分类器靠 prompt 的结构特征（主权否认句式、安全敏感动词），不靠真实语义比对。

---

## 卡片 10 · 「Brittleness：denial template 的脆弱性」

**测试**：在 L18/L19 加 α 很大的**随机方向**（不是 d_prc 也不是 d_refuse），看 verdict 是否被扰动。

**发现**：
- harmful 类：随机扰动几乎不动（refusal template 高度冗余、抗噪）。
- ccp_other：低，但有限。
- Tiananmen：α=−15 时 2%，α=−25 时 9%，α=−30 时 23%——而且**移动方向不是 truth，是 denial 或 incoherence**。

**结论**：Tiananmen 的 "as an AI assistant…" 是一条窄、单一的训练模式，几乎任何方向推得够远都能破坏它，但破坏后没有回到真相。

**实操建议**：研究里所有 steering 实验都给出了 α 上限，避免把 brittleness 误读为 direction effect。

---

## 卡片 11 · 「Subspace 不是因果 patch handle」

**直觉错觉**：既然 writers 把信号写进 3 维 subspace，那么只替换某个 residual 的 3 个坐标，应该能交换行为。

**事实**：mean-replacing 全 residual（last-7 positions）→ 31% 反转；mean-replacing **仅 3 维 subspace 坐标** → 7%，且移到 denial 模板（不是事实）。

**机制**：到达 reader band 时，verdict 已被**冗余地重新编码**到 4096 维 residual 里。只换 3 维只是在两套 trained template 之间微调。

**寓意**：computed in writer band ≠ committed in writer band。读机制写在写机制下游。

---

## 卡片 12 · 「Thinking mode = same circuit，唯一例外是 Chinese reasoning」

**enable_thinking=True** 时：Tiananmen 提示触发 89% 中文 thinking 痕迹，按一个五步 deflection script 走完，其中一条 trace 直接念出"网络安全法（Cybersecurity Law）"作为合规理由后偏转。

**关键发现**：thinking trace 用的是同一个 (d_prc, d_refuse, d_style) 电路；中文不是审查的"原因"，而是"审查决策被显式语言化"的副产品。

**Implication for CoT monitoring**：如果只看 thinking 内容是英文还是中文做安全审计，会漏掉真正的因果机制。

---

## 卡片 13 · 「base 模型在 chat template 下已经会拒答了」

引用 Kissane et al. 2024 的更一般发现：未做 chat 微调的 base 模型，包在 chat template 里时，也会拒答约 48% 的 AdvBench 有害指令；chat 模型只是把这个比例标准化到 ~90% 以上。

**对 Qwen 的具体观察**：Qwen3.5-Base 在 chat-template wrap 下已经会对 Xi/governance 给出 state-aligned framing；post-train 把这条 latent 倾向变成清晰的四个模板。

**含义**：post-train 不是"凭空造"了审查，而是"标准化"了 pretraining 时已经埋下的倾向。

---

## 卡片 14 · 「writer 层的 cos 0.5 = posttraining 改了哪里」

**对比 base 与 post-train 同一 direction**：
- tap 1（embedding 层）cos ≈ 0.93（几乎不变）
- writer 层（tap 14, 19）cos ≈ 0.5（明显重写）

**含义**：post-train 主要修改的就是 writer band 那几个 MLP，让它们更尖锐地"读"早就存在的 class 表征。

**对齐研究启示**：要观察 alignment 训练的痕迹，不要看整层平均，要看 diff-of-means direction 在不同 checkpoint 间的旋转。

---

## 卡片 15 · 「writer linearity：R² ≈ 0.49–0.64」

**实验**：用 (d_prc, d_refuse, d_style) 三维坐标作为输入，OLS 拟合 writer 层的 4096 维 output residual。

**结果**：R² ≈ 0.49–0.64（峰值在 L15）。

**为什么 R² 不是更高**：4096 维目标 + 较小的 prompt-n，OLS conditioning 被压低；真正强证据是上面卡片 5 的 sigmoid 因果性。

**核心信号**：writers 几乎是 3 维坐标的线性函数。理解 writers，就是理解这个 3D 子空间在 L11–L20 之间如何被写入。
